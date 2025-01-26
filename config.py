import os

class Config:
    """Game configuration class"""
    # Visual parameters
    DOT_SIZE = 8
    BOARD_WIDTH = DOT_SIZE*20
    BOARD_HEIGHT = DOT_SIZE*20

    # Gameplay parameters
    INITIAL_DELAY = 25
    PAUSE_DELAY = 0
    START_POS = (80, 80)

    # AI parameters
    GAMMA = 0.95
    LEARNING_RATE = 0.001
    MEMORY_SIZE = 50000
    BATCH_SIZE = 1000
    SAVE_INTERVAL = 10
    MODEL_SAVE_PATH = os.path.join("saved_models")
    SAVE_NAME_PREFIX = "snake_ai"


    METRICS_WINDOWS_SIZE = 1000
    METRICS_UPDATE_INTERVAL = 10

    VERBOSE_LOGGING = True  # Set to True for per-game logging
    LOG_INTERVAL = 50