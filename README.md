# 🤖 Recuria – AI-Powered Multi-Agent Recruitment Assistant

Recuria is a smart web application designed to revolutionize the traditional hiring process using a modular, multi-agent AI system. It simplifies resume screening, automates interviews, performs emotion analysis, and sends selection/rejection emails — all in one platform.

---

## 📌 Introduction

Recruitment often involves sifting through hundreds of resumes, conducting repetitive interviews, and manually handling candidate communication. **Recuria** solves this by acting as an intelligent hiring assistant that helps HR teams make **faster**, **smarter**, and **bias-free** hiring decisions.

![Demo](/homepage.gif)

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

## 🚀 Getting Started

1. Clone the repo  
   ```bash
   git clone https://github.com/your-username/recuria.git
   cd recuria
   ```

---

## Note
The project is in development stage
