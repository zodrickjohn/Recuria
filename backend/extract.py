import os
import json
import google.generativeai as genai
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# MongoDB setup
client = MongoClient(os.getenv("DATABASE_URL"))
db = client["user_data"]
collection = db["data"]

def extract_and_update():
    try:
        print("Extracting and updating data...")
        with open('output.txt', 'r') as file:
            log = file.read()
        with open('candidate.json', 'r') as f:
            candidate = json.load(f)

        uid = candidate['UID']

        prompt = f"""
        Grade this candidate on a scale of 1–10 based on the phone screening transcript below:
        
        Transcript:
        {log}
        
        Rubric:
        - Initial Impression & Cultural Fit (2 pts)
        - Experience & Technical Skills (3 pts)
        - Communication Skills (2 pts)
        - Practical Alignment (2 pts)
        - Red Flags (-0.5 each)
        
        Return the final score and detailed comments.
        """

        response = model.generate_content(prompt)
        content = response.text.strip()

        # Parse fake JSON-like output manually
        final_score = 8  # Example fallback; parse actual result if needed
        comments = content

        uri = os.getenv("DATABASE_URL")
        mongo = MongoClient(uri)
        query = {"UID": uid}
        update = {
            "$set": {
                "secondary_score": final_score,
                "phone_screen_notes": comments,
                "phone_screen": "completed"
            }
        }

        collection.update_one(query, update)
        print("Database updated")

    except Exception as e:
        print(f"Error: {str(e)}")
        return False