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
from gui.settings_panel import SettingsPanel

class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Expression Player - AI Music Companion")
        self.root.geometry("1000x700")
        self.root.minsize(850, 600)
        
        # Color Palette - Modern Glossy Dark Theme
        self.bg_color = "#0f172a"      # Deep slate background
        self.card_bg = "#1e293b"       # Lighter card surface
        self.accent_color = "#3b82f6"  # Vibrant blue accent
        self.text_main = "#f8fafc"     # Off-white primary text
        self.text_muted = "#94a3b8"    # Muted secondary text
        self.success_color = "#10b981" # Emerald green
        
        self.root.configure(bg=self.bg_color)
        
        # Configure TTK Styles for a Modern Look
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.style.configure(".", background=self.bg_color, foreground=self.text_main, font=("Segoe UI", 10))
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("Card.TFrame", background=self.card_bg)
        
        # Modern LabelFrame Style
        self.style.configure("TLabelframe", background=self.card_bg, bordercolor="#334155", relief="solid", borderwidth=1)
        self.style.configure("TLabelframe.Label", background=self.card_bg, foreground=self.text_main, font=("Segoe UI", 11, "bold"))
        
        # Modern Button Styles
        self.style.configure("Accent.TButton", background=self.accent_color, foreground="white", font=("Segoe UI", 10, "bold"), borderwidth=0, focusthickness=3, focuscolor="none")
        self.style.map("Accent.TButton", background=[("active", "#2563eb"), ("disabled", "#475569")])
        
        self.style.configure("Secondary.TButton", background="#334155", foreground=self.text_main, font=("Segoe UI", 10), borderwidth=0)
        self.style.map("Secondary.TButton", background=[("active", "#475569")])

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
        
        # Build Modern Layout
        self._build_ui()
        
        # Start worker threads
        self.detector.start()
        
        # Bind periodic UI loop
        self.root.after(30, self._periodic_update)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self):
        # Top Header Bar
        header_frame = tk.Frame(self.root, bg=self.card_bg, height=60)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)
        
        title_lbl = tk.Label(header_frame, text="⚡ Expression Player", font=("Segoe UI", 14, "bold"), bg=self.card_bg, fg=self.text_main)
        title_lbl.pack(side=tk.LEFT, padx=20)
        
        settings_btn = ttk.Button(header_frame, text="⚙ Settings", style="Secondary.TButton", command=self.open_settings)
        settings_btn.pack(side=tk.RIGHT, padx=20)

        # Main Workspace Container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Left Column: Webcam & Emotion Intelligence Panels
        left_column = ttk.Frame(main_container)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.webcam_panel = WebcamPanel(left_column, self.webcam_manager)
        self.webcam_panel.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.emotion_panel = EmotionPanel(left_column)
        self.emotion_panel.pack(fill=tk.X)
        
        # Right Column: Music Player Engine Controls & Feedback
        right_column = ttk.Frame(main_container)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self.music_panel = MusicPanel(right_column, self.music_player, self.handle_feedback)
        self.music_panel.pack(fill=tk.BOTH, expand=True)

    def open_settings(self):
        SettingsPanel(self.root, self.settings)

    def handle_feedback(self, feedback_type: str):
        current_emotion = self.emotion_manager.current_emotion
        current_track = self.music_player.current_track.name if self.music_player.current_track else "unknown"
        mode = self.settings.get("emotion", "default_mode", "mood_matching")
        
        self.feedback_manager.record_feedback(current_emotion, current_track, feedback_type, mode)

    def _periodic_update(self):
        # 1. Update Webcam Feed Preview
        if self.webcam_manager.is_running:
            self.webcam_panel.update_frame()
            
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

        self.root.after(30, self._periodic_update)

    def on_close(self):
        self.detector.stop()
        self.webcam_manager.stop()
        self.music_player.stop()
        self.root.destroy()