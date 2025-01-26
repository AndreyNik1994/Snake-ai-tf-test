# border.py
import os
import numpy as np
from config import Config

class BorderManager:
    """Handles loading and managing border walls"""

    def __init__(self):
        self.coordinates = []
        self.border_folder = "borders"

    def load_from_file(self, filename):
        """Load border coordinates from specified file"""
        self.coordinates = []
        try:
            with open(os.path.join(self.border_folder, filename), 'r') as f:
                for line in f:
                    x, y = line.strip().split('\t')
                    self.coordinates.append((
                        int(float(x)),
                        int(float(y))
                    ))
            return self.coordinates
        except Exception as e:
            print(f"Error loading borders: {e}")
            return False

    def get_scaled_coordinates(self):
        """Return coordinates scaled to game grid"""
        return [(x // Config.DOT_SIZE, y // Config.DOT_SIZE)
                for x, y in self.coordinates]