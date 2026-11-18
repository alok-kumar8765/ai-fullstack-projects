# app/services/database.py
import sqlite3
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.config import Config

def get_db_connection():
    conn = sqlite3.connect(Config.SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes SQLite tables for resumes and feedback."""
    conn = get_db_connection(); cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            email TEXT,
            total_experience_years REAL,
            primary_skills TEXT,
            previous_companies TEXT,
            highest_education TEXT,
            raw_text TEXT,
            embedding TEXT,
            feedback_score_boost REAL DEFAULT 0.0
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recruiter_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER,
            job_id TEXT,
            action TEXT,
            FOREIGN KEY (candidate_id) REFERENCES resumes (id)
        )
    """)
    conn.commit()
    conn.close()

def ingest_candidate(profile_data: dict, raw_text: str, embedding: list[float]):
    """Stores candidate profile and JSON-serialized vector embedding into SQLite."""
    conn = get_db_connection(); cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO resumes (full_name, email, total_experience_years, primary_skills, previous_companies, highest_education, raw_text, embedding)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        profile_data.get("full_name"),
        profile_data.get("email"),
        profile_data.get("total_experience_years"),
        json.dumps(profile_data.get("primary_skills", [])),
        json.dumps(profile_data.get("previous_companies", [])),
        profile_data.get("highest_education"),
        raw_text,
        json.dumps(embedding) # Store vector as a JSON string
    ))
    
    candidate_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return candidate_id

def search_candidates(jd_embedding: list[float], min_experience: float = 0, limit: int = 10):
    """Performs in-memory vector cosine similarity search for local SQLite dev."""
    conn = get_db_connection(); cursor = conn.cursor()
    
    # Fetch candidates meeting experience filter
    cursor.execute("""
        SELECT id, full_name, total_experience_years, primary_skills, embedding, feedback_score_boost 
        FROM resumes 
        WHERE total_experience_years >= ?
    """, (min_experience,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return []

    jd_vec = np.array(jd_embedding).reshape(1, -1)
    results = []

    for row in rows:
        cand_vec = np.array(json.loads(row["embedding"])).reshape(1, -1)
        # Compute cosine similarity (ranges from -1 to 1)
        semantic_score = float(cosine_similarity(jd_vec, cand_vec)[0][0])
        
        # Add feedback score boost
        final_score = round((semantic_score + row["feedback_score_boost"]) * 100, 2)

        results.append({
            "id": row["id"],
            "full_name": row["full_name"],
            "total_experience_years": row["total_experience_years"],
            "primary_skills": json.loads(row["primary_skills"]),
            "final_score": final_score
        })

    # Sort descending by final score and take top limit
    results.sort(key=lambda x: x["final_score"], reverse=True)
    return results[:limit]