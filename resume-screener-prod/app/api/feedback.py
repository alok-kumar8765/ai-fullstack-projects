# app/api/feedback.py
import io
import pandas as pd
from bson import ObjectId
from flask import Blueprint, request, jsonify, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app.api.auth import role_required
from app.services.vector_db import resumes_col, feedback_col

feedback_bp = Blueprint("feedback", __name__)

@feedback_bp.route("/feedback", methods=["POST"])
@role_required("recruiter", "hiring_manager")
def record_feedback():
    """Updates candidate boost weight based on recruiter action."""
    data = request.json
    candidate_id = ObjectId(data["candidate_id"])
    action = data["action"]  # "shortlisted" or "rejected"

    weight_delta = 0.05 if action == "shortlisted" else -0.05

    resumes_col.update_one(
        {"_id": candidate_id},
        {"$inc": {"feedback_score_boost": weight_delta}}
    )
    feedback_col.insert_one({
        "candidate_id": candidate_id,
        "job_id": data.get("job_id"),
        "action": action
    })
    return jsonify({"status": "Feedback recorded and ranking weights updated"}), 200

@feedback_bp.route("/export/<format_type>", methods=["POST"])
@role_required("recruiter", "hiring_manager")
def export_shortlist(format_type):
    """Generates CSV or PDF reports of shortlisted candidates."""
    candidates = request.json.get("candidates", [])
    
    if format_type == "csv":
        df = pd.DataFrame(candidates)
        buffer = io.BytesIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        return send_file(buffer, mimetype="text/csv", as_attachment=True, download_name="shortlist.csv")

    elif format_type == "pdf":
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, 750, "Shortlisted Candidates Report")
        
        y = 720
        p.setFont("Helvetica", 11)
        for c in candidates:
            line = f"{c['full_name']} | Exp: {c['total_experience_years']} yrs | Match: {c['final_score']}%"
            p.drawString(50, y, line)
            y -= 20
        p.save()
        buffer.seek(0)
        return send_file(buffer, mimetype="application/pdf", as_attachment=True, download_name="shortlist.pdf")

    return jsonify({"error": "Invalid format"}), 400