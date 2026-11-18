import time
from collections import deque
from typing import Dict, Any, Optional
from utils.logger import setup_logger

logger = setup_logger("EmotionManager")

class EmotionManager:
    def __init__(self, confidence_threshold: float = 0.65, debounce_duration: float = 4.0, window_size: int = 10):
        self.confidence_threshold = confidence_threshold
        self.debounce_duration = debounce_duration
        self.rolling_window = deque(maxlen=window_size)
        
        self.current_emotion = "neutral"
        self.pending_emotion = "neutral"
        self.pending_since: Optional[float] = None
        self.last_switch_time = 0.0

    def process_detection(self, detection: Dict[str, Any]) -> Optional[str]:
        emotion = detection.get("emotion", "neutral")
        confidence = detection.get("confidence", 0.0)

        if confidence < self.confidence_threshold:
            return None

        self.rolling_window.append(emotion)
        
        # Determine majority emotion in rolling window
        if len(self.rolling_window) < self.rolling_window.maxlen // 2:
            return None

        counts = {em: self.rolling_window.count(em) for em in set(self.rolling_window)}
        majority_emotion = max(counts, key=counts.get) # type: ignore
        
        if majority_emotion == self.current_emotion:
            self.pending_emotion = majority_emotion
            self.pending_since = None
            return None

        # Debounce logic
        current_time = time.time()
        if majority_emotion != self.pending_emotion:
            self.pending_emotion = majority_emotion
            self.pending_since = current_time
            logger.info("Pending emotion transition candidate: %s", majority_emotion)
            return None

        if self.pending_since and (current_time - self.pending_since >= self.debounce_duration):
            if majority_emotion != self.current_emotion:
                self.current_emotion = majority_emotion
                self.last_switch_time = current_time
                self.pending_since = None
                logger.info("Confirmed emotion transition to: %s", self.current_emotion)
                return self.current_emotion

        return None