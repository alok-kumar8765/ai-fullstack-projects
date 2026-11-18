import tkinter as tk
from tkinter import ttk

class EmotionPanel(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="AI Emotion State", padding=10)
        
        ttk.Label(self, text="Detected Emotion:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        self.emotion_val_lbl = ttk.Label(self, text="Neutral", font=("Segoe UI", 12, "bold"), foreground="#007ACC")
        self.emotion_val_lbl.grid(row=0, column=1, sticky="w", pady=5, padx=10)
        
        ttk.Label(self, text="Confidence:", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.conf_progress = ttk.Progressbar(self, orient="horizontal", length=180, mode="determinate")
        self.conf_progress.grid(row=1, column=1, sticky="w", pady=5, padx=10)
        
        ttk.Label(self, text="Confirmed State:", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        self.confirmed_val_lbl = ttk.Label(self, text="neutral", font=("Segoe UI", 10), foreground="green")
        self.confirmed_val_lbl.grid(row=2, column=1, sticky="w", pady=5, padx=10)

    def update_emotion(self, emotion: str, confidence: float, confirmed: str):
        self.emotion_val_lbl.config(text=emotion.capitalize())
        self.conf_progress['value'] = confidence * 100
        self.confirmed_val_lbl.config(text=confirmed.capitalize())