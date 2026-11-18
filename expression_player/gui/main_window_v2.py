import tkinter as tk
from tkinter import ttk
import queue
import threading
import time
from core.webcam_manager import WebcamManager
from core.emotion_detector import EmotionDetector
from core.emotion_manager import EmotionManager
from core.music_player import MusicPlayer
from core.feedback_manager import FeedbackManager
from core.settings_manager import SettingsManager
from gui.webcam_panel import WebcamPanel
from gui.emotion_panel import EmotionPanel
from gui.music_panel import MusicPanel

class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Expression Player - AI Music Companion")
        self.root.geometry("900x650")
        
        # Style configuration for dark theme
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Initialize core components
        self.settings = SettingsManager()
        self.webcam_manager = WebcamManager(
            camera_index=self.settings.get("camera", "camera_index", 0),
            target_fps=self.settings.get("camera", "target_fps", 30)
        )
        
        self.frame_queue = queue.Queue(maxsize=2)
        self.result_queue = queue.Queue()
        
        self.detector = EmotionDetector(
            frame_queue=self.frame_queue,
            result_queue=self.result_queue,
            inference_interval=self.settings.get("camera", "inference_interval_sec", 0.8)
        )
        
        self.emotion_manager = EmotionManager(
            confidence_threshold=self.settings.get("emotion", "confidence_threshold", 0.65),
            debounce_duration=self.settings.get("emotion", "debounce_duration_sec", 4.0),
            window_size=self.settings.get("emotion", "rolling_window_size", 10)
        )
        
        self.music_player = MusicPlayer(
            music_dir=self.settings.get("audio", "music_directory", "music"),
            volume=self.settings.get("audio", "volume", 0.7)
        )
        
        self.feedback_manager = FeedbackManager()
        
        # Build Layout
        self._build_ui()
        
        # Start background worker threads
        self.detector.start()
        
        # Bind periodic UI update loop
        self.root.after(30, self._periodic_update)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left Column: Webcam & Emotion Panels
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.webcam_panel = WebcamPanel(left_frame, self.webcam_manager)
        self.webcam_panel.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.emotion_panel = EmotionPanel(left_frame)
        self.emotion_panel.pack(fill=tk.X, pady=5)
        
        # Right Column: Music Controls & Feedback
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        self.music_panel = MusicPanel(right_frame, self.music_player, self.handle_feedback)
        self.music_panel.pack(fill=tk.BOTH, expand=True, pady=5)

    def handle_feedback(self, feedback_type: str):
        current_emotion = self.emotion_manager.current_emotion
        current_track = self.music_player.current_track.name if self.music_player.current_track else "unknown"
        mode = self.settings.get("emotion", "default_mode", "mood_matching")
        
        self.feedback_manager.record_feedback(current_emotion, current_track, feedback_type, mode)

    def _periodic_update(self):
        # 1. Update Webcam Feed Preview
        if self.webcam_manager.is_running:
            self.webcam_panel.update_frame()
            
            # Feed frame to detection queue if space allows
            frame = self.webcam_manager.get_frame()
            if frame is not None:
                if self.frame_queue.full():
                    try:
                        self.frame_queue.get_nowait()
                    except queue.Empty:
                        pass
                self.frame_queue.put(frame)

        # 2. Check Emotion Detection Results
        try:
            while True:
                res = self.result_queue.get_nowait()
                emotion = res.get("emotion")
                conf = res.get("confidence")
                
                confirmed = self.emotion_manager.process_detection(res)
                self.emotion_panel.update_emotion(emotion, conf, self.emotion_manager.current_emotion)
                
                if confirmed:
                    track_name = self.music_player.play_for_emotion(confirmed)
                    if track_name:
                        self.music_panel.update_track_label(track_name)
        except queue.Empty:
            pass

        # Schedule next loop iteration
        self.root.after(30, self._periodic_update)

    def on_close(self):
        self.detector.stop()
        self.webcam_manager.stop()
        self.music_player.stop()
        self.root.destroy()