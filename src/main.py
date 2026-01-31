import cv2
import numpy as np
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# === Settings ===
MODEL_PATH = "models/hand_landmarker.task"

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Initialize hand landmarker in VIDEO mode
options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=2,
)
landmarker = HandLandmarker.create_from_options(options)

# Open webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Could not open webcam")

# Function to compute Euclidean distance
def distance(p1, p2):
    return np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def isFingerExtended(tip, pip):
    return tip.y < pip.y

def isFist(lm):
    fingers = [
        isFingerExtended(lm[8], lm[6]),
        isFingerExtended(lm[12], lm[10]),
        isFingerExtended(lm[16], lm[14]),
        isFingerExtended(lm[20], lm[18]),
    ]
    return not any(fingers)

def isPinch(lm, w, h, threshold=40):
    idx = (int(lm[8].x * w), int(lm[8].y * h))
    thumb = (int(lm[4].x * w), int(lm[4].y * h))
    return np.linalg.norm(np.array(idx) - np.array(thumb)) < threshold

frame_count = 0  # For monotonically increasing timestamp
prev_cx = None
GESTURE_COOLDOWN_FRAMES = 8
cooldown = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape

    # Convert BGR to RGB for MediaPipe
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

    # Generate monotonically increasing timestamp (ms)
    timestamp_ms = frame_count * 33  # ~30 FPS
    hand_landmarker_result = landmarker.detect_for_video(mp_image, timestamp_ms)
    frame_count += 1

    gesture_text = ""

    # Process hand landmarks
    if hand_landmarker_result.hand_landmarks:
        for hand_landmarks in hand_landmarker_result.hand_landmarks:
            # Draw landmarks
            for lm in hand_landmarks:
                x_px = int(lm.x * w)
                y_px = int(lm.y * h)
                cv2.circle(frame, (x_px, y_px), 5, (0, 255, 0), -1)

            # Landmark references
            idx = hand_landmarks[8]      # index fingertip
            thumb = hand_landmarks[4]    # thumb tip
            wrist = hand_landmarks[0]
            mid_base = hand_landmarks[9] # middle finger MCP

            idx_x, idx_y = int(idx.x * w), int(idx.y * h)
            thumb_x, thumb_y = int(thumb.x * w), int(thumb.y * h)
            cx = int((wrist.x + mid_base.x) / 2 * w)
            cy = int((wrist.y + mid_base.y) / 2 * h)

        # --- Gesture Detection (Intent-Based) ---

        if cooldown > 0:
            cooldown -= 1
        else:
            # 1. DROP (Fist)
            if isFist(hand_landmarks):
                gesture_text = "DROP"
                cooldown = GESTURE_COOLDOWN_FRAMES

            # 2. ROTATE (Pinch + Handedness)
            elif isPinch(hand_landmarks, w, h):
                handedness = hand_landmarker_result.handedness[0][0].category_name

                if handedness == "Right":
                    gesture_text = "ROTATE CW"
                else:
                    gesture_text = "ROTATE CCW"

                cooldown = GESTURE_COOLDOWN_FRAMES

            # 3. MOVE (Horizontal Motion)
            else:
                if prev_cx is not None:
                    dx = cx - prev_cx

                    if dx > 25:
                        gesture_text = "MOVE RIGHT"
                        cooldown = GESTURE_COOLDOWN_FRAMES
                    elif dx < -25:
                        gesture_text = "MOVE LEFT"
                        cooldown = GESTURE_COOLDOWN_FRAMES

                prev_cx = cx

    # Display gesture text
    cv2.putText(frame, gesture_text, (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

    # Show frame
    cv2.imshow("Gesture Detection", frame)

    # ESC to quit
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
landmarker.close()