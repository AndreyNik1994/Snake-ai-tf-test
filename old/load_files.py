import os
import sys


class Files:
    def __init__(self):
        self.main_directory = os.getcwd()
        self.folder_name = "borders"
        self.file_name = None
        self.file_list = None
        self.file = None
        self.x = list()
        self.y = list()

        self.files_in_dir()
        self.read_file()



    def files_in_dir(self):
        self.file_list = os.listdir(self.folder_name)



    def read_file(self):
        for i in range(len(self.file_list)):
            self.file_name = self.file_list[i]

            try:
                path = self.main_directory + "/" + self.folder_name
                os.chdir(path)
                with open(self.file_name, "r", newline="\n") as file:
                    for line in file:
                        line = line.splitlines(0)
                        line = line[0].split("\t")
                        self.x.append(int(line[0]))
                        self.y.append(int(line[1]))
                print(self.x, self.y, sep="\n")


            except IOError as e:
                print(e)
                sys.exit(1)
        return self.x, self.y
