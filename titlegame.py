# For this final project, I want to use my humble coding skills to polish the game structure i created for week 9 assignment.
# I will pick up the existing structure and make a more polished pygame.
import pygame
import random
import sys

pygame.init()

# Window settings
WIDTH, HEIGHT = 640, 480
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Navigator")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# --- Maze Generation Constants ---
# Size of each individual cell in the maze grid (in pixels)
CELL_SIZE = 40
# Thickness of the maze walls (in pixels)
WALL_THICKNESS = 4
# Number of columns in the maze grid based on window width and cell size
MAZE_COLS = WIDTH // CELL_SIZE
# Number of rows in the maze grid based on window height and cell size
MAZE_ROWS = HEIGHT // CELL_SIZE

# --- Player and Goal Sizing ---
# Player size, relative to CELL_SIZE for easy scaling
PLAYER_SIZE = CELL_SIZE // 2
# Goal size, relative to CELL_SIZE for easy scaling
GOAL_SIZE = CELL_SIZE // 2


class Wall:
    """Represents a wall segment in the maze."""

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface):
        """Draws the wall on the given surface."""
        pygame.draw.rect(surface, BLACK, self.rect)