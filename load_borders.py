import sys
import os

class LoadBorders():
    """Load borders from the saved file (aka map)"""
    def __init__(self):
        self.path = os.path.join(os.getcwd(), 'borders')
        self.values = None
        self.file_list = None
        self.file = None
        self.x = list()
        self.y = list()

    def load_list_func(self):
        try:
            self.file_list = os.listdir(self.path)
            return self.file_list

        except IOError as e:
            print(e)
            sys.exit(1)

    def load_coords(self, file_name):
        try:
            path = os.path.join(self.path, file_name)
            with open(path, "r", newline="\n") as file:
                for line in file:
                    line = line.splitlines(0)
                    line = line[0].split("\t")
                    self.x.append(int(line[0]))
                    self.y.append(int(line[1]))
            os.chdir(os.getcwd())
            return self.x, self.y

        except IOError as e:
            print(e)
            sys.exit(1)