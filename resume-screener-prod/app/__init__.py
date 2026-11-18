# app/__init__.py
from flask import Flask
from flask_jwt_extended import JWTManager
from app.config import Config
from app.services.database import init_db
from app.api.routes import main_bp
from app.api.feedback import feedback_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    jwt = JWTManager(app)
    
    # Initialize SQLite database tables
    init_db()

    # Register Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(feedback_bp, url_prefix="/api")
    
    return app