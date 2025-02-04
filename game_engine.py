import numpy as np

from config import Config
from game_entities import Direction, Snake, Apple, Border
from border import BorderManager

class GameEngine:
    """Handles game logic and state management"""
    def __init__(self, file_name):
        self.snake = Snake()
        self.apple = Apple()
        self.border_manager = BorderManager()
        self.game_over = False
        self.border = Border(self.border_manager.load_from_file(f'{file_name}.txt'))
        self.satiety = 1
        self.score = 0
        self.frame_iteration = 0
        self.max_distance = (Config.BOARD_WIDTH**2 + Config.BOARD_HEIGHT**2)**0.5
        self.apple_just_eaten = False
        self.prev_distance = self.get_apple_distance()
        self.reward = 0
        self.max_reward = 10
        self.min_reward = -10
        self.step_distance = 8

    def reset(self):
        self.snake.reset()
        self.apple.respawn(exclude_positions=self.snake.body + self.border.coordinates)
        self.reward = 0
        self.score = 0
        self.frame_iteration = 0
        self.game_over = False

    def get_apple_distance(self):
        head = self.snake.body[0]
        apple = self.apple.position

        dx = abs(apple[0] - head[0])
        dy = abs(apple[1] - head[1])

        dx = min(dx, Config.BOARD_WIDTH - dx)
        dy = min(dx, Config.BOARD_HEIGHT - dy)

        return (dx**2 + dy**2)**0.5

    def _get_danger_states(self, head: tuple | list | np.ndarray):
        directions = [
            Direction.UP.value,
            Direction.DOWN.value,
            Direction.LEFT.value,
            Direction.RIGHT.value
        ]

        # Danger detection
        danger = [self._is_collision(
            (head[0] + dx * Config.DOT_SIZE, head[1] + dy * Config.DOT_SIZE)
        ) for dx, dy in directions]

        return danger

    def get_state(self):
        """Create state array for neural network input"""
        head = list(self.snake.body[0])

        danger = self._get_danger_states(self.snake.body[0])

        # Apple location
        apple_relative_location = [
            self.apple.position[1] < head[1],  # Up
            self.apple.position[1] > head[1],  # Down
            self.apple.position[0] < head[0],  # Left
            self.apple.position[0] > head[0]  # Right
        ]

        apple_distance = [self.get_apple_distance() / self.max_distance]

        satiety = [self.satiety]
        return np.array(head + danger + list(self.apple.position) + apple_relative_location + apple_distance + satiety, dtype=int)

    def _is_collision(self, pt):
        """Check collisions with self and borders"""
        # Convert to grid coordinates
        grid_pt = (pt[0] // Config.DOT_SIZE, pt[1] // Config.DOT_SIZE)

        # Boundary check (wrap instead of die)
        if not (0 <= grid_pt[0] < Config.BOARD_WIDTH // Config.DOT_SIZE or
                0 <= grid_pt[1] < Config.BOARD_HEIGHT // Config.DOT_SIZE):
            return False  # Allow wrapping

        # Self collision
        if grid_pt in {(x // Config.DOT_SIZE, y // Config.DOT_SIZE)
                       for x, y in self.snake.body[1:]}:
            return True

        # Border collision
        if self.border and grid_pt in self.border.grid_cells:
            return True
        return False


    def _update_direction(self, action):
        """Convert neural network output to direction change"""
        directions = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]

        # Prevent 180-degree turns
        current_dir = self.snake.direction
        if action == 0 and current_dir != Direction.DOWN:
            new_dir = Direction.UP
        elif action == 1 and current_dir != Direction.UP:
            new_dir = Direction.DOWN
        elif action == 2 and current_dir != Direction.RIGHT:
            new_dir = Direction.LEFT
        elif action == 3 and current_dir != Direction.LEFT:
            new_dir = Direction.RIGHT
        else:
            new_dir = current_dir  # Maintain current direction if invalid move

        self.snake.direction = new_dir


    def step(self, action):
        if self.game_over:
            return 0, True, self.score, 0
        """Perform one game step"""
        self.frame_iteration += 1
        game_over = False

        # Update direction
        self._update_direction(action)

        # Move snake
        self.snake.move()

        # Hungry motivator
        self.satiety -= 0.005

        # Moving in right direction reward / penalty
        new_dist = self.get_apple_distance()
        distance_reward = (self.prev_distance - new_dist) / self.step_distance
        print(distance_reward)
        self.prev_distance = new_dist


        # Skipping false negative reward right after eating an apple.
        if self.apple_just_eaten:
            self.reward += 0
            self.apple_just_eaten = False
        else:
            self.reward += 2 * distance_reward

        # Eaten self penalty
        if self._is_collision(self.snake.body[0]):
            self.reward -= 5
            game_over = True
            return self.reward, game_over, self.score, self.satiety

        # Die from hungry penalty
        if self.satiety <= 0:
            self.reward -= 5
            game_over = True
            return self.reward, game_over, self.score, self.satiety

        # Check apple consumption
        if self.snake.body[0] == self.apple.position:
            self.score += 1
            self.reward += 8
            self.snake.growth_pending += 1
            self.satiety = 1
            self.apple_just_eaten = True
            self.apple.respawn(exclude_positions=self.snake.body)

        # Penalize repetitive behavior
        self.reward -= 0.1 * (self.frame_iteration % 100 == 0)
        self.reward -= 0.1
        if not game_over:
            self.reward += 0.5


        if self.reward >= self.max_reward:
            self.reward = self.max_reward
        elif self.reward <= self.min_reward:
            self.reward = self.min_reward
        self.reward /= self.max_reward
        return self.reward, game_over, self.score, self.satiety