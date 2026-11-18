import tkinter as tk
from tkinter import ttk
from core.settings_manager import SettingsManager

class SettingsPanel(tk.Toplevel):
    def __init__(self, parent, settings_manager: SettingsManager):
        super().__init__(parent)
        self.title("Expression Player - Settings")
        self.geometry("400x350")
        self.resizable(False, False)
        self.settings = settings_manager

        self._build_ui()

    def _build_ui(self):
        padding_frame = ttk.Frame(self, padding=15)
        padding_frame.pack(fill=tk.BOTH, expand=True)

        # Confidence Threshold
        ttk.Label(padding_frame, text="Confidence Threshold (0.1 - 1.0):").pack(anchor="w", pady=(5, 2))
        self.conf_spin = ttk.Spinbox(padding_frame, from_=0.1, to=1.0, increment=0.05)
        self.conf_spin.set(str(self.settings.get("emotion", "confidence_threshold", 0.65)))
        self.conf_spin.pack(fill=tk.X, pady=(0, 10))

        # Debounce Duration
        ttk.Label(padding_frame, text="Debounce Duration (seconds):").pack(anchor="w", pady=(5, 2))
        self.debounce_spin = ttk.Spinbox(padding_frame, from_=1.0, to=10.0, increment=1.0)
        self.debounce_spin.set(str(self.settings.get("emotion", "debounce_duration_sec", 4.0)))
        self.debounce_spin.pack(fill=tk.X, pady=(0, 10))

        # Volume
        ttk.Label(padding_frame, text="Default Volume (0.0 - 1.0):").pack(anchor="w", pady=(5, 2))
        self.vol_spin = ttk.Spinbox(padding_frame, from_=0.0, to=1.0, increment=0.1)
        self.vol_spin.set(str(self.settings.get("audio", "volume", 0.7)))
        self.vol_spin.pack(fill=tk.X, pady=(0, 20))

        # Save Button
        save_btn = ttk.Button(padding_frame, text="Save Settings", command=self.save_settings)
        save_btn.pack(fill=tk.X, pady=5)

    def save_settings(self):
        try:
            conf = float(self.conf_spin.get())
            debounce = float(self.debounce_spin.get())
            vol = float(self.vol_spin.get())

            self.settings.set("emotion", "confidence_threshold", conf)
            self.settings.set("emotion", "debounce_duration_sec", debounce)
            self.settings.set("audio", "volume", vol)
            self.destroy()
        except ValueError:
            pass