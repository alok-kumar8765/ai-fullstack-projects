import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import pyautogui
import numpy as np
import time

# Initialize MediaPipe Face Landmarker
base_options = python.BaseOptions(model_asset_path="face_landmarker.task")
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    output_face_blendshapes=True,
    num_faces=1
)
detector = vision.FaceLandmarker.create_from_options(options)

cam = cv2.VideoCapture(0)
screen_w, screen_h = pyautogui.size()

RIGHT_IRIS = [469, 470, 471, 472]

# Smoothing variables
history_size = 7
prev_x_coords = []
prev_y_coords = []

# Dwell Clicking & Keyboard Variables
dwell_start_time = None
dwell_threshold = 1.0
last_target_x, last_target_y = 0, 0
dwell_radius = 35

# Calibration variables
calibrated = False
calib_start_time = time.time()
calib_duration = 4.0  # 4 seconds to calibrate
min_x, max_x = float('inf'), float('-inf')
min_y, max_y = float('inf'), float('-inf')

keys = [
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L", "BKSP"],
    ["Z", "X", "C", "V", "B", "N", "M", "SPACE"]
]

try:
    while cam.isOpened():
        success, frame = cam.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        detection_result = detector.detect(mp_image)

        # Draw Keyboard UI
        key_boxes = {}
        start_y = h - 180
        for r_idx, row in enumerate(keys):
            start_x = 50
            for c_idx, key in enumerate(row):
                kw = 90 if key == "SPACE" else 55
                kh = 45
                kx = start_x
                ky = start_y + (r_idx * 50)
                key_boxes[key] = (kx, ky, kw, kh)
                cv2.rectangle(frame, (kx, ky), (kx + kw, ky + kh), (50, 50, 50), -1)
                cv2.rectangle(frame, (kx, ky), (kx + kw, ky + kh), (200, 200, 200), 1)
                cv2.putText(frame, key, (kx + 12, ky + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                start_x += kw + 10

        if detection_result.face_landmarks:
            landmarks = detection_result.face_landmarks[0]
            blendshapes = detection_result.face_blendshapes[0] if detection_result.face_blendshapes else []
            
            bs_dict = {bs.category_name: bs.score for bs in blendshapes}
            jaw_open = bs_dict.get('jawOpen', 0.0)
            
            r_iris_x = int(np.mean([landmarks[i].x * w for i in RIGHT_IRIS]))
            r_iris_y = int(np.mean([landmarks[i].y * h for i in RIGHT_IRIS]))
            
            # --- Calibration Phase ---
            if not calibrated:
                elapsed = time.time() - calib_start_time
                remaining = int(calib_duration - elapsed)
                
                min_x = min(min_x, r_iris_x)
                max_x = max(max_x, r_iris_x)
                min_y = min(min_y, r_iris_y)
                max_y = max(max_y, r_iris_y)
                
                cv2.putText(frame, f"CALIBRATING... Look around edges! ({max(0, remaining)}s)", (25, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
                
                if elapsed >= calib_duration:
                    # Add a small buffer to min/max to prevent boundary trapping
                    min_x += 10
                    max_x -= 10
                    min_y += 10
                    max_y -= 10
                    calibrated = True
            else:
                # --- Scroll Mode ---
                if r_iris_y < min_y + 15:
                    pyautogui.scroll(35)
                    cv2.putText(frame, "MODE: SCROLL UP", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                elif r_iris_y > max_y - 15:
                    pyautogui.scroll(-35)
                    cv2.putText(frame, "MODE: SCROLL DOWN", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                else:
                    # --- Cursor Movement with Dynamic Calibration Mapping ---
                    target_x = np.interp(r_iris_x, [min_x, max_x], [0, screen_w])
                    target_y = np.interp(r_iris_y, [min_y, max_y], [0, screen_h])
                    
                    prev_x_coords.append(target_x)
                    prev_y_coords.append(target_y)
                    if len(prev_x_coords) > history_size:
                        prev_x_coords.pop(0)
                        prev_y_coords.pop(0)
                        
                    smoothed_x = np.mean(prev_x_coords)
                    smoothed_y = np.mean(prev_y_coords)
                    
                    pyautogui.moveTo(smoothed_x, smoothed_y)

                    # --- Jaw Open Right-Click ---
                    if jaw_open > 0.5:
                        pyautogui.rightClick()
                        cv2.putText(frame, "RIGHT CLICK!", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                        time.sleep(0.4)

                    # --- Dwell Click & Keyboard ---
                    active_key = None
                    for key, (kx, ky, kw, kh) in key_boxes.items():
                        if kx <= r_iris_x <= kx + kw and ky <= r_iris_y <= ky + kh:
                            active_key = key
                            cv2.rectangle(frame, (kx, ky), (kx + kw, ky + kh), (0, 255, 0), 2)
                            break

                    distance_moved = np.hypot(r_iris_x - last_target_x, r_iris_y - last_target_y)
                    
                    if distance_moved < dwell_radius:
                        if dwell_start_time is None:
                            dwell_start_time = time.time()
                        elif time.time() - dwell_start_time >= dwell_threshold:
                            if active_key:
                                if active_key == "SPACE":
                                    pyautogui.press("space")
                                elif active_key == "BKSP":
                                    pyautogui.press("backspace")
                                else:
                                    pyautogui.write(active_key.lower())
                                cv2.putText(frame, f"TYPED: {active_key}", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                            else:
                                pyautogui.click()
                                cv2.putText(frame, "LEFT CLICK", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                            
                            dwell_start_time = None
                            time.sleep(0.3)
                    else:
                        dwell_start_time = None
                        last_target_x, last_target_y = r_iris_x, r_iris_y

            for i in RIGHT_IRIS:
                cx = int(landmarks[i].x * w)
                cy = int(landmarks[i].y * h)
                cv2.circle(frame, (cx, cy), 2, (0, 255, 0), -1)

        cv2.imshow("Calibrated Eye Mouse & Keyboard", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cam.release()
    detector.close()
    cv2.destroyAllWindows()