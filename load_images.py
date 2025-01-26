import sys
from PIL import Image, ImageTk
import os

class LoadImages:
    def __init__(self):
        """Load images from the disk"""
        self.img_names = [
            'dot.png',
            'eaten_dot.png',
            'head.png',
            'apple.png',
            'border.png',
        ]
        self.game_objects = dict()

        try:
            self.image_folder = os.path.join("images")
            for img_name in self.img_names:
                image_path = os.path.join(self.image_folder, img_name)
                image_file = Image.open(image_path)
                self.game_objects.update({img_name.split('.')[0]: ImageTk.PhotoImage(image_file)})

            self.dot = self.game_objects['dot']
            self.eaten_dot = self.game_objects['eaten_dot']
            self.head = self.game_objects['head']
            self.apple = self.game_objects['apple']
            self.border = self.game_objects['border']


        except IOError as e:
            print(e)
            sys.exit(1)

if __name__ == "__main__":
    import tkinter as tk
    root = tk.Tk()
    LoadImages()