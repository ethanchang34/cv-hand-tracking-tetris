import cv2
import numpy as np
import mediapipe as mp
import math

# === Settings ===
MODEL_PATH = "models/hand_landmarker.task"
GESTURE_COOLDOWN_FRAMES = 30
NEUTRAL_GESTURE_COOLDOWN_FRAMES = 10

# --- Setup MediaPipe ---
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=2,
)
landmarker = HandLandmarker.create_from_options(options)

# --- Internal state ---
cooldown = 0
frame_count = 0

# --- Utility functions ---
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

def isOpenHand(lm):
    fingers = [
        isFingerExtended(lm[8], lm[6]),   # index
        isFingerExtended(lm[12], lm[10]), # middle
        isFingerExtended(lm[16], lm[14]), # ring
        isFingerExtended(lm[20], lm[18]), # pinky
    ]
    return all(fingers)

def is_pinch_between(lm, w, h, i, j, threshold=40):
    p1 = np.array([lm[i].x * w, lm[i].y * h])
    p2 = np.array([lm[j].x * w, lm[j].y * h])
    return np.linalg.norm(p1 - p2) < threshold

# --- Main detection function ---
def detect_gesture(frame):
    global frame_count, cooldown

    h, w, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
    timestamp_ms = frame_count * 33
    hand_landmarker_result = landmarker.detect_for_video(mp_image, timestamp_ms)
    frame_count += 1

    gesture_text = ""
    if hand_landmarker_result.hand_landmarks:
        for hand_landmarks in hand_landmarker_result.hand_landmarks:

            if cooldown > 0:
                cooldown -= 1
                continue
            
            # --- Gesture Detection ---
            gesture_text = "NEUTRAL"
            cooldown = NEUTRAL_GESTURE_COOLDOWN_FRAMES

            # DROP (Fist)
            if isFist(hand_landmarks):
                gesture_text = "DROP"
                cooldown = GESTURE_COOLDOWN_FRAMES

            # ROTATE (Thumb-Pinky = Clockwise)
            elif is_pinch_between(hand_landmarks, w, h, 4, 20):
                gesture_text = "ROTATE CW"
                cooldown = GESTURE_COOLDOWN_FRAMES
            
            # ROTATE (Thumb-Index = Counter-Clockwise)
            elif is_pinch_between(hand_landmarks, w, h, 4, 8):
                gesture_text = "ROTATE CCW"
                cooldown = GESTURE_COOLDOWN_FRAMES

            # MOVE (Horizontal Motion)
            else:
                hand_label = hand_landmarker_result.handedness[0][0].category_name
                thumb_x = hand_landmarks[4].x
                pinky_x = hand_landmarks[20].x

                # How sideways the hand is (bigger = more slap-like)
                index_mcp = hand_landmarks[5]
                pinky_mcp = hand_landmarks[17]
                dx = pinky_mcp.x - index_mcp.x
                dy = pinky_mcp.y - index_mcp.y
                angle = abs(math.atan2(dy, dx))  # radians
                angle = min(angle, math.pi - angle)  # mirror left/right
                tilted = angle > math.radians(45)

                if tilted:
                    move_right = thumb_x < pinky_x
                    if move_right:
                        gesture_text = "MOVE RIGHT"
                    else:
                        gesture_text = "MOVE LEFT"

                    cooldown = GESTURE_COOLDOWN_FRAMES
    return gesture_text