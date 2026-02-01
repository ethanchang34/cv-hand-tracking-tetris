import cv2
import pygame
import tetris
from gestures import detect_gesture


# --- Pygame init ---
pygame.init()

# --- Open webcam ---
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Could not open webcam")

GESTURE_COOLDOWN_FRAMES = 30
NEUTRAL_GESTURE_COOLDOWN_FRAMES = 10
cooldown = 0

frame_count = 0

# --- Trigger actions ---
def trigger_action(gesture):
    print(f"Action triggered: {gesture}")
    if gesture == "MOVE LEFT":
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT))
    elif gesture == "MOVE RIGHT":
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT))
    elif gesture in ["ROTATE CW", "ROTATE CCW"]:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP))
    elif gesture == "DROP":
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))

# --- Main loop ---
def main_loop():
    global frame_count, cooldown
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)

        # Detect gesture
        gesture_text = detect_gesture(frame)

        # Trigger the corresponding action
        trigger_action(gesture_text)

        # Draw gesture overlay
        cv2.putText(frame, gesture_text, (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

        # Show webcam
        cv2.imshow("Gesture Detection", frame)

        # ESC to quit
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
# Run Tetris in main thread
    import threading
    tetris_thread = threading.Thread(target=tetris.main)
    tetris_thread.start()

    # Run gesture detection loop
    main_loop()

    # Wait for Tetris to finish if it ever does
    tetris_thread.join()

    # Clean up Pygame
    pygame.quit()