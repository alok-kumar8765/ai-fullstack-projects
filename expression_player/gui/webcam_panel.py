import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
from typing import Optional

class WebcamPanel(ttk.LabelFrame):
    def __init__(self, parent, webcam_manager):
        super().__init__(parent, text="Live Webcam Feed", padding=10)
        self.webcam_manager = webcam_manager
        
        self.canvas_width = 400
        self.canvas_height = 300
        
        self.video_label = ttk.Label(self, text="Camera Offline", background="black", foreground="white", anchor="center")
        self.video_label.pack(fill=tk.BOTH, expand=True, ipadx=5, ipady=5)
        
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.start_btn = ttk.Button(btn_frame, text="Start Camera", command=self.start_camera)
        self.start_btn.pack(side=tk.LEFT, expand=True, padx=2)
        
        self.stop_btn = ttk.Button(btn_frame, text="Stop Camera", command=self.stop_camera, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, expand=True, padx=2)

    def start_camera(self):
        if self.webcam_manager.start():
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)

    def stop_camera(self):
        self.webcam_manager.stop()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.video_label.config(image="", text="Camera Offline")

    def update_frame(self):
        frame = self.webcam_manager.get_frame()
        if frame is not None:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            image = image.resize((self.canvas_width, self.canvas_height), Image.Resampling.BILINEAR)
            imgtk = ImageTk.PhotoImage(image=image)
            self.video_label.imgtk = imgtk  # type: ignore
            self.video_label.config(image=imgtk, text="")