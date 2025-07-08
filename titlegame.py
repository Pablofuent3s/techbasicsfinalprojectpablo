# For this final project, I want to use my humble coding skills to polish the game structure i created for week 9 assignment.
# I will pick up the existing structure and make a more polished pygame.
import pygame
import random
import sys
from pygame import mixer #(sound effects)

pygame.init()
mixer.init()
# Loading audio files
pygame.mixer.Sound ("media/collision.mp3")
pygame.mixer.Sound ("media/sound_effect_levelpass.mp3")
collision = pygame.mixer.Sound("media/collision.mp3")
levelpass = pygame.mixer.Sound("media/sound_effect_levelpass.mp3")
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

class Player:
    """Represents the player character."""

    def __init__(self, x, y, size):
        self.rect = pygame.Rect(x, y, size, size)
        self.speed = 2
        self.image = pygame.image.load("media/littlecarfromabove.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (25, 25))
        self.direction = 'UP'  # Default facing direction

    def move(self, keys, walls, game):
        """
        Moves the player based on key presses (arrow keys) and checks for collisions with walls.
        Collision detection is handled by attempting a move, then reverting if a collision occurs.
        This prevents the player from "sticking" to walls.
        """
        dx, dy = 0, 0
        if keys[pygame.K_UP]:
            dy = -self.speed
            self.direction = 'UP'
        elif keys[pygame.K_DOWN]:
            dy = self.speed
            self.direction = 'DOWN'
        elif keys[pygame.K_LEFT]:
            dx = -self.speed
            self.direction = 'LEFT'
        elif keys[pygame.K_RIGHT]:
            dx = self.speed
            self.direction = 'RIGHT'

        # Store the original position before attempting movement
        original_x, original_y = self.rect.x, self.rect.y

        # Attempt to move horizontally and check for collisions
        self.rect.x += dx
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                mixer.Sound.play(collision)
                self.rect.x = original_x  # Revert x movement if collision detected
                game.collisions += 1  # Count collision
                break

        # Attempt to move vertically and check for collisions
        self.rect.y += dy
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                mixer.Sound.play(collision)
                self.rect.y = original_y  # Revert y movement if collision detected
                game.collisions += 1  # Count collision
                break

    def draw(self, surface):
        """Draws the player on the given surface."""
        # Choose angle based on direction
        angle = 0
        if self.direction == 'UP':
            angle = 0
        elif self.direction == 'RIGHT':
            angle = -90
        elif self.direction == 'DOWN':
            angle = 180
        elif self.direction == 'LEFT':
            angle = 90

        # Rotate original image (not already-rotated one)
        rotated_image = pygame.transform.rotate(self.image, angle)
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        surface.blit(rotated_image, rotated_rect.topleft)


class Goal:
    """Represents the goal in the maze."""

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface):
        """Draws the goal on the given surface."""
        pygame.draw.rect(surface, GREEN, self.rect)


class Cell:
    """
    Represents a single cell within the maze grid.
    Used for the logical representation of the maze during generation.
    """

    def __init__(self, x, y):
        self.x, self.y = x, y  # Grid coordinates (column, row)
        self.visited = False  # Flag used by maze generation algorithm
        # Dictionary to keep track of walls: True if wall exists, False if removed
        self.walls = {'N': True, 'S': True, 'E': True, 'W': True}

    def get_neighbors(self, grid):
        """
        Finds and returns all unvisited neighbors of the current cell.
        A neighbor is returned as a tuple: (neighbor_cell_object, direction_from_current_cell).
        """
        neighbors = []
        # Check North neighbor
        if self.y > 0 and not grid[self.y - 1][self.x].visited:
            neighbors.append((grid[self.y - 1][self.x], 'N'))
        # Check South neighbor
        if self.y < MAZE_ROWS - 1 and not grid[self.y + 1][self.x].visited:
            neighbors.append((grid[self.y + 1][self.x], 'S'))
        # Check East neighbor
        if self.x < MAZE_COLS - 1 and not grid[self.y][self.x + 1].visited:
            neighbors.append((grid[self.y][self.x + 1], 'E'))
        # Check West neighbor
        if self.x > 0 and not grid[self.y][self.x - 1].visited:
            neighbors.append((grid[self.y][self.x - 1], 'W'))
        return neighbors


def remove_walls(current_cell, next_cell, direction):
    """
    Removes the wall between two adjacent cells, making a path.
    This operation is symmetrical, updating the wall status for both cells.
    """
    if direction == 'N':  # 'next_cell' is North of 'current_cell'
        current_cell.walls['N'] = False
        next_cell.walls['S'] = False
    elif direction == 'S':  # 'next_cell' is South of 'current_cell'
        current_cell.walls['S'] = False
        next_cell.walls['N'] = False
    elif direction == 'E':  # 'next_cell' is East of 'current_cell'
        current_cell.walls['E'] = False
        next_cell.walls['W'] = False
    elif direction == 'W':  # 'next_cell' is West of 'current_cell'
        current_cell.walls['W'] = False
        next_cell.walls['E'] = False


def generate_maze_recursive_backtracking(rows, cols):
    """
    Generates a maze grid using the Recursive Backtracking algorithm.
    This algorithm starts at a cell, explores unvisited neighbors randomly,
    carving paths by removing walls, and backtracking when no unvisited
    neighbors are available.
    Returns a 2D list (grid) of Cell objects, representing the maze structure.
    """
    grid = [[Cell(x, y) for x in range(cols)] for y in range(rows)]
    stack = []  # Stack to keep track of visited cells for backtracking

    # Start the maze generation from the top-left cell (0,0)
    start_cell = grid[0][0]
    start_cell.visited = True
    stack.append(start_cell)

    while stack:
        current_cell = stack[-1]  # Look at the top of the stack (current position)

        neighbors = current_cell.get_neighbors(grid)

        if neighbors:
            # If there are unvisited neighbors, pick one randomly
            next_cell, direction_to_neighbor = random.choice(neighbors)

            # Carve a path by removing the wall between the current and next cell
            remove_walls(current_cell, next_cell, direction_to_neighbor)

            # Move to the next cell: mark it visited and push onto the stack
            next_cell.visited = True
            stack.append(next_cell)
        else:
            # If no unvisited neighbors, backtrack by popping the current cell from the stack
            stack.pop()
    return grid


class Game:
    """Main game class to manage game state, logic, and rendering."""
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.running = True
        self.level = 1
        self.max_levels = 3
        self.font = pygame.font.SysFont(None, 36)
        self.title_font = pygame.font.SysFont(None, 48)
        self.collisions = 0
        self.start_time = pygame.time.get_ticks()  # In milliseconds
        # Initial maze and game elements
        self.generate_new_maze()

    def convert_grid_to_pygame_walls(self, grid):
        """Converts the logical maze grid into clean, non-overlapping Pygame walls."""
        walls = []

        # Border walls (frame)
        walls.append(Wall(0, 0, WIDTH, WALL_THICKNESS))  # Top
        walls.append(Wall(0, HEIGHT - WALL_THICKNESS, WIDTH, WALL_THICKNESS))  # Bottom
        walls.append(Wall(0, 0, WALL_THICKNESS, HEIGHT))  # Left
        walls.append(Wall(WIDTH - WALL_THICKNESS, 0, WALL_THICKNESS, HEIGHT))  # Right

        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                px = x * CELL_SIZE
                py = y * CELL_SIZE

                # South wall (draw only if last row or cell has bottom wall)
                if cell.walls['S']:
                    walls.append(Wall(
                        px,
                        py + CELL_SIZE - WALL_THICKNESS,
                        CELL_SIZE,
                        WALL_THICKNESS
                    ))

                # East wall (draw only if last column or cell has right wall)
                if cell.walls['E']:
                    walls.append(Wall(
                        px + CELL_SIZE - WALL_THICKNESS,
                        py,
                        WALL_THICKNESS,
                        CELL_SIZE
                    ))

        return walls

    def generate_new_maze(self):
        """Generates a new maze and updates walls, player, and goal."""
        self.maze_grid = generate_maze_recursive_backtracking(MAZE_ROWS, MAZE_COLS)
        self.walls = self.convert_grid_to_pygame_walls(self.maze_grid)

        # Player starts at top-left
        player_start_x = CELL_SIZE // 2 - (PLAYER_SIZE // 2)
        player_start_y = CELL_SIZE // 2 - (PLAYER_SIZE // 2)
        self.player = Player(player_start_x, player_start_y, PLAYER_SIZE)

        # Goal at bottom-right
        goal_x = (MAZE_COLS - 1) * CELL_SIZE + (CELL_SIZE // 2 - (GOAL_SIZE // 2))
        goal_y = (MAZE_ROWS - 1) * CELL_SIZE + (CELL_SIZE // 2 - (GOAL_SIZE // 2))
        self.goal = Goal(goal_x, goal_y, GOAL_SIZE, GOAL_SIZE)

    def show_start_screen(self):
        """Displays an intro screen with instructions."""
        WIN.fill(WHITE)
        title = self.title_font.render("Maze Navigator", True, BLACK)
        instructions1 = self.font.render("Test your reflexes with this pygame!", True, BLACK)
        instructions2 = self.font.render("Use the arrow keys to move the blue square.", True, BLACK)
        instructions3 = self.font.render("Get to the green square to pass the level.", True, BLACK)
        instructions4 = self.font.render("You need to complete three levels to win.", True, BLACK)
        start_msg = self.font.render("Press any key to continue...", True, BLUE)

        WIN.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
        WIN.blit(instructions1, (WIDTH // 2 - instructions1.get_width() // 2, 125))
        WIN.blit(instructions2, (WIDTH // 2 - instructions2.get_width() // 2, 160))
        WIN.blit(instructions3, (WIDTH // 2 - instructions3.get_width() // 2, 200))
        WIN.blit(instructions4, (WIDTH // 2 - instructions4.get_width() // 2, 240))
        WIN.blit(start_msg, (WIDTH // 2 - start_msg.get_width() // 2, 320))

        pygame.display.update()

        # Wait for any key press
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    waiting = False

    def show_victory_screen(self):
        """Displays a victory message after all levels are completed."""
        WIN.fill(WHITE)
        total_time = (pygame.time.get_ticks() - self.start_time) // 1000

        victory = self.title_font.render("Congrats!", True, GREEN)
        message = self.font.render("You completed all the levels.", True, BLACK)
        time_msg = self.font.render(f"Total time: {total_time} s", True, BLACK)
        coll_msg = self.font.render(f"Time stuck in a wall: {self.collisions} ms", True, BLACK)
        exit_msg = self.font.render("Close the window to exit the game.", True, BLUE)

        WIN.blit(victory, (WIDTH // 2 - victory.get_width() // 2, 100))
        WIN.blit(message, (WIDTH // 2 - message.get_width() // 2, 160))
        WIN.blit(time_msg, (WIDTH // 2 - time_msg.get_width() // 2, 200))
        WIN.blit(coll_msg, (WIDTH // 2 - coll_msg.get_width() // 2, 240))
        WIN.blit(exit_msg, (WIDTH // 2 - exit_msg.get_width() // 2, 300))

        pygame.display.update()

        # Wait until window is closed
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

    def run(self):
        """Starts and manages the main game loop."""
        self.show_start_screen()

        while self.running:
            self.clock.tick(60)
            WIN.fill(WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            keys = pygame.key.get_pressed()
            self.player.move(keys, self.walls, self)

            for wall in self.walls:
                wall.draw(WIN)
            self.goal.draw(WIN)
            self.player.draw(WIN)

            if self.player.rect.colliderect(self.goal.rect):
                levelpass.play()
                pygame.time.delay(500)

                if self.level < self.max_levels:
                    self.level += 1
                    self.generate_new_maze()
                else:
                    self.show_victory_screen()
            # Display collision count and timer
            elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000  # in seconds
            timer_text = self.font.render(f"Time: {elapsed_time}s", True, BLACK)
            collision_text = self.font.render(f"Collision time: {self.collisions} ms", True, BLACK)
            WIN.blit(timer_text, (10, 10))
            WIN.blit(collision_text, (10, 40))
            pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()

# use the keys up, down, left and right to get the blue cube to meet the green cube!