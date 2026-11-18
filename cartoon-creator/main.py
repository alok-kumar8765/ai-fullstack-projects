import uuid
import base64
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

# Import database models and schemas
from models import SessionLocal, init_db, CartoonModel
from schemas import SaveCartoonRequest, CartoonResponse

app = FastAPI(title="Cartoon Creator API", version="1.0.0")

# Allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory setup for saved exports and assets
EXPORT_DIR = Path("exports")
EXPORT_DIR.mkdir(exist_ok=True)
app.mount("/exports", StaticFiles(directory="exports"), name="exports")

# Initialize database tables on startup
init_db()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Endpoints ---

@app.get("/api/assets")
async def get_available_assets():
    """Returns curated character presets and backgrounds."""
    return {
        "characters": [
            {"id": "boy_casual", "name": "Casual Boy", "url": "/assets/boy_casual.png"},
            {"id": "girl_hoodie", "name": "Hoodie Girl", "url": "/assets/girl_hoodie.png"},
            {"id": "glasses_kid", "name": "Nerdy Kid", "url": "/assets/glasses_kid.png"},
            {"id": "cat_avatar", "name": "Cool Cat", "url": "/assets/cat_avatar.png"},
        ],
        "bubbles": [
            {"id": "speech_1", "name": "Classic Speech", "url": "/assets/speech_bubble.png"}
        ]
    }


@app.post("/api/cartoons/save", response_model=CartoonResponse)
async def save_cartoon(payload: SaveCartoonRequest, db: Session = Depends(get_db)):
    """Decodes base64 canvas output, saves PNG file, and persists data to SQLite/PostgreSQL."""
    try:
        # Strip 'data:image/png;base64,' header
        header, encoded = payload.image_base64.split(",", 1)
        image_data = base64.b64decode(encoded)
        
        file_id = str(uuid.uuid4())
        file_path = EXPORT_DIR / f"{file_id}.png"
        
        with open(file_path, "wb") as f:
            f.write(image_data)
            
        image_url = f"http://localhost:8000/exports/{file_id}.png"

        # Persist to database using SQLAlchemy session
        db_cartoon = CartoonModel(
            id=file_id,
            title=payload.title,
            user_id=payload.user_id,
            image_url=image_url,
            canvas_json=payload.canvas_json
        )
        db.add(db_cartoon)
        db.commit()
        db.refresh(db_cartoon)
            
        return db_cartoon
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to process image: {str(e)}")


@app.post("/api/ai/generate-character")
async def generate_ai_character(prompt: str):
    """Hook for Stable Diffusion / Replicate API to generate transparent PNG assets."""
    return {
        "status": "queued",
        "prompt": prompt,
        "estimated_seconds": 4
    }