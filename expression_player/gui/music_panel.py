import tkinter as tk
from tkinter import ttk

class MusicPanel(ttk.LabelFrame):
    def __init__(self, parent, music_player, feedback_callback):
        super().__init__(parent, text="Music Player Engine", padding=10)
        self.music_player = music_player
        self.feedback_callback = feedback_callback
        
        self.track_lbl = ttk.Label(self, text="No track playing", font=("Segoe UI", 11, "italic"))
        self.track_lbl.pack(pady=5)
        
        ctrl_frame = ttk.Frame(self)
        ctrl_frame.pack(pady=5)
        
        self.play_btn = ttk.Button(ctrl_frame, text="▶ / ⏸", command=self.toggle_play)
        self.play_btn.grid(row=0, column=0, padx=5)
        
        self.stop_btn = ttk.Button(ctrl_frame, text="⏹ Stop", command=self.stop_music)
        self.stop_btn.grid(row=0, column=1, padx=5)
        
        self.next_btn = ttk.Button(ctrl_frame, text="⏭ Next", command=self.next_track)
        self.next_btn.grid(row=0, column=2, padx=5)
        
        # Feedback section
        fb_frame = ttk.Frame(self)
        fb_frame.pack(pady=10)
        
        ttk.Button(fb_frame, text="👍 Thumbs Up", command=lambda: self.feedback_callback("thumbs_up")).pack(side=tk.LEFT, padx=5)
        ttk.Button(fb_frame, text="👎 Thumbs Down", command=lambda: self.feedback_callback("thumbs_down")).pack(side=tk.LEFT, padx=5)

    def toggle_play(self):
        self.music_player.toggle_play_pause()

    def stop_music(self):
        self.music_player.stop()
        self.track_lbl.config(text="Playback Stopped")

    def next_track(self):
        track = self.music_player.next_track()
        if track:
            self.track_lbl.config(text=track)

    def update_track_label(self, name: str):
        self.track_lbl.config(text=name)