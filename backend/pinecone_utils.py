import pymongo
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
import google.generativeai as genai
import json
from PyPDF2 import PdfReader
import re

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize MongoDB connection
client = pymongo.MongoClient(os.getenv("DATABASE_URL"))
db = client["user_data"]
collection = db["data"]

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Connect to existing index or create one if needed
INDEX_NAME = "hoyahacks"

if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=384,  # Match 'all-MiniLM-L6-v2' embedding size
        metric='cosine',
        spec=ServerlessSpec(cloud='aws', region='us-east-1')
    )

index = pc.Index(INDEX_NAME)


# Local Embedding Model (Free & Offline)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')


def embed_query(text):
    """Generate embedding using local model"""
    return embedding_model.encode(text).tolist()


def generate_candidate_justification(metadata, query):
    """Use Gemini Flash instead of GPT-3.5-turbo"""
    try:
        prompt = f"""
        You are a professional recruiter evaluating this candidate based on the following details.

        Candidate Name: {metadata.get('name', 'Unknown')}
        Education: {metadata.get('education', 'N/A')}
        Skills: {metadata.get('skills', 'N/A')}
        Experience: {metadata.get('experience_years', 0)} years
        Notes: {metadata.get('full_text', 'N/A')}

        Search Query: {query}

        Write a concise justification explaining why this candidate is a strong match.
        """
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Unable to generate justification: {str(e)}"


def create_searchable_text(resume_entry):
    """Create a searchable text string from resume fields."""
    search_fields = [
        resume_entry.get('name', ''),
        resume_entry.get('education', ''),
        resume_entry.get('technical_skills', ''),
        resume_entry.get('notes', ''),
        str(resume_entry.get('graduation_year', '')),
        str(resume_entry.get('yoe', ''))
    ]
    return ' '.join(filter(bool, search_fields))


def upsert_resume_vectors():
    """Generate embeddings and upsert into Pinecone using local embeddings"""
    vectors_to_upsert = []

    for entry in collection.find():
        search_text = create_searchable_text(entry)
        vector = embed_query(search_text)

        vectors_to_upsert.append({
            "id": str(entry['_id']),
            "values": vector,
            "metadata": {
                "uid": entry.get('UID', ''),
                "id": str(entry['_id']),
                "name": entry.get('name', ''),
                "skills": entry.get('technical_skills', ''),
                "education": entry.get('education', ''),
                "graduation_year": entry.get('graduation_year', ''),
                "experience_years": entry.get('yoe', 0),
                "full_text": search_text
            }
        })

    batch_size = 100
    for i in range(0, len(vectors_to_upsert), batch_size):
        batch = vectors_to_upsert[i:i + batch_size]
        index.upsert(vectors=batch, namespace="resumes")

    print(f"Upserted {len(vectors_to_upsert)} resume vectors")


def advanced_resume_search(query, top_k=5):
    """Search resumes using semantic similarity and generate justifications."""
    try:
        # Generate embedding for the query
        query_embedding = embed_query(query)

        # Perform Pinecone search
        results = index.query(
            vector=query_embedding,
            top_k=top_k * 3,
            include_metadata=True,
            namespace="resumes"
        )

        detailed_matches = []
        for match in sorted(results.get('matches', []), key=lambda x: x.get('score', 0), reverse=True):
            if len(detailed_matches) >= top_k:
                break

            metadata = match.get('metadata', {})
            if match.get('score', 0) > 0.6:
                uid = int(metadata.get('uid', 0))
                justification = generate_candidate_justification(metadata, query)

                detailed_matches.append({
                    "uid": uid,
                    "justification": justification,
                    "relevance_score": match.get('score', 0)
                })

        for match in detailed_matches:
            print(json.dumps(match, indent=2))

        return {"candidates": detailed_matches}

    except Exception as e:
        return {"error": f"An error occurred during search: {str(e)}"}


def delete_all_entries_from_pinecone():
    """Delete all entries from the Pinecone index under the 'resumes' namespace."""
    try:
        namespaces = index.describe_index_stats().get("namespaces", [])
        if "resumes" in namespaces:
            index.delete(delete_all=True, namespace="resumes")
            print("All entries deleted from Pinecone index in 'resumes' namespace.")
        else:
            print("Namespace 'resumes' not found.")
    except Exception as e:
        print(f"Error deleting entries from Pinecone: {str(e)}")


def extract_pdf_text(pdf_path):
    """Extract text content from a PDF file."""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def chat_person(uid, query):
    """Chat with a specific candidate based on their resume and data."""
    try:
        candidate_data = collection.find_one({"UID": int(uid)})
        if not candidate_data:
            return {"error": "Candidate not found"}

        candidate_file = candidate_data.get("file_name")
        if not candidate_file:
            return {"error": "Candidate file name not found"}

        resume_text = extract_pdf_text(os.path.join('resumes', candidate_file))

        candidate_profile = "\n".join([f"{key}: {value}" for key, value in candidate_data.items()])

        prompt = f"""
        Here is the candidate's full profile:
        {candidate_profile}

        Here is the candidate's resume:
        {resume_text}

        Now, answer the following query:
        {query}
        """

        response = gemini_model.generate_content(prompt)
        chat_response = response.text.strip()
        return {"chat_response": chat_response}

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}