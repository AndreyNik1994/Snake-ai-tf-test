from enum import Enum
import numpy as np
from config import Config


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    def opposite(self):
        return {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }[self]


class Snake:
    """Manages snake state and movement"""

    def __init__(self):
        self.reset()

    def reset(self):
        """Placing snake in start position"""
        start_x, start_y = Config.START_POS
        self.body = [
            Config.START_POS,
            (start_x - Config.DOT_SIZE, start_y),
            (start_x - 2 * Config.DOT_SIZE, start_y),
            (start_x - 3 * Config.DOT_SIZE, start_y)
        ]

        self.direction = Direction.RIGHT
        self.growth_pending = 0

    def move(self):
        """Update snake position based on current direction"""
        dx, dy = self.direction.value
        new_head = (
            self.body[0][0] + dx * Config.DOT_SIZE,
            self.body[0][1] + dy * Config.DOT_SIZE
        )

        # Border wrapping logic
        if new_head[0] < 0:
            new_head = (Config.BOARD_WIDTH - Config.DOT_SIZE, new_head[1])
        elif new_head[0] >= Config.BOARD_WIDTH:
            new_head = (0, new_head[1])

        if new_head[1] < 0:
            new_head = (new_head[0], Config.BOARD_HEIGHT - Config.DOT_SIZE)
        elif new_head[1] >= Config.BOARD_HEIGHT:
            new_head = (new_head[0], 0)

        self.body.insert(0, new_head)

        if self.growth_pending > 0:
            self.growth_pending -= 1
        else:
            self.body.pop()


class Apple:
    """Manages apple placement"""

    def __init__(self):
        self.position = (0, 0)
        self.respawn()

    def respawn(self, exclude_positions=None):
        """Place apple avoiding snake and borders"""
        if exclude_positions is None:
            exclude_positions = []
        while True:
            x = np.random.randint(1, (Config.BOARD_WIDTH // Config.DOT_SIZE) - 1) * Config.DOT_SIZE
            y = np.random.randint(1, (Config.BOARD_HEIGHT // Config.DOT_SIZE) - 1) * Config.DOT_SIZE
            if (x, y) not in exclude_positions:
                self.position = (x, y)
                break


class Border:
    """Represents game wall objects"""

    def __init__(self, coordinates):
        self.coordinates = coordinates
        self.grid_cells = set((x // Config.DOT_SIZE, y // Config.DOT_SIZE)
                              for x, y in coordinates)
