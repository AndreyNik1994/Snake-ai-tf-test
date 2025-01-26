from config import Config as Cons
from load_images import LoadImages
import sys
import os
from tkinter import Tk, Canvas, CENTER, ttk, Widget
from datetime import datetime


class Border(Canvas, Widget):
    def __init__(self, Widget):
        super().__init__(Widget, width=Cons.BOARD_WIDTH, height=Cons.BOARD_HEIGHT,
                         background="black", highlightthickness=0)
        self.border_image = LoadImages().border
        self.head = LoadImages().head
        self.pack()

    def draw_line(self, x1, y1, x2, y2):
        x1, y1, x2, y2 = self.coords_grid(x1, y1, x2, y2)
        x_len = self.int_r((x2 - x1)/Cons.DOT_SIZE)
        y_len = self.int_r((y2 - y1)/Cons.DOT_SIZE)

        for i in range(abs(x_len)):
            if x_len > 0:
                self.create_image(x1 + i*Cons.DOT_SIZE, y1, image=self.border_image, anchor=CENTER, tag="border")
            else:
                self.create_image(x1 - i * Cons.DOT_SIZE, y1, image=self.border_image, anchor=CENTER, tag="border")
        for i in range(abs(y_len)):
            if y_len > 0:
                self.create_image(x1+x_len*Cons.DOT_SIZE, y1+i*Cons.DOT_SIZE, image=self.border_image, anchor=CENTER, tag="border")
            else:
                self.create_image(x1 + x_len * Cons.DOT_SIZE, y1 - i * Cons.DOT_SIZE, image=self.border_image,
                                  anchor=CENTER, tag="border")


    def draw_line_control(self, x1, y1, x2, y2):
        x1, y1, x2, y2 = self.coords_grid(x1, y1, x2, y2)
        A, B, P, dx, dy = self.line_parameters(x1, y1, x2, y2)

        x_len = abs(int((x2 - x1)/Cons.DOT_SIZE))
        y_len = abs(int((y2 - y1)/Cons.DOT_SIZE))

        x = x1
        y = y1

        # slope < 1
        if abs(dy) < abs(dx):
            # slope up
            if dx >= 0 and dy >= 0:
                print("done")
                for i in range(x_len):

                    x = x1 + i * Cons.DOT_SIZE
                    if P >= 0:
                        y = y + Cons.DOT_SIZE
                        P = P + B
                    else:
                        y = y
                        P = P + A

                    self.create_image(x, y, image=self.border_image, anchor=CENTER, tag="border")
            # slope down
            elif dx >= 0 and dy < 0:
                print("done")
                for i in range(x_len):
                    x = x1 + i * Cons.DOT_SIZE
                    if P >= 0:
                        y = y - Cons.DOT_SIZE
                        P = P + B
                    else:
                        y = y
                        P = P + A

                    self.create_image(x, y, image=self.border_image, anchor=CENTER, tag="border")

            # slope up
            elif dx < 0 and dy >= 0:
                print("Done")
                for i in range(x_len):
                    x = x1 - i * Cons.DOT_SIZE
                    if P >= 0:
                        y = y + Cons.DOT_SIZE
                        P = P + B
                    else:
                        y = y
                        P = P + A

                    self.create_image(x, y, image=self.border_image, anchor=CENTER, tag="border")
            # slope down
            elif dx < 0 and dy < 0:

                for i in range(x_len):
                    print("Done")
                    x = x1 - i * Cons.DOT_SIZE
                    if P >= 0:
                        y = y - Cons.DOT_SIZE
                        P = P + B
                    else:
                        y = y
                        P = P + A

                    self.create_image(x, y, image=self.border_image, anchor=CENTER, tag="border")
        # slope > 1
        elif abs(dy) > abs(dx):
            # slope up
            if dx >= 0 and dy > 0:
                print("done")
                for i in range(y_len):
                    y = y1 + i * Cons.DOT_SIZE
                    if P >= 0:
                        x = x + Cons.DOT_SIZE
                        P = P + B
                    else:
                        x = x
                        P = P + A

                    self.create_image(x, y, image=self.border_image, anchor=CENTER, tag="border")
            # slope down
            elif dx >= 0 and dy < 0:
                print("done")
                for i in range(y_len):
                    y = y1 - i * Cons.DOT_SIZE

                    if P >= 0:
                        x = x + Cons.DOT_SIZE
                        P = P + B
                    else:
                        x = x
                        P = P + A

                    self.create_image(x, y, image=self.border_image, anchor=CENTER, tag="border")
            # slope up
            elif dx < 0 and dy > 0:
                for i in range(y_len):
                    print(A, B, P, "A ,B P")
                    y = y1 + i * Cons.DOT_SIZE
                    if P >= 0:
                        x = x - Cons.DOT_SIZE
                        P = P + B
                    else:
                        x = x
                        P = P + A

                    self.create_image(x, y, image=self.border_image, anchor=CENTER, tag="border")
            # slope down
            elif dx < 0 and dy <= 0:
                for i in range(y_len):
                    print("Done")
                    y = y1 - i * Cons.DOT_SIZE
                    if P >= 0:
                        x = x - Cons.DOT_SIZE
                        P = P + B
                    else:
                        x = x
                        P = P + A

                    self.create_image(x, y, image=self.border_image, anchor=CENTER, tag="border")

    def line_parameters(self, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1

        if abs(dy) > abs(dx):
            # print("inv")
            if dy <= 0 and dx >= 0:
                A = 2 * dx
                B = A + 2 * dy
                P = A + dy
            elif dy > 0 and dx >= 0:
                A = 2 * dx
                B = A - 2 * dy
                P = A - dy
            elif dy > 0 and dx < 0:
                A = -2 * dx
                B = A - 2 * dy
                P = A - dy
            elif dy <= 0 and dx < 0:
                A = - 2 * dx
                B = A + 2 * dy
                P = A + dy


        elif abs(dy) <= abs(dx):
            print("dir")
            if dy <= 0 and dx >= 0:
                A = -2 * dy
                B = A - 2 * dx
                P = A - dx
            elif dy > 0 and dx >=0:
                A = 2 * dy
                B = A - 2 * dx
                P = A - dx
            elif dy > 0 and dx < 0:
                A = 2 * dy
                B = A + 2 * dx
                P = A + dx
            elif dy <=0 and dx < 0:
                A = -2 * dy
                B = A + 2 * dx
                P = A + dx


        return A, B, P, dx, dy





    def int_r(self, number):
        number = int(number + (0.5 if number > 0 else -0.5))
        return number

    def sign(self, number):
        if number > 0:
            x = 1
        elif number < 0:
            x = -1
        else:
            x = 0
        return x


    def coords_grid(self, x1, y1, x2, y2):
        x1_grid = self.int_r(x1 / Cons.DOT_SIZE) * Cons.DOT_SIZE
        x2_grid = self.int_r(x2 / Cons.DOT_SIZE) * Cons.DOT_SIZE
        y1_grid = self.int_r(y1 / Cons.DOT_SIZE) * Cons.DOT_SIZE
        y2_grid = self.int_r(y2 / Cons.DOT_SIZE) * Cons.DOT_SIZE
        return (x1_grid, y1_grid, x2_grid, y2_grid)

    def collision_check(self):
        border_all = self.find_withtag("border")
        for i in range(len(border_all)):
            x1_over, y1_over, x2_over, y2_over = self.bbox(border_all[i])
            overlap = self.find_overlapping(x1_over, y1_over, x2_over, y2_over)
            if len(overlap) <= 2:
                x1_grid, y1_grid, x2_grid, y2_grid = self.coords_grid(x1_over, y1_over, x2_over, y2_over)
                self.create_image(x2_grid, y2_grid, image=self.head,
                                  tag="border_true", anchor=CENTER)
            else:
                pass
        for i in range(len(border_all)):
            self.delete(border_all[i])

        border_true = self.find_withtag("border_true")

        for i in range(len(border_true)):
            x1_over, y1_over, x2_over, y2_over = self.bbox(border_true[i])
            x1_grid, y1_grid, x2_grid, y2_grid = self.coords_grid(x1_over, y1_over, x2_over, y2_over)
            self.create_image(x2_grid, y2_grid, image=self.border_image,
                              tag="border", anchor=CENTER)
            self.delete(border_true[i])




class Building_creator():
    def __init__(self):
        self.save_path = os.getcwd() + "/borders"
        self.root = Tk()
        self.root.title("Border Creator")
        self.root.resizable(0, 0)
        self.create_items()
        self.variables()
        self.root.mainloop()


    def variables(self):
        self.left_click_check = False
        self.shift_left_click_check = False


    def create_items(self):
        self.frame = ttk.LabelFrame(self.root, text="Border creator", width=Cons.BOARD_WIDTH, height=Cons.BOARD_HEIGHT)
        self.frame.grid(column=0, row=0)
        self.border = Border(self.frame)
        self.border.grid(column=0, row=0, columnspan=3, rowspan=6)

        self.button_refresh = ttk.Button(self.frame, text="Refresh")
        self.button_refresh.grid(column=0, row=6)
        self.button_close = ttk.Button(self.frame, text="Exit")
        self.button_close.grid(column=2, row=6)
        self.button_save = ttk.Button(self.frame, text="Save")
        self.button_save.grid(column=1, row=6)

        self.buttons_commands()
        self.tap_func()


    def buttons_commands(self):
        self.button_close.configure(command=self._quit)
        self.button_refresh.configure(command=self.restart)
        self.button_save.configure(command=self.save)


    def _quit(self):
        self.root.destroy()
        self.root.quit()


    def restart(self):
        self.border.destroy()
        self.button_refresh.destroy()
        self.button_close.destroy()
        self.button_save.destroy()
        self.frame.destroy()
        self.create_items()

    def save(self):
        self.date = datetime.strftime(datetime.now(), "%Y_%m_%d_%H_%M_%S")
        self.filename = "border_" + self.date + ".txt"

        os.chdir(self.save_path)
        self.border.collision_check()
        border = self.border.find_withtag("border")
        try:
            self.file = open(self.filename, "a")
            for i in range(len(border)):
                self.data = self.border.coords(border[i])
                # x1, y1, x2, y2 = self.border.bbox(border[i])
                # x1, y1, x2, y2 = self.border.coords_grid(x1, y1, x2, y2)
                data = str(self.data[0]) + "\t" + str(self.data[1]) + "\n"
                self.file.write(data)

        except IOError as e:
            print(e)
            sys.exit(1)


    def tap_func(self):
        self.root.bind("<Key>", self.keysym_func)
        self.border.bind("<Button-1>", self.left_button_click)
        self.border.bind("<Button-2>", self.wheel_button_click)
        self.border.bind("<Button-3>", self.right_button_click)
        self.root.bind("<Control-z>", self.control_z_func)
        self.border.bind("<Control-Button-1>", self.control_left_click)
        self.border.bind("<Control-Button-3>", self.control_right_click)
        self.border.bind("<Shift-ButtonPress-1>", self.shift_left_click)
        self.border.bind("<Motion>", self.draw_pixel_border)
        self.border.bind("<Shift-ButtonRelease-1>", self.stop_draw_pixel_border)



    def left_button_click(self, event):
        print("left")
        self.x_left = event.x
        self.y_left = event.y
        print(self.x_left, self.y_left)
        self.left_click_check = True


    def right_button_click(self, event):
        print("right")
        self.x_right = event.x
        self.y_right = event.y
        print(self.x_right, self.y_right)

        if self.left_click_check == True:
            self.border.draw_line(self.x_left, self.y_left, self.x_right, self.y_right)
            self.left_click_check = False


    def shift_left_click(self, event):
        print("shift_left_click")


        self.shift_left_click_check = True

    def draw_pixel_border(self, event):
        if self.shift_left_click_check == True:
            self.x_left = event.x
            self.y_left = event.y

            self.x_left = self.border.int_r(self.x_left/Cons.DOT_SIZE)
            self.y_left = self.border.int_r(self.y_left/Cons.DOT_SIZE)
            self.x_left = self.x_left * Cons.DOT_SIZE
            self.y_left = self.y_left * Cons.DOT_SIZE

            self.border.create_image(self.x_left, self.y_left, image=self.border.border_image, anchor=CENTER, tag="border")

    def stop_draw_pixel_border(self, event):
        self.shift_left_click_check = False


    def wheel_button_click(self, event):
        print("wheel")

    def keysym_func(self, event):
        p=1
        # print(repr(event.keysym))

    def control_z_func(self, event):
        print("control-z")

    def control_left_click(self, event):
        print("Control with left mouse")
        self.x_left = event.x
        self.y_left = event.y
        self.left_click_check = True

    def control_right_click(self, event):
        print("Control with right mouse")
        self.x_right = event.x
        self.y_right = event.y

        if self.left_click_check == True:
            self.border.draw_line_control(self.x_left, self.y_left, self.x_right, self.y_right)
            self.left_click_check = False

if __name__ == "__main__":
    Building_creator()
