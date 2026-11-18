import cv2
import threading
import queue
import time
from typing import Optional, Dict, Any
from deepface import DeepFace
from utils.logger import setup_logger

logger = setup_logger("EmotionDetector")

class EmotionDetector:
    def __init__(self, frame_queue: queue.Queue, result_queue: queue.Queue, inference_interval: float = 0.8):
        self.frame_queue = frame_queue
        self.result_queue = result_queue
        self.inference_interval = inference_interval
        self.is_running = False
        self.thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self.is_running:
            return
        self.is_running = True
        self.thread = threading.Thread(target=self._detection_loop, daemon=True, name="EmotionDetectorWorker")
        self.thread.start()
        logger.info("Emotion detector worker started.")

    def stop(self) -> None:
        self.is_running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        logger.info("Emotion detector worker stopped.")

    def _detection_loop(self) -> None:
        last_inference_time = 0.0
        while self.is_running:
            current_time = time.time()
            if current_time - last_inference_time < self.inference_interval:
                time.sleep(0.05)
                continue

            try:
                frame = self.frame_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            last_inference_time = time.time()
            try:
                analysis = DeepFace.analyze(
                    img_path=frame,
                    actions=['emotion'],
                    enforce_detection=False,
                    silent=True
                )
                if isinstance(analysis, list) and len(analysis) > 0:
                    dominant_emotion = analysis[0].get('dominant_emotion', 'neutral').lower()
                    emotions_dict = analysis[0].get('emotion', {})
                    confidence = emotions_dict.get(dominant_emotion, 0.0) / 100.0
                    
                    result = {
                        "emotion": dominant_emotion,
                        "confidence": float(confidence),
                        "timestamp": time.time()
                    }
                    self.result_queue.put(result)
            except Exception as e:
                logger.debug("DeepFace analysis skipped/failed on frame: %s", e)