import os.path
from os import PathLike

import keras

from model import SnakeModel
import numpy as np
from collections import deque
import random
from config import Config

# # Global
# MAX_MEMORY = 10000
# LR = 0.0001
# BATCH_SIZE = 10


class Agent:
    def __init__(self, input_size, load_existing=False):
        self.load_existing = load_existing
        if self.load_existing:
            try:
                self.model = self._load_existing_model()
                print("Agent is loaded as pretrained model")
            except:
                print("Failed to load model, creating new one")
                self.model = SnakeModel(input_size, [256, 64])
        else:
            self.model = SnakeModel(input_size,[256, 64])
        self.long_memory = deque(maxlen=Config.MEMORY_SIZE)
        self.short_memory = []
        self.gamma = Config.GAMMA
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995


        self.losses = []
        self.scores = []
        self.epsilons = []
        self.steps_history = []
        self.n_games = 0


    def get_action(self, state):
        """Epsilon-greedy action selection
        Return action as movement direction in format [up, left, down, right]"""
        if np.random.rand() < self.epsilon:
            return random.randint(0, 3)
        else:
            state = np.array(state).reshape(1, -1)
            q_values = self.model.predict(state)
            return np.argmax(q_values[0])


    def remember(self, data_to_remember: list | tuple | np.ndarray):
        """Checking data_to_remember length"""
        self.long_memory.append(data_to_remember)
        self.short_memory.append(data_to_remember)

    def replay(self):
        """Experience replay with mini-batch sampling"""
        if len(self.short_memory) < Config.BATCH_SIZE:
            return

        batch = random.sample(self.long_memory, Config.BATCH_SIZE)

        states, actions, rewards, next_states, dones = [], [], [], [], []
        targets, nums_of_not_done = [], []
        num = 0
        for state, action, reward, next_state, done in batch:
            targets.append(reward)
            states.append(state)
            actions.append(action)
            rewards.append(reward),
            next_states.append(next_state)
            dones.append(done)
            if not done:
                nums_of_not_done.append(num)

            num += 1

        next_qs = self.model.predict(np.array(next_states))
        next_qs = np.max(next_qs, axis=1)

        q_values = self.model.predict(np.array(states))

        for not_done_num in nums_of_not_done:
            targets[not_done_num] = rewards[not_done_num] + self.gamma * next_qs[not_done_num]

        for q_value, action, target  in zip(q_values, actions, targets):
            q_values[0][action] = target

        loss = self.model.train_step([np.array(states), np.array(q_values)])

        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

        # Reset short memory to continue learning
        self.short_memory = []
        return loss

    def record_metrics(self, score, steps):
        self.scores.append(score)
        self.steps_history.append(steps)
        self.epsilons.append(self.epsilon)

    def save_model(self, game_count, score):
        if not os.path.exists(Config.MODEL_SAVE_PATH):
            os.makedirs(Config.MODEL_SAVE_PATH)

        filename = f"{Config.SAVE_NAME_PREFIX}_game{game_count}_score{score}.h5"
        path = os.path.join(Config.MODEL_SAVE_PATH, filename)
        self.model.model.save(path, save_format='keras')
        print(f"Model saved to {path}")

    def clear_memory(self):
        self.long_memory.clear()
        self.scores.clear()
        self.epsilons.clear()
        self.losses.clear()

    def _load_existing_model(self, model_path: PathLike | str =os.path.join("trained_models/best_model.keras")):
        """Create agent with pretrained model"""
        try:
            model = keras.models.load_model(model_path)
            print("Loaded pretrained model successfully")
            return model
        except Exception as e:
            print(f"Error loading model")
            raise e
