import tkinter as tk
from tkinter import Canvas, ALL, CENTER, ttk
from config import Config
from load_images import LoadImages
from game_engine import GameEngine
from agent import Agent
from load_borders import LoadBorders
import numpy as np
from metrics import MetricLogger


class SnakeGameGUI:
    """Handles GUI visualization and game loop"""

    def __init__(self, root, border_map="empty"):
        self.root = root
        self.root.title("AI Snake Game")
        self.root.resizable(False, False)

        # Game components
        self.border_map = border_map
        self.engine = GameEngine(file_name=self.border_map)
        self.after_id = None
        self._initialize_agent(
            input_size=14)  # 2 head coordinates + 4 dangers + 2 apple coordinates + 4 apple directions + apple distance + satiety
        self.images = LoadImages()
        self.border_loader = LoadBorders()

        self.metrics_logger = MetricLogger()
        self.training_step_counter = 0

        with open("score.txt", "r") as file:
            self.score_stored = int(file.read())

        # GUI setup
        self._create_gui()
        self._setup_bindings()
        self.running = False
        self.total_games = 0
        self.high_score = 0


    def _create_gui(self):
        """Initialize visual elements and buttons"""
        # Drawing input_size frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        # Drawing game Board
        self.canvas = Canvas(
            self.main_frame,
            width=Config.BOARD_WIDTH,
            height=Config.BOARD_HEIGHT,
            bg="black",
            highlightthickness=0
        )
        self.canvas.grid(row=0, column=0, columnspan=3, rowspan=5, padx=5, pady=5)

        # Drawing buttons
        self.btn_restart = ttk.Button(self.main_frame, text="Restart", command=self.reset_game)
        self.btn_restart.grid(row=5, column=0, padx=5, pady=5)

        self.btn_close = ttk.Button(self.main_frame, text="Close", command=self.root.destroy)
        self.btn_close.grid(row=5, column=1, padx=5, pady=5)

        # Score display
        self.score_text = self.canvas.create_text(
            10, 10,
            text=f"Score: 0 | High: 0 | Games: 0",
            fill="white",
            anchor="nw",
            font=('Arial', 10)
        )

        # Game over display
        self.game_over_text = self.canvas.create_text(
            Config.BOARD_WIDTH / 2,
            Config.BOARD_HEIGHT / 2,
            text="",
            fill="red",
            font=('Arial', 24),
            state="hidden"
        )

        self.metrics_text = self.canvas.create_text(
            Config.BOARD_WIDTH - 10, 10,
            text="",
            fill="white",
            anchor="ne",
            font=('Arial', 10),
            tags="metrics"
        )

    def _setup_bindings(self):
        """Set up control bindings"""
        self.root.bind('<space>', lambda _: self.toggle_pause())
        self.root.bind('r', lambda _: self.reset_game())
        self.root.bind('p', lambda _: self.toggle_pause())

    def reset_game(self):
        """Reset game state"""
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.engine = GameEngine(self.border_map)  # Creates fresh engine instance
        self.engine.game_over = False
        self.canvas.itemconfig(self.game_over_text, state="hidden")
        self.running = True
        self._draw_objects()
        self.after_id = self.root.after(Config.INITIAL_DELAY, self._update_game)

    def _update_game(self):
        """Main game update log"""
        self.after_id = None

        try:
            if self.running and not self.engine.game_over:


                # Get current state
                state = np.array(self.engine.get_state() + self.total_games)


                # Get AI action
                action = self.agent.get_action(state)


                # Perform game step
                reward, done, score, satiety = self.engine.step(action)


                # Get new state and remember experience
                new_state = np.array(self.engine.get_state() + self.total_games)


                # Store experience
                self.agent.remember([self.engine.score, (state, action, reward, new_state, done)])


                # Trying to fix a disbalanced data in memory
                if not done and self.engine.apple_just_eaten:
                    for _ in range(2 ** 5):
                        self.agent.remember([self.engine.score, (state, action, reward, new_state, done)])

                if len(self.agent.short_memory) >= Config.BATCH_SIZE:
                    self._log_training_metrics()
                    self.training_step_counter += 1

                # Train short memory
                loss = self.agent.replay()


                self.agent.losses.append(loss)
                self.agent.scores.append(self.engine.score)


                # Update display
                self._draw_objects()

                if done:
                    if score > self.agent.best_score:
                        self.agent.update_best_model(score)  # Updating best model if games ended
                    self._handle_game_over()
                    self.reset_game()
                    return
                self.after_id = self.root.after(Config.INITIAL_DELAY, self._update_game)

        except Exception as e:
            print(f"Game loop error: {e}")
            self._handle_game_over()

    def _log_training_metrics(self):
        """Logs metrics before each training step"""
        current_game = self.total_games + (1 if not self.engine.game_over else 0)
        metrics_text = (
            f"\n--Training Step {self.training_step_counter}---\n"
            f"Current Game: {current_game}\n"
            f"Current Score: {self.engine.score}\tBest Score: {self.agent.best_score}\tAvg Score: {self.agent.avg_score:.4f}\n"
            f"Steps in Game: {self.engine.frame_iteration}\n"
            f"Epsilon: {self.agent.epsilon:.6f}\tBest Epsilon: {self.agent.best_epsilon:.6f}\n"
            f"Memory Size: {len(self.agent.long_memory)}\n"
        )

        print(metrics_text)


        self.metrics_logger.add_record(
            training_step=self.training_step_counter,
            game_num=current_game,
            score=self.engine.score,
            best_score=self.agent.best_score,
            steps=self.engine.frame_iteration,
            epsilon=self.agent.epsilon,
            best_epsilon=self.agent.best_epsilon,
            loss=self.agent.losses[-1] if self.agent.losses else 0
        )

    def _initialize_agent(self, input_size=4):
        """Load pretrained model instead of creating new"""
        self.agent = Agent(input_size=input_size)

    def _draw_objects(self):
        """Drawing objects on the canvas"""

        # Deleting all previous objects from the canvas
        self.canvas.delete(ALL)

        # Drawing Snake body and head
        for idx, (x, y) in enumerate(self.engine.snake.body):
            img = self.images.head if idx == 0 else self.images.dot
            self.canvas.create_image(x, y, image=img, anchor=CENTER)

        # Drawing borders
        for idx, (x, y) in enumerate(self.engine.border.coordinates):
            img = self.images.border
            self.canvas.create_image(x, y, image=img, anchor=CENTER)

        # Update score display
        self.canvas.itemconfig(self.score_text,
                               text=f"Score: {self.engine.score} | High: {self.high_score} | Games: {self.total_games}")

        # Drawing an apple
        self.canvas.create_image(
            self.engine.apple.position[0],
            self.engine.apple.position[1],
            image=self.images.apple,
            anchor=CENTER
        )

    def toggle_pause(self):
        """Toggle pause state"""
        self.running = not self.running
        if self.running:
            self.canvas.itemconfig(self.game_over_text, state="Hidden")
            self._update_game()
        else:
            if self.after_id is not None:
                self.root.after_cancel(self.after_id)
                self.after_id = None

    def _handle_game_over(self):
        """Handle game over state"""
        # Ensure game state is fully reset
        self.running = False
        self.engine.game_over = True
        self.total_games += 1
        self.high_score = max(self.high_score, self.engine.score)

        if self.high_score > int(self.score_stored):
            with open("score.txt", "w+") as file:
                file.write("{0}".format(self.high_score))

        # Show game over text
        self.canvas.itemconfig(self.game_over_text,
                               text=f"Gave Over! Score: {self.engine.score}\nPress R to restart",
                               state="normal")


        if self.total_games % Config.SAVE_INTERVAL == 0:
            self.agent.save_model(
                game_count=self.total_games,
                score=self.engine.score
            )

        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        # Record metrics
        if self.engine.score > self.high_score:
            self.agent.save_model(self.total_games, self.engine.score)
            self.agent.restore_best_model()


if __name__ == "__main__":
    mainroot = tk.Tk()
    game = SnakeGameGUI(mainroot, border_map="empty")
    mainroot.after(Config.INITIAL_DELAY, game.reset_game)  # Initial delay before starting
    mainroot.mainloop()
