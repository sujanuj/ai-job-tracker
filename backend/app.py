from flask import Flask, request, jsonify, send_file
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from openai import OpenAI
import os
import json

load_dotenv()

app = Flask(__name__)
CORS(app, origins="*")



app.config["JWT_SECRET_KEY"] = "super-secret-key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
jwt = JWTManager(app)
api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    client = OpenAI(api_key=api_key)
else:
    client = None

# MODELS 
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))

class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(100))
    role = db.Column(db.String(100))
    status = db.Column(db.String(50))
    user_id = db.Column(db.Integer)

    link = db.Column(db.String(300))
    notes = db.Column(db.String(300))
    deadline = db.Column(db.String(50))

    def to_dict(self):
        return {
            "id": self.id,
            "company": self.company,
            "role": self.role,
            "status": self.status,
            "link": self.link,
            "notes": self.notes,
            "deadline": self.deadline
        }

with app.app_context():
    db.create_all()

# AUTH

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        print("DEBUG LOGIN DATA:", data)

        if not data:
            return jsonify({"error": "No data received"}), 400

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Missing fields"}), 400

        user = User.query.filter_by(username=username).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        if user.password != password:
            return jsonify({"error": "Wrong password"}), 401

        return jsonify({"token": "dummy-token"})
    
    except Exception as e:
        print("LOGIN ERROR:", str(e))   # 🔥 IMPORTANT
        return jsonify({"error": str(e)}), 500

@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        print("DEBUG REGISTER DATA:", data)

        if not data:
            return jsonify({"error": "No data received"}), 400

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Missing fields"}), 400

        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({"error": "User already exists"}), 400

        # Create new user
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User registered successfully"})
    
    except Exception as e:
        print("REGISTER ERROR:", str(e))   # 🔥 IMPORTANT
        return jsonify({"error": str(e)}), 500

# JOB CRUD 
@app.route("/add-job", methods=["POST"])
def add_job():
    user_id = 1
    data = request.json

    job = JobApplication(
        company=data.get("company"),
        role=data.get("role"),
        status="Applied",
        user_id=user_id,
        link=data.get("link"),
        notes=data.get("notes"),
        deadline=data.get("deadline")
    )

    db.session.add(job)
    db.session.commit()

    return jsonify({"message": "Job added"})

@app.route("/jobs", methods=["GET"])
def get_jobs():
    user_id = 1
    jobs = JobApplication.query.filter_by(user_id=user_id).all()
    return jsonify([j.to_dict() for j in jobs])

@app.route("/update-status/<int:job_id>", methods=["PUT"])
def update_status(job_id):
    user_id = 1
    data = request.json

    job = JobApplication.query.filter_by(id=job_id, user_id=user_id).first()
    if not job:
        return jsonify({"error": "Not found"}), 404

    job.status = data.get("status")
    db.session.commit()

    return jsonify({"message": "Updated"})

@app.route("/delete-job/<int:job_id>", methods=["DELETE"])
def delete_job(job_id):
    user_id = 1

    job = JobApplication.query.filter_by(id=job_id, user_id=user_id).first()
    if not job:
        return jsonify({"error": "Not found"}), 404

    db.session.delete(job)
    db.session.commit()

    return jsonify({"message": "Deleted"})

@app.route("/edit-job/<int:job_id>", methods=["PUT"])
def edit_job(job_id):
    user_id = 1
    data = request.json

    job = JobApplication.query.filter_by(id=job_id, user_id=user_id).first()
    if not job:
        return jsonify({"error": "Not found"}), 404

    job.company = data.get("company", job.company)
    job.role = data.get("role", job.role)
    job.notes = data.get("notes", job.notes)
    job.deadline = data.get("deadline", job.deadline)

    db.session.commit()

    return jsonify({"message": "Updated"})

import json

@app.route("/generate-questions", methods=["POST"])
def generate_questions():
    if not client:
        return jsonify({"error": "AI not configured"}), 500
    data = request.json

    role = data.get("role")
    company = data.get("company")

    prompt = f"""
Generate interview questions for:

Role: {role}
Company: {company}

Return STRICT JSON like this:

{{
  "technical": ["question1", "question2"],
  "behavioral": ["question3", "question4"]
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.choices[0].message.content.strip()
        print("DEBUG RESPONSE:", text)

        try:
            questions = json.loads(text)
        except:
            questions = {
                "technical": ["Unable to parse"],
                "behavioral": []
            }

        return jsonify(questions)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# JOB MATCH 
@app.route("/match-job", methods=["POST"])
def match_job():
    if not client:
        return jsonify({"error": "AI not configured"}), 500
    data = request.json
    resume = data.get("resume")
    job_desc = data.get("job_description")

    if not resume or not job_desc:
        return jsonify({"error": "Missing data"}), 400

    prompt = f"""
Return STRICT JSON ONLY.

Resume:
{resume}

Job Description:
{job_desc}

Format:
{{
  "match_score": number,
  "keyword_score": number,
  "skills_match": [],
  "missing_keywords": [],
  "strengths": [],
  "weaknesses": [],
  "suggestions": []
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return jsonify(json.loads(response.choices[0].message.content))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# RESUME OPTIMIZER (FIXED) 
@app.route("/optimize-resume", methods=["POST"])
def optimize_resume():
    if not client:
        return jsonify({"error": "AI not configured"}), 500
    data = request.json

    resume = data.get("resume")
    job_desc = data.get("job_description")

    if not resume or not job_desc:
        return jsonify({"error": "Missing data"}), 400

    prompt = f"""
Rewrite this resume for the job.

Resume:
{resume}

Job Description:
{job_desc}

Return clearly:

Optimized Summary:
...

Improved Experience Points:
- ...
- ...

Final ATS Optimized Resume:
...
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return jsonify({
            "result": response.choices[0].message.content
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# COVER LETTER GENERATOR 


@app.route("/generate-cover-letter", methods=["POST"])
def generate_cover_letter():
    if not client:
        return jsonify({"error": "AI not configured"}), 500
    data = request.json

    resume = data.get("resume")
    job_desc = data.get("job_description")
    tone = data.get("tone", "professional")  

    if not resume or not job_desc:
        return jsonify({"error": "Missing resume or job description"}), 400

    prompt = f"""
You are an expert cover letter writer. Write a polished, personalized cover letter based on the resume and job description below.

Tone: {tone}

Resume:
{resume}

Job Description:
{job_desc}

Instructions:
- Start with a strong opening line (no "Dear Hiring Manager" cliché — use the company name if mentioned)
- Highlight 2-3 specific achievements from the resume that directly match the job
- Show genuine enthusiasm for the role/company
- End with a confident call to action
- Keep it under 350 words
- Do NOT use bullet points — write in flowing paragraphs
- Do NOT include placeholders like [Your Name] — infer from resume if possible

Return ONLY the cover letter text. No preamble, no notes, no extra explanation.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return jsonify({"result": response.choices[0].message.content})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route("/interview-prep", methods=["POST"])
def interview_prep():
    if not client:
        return jsonify({"error": "AI not configured"}), 500
    data = request.json
    role = data.get("role", "").strip()
    job_desc = data.get("job_description", "").strip()

    if not role and not job_desc:
        return jsonify({"error": "Please provide a role or job description"}), 400

    prompt = f"""
You are an expert technical interviewer. Generate interview questions for this role.

Role: {role}
Job Description: {job_desc}

Return STRICT JSON ONLY — no markdown, no explanation, no backticks.

{{
  "technical": [
    {{"question": "...", "answer": "..."}},
    {{"question": "...", "answer": "..."}},
    {{"question": "...", "answer": "..."}},
    {{"question": "...", "answer": "..."}},
    {{"question": "...", "answer": "..."}}
  ],
  "behavioral": [
    {{"question": "...", "answer": "..."}},
    {{"question": "...", "answer": "..."}},
    {{"question": "...", "answer": "..."}},
    {{"question": "...", "answer": "..."}},
    {{"question": "...", "answer": "..."}}
  ]
}}

Rules:
- Technical questions must be specific to the role/stack mentioned
- Answers should be 2-4 sentences, concise and practical
- Behavioral answers should use the STAR format briefly
- Return ONLY the JSON object, nothing else
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.choices[0].message.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        return jsonify(json.loads(text))

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/analyze", methods=["POST"])
def analyze_resume():
    if not client:
        return jsonify({"error": "AI not configured"}), 500
    data = request.json

    resume = data.get("resume")
    role = data.get("role")

    if not resume:
        return jsonify({"error": "Resume is required"}), 400

    prompt = f"""
Analyze the resume for ATS optimization.

Resume:
{resume}

Target Role:
{role}

Return:

Score: <number out of 100>

Missing Keywords:
- ...

Improvements:
- ...

Better Bullet Suggestions:
- ...
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return jsonify({
            "result": response.choices[0].message.content
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
from flask import send_from_directory
import os

@app.route("/")
def serve_ui():
    return send_from_directory(
        os.path.dirname(os.path.abspath(__file__)),
        "index.html"
    )

# ================= RUN =================
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)