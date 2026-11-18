import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, List
from utils.logger import setup_logger

logger = setup_logger("FeedbackManager")

class FeedbackManager:
    def __init__(self, db_path: str = "database/feedback.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True, parents=True)
        self._init_db()

    def _init_db(self) -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS feedback (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL,
                        detected_emotion TEXT,
                        selected_track TEXT,
                        feedback_type TEXT,
                        mode TEXT
                    )
                """)
                conn.commit()
            logger.info("Feedback database initialized successfully.")
        except Exception as e:
            logger.error("Failed to initialize feedback database: %s", e)

    def record_feedback(self, detected_emotion: str, selected_track: str, feedback_type: str, mode: str) -> None:
        try:
            import time
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO feedback (timestamp, detected_emotion, selected_track, feedback_type, mode)
                    VALUES (?, ?, ?, ?, ?)
                """, (time.time(), detected_emotion, selected_track, feedback_type, mode))
                conn.commit()
            logger.info("Recorded feedback [%s] for emotion [%s]", feedback_type, detected_emotion)
        except Exception as e:
            logger.error("Failed to record feedback: %s", e)

    def get_preference_weight(self, emotion: str, track: str) -> int:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT SUM(CASE WHEN feedback_type = 'thumbs_up' THEN 1 ELSE -1 END)
                    FROM feedback WHERE detected_emotion = ? AND selected_track = ?
                """, (emotion, track))
                res = cursor.fetchone()
                return res[0] if res and res[0] is not None else 0
        except Exception as e:
            logger.error("Failed to fetch preference weight: %s", e)
            return 0