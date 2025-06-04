from PyPDF2 import PdfReader
import re
import os
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Dict
from pymongo import MongoClient
import google.generativeai as genai
import json

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# PDF Text Extraction
def extract_pdf_text(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def save_pdf(source_path, target_folder, new_name):
    os.makedirs(target_folder, exist_ok=True)

    new_name = new_name.replace(" ", "_")
    if not new_name.endswith('.pdf'):
        new_name += '.pdf'

    base, ext = os.path.splitext(new_name)
    counter = 1
    target_path = os.path.join(target_folder, new_name)

    while os.path.exists(target_path):
        new_name = f"{base}_{counter}{ext}"
        target_path = os.path.join(target_folder, new_name)
        counter += 1

    with open(source_path, 'rb') as src, open(target_path, 'wb') as dst:
        dst.write(src.read())

    return new_name


class Result(BaseModel):
    name: str
    graduation_year: int
    years_of_experience: int
    education: str
    gpa: float
    email: str
    phone: str
    initial_score: float
    notes: str
    technical_skills: str


def process_pdf(pdf_path):
    try:
        resume_text = extract_pdf_text(pdf_path)
        with open('job.txt', 'r') as f:
            job = f.read().strip()

        with open('uid_count.txt', 'r') as f:
            uid = int(f.read().strip())

        print("Processing pdf...")

        system_prompt = f"""
        You are part of a HR recruiting team whose job is to extract information from resumes and give an initial score to applicants based on just their resumes.
        
        This is the description of the job that you should use to grade the applicants:
        {job}
        
        The Education section should be filled out in the following format: 
        "<Major> - <University>"
        
        Scoring Rubric:
        - 2 points for relevant work experience that directly aligns with the position's requirements, demonstrating progressive responsibility and quantifiable achievements
        - 2 points for education and certifications that match or exceed the role's prerequisites
        - 2 points for technical skills and competencies specifically mentioned in the job description
        - 1.5 points for clear, professional formatting with no errors, consistent styling, and easy readability
        - 1.5 points for compelling accomplishment statements that use strong action verbs and include measurable results or impacts
        - 1 point for additional relevant elements like volunteer work, leadership roles, or professional memberships
        
        Total score will always be out of 10 points.

        Additionally, summarize and add notes of anything that can help the recruiter make a decision about the applicant.
        """

        user_prompt = f"""
        Extract and score this resume:
        {resume_text}
        """

        response = gemini_model.generate_content(
            contents=[{"role": "user", "parts": [system_prompt, user_prompt]}],
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "graduation_year": {"type": "integer"},
                        "years_of_experience": {"type": "integer"},
                        "education": {"type": "string"},
                        "gpa": {"type": "number"},
                        "email": {"type": "string"},
                        "phone": {"type": "string"},
                        "initial_score": {"type": "number"},
                        "notes": {"type": "string"},
                        "technical_skills": {"type": "string"}
                    },
                    "required": list(Result.__annotations__.keys())
                }
            }
        )

        # Parse JSON manually since we don't have a native model
        applicant_data = json.loads(response.text.strip())
        applicant = type('obj', (object,), applicant_data)

        pdf_name = save_pdf(pdf_path, "resumes", f"{applicant.name}.pdf")

        uri = os.getenv("DATABASE_URL")
        mongo = MongoClient(uri)
        db = mongo['user_data']
        collection = db['data']

        applicant_info = {
            "name": applicant.name,
            "graduation_year": applicant.graduation_year,
            "education": applicant.education,
            "yoe": applicant.years_of_experience,
            "gpa": applicant.gpa,
            "email": applicant.email,
            "phone": applicant.phone,
            "initial_score": applicant.initial_score,
            "notes": applicant.notes,
            "phone_screen": "not completed",
            "status": "new",
            "secondary_score": 0,
            "location": pdf_name,
            "file_name": pdf_name,
            "technical_skills": applicant.technical_skills,
            "UID": uid
        }

        print(applicant_info)
        print("Inserting applicant into db...")
        collection.insert_one(applicant_info)

        with open('uid_count.txt', 'w') as f:
            f.write(str(uid + 1))

        return True

    except Exception as e:
        print(f"Error: {str(e)}")
        return False


if __name__ == "__main__":
    process_pdf("resumes/Ritesh_Thipparthi.pdf")