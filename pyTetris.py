"""
Tetris Clone in Python using Pygame
Author: Josh O'Neill
Year: 2025
License: None
"""

import pygame
import random

# === Initialize Pygame ===
pygame.init()

# === Game Constants ===
COLUMNS = 10       # Number of columns in game grid
ROWS = 20          # Number of rows in game grid
CELL_SIZE = 30     # Size of each grid cell in pixels
GAME_WIDTH = COLUMNS * CELL_SIZE
GAME_HEIGHT = ROWS * CELL_SIZE
SIDEBAR_WIDTH = 200  # Width of the information sidebar
WINDOW_WIDTH = GAME_WIDTH + SIDEBAR_WIDTH
WINDOW_HEIGHT = GAME_HEIGHT

# === Color Definitions ===
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)       # Grid line color
CYAN = (0, 255, 255)      # I-piece color
BLUE = (0, 0, 255)        # J-piece color
ORANGE = (255, 165, 0)    # L-piece color
YELLOW = (255, 255, 0)    # O-piece color
GREEN = (0, 255, 0)       # S-piece color
PURPLE = (128, 0, 128)    # T-piece color
RED = (255, 0, 0)         # Z-piece color

# === Tetromino Configuration ===
SHAPES = {
    # Dictionary mapping piece types to their base shape matrices
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]]
}

COLORS = {
    # Maps piece types to their display colors
    'I': CYAN,
    'O': YELLOW,
    'T': PURPLE,
    'L': ORANGE,
    'J': BLUE,
    'S': GREEN,
    'Z': RED
}

class Tetromino:
    """Represents a single tetromino piece with rotation capabilities"""
    def __init__(self, x, y, shape):
        self.x = x              # Grid x-position (left edge)
        self.y = y              # Grid y-position (top edge)
        self.shape = shape      # Piece type identifier
        self.color = COLORS[shape]
        self.rotation = 0       # Current rotation index (0-3)
        self.shapes = self._get_rotations(SHAPES[shape])  # All rotation states
        self.current_shape = self.shapes[self.rotation]   # Active rotation state

    def _get_rotations(self, shape):
        """Generate all 4 rotational states of a piece using matrix rotation"""
        rotations = [shape]
        last_rotation = shape
        # Generate 3 additional rotations (90°, 180°, 270°)
        for _ in range(3):
            new_rotation = self._rotate_matrix(last_rotation)
            rotations.append(new_rotation)
            last_rotation = new_rotation
        return rotations

    def _rotate_matrix(self, shape):
        """Rotate a 2D matrix 90 degrees clockwise"""
        return [[shape[y][x] 
                for y in range(len(shape)-1, -1, -1)]
                for x in range(len(shape[0]))]

    def rotate(self):
        """Advance to next rotation state"""
        self.rotation = (self.rotation + 1) % len(self.shapes)
        self.current_shape = self.shapes[self.rotation]

class Tetris:
    """Main game controller handling game logic and state"""
    def __init__(self):
        self.grid = [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]  # Game board
        self.current_piece = self.new_piece()   # Active falling piece
        self.next_piece = self.new_piece()      # Preview piece
        self.score = 0                          # Player score
        self.level = 1                          # Current level
        self.fall_speed = 1000   # Time between automatic drops (milliseconds)
        self.last_fall = pygame.time.get_ticks()  # Timer for automatic drops
        self.game_over = False    # Game state flag

    def new_piece(self):
        """Create a new random tetromino piece"""
        shape = random.choice(list(SHAPES.keys()))
        # Center the piece horizontally (approximate for all shapes)
        return Tetromino(COLUMNS // 2 - 2, 0, shape)

    def valid_move(self, piece, x, y):
        """
        Check if a potential move is valid
        Args:
            piece: Tetromino piece to check
            x: Horizontal movement delta
            y: Vertical movement delta
        Returns:
            bool: True if move is valid, False if collision occurs
        """
        for row in range(len(piece.current_shape)):
            for col in range(len(piece.current_shape[row])):
                if piece.current_shape[row][col]:
                    new_x = piece.x + x + col
                    new_y = piece.y + y + row
                    # Check for:
                    # - Horizontal boundaries
                    # - Vertical bottom boundary
                    # - Collision with existing blocks
                    if (new_x < 0 or new_x >= COLUMNS or
                        new_y >= ROWS or
                        (new_y >= 0 and self.grid[new_y][new_x])):
                        return False
        return True

    def lock_piece(self):
        """Lock the current piece into the grid and check for game over"""
        for row in range(len(self.current_piece.current_shape)):
            for col in range(len(self.current_piece.current_shape[row])):
                if self.current_piece.current_shape[row][col]:
                    y = self.current_piece.y + row
                    x = self.current_piece.x + col
                    # Check if piece is locked above visible grid
                    if y < 0:
                        self.game_over = True
                        return
                    self.grid[y][x] = self.current_piece.color

        # Handle line clearing and piece management
        lines_cleared = self.clear_lines()
        self.update_score(lines_cleared)
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()

    def clear_lines(self):
        """Clear completed lines and return number of lines cleared"""
        lines_cleared = 0
        for row in range(ROWS):
            if all(self.grid[row]):  # Check if entire row is filled
                del self.grid[row]
                # Add new empty row at top
                self.grid.insert(0, [0 for _ in range(COLUMNS)])
                lines_cleared += 1
        return lines_cleared

    def update_score(self, lines):
        """
        Update score based on cleared lines and adjust level
        Scoring system:
        0 lines: 0 points
        1 line: 100 * level
        2 lines: 300 * level
        3 lines: 500 * level
        4 lines: 800 * level
        """
        line_scores = {0: 0, 1: 100, 2: 300, 3: 500, 4: 800}
        self.score += line_scores[lines] * self.level
        # Level up every 1000 points
        if self.score // 1000 > self.level:
            self.level += 1
            # Increase speed but cap at minimum 100ms
            self.fall_speed = max(100, 1000 - (self.level * 100))

    def move_down(self):
        """Move piece down one space or lock it if unable to move"""
        if self.valid_move(self.current_piece, 0, 1):
            self.current_piece.y += 1
        else:
            self.lock_piece()

    def hard_drop(self):
        """Instantly drop piece to lowest possible position"""
        while self.valid_move(self.current_piece, 0, 1):
            self.current_piece.y += 1
        self.lock_piece()

    def move_horizontal(self, dx):
        """Move piece horizontally by delta (dx) if possible"""
        if self.valid_move(self.current_piece, dx, 0):
            self.current_piece.x += dx

    def rotate(self):
        """Attempt to rotate piece with collision checking"""
        original_rotation = self.current_piece.rotation
        self.current_piece.rotate()
        # Revert rotation if it causes collision
        if not self.valid_move(self.current_piece, 0, 0):
            self.current_piece.rotation = original_rotation
            self.current_piece.current_shape = self.current_piece.shapes[self.current_piece.rotation]

# === Drawing Functions ===
def draw_grid(surface, grid):
    """Draw the game grid with existing blocks"""
    for y in range(ROWS):
        for x in range(COLUMNS):
            rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = grid[y][x] if grid[y][x] else GRAY  # Use gray for empty cells
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, BLACK, rect, 1)  # Grid lines

def draw_piece(surface, piece):
    """Draw the current falling piece"""
    for y in range(len(piece.current_shape)):
        for x in range(len(piece.current_shape[y])):
            if piece.current_shape[y][x]:
                rect = pygame.Rect(
                    (piece.x + x) * CELL_SIZE,
                    (piece.y + y) * CELL_SIZE,
                    CELL_SIZE, CELL_SIZE
                )
                pygame.draw.rect(surface, piece.color, rect)
                pygame.draw.rect(surface, BLACK, rect, 1)

def draw_sidebar(surface, next_piece, score, level):
    """Draw the right sidebar with game information"""
    font = pygame.font.Font(None, 36)
    
    # Next Piece Preview
    text = font.render("Next:", True, WHITE)
    surface.blit(text, (GAME_WIDTH + 10, 10))
    
    preview_x = GAME_WIDTH + 50
    preview_y = 50
    # Draw next piece preview
    for y in range(len(next_piece.current_shape)):
        for x in range(len(next_piece.current_shape[y])):
            if next_piece.current_shape[y][x]:
                rect = pygame.Rect(
                    preview_x + x * CELL_SIZE,
                    preview_y + y * CELL_SIZE,
                    CELL_SIZE, CELL_SIZE
                )
                pygame.draw.rect(surface, next_piece.color, rect)
                pygame.draw.rect(surface, BLACK, rect, 1)
    
    # Score Display
    text = font.render(f"Score: {score}", True, WHITE)
    surface.blit(text, (GAME_WIDTH + 10, 200))
    
    # Level Display
    text = font.render(f"Level: {level}", True, WHITE)
    surface.blit(text, (GAME_WIDTH + 10, 250))

def draw_game_over(surface):
    """Display game over screen"""
    font = pygame.font.Font(None, 72)
    text = font.render("GAME OVER", True, RED)
    text_rect = text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
    surface.blit(text, text_rect)

def main():
    """Main game loop and initialization"""
    # Initialize display
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    game = Tetris()

    # Game loop
    while True:
        screen.fill(BLACK)
        current_time = pygame.time.get_ticks()
        
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if game.game_over:
                    # Reset game on any key press after game over
                    game = Tetris()
                else:
                    # Control handling
                    if event.key == pygame.K_LEFT:
                        game.move_horizontal(-1)
                    elif event.key == pygame.K_RIGHT:
                        game.move_horizontal(1)
                    elif event.key == pygame.K_DOWN:
                        game.move_down()
                    elif event.key == pygame.K_UP:
                        game.rotate()
                    elif event.key == pygame.K_SPACE:
                        game.hard_drop()

        # Automatic Falling
        if not game.game_over and current_time - game.last_fall > game.fall_speed:
            game.move_down()
            game.last_fall = current_time

        # Rendering
        draw_grid(screen, game.grid)
        draw_piece(screen, game.current_piece)
        draw_sidebar(screen, game.next_piece, game.score, game.level)
        if game.game_over:
            draw_game_over(screen)
        
        # Update display
        pygame.display.flip()
        clock.tick(60)  # Cap at 60 FPS

if __name__ == "__main__":
    main()
