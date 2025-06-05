# 🤖 Recuria – AI-Powered Multi-Agent Recruitment Assistant

Recuria is a smart web application designed to revolutionize the traditional hiring process using a modular, multi-agent AI system. It simplifies resume screening, automates interviews, performs emotion analysis, and sends selection/rejection emails — all in one platform.

---

## 📌 Introduction

Recruitment often involves sifting through hundreds of resumes, conducting repetitive interviews, and manually handling candidate communication. **Recuria** solves this by acting as an intelligent hiring assistant that helps HR teams make **faster**, **smarter**, and **bias-free** hiring decisions.

![1](/1.png)
![2](/2.png)
![3](/3.png)
![4](/4.png)
![5](/5.png)
![6](/6.png)

---

## ⚙️ How It Works

### 🧑‍💼 Step 1: Resume Screening
- Recruiter enters a **Job Description**
- Uploads multiple **CVs**
- AI scores and ranks CVs based on relevance

### 📞 Step 2: Telephonic Interview (Automated)
- AI agent places calls using pre-fed or AI-generated questions
- Transcribes and evaluates candidate responses
- Ranks candidates based on verbal answers

### 🎥 Step 3: Video Interview
- In-app video interview with transcription + emotion & tone analysis
- Generates a detailed candidate interaction report

### 📧 Step 4: Final Decision & Communication
- Recruiter reviews all stages + cumulative scores
- AI drafts personalized email templates
- Sends selection/rejection emails

---

## 🧰 Tech Stack

| Layer              | Technology Used                                    |
|-------------------|-----------------------------------------------------|
| **Frontend**       | ReactJS, Tailwind CSS, Next.js                     |
| **Backend**        | Python (FastAPI / Flask)                           |
| **NLP & Scoring**  | OpenAI GPT-4, LangChain, Sentence-BERT             |
| **Speech & Voice** | Twilio, Google STT, Whisper, ElevenLabs            |
| **Emotion Analysis** | RAVDESS-trained models, OpenFace, BERT           |
| **Database**       | MongoDB, PostgreSQL                                |
| **Email**          | SMTP, SendGrid, Nodemailer                         |
| **Deployment**     | Docker, Render, Vercel, GitHub Actions             |

---

## ✅ Feasibility Analysis

| Aspect                 | Feasibility Level | Notes                                                                 |
|------------------------|------------------|-----------------------------------------------------------------------|
| **Technical**          | ✅ High           | All APIs and models are production-ready or open-source               |
| **Operational**        | ✅ Medium-High    | Seamlessly fits into existing HR workflows                            |
| **Financial**          | ✅ Moderate       | MVP can run on free-tier services and low-cost APIs                   |
| **Scalability**        | ✅ High           | Microservice-based + Dockerized for cloud-native deployments          |
| **User Acceptance**    | ✅ High           | Saves recruiter time, improves hiring quality, and reduces human bias |

---

## Dashboard page

 - ### Dashboard page view
![1](/dashboard1.png)

 - ### Add Candiadte
Upload candidate's resumes
![2](/upload.png)

 - ### Candidates whose resumes are uploaded
![3](/candidates.png)

 - ### More info option
Shows brief summary in form of academic information, professional details, contact information and evaluation details
![4](/moreinfo.png)

 - ### Resume attribute from more info option
Shows the resume of the given candidate
![5](/resume.png)

 - ### Ask AI attribute from more info option
Ask any question about the given candidate's background, experience, or qualifications, etc which are mentioned in its resume
![6](/askai.png)

### Features in Developemnt
 - Calling the candidate with its given phone no. in resume and ask him/her questions regarding job and evaluating them

### Pending Features 
 - Making an video call to candidate and evaluating them based on tone and emotion analysis while answering the HR's questions
 - Publishing the final report to the user containing the final of the candidate ( resume + call interview + video call interview )
 - Sending e-mails to the selected candidates

---

## 🚀 Getting Started

1. Clone the repo  
   ```bash
   git clone https://github.com/your-username/recuria.git
   cd recuria
   ```

---

## Note
The project is in development stage
