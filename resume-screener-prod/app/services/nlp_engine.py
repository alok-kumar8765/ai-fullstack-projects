# app/services/nlp_engine.py
import json
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from app.config import Config

# Load once at worker startup, never inside a request route
embedder = SentenceTransformer("all-MiniLM-L6-v2") # Outputs 384-dim vectors
llm_client = OpenAI(api_key=Config.OPENAI_API_KEY)

class CandidateProfile(BaseModel):
    full_name: str
    email: str
    total_experience_years: float
    primary_skills: list[str]
    previous_companies: list[str]
    highest_education: str

def generate_embedding(text: str) -> list[float]:
    """Generates dense vector embedding for semantic search."""
    return embedder.encode(text, normalize_embeddings=True).tolist()

def extract_structured_resume(raw_text: str) -> dict:
    """Uses Structured Outputs to extract deterministic JSON from raw resume text."""
    response = llm_client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Extract structured candidate data accurately."},
            {"role": "user", "content": raw_text}
        ],
        response_format=CandidateProfile,
    )
    return response.choices[0].message.parsed.model_dump()