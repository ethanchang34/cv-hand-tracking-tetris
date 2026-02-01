import cv2
import pygame
import numpy as np
from tetris import Game, SCREEN_WIDTH, SCREEN_HEIGHT

# --- Pygame init ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris with Hand Gestures")
clock = pygame.time.Clock()

# --- Loading screen ---
font = pygame.font.Font(None, 36)
screen.fill((0, 0, 0))
loading_text = font.render("Loading MediaPipe model...", True, (255, 255, 255))
screen.blit(loading_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
pygame.display.flip()

# --- Open webcam ---
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Could not open webcam")

# --- Initialize gesture detection (loads ML model - can take a few seconds) ---
print("Loading hand tracking model...")
from gestures import detect_gesture
print("Model loaded!")

# --- Game setup ---
game = Game()

# --- Gesture-to-action mapping ---
def apply_gesture_to_game(gesture, game):
    """Map gesture to game action"""
    if gesture == "MOVE LEFT":
        game.move_piece(-1, 0)
    elif gesture == "MOVE RIGHT":
        game.move_piece(1, 0)
    elif gesture == "ROTATE CW":
        game.rotate_piece(direction=1)
    elif gesture == "ROTATE CCW":
        game.rotate_piece(direction=-1)
    elif gesture == "DROP":
        game.hard_drop()

# --- Get screen size ---
# Initialize Pygame display module
pygame.display.init()
screen_info = pygame.display.Info()
screen_width = screen_info.current_w
screen_height = screen_info.current_h

# Calculate desired webcam window size and position
window_width = int(screen_width * 1.25)
window_height = (screen_height * 2) // 3 
window_x = screen_width // 4
window_y = (screen_height) // 2

# --- Setup webcam window ---
window_name = "Hand Gesture Detection"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, window_width, window_height)
cv2.moveWindow(window_name, window_x, window_y)

# --- Main integrated loop ---
def main():
    running = True
    
    while running:
        # Get current time delta
        dt = clock.tick(60)  # 60 FPS
        
        # --- Handle pygame events (ESC to quit, P to pause, R to restart, etc.) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                if event.key == pygame.K_p:
                    game.paused = not game.paused
                
                if event.key == pygame.K_r:
                    game.reset()
                
                # Allow keyboard control too (for testing)
                if not game.game_over and not game.paused:
                    if event.key == pygame.K_LEFT:
                        game.move_piece(-1, 0)
                    if event.key == pygame.K_RIGHT:
                        game.move_piece(1, 0)
                    if event.key == pygame.K_UP:
                        game.rotate_piece()
                    if event.key == pygame.K_DOWN:
                        game.soft_drop()
                    if event.key == pygame.K_SPACE:
                        game.hard_drop()
        
        # --- Read webcam and detect gesture ---
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            
            # Detect gesture from frame (cooldown handled in gestures.py)
            gesture_text = detect_gesture(frame)
            
            # Apply gesture to game
            if gesture_text and gesture_text != "":
                apply_gesture_to_game(gesture_text, game)
                print(f"Gesture: {gesture_text}")
            
            # Draw gesture on webcam frame
            cv2.putText(frame, gesture_text, (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
        
        # --- Update game state ---
        game.update(dt)
        
        # --- Draw tetris game ---
        game.draw()
        pygame.display.flip()
        
        # --- Show webcam window ---
        if ret:
            cv2.imshow(window_name, frame)
        
        # Check for ESC key in OpenCV window
        if cv2.waitKey(1) & 0xFF == 27:
            running = False
    
    # --- Cleanup ---
    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()

if __name__ == "__main__":
    main()