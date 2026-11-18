import cv2
import threading
import time
from typing import Optional, Tuple
from utils.logger import setup_logger

logger = setup_logger("WebcamManager")

class WebcamManager:
    def __init__(self, camera_index: int = 0, target_fps: int = 30):
        self.camera_index = camera_index
        self.target_fps = target_fps
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_running = False
        self.current_frame: Optional[cv2.Matrixtype] = None
        self.frame_lock = threading.Lock()
        self.thread: Optional[threading.Thread] = None

    def start(self) -> bool:
        if self.is_running:
            return True
        try:
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_ANY)
            if not self.cap.isOpened():
                logger.error("Could not open webcam index %d", self.camera_index)
                return False
            self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
            self.is_running = True
            self.thread = threading.Thread(target=self._capture_loop, daemon=True, name="WebcamWorker")
            self.thread.start()
            logger.info("Webcam started successfully on index %d", self.camera_index)
            return True
        except Exception as e:
            logger.error("Exception occurred while starting webcam: %s", e)
            self.is_running = False
            return False

    def _capture_loop(self) -> None:
        frame_interval = 1.0 / self.target_fps
        while self.is_running and self.cap and self.cap.isOpened():
            start_time = time.time()
            ret, frame = self.cap.read()
            if ret:
                with self.frame_lock:
                    self.current_frame = frame
            else:
                logger.warning("Failed to grab frame from webcam.")
                time.sleep(0.1)
            
            elapsed = time.time() - start_time
            if elapsed < frame_interval:
                time.sleep(frame_interval - elapsed)

    def get_frame(self) -> Optional[any]:
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
        return None

    def stop(self) -> None:
        self.is_running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        if self.cap:
            self.cap.release()
            self.cap = None
        logger.info("Webcam resources released.")