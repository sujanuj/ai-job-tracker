# 🚀 AI Job Tracker

A full-stack AI-powered job application tracking system built with Flask and OpenAI. Track your job applications, analyze your resume, generate cover letters, and prepare for interviews — all in one place.

**Live Demo:** [https://ai-job-tracker-413l.onrender.com](https://ai-job-tracker-413l.onrender.com)

---

## ✨ Features

| Feature | Description |
|---|---|
| 📋 **Job Tracker** | Add, update, and delete job applications with status tracking |
| 📊 **Analytics Dashboard** | Visual donut chart showing Applied / Interview / Rejected stats |
| ⏰ **Deadline Alerts** | Automatic banner alerts for upcoming and overdue deadlines |
| 🤖 **AI Resume Analyzer** | ATS scoring with missing keywords and improvement suggestions |
| 🎯 **Job Matcher** | Match your resume to a job description with a compatibility score |
| 🔥 **Resume Optimizer** | AI-rewritten resume tailored to a specific job description |
| ✉️ **Cover Letter Generator** | Personalized cover letters in Professional / Enthusiastic / Concise tone |
| 🎤 **Interview Prep AI** | Role-specific technical and behavioral Q&A with model answers |
| 📄 **PDF Export** | Download optimized resume and cover letter as PDF |
| 🔐 **User Auth** | Register and login with session-based token authentication |

---

## 🛠️ Tech Stack

**Backend**
- Python 3.10
- Flask + Flask-SQLAlchemy + Flask-CORS
- SQLite (via SQLAlchemy ORM)
- OpenAI API (`gpt-4o-mini`)
- Gunicorn (production server)

**Frontend**
- Vanilla HTML / CSS / JavaScript (single-file, no framework)
- Chart.js (analytics donut chart)
- html2pdf.js (PDF export)
- Google Fonts (Syne + DM Sans)

**Deployment**
- Render (free tier web service)
- GitHub (auto-deploy on push)

---

## 📁 Project Structure

```
ai-job-tracker/
├── backend/
│   ├── app.py              # Main Flask app — all routes and AI logic
│   ├── index.html          # Frontend UI (served by Flask)
│   ├── requirements.txt    # Python dependencies
│   ├── runtime.txt         # Python version for Render
│   ├── backend/__init__.py # Package init
│   └── instance/
│       └── jobs.db         # SQLite database (auto-created)
```

---

## ⚙️ Local Setup

### Prerequisites
- Python 3.10+
- An OpenAI API key ([get one here](https://platform.openai.com/api-keys))

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/sujanuj/ai-job-tracker.git
cd ai-job-tracker/backend
```

**2. Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Create a `.env` file**
```bash
touch .env
```
Add the following to `.env`:
```
OPENAI_API_KEY=sk-your-key-here
```

**5. Run the app**
```bash
python app.py
```

**6. Open in browser**
```
http://localhost:10000
```

---

## 🌐 Deployment (Render)

This project is deployed on [Render](https://render.com).

### Render Settings

| Setting | Value |
|---|---|
| **Root Directory** | `backend` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |
| **Environment Variable** | `OPENAI_API_KEY` = your key |

### Keep-Alive (Free Tier)
Render's free tier spins down after 15 minutes of inactivity. To prevent this, set up a free monitor on [UptimeRobot](https://uptimerobot.com) to ping your URL every 5 minutes.

---

## 🔌 API Endpoints

| Method | Route | Description |
|---|---|---|
| POST | `/register` | Register a new user |
| POST | `/login` | Login and receive token |
| POST | `/add-job` | Add a job application |
| GET | `/jobs` | Get all jobs for current user |
| PUT | `/update-status/<id>` | Update job status |
| PUT | `/edit-job/<id>` | Edit job details |
| DELETE | `/delete-job/<id>` | Delete a job |
| POST | `/analyze` | AI resume ATS analysis |
| POST | `/match-job` | AI resume vs job description match |
| POST | `/optimize-resume` | AI resume rewriter |
| POST | `/generate-cover-letter` | AI cover letter generator |
| POST | `/interview-prep` | AI interview Q&A generator |

---

## 📦 Dependencies

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

## 🔮 Future Improvements

- [ ] Real JWT authentication (replace dummy token)
- [ ] Multi-user support with proper session isolation
- [ ] Email reminders for upcoming deadlines
- [ ] LinkedIn job scraping integration
- [ ] Resume version history
- [ ] Dark/light mode toggle
- [ ] Mobile responsive improvements

---

## 👨‍💻 Author

**Sujan Uppalli Jayadevappa**  
M.S. Software Engineering @ Arizona State University  
[LinkedIn](https://www.linkedin.com/in/sujan-uppalli-jayadevappa-504b721b9/) • [GitHub](https://github.com/sujanuj) • supalli@asu.edu

---

## 📄 License

This project is for personal and educational use.