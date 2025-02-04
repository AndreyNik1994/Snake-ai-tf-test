import csv
import pandas as pd
from datetime import datetime
import os
from config import Config

class MetricLogger:
    def __init__(self):
        self.metrics = {
            "training_step": [],
            "game": [],
            "score": [],
            "best_score": [],
            "steps": [],
            "epsilon": [],
            "best_epsilon": [],
            "loss": [],
            "timestamp": [],
        }

        if not os.path.exists("metrics"):
            os.mkdir(os.path.join("metrics"))
        self.file_path = os.path.join("metrics", "training_metrics.csv")

        self._initialize_file()

    def _initialize_file(self):
        """Create CSV file with headers if it doesn't exist"""
        try:
            with open(self.file_path, 'x', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.metrics.keys())
                writer.writeheader()
        except FileExistsError:
            pass

    def add_record(self, training_step, game_num, score, best_score, steps, epsilon, best_epsilon, loss):
        """Add a new metrics record"""
        with open (self.file_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.metrics.keys())
            writer.writerow({
                'training_step': training_step,
                'game': game_num,
                'score': score,
                'best_score': best_score,
                'steps': steps,
                'epsilon': epsilon,
                'best_epsilon': best_epsilon,
                'loss': loss,
                'timestamp': datetime.now().isoformat(),
            })
        # Old version of metrics
        # self.metrics['training_step'].append(training_step)
        # self.metrics['game'].append(game_num)
        # self.metrics['score'].append(score)
        # self.metrics['best_score'].append(best_score)
        # self.metrics['steps'].append(steps)
        # self.metrics['epsilon'].append(epsilon)
        # self.metrics['best_epsilon'].append(best_epsilon)
        # self.metrics['loss'].append(loss)
        # self.metrics['timestamp'].append(datetime.now().isoformat())

    def save_to_file(self):
        """Save metrics to CSV file"""
        df = pd.DataFrame(self.metrics)
        df.to_csv(self.file_path, mode='w', index=False)
        print(f"Metrics saved to {self.file_path}")

    def save_to_excel(self):
        """Save metrics to Excel file (alternative format)"""
        df = pd.DataFrame(self.metrics)
        df.to_excel("training_metrics.xlsx", index=False)
        print(f"Metrics saved to training_metrics.xlsx")

    def get_recent_metrics(self, num_games=100):
        """Get recent metrics for console display"""
        return {k: v[-num_games:] for k, v in self.metrics.items()}