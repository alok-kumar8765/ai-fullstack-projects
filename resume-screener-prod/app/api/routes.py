# app/api/routes.py
from flask import Blueprint, render_template_string, request, jsonify
from app.services.database import ingest_candidate, search_candidates
from app.services.parser import validate_and_extract_text
from app.services.nlp_engine import generate_embedding, extract_structured_resume

main_bp = Blueprint("main", __name__)

# Simple HTML frontend template for development testing
HOME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>Resume Screener</title></head>
<body style="font-family: Arial; padding: 40px; max-width: 600px; margin: auto;">
    <h2>🚀 AI Resume Screener (Dev Mode)</h2>
    <form action="/screen" method="POST" enctype="multipart/form-data" style="background: #f4f4f4; padding: 20px; border-radius: 8px;">
        <label><b>Job Description:</b></label><br>
        <textarea name="job_desc" rows="4" style="width: 100%; margin-top: 8px; margin-bottom: 15px;" placeholder="Enter requirements..."></textarea><br>
        
        <label><b>Upload Resume (PDF/DOCX):</b></label><br>
        <input type="file" name="resume_file" style="margin-top: 8px; margin-bottom: 15px;"><br>
        
        <button type="submit" style="background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer;">Upload & Screen</button>
    </form>
</body>
</html>
"""

@main_bp.route("/", methods=["GET"])
def index():
    return render_template_string(HOME_TEMPLATE)

@main_bp.route("/screen", methods=["POST"])
def screen_resumes():
    job_desc = request.form.get("job_desc", "")
    file = request.files.get("resume_file")

    if file and file.filename:
        try:
            # 1. Parse and extract text securely
            raw_text = validate_and_extract_text(file.stream, file.filename)
            
            # 2. Extract structured profile using OpenAI Pydantic schema
            profile_dict = extract_structured_resume(raw_text)
            
            # 3. Generate embedding vector
            embedding = generate_embedding(raw_text)
            
            # 4. Save to SQLite database
            ingest_candidate(profile_dict, raw_text, embedding)
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    # If job description is provided, run semantic vector search
    if job_desc:
        jd_embedding = generate_embedding(job_desc)
        results = search_candidates(jd_embedding, limit=5)
        return jsonify({"top_matches": results})

    return jsonify({"status": "Resume uploaded successfully, but no Job Description provided to search."})