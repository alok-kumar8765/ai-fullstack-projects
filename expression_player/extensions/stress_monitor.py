import time
from utils.logger import setup_logger

logger = setup_logger("StressMonitorExtension")

class StressMonitorExtension:
    """Experimental workplace/study stress and emotion trend tracker."""
    def __init__(self, break_interval_min: int = 45):
        self.break_interval_min = break_interval_min
        self.session_start_time = time.time()
        self.negative_emotion_count = 0
        logger.info("Stress monitor extension initialized.")

    def check_break_needed(self) -> bool:
        elapsed_min = (time.time() - self.session_start_time) / 60.0
        if elapsed_min >= self.break_interval_min:
            return True
        return False

    def log_emotion_trend(self, emotion: str):
        if emotion in ["sad", "angry"]:
            self.negative_emotion_count += 1
            if self.negative_emotion_count >= 5:
                logger.warning("Sustained negative emotions detected. Suggesting relaxation break.")
                self.negative_emotion_count = 0
                return True
        return False

    def reset_session(self):
        self.session_start_time = time.time()
        self.negative_emotion_count = 0