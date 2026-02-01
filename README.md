# cv-hand-tracking-tetris
Play Tetris using real-time hand tracking powered by MediaPipe.

## Tech
- Python 3.10+
- MediaPipe
- OpenCV
- Pygame
- NumPy

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/ethanchang34/cv-hand-tracking-tetris.git
cd cv-hand-tracking-tetris
```

### 2. Create a virtual environment (recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

## Usage

Run the game with hand gesture control:
```bash
python src/main.py
```

### Controls
- **Right Hand:**
  - Thumb + Pinky Pinch → Rotate Clockwise
  - Thumb + Index Pinch → Rotate Counter-Clockwise
  
- **Left Hand:**
  - Thumb + Pinky Pinch → Rotate Counter-Clockwise
  - Thumb + Index Pinch → Rotate Clockwise

- **Either Hand:**
  - Fist → Drop
  - Open Hand Facing Left/Right → Move Left/Right

### Keyboard Controls (for testing)
- `LEFT/RIGHT` → Move piece
- `UP` → Rotate
- `DOWN` → Soft drop
- `SPACE` → Hard drop
- `P` → Pause
- `R` → Restart
- `ESC` → Quit