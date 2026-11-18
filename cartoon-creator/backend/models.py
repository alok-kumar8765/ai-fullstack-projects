from sqlalchemy import Column, String, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import datetime

# For local production-ready testing, use SQLite or swap to PostgreSQL connection string:
# DATABASE_URL = "postgresql://user:password@localhost:5432/cartoons_db"
DATABASE_URL = "sqlite:///./cartoons.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class CartoonModel(Base):
    __tablename__ = "cartoons"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    user_id = Column(String, default="guest", index=True)
    image_url = Column(String, nullable=False)
    canvas_json = Column(JSON, nullable=False)  # Stores raw Fabric.js JSON state for reloading
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)