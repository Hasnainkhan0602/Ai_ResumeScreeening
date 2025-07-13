from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sqlite3
from datetime import datetime
from utils import extract_text
import pdfplumber
from flask import Flask, request, jsonify, render_template



app = Flask(__name__)
CORS(app)

DB_NAME = "resume_screening.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jd_filename TEXT,
            resume_filename TEXT,
            score REAL,
            matched_keywords TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def save_result(jd_file, resume_file, score, keywords):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO results (jd_filename, resume_filename, score, matched_keywords, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (jd_file, resume_file, score, ', '.join(keywords), datetime.now().isoformat()))
    conn.commit()
    conn.close()

@app.route("/upload", methods=["POST"])
def upload():
    jd_file = request.files.get("job_description")
    resumes = request.files.getlist("resumes")

    if not jd_file or not resumes:
        return jsonify({"error": "Both job description and resumes are required."}), 400

    jd_text = extract_text(jd_file)
    jd_words = set(jd_text.lower().split())

    results = []
    for resume in resumes:
        resume_text = extract_text(resume)
        resume_words = set(resume_text.lower().split())
        matched = list(jd_words & resume_words)
        score = round(len(matched) / len(jd_words) * 100, 2) if jd_words else 0

        save_result(jd_file.filename, resume.filename, score, matched[:20])

        results.append({
            "filename": resume.filename,
            "text": resume_text,
            "score": score,
            "match": matched[:20]
        })

    return jsonify({
        "job_description": {
            "filename": jd_file.filename,
            "text": jd_text
        },
        "resumes": results
    })
def extract_text_from_pdf(file_path):
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    except Exception as e:
        print(f"PDF extraction error: {e}")
    return text

if __name__ == "__main__":
    app.run(debug=True)
@app.route("/upload", methods=["POST"])
def upload():
    # your logic here
    return jsonify({"message": "Upload received"})
