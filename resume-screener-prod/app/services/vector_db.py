# app/services/vector_db.py
from app.services.database import get_db_connection

# Dummy placeholders so old imports don't crash
class DummyCollection:
    def update_one(self, *args, **kwargs):
        conn = get_db_connection(); cursor = conn.cursor()
        candidate_id = args[0].get("_id")
        weight_delta = args[1].get("$inc", {}).get("feedback_score_boost", 0.0)
        cursor.execute("UPDATE resumes SET feedback_score_boost = feedback_score_boost + ? WHERE id = ?", (weight_delta, candidate_id))
        conn.commit(); conn.close()

    def insert_one(self, doc):
        conn = get_db_connection(); cursor = conn.cursor()
        cursor.execute("INSERT INTO recruiter_feedback (candidate_id, job_id, action) VALUES (?, ?, ?)", 
                       (doc.get("candidate_id"), doc.get("job_id"), doc.get("action")))
        conn.commit(); conn.close()

resumes_col = DummyCollection()
feedback_col = DummyCollection()