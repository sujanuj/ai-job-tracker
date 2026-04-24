# AI Job Tracker — Intelligent Job Application Management System

A full-stack AI-powered job application tracking system built as a personal tool during my M.S. in Software Engineering at Arizona State University. The application combines a structured job management pipeline with GPT-4o-mini to automate resume analysis, job description matching, cover letter generation, and interview preparation — reducing the manual overhead of a technical job search.

**Live Application:** [https://ai-job-tracker-413l.onrender.com](https://ai-job-tracker-413l.onrender.com)  
**GitHub Repository:** [https://github.com/sujanuj/ai-job-tracker](https://github.com/sujanuj/ai-job-tracker)

---

## Motivation

Managing a graduate-level job search involves tracking dozens of applications, tailoring resumes to individual job descriptions, writing personalized cover letters, and preparing for role-specific technical interviews — all simultaneously. Existing tools like Notion or spreadsheets handle tracking but offer no AI-assisted content generation. This project integrates both: a structured application tracker backed by a relational database, and an AI layer that generates actionable, context-aware content for each application.

---

## System Overview

The application is a Flask-based REST API that serves a single-page frontend. User authentication is handled via token-based sessions. Job applications are stored in a SQLite database with full CRUD support. All AI features call OpenAI's `gpt-4o-mini` model with carefully engineered prompts that return structured JSON or formatted text, which the frontend parses and renders dynamically.

---

## Features

**Job Application Tracker**  
Full create, read, update, and delete functionality for job applications. Each entry stores company name, role, application status (Applied / Interview / Rejected), job link, notes, and deadline. A visual analytics dashboard displays application distribution across statuses using a donut chart rendered with Chart.js. Deadline alerts surface overdue applications automatically on page load.

**AI Resume Analyzer (ATS Optimization)**  
Users paste their resume text and a target role. The system prompts GPT-4o-mini to score the resume out of 100 for ATS compatibility, identify missing keywords, suggest general improvements, and propose stronger bullet point rewrites. The response is parsed and rendered as a structured analysis panel.

**Job Description Matcher**  
Given a resume and a job description, the model returns a structured JSON object containing a match score, keyword score, matched skills, missing keywords, strengths, weaknesses, and tailored suggestions. This gives users a quantitative signal of fit before applying and highlights gaps to address.

**Resume Optimizer**  
The system rewrites the user's resume specifically for a target job description, returning an optimized summary section, improved experience bullet points, and a complete ATS-optimized resume draft. Output can be downloaded as a PDF via html2pdf.js.

**Cover Letter Generator**  
Users select a writing tone (Professional, Enthusiastic, or Concise) and provide their resume alongside the job description. The model generates a fully personalized cover letter under 350 words, written in flowing paragraphs without generic placeholders, using specific achievements from the resume that match the role requirements.

**Interview Prep AI**  
Given a target role and optional job description, the system generates five technical questions and five behavioral questions with model answers. Technical answers are concise and practical; behavioral answers follow the STAR format. Results are rendered as expandable cards for study.

**Analytics Dashboard**  
A Chart.js donut chart visualizes application status distribution in real time. Application counts for Applied, Interview, and Rejected statuses update dynamically as the user manages their pipeline.

**User Authentication**  
Register and login with username/password. Sessions are maintained via localStorage tokens. All job data is scoped per user through a user_id foreign key.

---

## Technical Architecture

```
┌──────────────────────────────────────────────────┐
│               Frontend (Single Page)             │
│        Vanilla JS + Chart.js + html2pdf.js       │
└───────────────────┬──────────────────────────────┘
                    │ HTTP/REST
┌───────────────────▼──────────────────────────────┐
│              Flask REST API (Python)              │
│                                                  │
│  ┌────────────┐   ┌──────────────────────────┐  │
│  │ Auth Routes│   │     AI Feature Routes    │  │
│  │ /login     │   │ /analyze  /match-job     │  │
│  │ /register  │   │ /optimize-resume         │  │
│  └────────────┘   │ /generate-cover-letter   │  │
│                   │ /interview-prep          │  │
│  ┌────────────┐   └──────────────────────────┘  │
│  │ Job CRUD   │                                  │
│  │ /add-job   │   ┌──────────────────────────┐  │
│  │ /jobs      │   │   SQLAlchemy ORM         │  │
│  │ /edit-job  │   │   User | JobApplication  │  │
│  │ /delete-job│   └──────────────────────────┘  │
│  └────────────┘                                  │
└──────────────────────────────────────────────────┘
                    │
              OpenAI API
              (GPT-4o-mini)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10, Flask 3.x |
| ORM | Flask-SQLAlchemy, SQLite |
| AI | OpenAI Python SDK, GPT-4o-mini |
| Frontend | Vanilla HTML / CSS / JavaScript |
| Charts | Chart.js |
| PDF Export | html2pdf.js |
| CORS | Flask-CORS |
| Deployment | Render, GitHub |

---

## Data Models

```python
User             # id, username, password
JobApplication   # id, company, role, status, user_id, link, notes, deadline
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| POST | `/register` | Register new user |
| POST | `/login` | Authenticate user |
| POST | `/add-job` | Add job application |
| GET | `/jobs` | Get all jobs for user |
| PUT | `/update-status/:id` | Update application status |
| PUT | `/edit-job/:id` | Edit job details |
| DELETE | `/delete-job/:id` | Delete application |
| POST | `/analyze` | ATS resume analysis |
| POST | `/match-job` | Resume vs job description match |
| POST | `/optimize-resume` | AI resume rewriter |
| POST | `/generate-cover-letter` | Cover letter generator |
| POST | `/interview-prep` | Interview Q&A generator |
| GET | `/` | Serve frontend |

---

## Local Development Setup

Prerequisites: Python 3.10+, pip, OpenAI API key.

```bash
# Clone the repository
git clone https://github.com/sujanuj/ai-job-tracker.git
cd ai-job-tracker/backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
nano .env
```

Add the following to `.env`:

```
OPENAI_API_KEY=sk-your-openai-key-here
```

```bash
# Run the development server
python app.py
# Application available at http://localhost:10000
```

---

## Deployment

Deployed on Render as a Web Service connected to the GitHub repository with automatic deploys on push to main.

| Setting | Value |
|---|---|
| Root Directory | `backend` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app` |
| Python Version | 3.10 |

Required environment variable: `OPENAI_API_KEY`

The free tier on Render spins down after 15 minutes of inactivity, causing approximately 50 seconds of cold start latency on the first request. Setting up a free monitor on UptimeRobot to ping the service every 5 minutes keeps the instance continuously available.

---

## AI Prompt Engineering

Each AI feature uses a carefully structured prompt designed to return consistent, parseable output:

The resume analyzer and job matcher use strict JSON return format instructions to ensure the frontend can reliably parse structured data (scores, arrays of keywords, lists of suggestions) without fragile regex parsing.

The resume optimizer and cover letter generator return formatted text with clearly labeled sections, allowing the frontend to render them directly without additional processing.

The interview prep endpoint strips markdown fences from the response before JSON parsing, since GPT-4o-mini occasionally wraps JSON responses in code blocks despite explicit instructions to the contrary.

---

## Dependencies

```
flask
flask_sqlalchemy
flask_cors
flask_jwt_extended
python-dotenv
openai
gunicorn
```

---

## Limitations and Future Work

The current authentication implementation stores passwords in plaintext and uses a static dummy token rather than real JWT generation — this is a known gap that would be resolved with bcrypt hashing and proper Flask-JWT-Extended token issuance before any public multi-user deployment.

All job data is currently scoped to a hardcoded `user_id = 1` in several routes, meaning the multi-user architecture is partially implemented but not fully enforced. Completing the JWT integration would resolve this.

Planned extensions include LinkedIn job scraping to auto-populate application details, email reminders for upcoming deadlines, resume version history with diff comparison, and a salary negotiation assistant feature.

---

## Project Structure

```
ai-job-tracker/
├── backend/
│   ├── app.py            # Flask application, all routes and AI logic
│   ├── index.html        # Single-page frontend
│   ├── requirements.txt  # Python dependencies
│   ├── runtime.txt       # Python version specification
│   └── instance/
│       └── jobs.db       # SQLite database (auto-created)
├── .gitignore
└── README.md
```

---

## Author

**Sujan Uppalli Jayadevappa**  
M.S. Software Engineering — Data Science Specialization  
Arizona State University, Tempe, AZ  
Expected Graduation: December 2026

[LinkedIn](https://www.linkedin.com/in/sujan-uppalli-jayadevappa-504b721b9/) • [GitHub](https://github.com/sujanuj) • supalli@asu.edu
