import pygame
import random
import sys

# --- Pygame init ---
pygame.init()

# --- Settings ---
SCREEN_WIDTH = 650
SCREEN_HEIGHT = 700
GRID_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
GRID_X_OFFSET = 50
GRID_Y_OFFSET = 30

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (40, 40, 40)

# Tetromino colors
COLORS = {
    'I': (0, 255, 255),
    'O': (255, 255, 0),
    'T': (128, 0, 128),
    'S': (0, 255, 0),
    'Z': (255, 0, 0),
    'J': (0, 0, 255),
    'L': (255, 165, 0),
}

# Tetromino shapes
SHAPES = {
    'I': [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
        [(0, 2), (1, 2), (2, 2), (3, 2)],
        [(1, 0), (1, 1), (1, 2), (1, 3)],
    ],
    'O': [
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
    ],
    'T': [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ],
    'S': [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
        [(1, 1), (2, 1), (0, 2), (1, 2)],
        [(0, 0), (0, 1), (1, 1), (1, 2)],
    ],
    'Z': [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(1, 0), (0, 1), (1, 1), (0, 2)],
    ],
    'J': [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    'L': [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
}

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris with Hand Gestures")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)


class Tetromino:
    def __init__(self, shape_type):
        self.shape_type = shape_type
        self.color = COLORS[shape_type]
        self.rotation = 0
        self.x = GRID_WIDTH // 2 - 2
        self.y = 0
    
    def get_blocks(self):
        shape = SHAPES[self.shape_type][self.rotation]
        return [(self.x + x, self.y + y) for x, y in shape]
                
    def rotate(self, direction=1):
        self.rotation = (self.rotation + direction) % 4

    def move(self, dx, dy):
        self.x += dx
        self.y += dy


class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.paused = False
        self.fall_time = 0
        self.fall_speed = 500  # milliseconds

    def new_piece(self):
        shape = random.choice(list(SHAPES.keys()))
        return Tetromino(shape)
    
    def valid_position(self, piece, adj_x=0, adj_y=0, adj_rotation=0):
        original_rotation = piece.rotation
        piece.rotation = (piece.rotation + adj_rotation) % 4

        for x, y in piece.get_blocks():
            new_x = x + adj_x
            new_y = y + adj_y

            if new_x < 0 or new_x >= GRID_WIDTH or new_y < 0 or new_y >= GRID_HEIGHT:
                piece.rotation = original_rotation
                return False
            
            if new_y >= 0 and self.grid[new_y][new_x] is not None:
                piece.rotation = original_rotation
                return False
            
        piece.rotation = original_rotation
        return True
    
    def lock_piece(self):
        for x, y in self.current_piece.get_blocks():
            if y >= 0:
                self.grid[y][x] = self.current_piece.color

        lines = self.clear_lines()

        if lines > 0:
            self.lines_cleared += lines
            points = {1: 100, 2: 300, 3: 500, 4: 800}
            self.score += points[lines] * self.level

            self.level = self.lines_cleared // 10 + 1
            # self.fall_speed = max(50, 500 - (self.level - 1) * 50)
            self.fall_speed = 500

        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()

        if not self.valid_position(self.current_piece):
            self.game_over = True

    def clear_lines(self):
        lines_to_clear = []
        for i, row in enumerate(self.grid):
            if all(cell is not None for cell in row):
                lines_to_clear.append(i)

        for i in lines_to_clear:
            del self.grid[i]
            self.grid.insert(0, [None for _ in range(GRID_WIDTH)])

        return len(lines_to_clear)
    
    def move_piece(self, dx, dy):
        if self.valid_position(self.current_piece, adj_x=dx, adj_y=dy):
            self.current_piece.move(dx, dy)
            return True
        return False
    
    def rotate_piece(self, direction=1):
        if self.valid_position(self.current_piece, adj_rotation=direction):
            self.current_piece.rotate(direction)
            return True
        
        for kick in [-1, 1, -2, 2]:
            if self.valid_position(self.current_piece, adj_x=kick, adj_rotation=direction):
                self.current_piece.rotate(direction)
                self.current_piece.move(kick, 0)
                return True
            
        return False
    
    def hard_drop(self):
        while self.move_piece(0, 1):
            self.score += 2
        self.lock_piece()

    def soft_drop(self):
        if not self.move_piece(0, 1):
            self.lock_piece()
        else:
            self.score += 1

    def get_ghost_position(self):
        ghost_y = self.current_piece.y

        while self.valid_position(self.current_piece, adj_y=ghost_y - self.current_piece.y + 1):
            ghost_y += 1

        return ghost_y
    
    def update(self, dt):
        if self.game_over or self.paused:
            return

        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            self.fall_time = 0
            if not self.move_piece(0, 1):
                self.lock_piece()

    def draw(self):
        screen.fill(BLACK)

        # Draw grid background
        grid_rect = pygame.Rect(
            GRID_X_OFFSET - 2,
            GRID_Y_OFFSET - 2,
            GRID_WIDTH * GRID_SIZE + 4,
            GRID_HEIGHT * GRID_SIZE + 4
        )
        pygame.draw.rect(screen, DARK_GRAY, grid_rect, 2)

        # Draw placed blocks
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x] is not None:
                    self.draw_block(x, y, self.grid[y][x])

        # Draw ghost piece
        if not self.game_over:
            ghost_y = self.get_ghost_position()
            for x, y in self.current_piece.get_blocks():
                ghost_block_y = y + (ghost_y - self.current_piece.y)
                if ghost_block_y >= 0:
                    rect = pygame.Rect(
                        GRID_X_OFFSET + x * GRID_SIZE,
                        GRID_Y_OFFSET + ghost_block_y * GRID_SIZE,
                        GRID_SIZE - 1,
                        GRID_SIZE - 1
                    )
                    pygame.draw.rect(screen, GRAY, rect, 2)

        # Draw current piece
        if not self.game_over:
            for x, y in self.current_piece.get_blocks():
                self.draw_block(x, y, self.current_piece.color)

        # Draw grid lines
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(
                screen, DARK_GRAY,
                (GRID_X_OFFSET + x * GRID_SIZE, GRID_Y_OFFSET),
                (GRID_X_OFFSET + x * GRID_SIZE, GRID_Y_OFFSET + GRID_HEIGHT * GRID_SIZE)
            )
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(
                screen, DARK_GRAY,
                (GRID_X_OFFSET, GRID_Y_OFFSET + y * GRID_SIZE),
                (GRID_X_OFFSET + GRID_WIDTH * GRID_SIZE, GRID_Y_OFFSET + y * GRID_SIZE)
            )
        
        self.draw_ui()

        if self.game_over:
            self.draw_game_over()
        elif self.paused:
            self.draw_paused()
    
    def draw_block(self, grid_x, grid_y, color):
        rect = pygame.Rect(
            GRID_X_OFFSET + grid_x * GRID_SIZE + 1,
            GRID_Y_OFFSET + grid_y * GRID_SIZE + 1,
            GRID_SIZE - 2,
            GRID_SIZE -2
        )
        pygame.draw.rect(screen, color, rect)

        highlight = tuple(min(255, c + 50) for c in color)
        pygame.draw.line(screen, highlight, rect.topleft, rect.topright, 2)
        pygame.draw.line(screen, highlight, rect.topleft, rect.bottomleft, 2)

        shadow = tuple(max(0, c - 50) for c in color)
        pygame.draw.line(screen, shadow, rect.bottomleft, rect.bottomright, 2)
        pygame.draw.line(screen, shadow, rect.topright, rect.bottomright, 2)

    def draw_ui(self):
        ui_x = GRID_X_OFFSET + GRID_WIDTH * GRID_SIZE + 30

        # Score
        score_text = font.render("SCORE", True, WHITE)
        screen.blit(score_text, (ui_x, 30))
        score_value = font.render(str(self.score), True, WHITE)
        screen.blit(score_value, (ui_x, 60))

        # Level
        level_text = font.render("LEVEL", True, WHITE)
        screen.blit(level_text, (ui_x, 120))
        level_value = font.render(str(self.level), True, WHITE)
        screen.blit(level_value, (ui_x, 150))

        # Lines
        lines_text = font.render("LINES CLEARED", True, WHITE)
        screen.blit(lines_text, (ui_x, 210))
        lines_value = font.render(str(self.lines_cleared), True, WHITE)
        screen.blit(lines_value, (ui_x, 240))

        # Next Piece
        next_text = font.render("NEXT", True, WHITE)
        screen.blit(next_text, (ui_x, 300))

        preview_x = ui_x + 20
        preview_y = 340

        for x, y in SHAPES[self.next_piece.shape_type][0]:
            rect = pygame.Rect(
                preview_x + x * 20,
                preview_y + y * 20,
                18,
                18
            )
            pygame.draw.rect(screen, self.next_piece.color, rect)

        # Controls
        controls = [
            "CONTROLS:",
            "Left/Right: Move",
            "Up: Rotate",
            "Down: Soft Drop",
            "Space: Hard Drop",
            "P: Pause",
            "R: Restart",
            "ESC: Quit"
        ]

        small_font = pygame.font.Font(None, 24)
        for i, text in enumerate(controls):
            control_text = small_font.render(text, True, GRAY)
            screen.blit(control_text, (ui_x, 450 + i * 25))

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        game_over_text = large_font.render("GAME OVER", True, WHITE)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(game_over_text, text_rect)

        score_text = font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        screen.blit(score_text, score_rect)

        restart_text = font.render("Press R to Restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        screen.blit(restart_text, restart_rect)

    def draw_paused(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        paused_text = large_font.render("PAUSED", True, WHITE)
        text_rect = paused_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(paused_text, text_rect)

        resume_text = font.render("Press P to Resume", True, WHITE)
        resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(resume_text, resume_rect)


def main():
    game = Game()
    pygame.key.set_repeat(150, 50)

    running = True
    while running:
        dt = clock.tick(60)

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

                if not game.game_over and not game.paused:
                    if event.key == pygame.K_LEFT:
                        game.move_piece(-1, 0)
                    if event.key == pygame.K_RIGHT:
                        game.move_piece(1, 0)
                    if event.key == pygame.K_UP:
                        game.rotate_piece()
                    if event.key == pygame.K_z:
                        game.rotate_piece(direction=-1)
                    if event.key == pygame.K_DOWN:
                        game.soft_drop()
                    if event.key == pygame.K_SPACE:
                        game.hard_drop()

        game.update(dt)
        game.draw()

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()