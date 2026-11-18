## app/config.py
#import os
#from dotenv import load_dotenv

#load_dotenv()

#class Config:
#    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
#    DB_NAME = os.environ.get("DB_NAME", "ats_production")
#    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
#    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
#    ALLOWED_EXTENSIONS = {'pdf', 'docx'}


## app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLITE_DB_PATH = os.environ.get("SQLITE_DB_PATH", "ats_dev.db")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret-key")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")