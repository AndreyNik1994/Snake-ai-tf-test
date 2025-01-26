import random
import tkinter as tk
from tkinter import Tk, Canvas, ALL, CENTER, ttk, Widget

import numpy as np
# from adodbapi.ado_consts import directions
from agent import Agent
from config import Cons as Cons
import load_borders as lb
from load_images import LoadImages


class Board(Canvas, Widget):
    def __init__(self, Widget, checkmode: bool = False, coords: list | tuple = None):
        super().__init__(Widget, width=Cons.BOARD_WIDTH, height=Cons.BOARD_HEIGHT,
                         background="black", highlightthickness=0)

        # Loading images from folder
        self.LoadImages = LoadImages()
        self.dot = self.LoadImages.dot
        self.eaten_dot = self.LoadImages.eaten_dot
        self.head = self.LoadImages.head
        self.apple = self.LoadImages.apple
        self.border = self.LoadImages.border

        self.agent = Agent()
        self.record = 0


        # Coords variables
        self.reward = 0
        self.eaten_dots_coords = list()
        self.dots_coords = list()
        self.apple_coords = None
        self.head_coords = None
        self.eaten_dots_count = None
        self.dots_count = None
        self.state = None
        self.game_step = 0
        self.mode = [
            # "onTimer",
            "onAction"
        ]
        self.apple_collision_status = False

        # Starting variables and parameters.
        self.inGame = True
        self.dots = 3
        self.score = 0

        # variables used to move snake object
        self.general_direction = "right"
        self.moveX = Cons.DOT_SIZE
        self.moveY = 0.0

        # Set first movement direction by default
        self.direction = (self.moveX, self.moveY)
        self._reward_sum = 0
        # Starting apple coordinates
        self.appleX = 104.0
        self.appleY = 80.0

        # Checking button's press
        self.checkpress = False
        self.check_pause = False

        # Setting default game speed
        self.prev_delay = Cons.DELAY

        # Map of possible move direction (straight, left, right)
        self.direction_map = {
            (0, -Cons.DOT_SIZE): ((0, -Cons.DOT_SIZE), (-Cons.DOT_SIZE, 0), (Cons.DOT_SIZE, 0), [1, 0, 0, 0]),
            # (from bottom to up)
            (-Cons.DOT_SIZE, 0): ((-Cons.DOT_SIZE, 0), (0, Cons.DOT_SIZE), (0, -Cons.DOT_SIZE), [0, 1, 0, 0]),
            # (from right to left)
            (0, Cons.DOT_SIZE): ((0, Cons.DOT_SIZE), (Cons.DOT_SIZE, 0), (-Cons.DOT_SIZE, 0), [0, 0, 1, 0]),
            # (from up to bottom)
            (Cons.DOT_SIZE, 0): ((Cons.DOT_SIZE, 0), (0, -Cons.DOT_SIZE), (0, Cons.DOT_SIZE), [0, 0, 0, 1])
            # (from left to right)
        }

        self.movement_map = {
            'up': ((0, -Cons.DOT_SIZE), [1, 0, 0, 0]),  # (from bottom to up)
            'left': ((-Cons.DOT_SIZE, 0), [0, 1, 0, 0]),  # (from right to left)
            'down': ((0, Cons.DOT_SIZE), [0, 0, 1, 0]),  # (from up to bottom)
            'right': ((Cons.DOT_SIZE, 0), [0, 0, 0, 1])  # (from left to right)
        }

        self.revert_map = {
            (1, 0, 0, 0): ((0, -Cons.DOT_SIZE), 'up'),  # (from bottom to up)
            (0, 1, 0, 0): ((-Cons.DOT_SIZE, 0), 'left'),  # (from right to left)
            (0, 0, 1, 0): ((0, Cons.DOT_SIZE), "down"),  # (from up to bottom)
            (0, 0, 0, 1): ((Cons.DOT_SIZE, 0), 'right')  # (from left to right)
        }

        self.check_mode = checkmode
        self.custom_coords: list | tuple = coords
        self.initGame()
        self.pack()

    @property
    def height(self):
        return float(self["height"])

    @property
    def width(self):
        return float(self["width"])

    def initGame(self):
        # Creating all game's objects, locating an apple and binding keys
        self.create_objects()
        self.locate_apple()
        self.bind_all("<Key>", self.onKeyPressed)

        self.play_step(movement=self.movement_map[f"{self.general_direction}"][0],
                       direction=self.movement_map[f"{self.general_direction}"][1])
        self.train()

    def get_state(self):
        """Creating and returning 'state' array, containing data to  train"""
        # Getting array of dangerous directions
        dangers = self.get_danger_direction()
        dangers = np.array(dangers, dtype=float)

        # Getting array of snake movement direction
        direction = self.direction_map[(self.moveX, self.moveY)][-1]
        direction = np.array(direction, dtype=float)

        # Getting food relative location
        food_location = self.get_food_relative_location()

        # Concatenating numpy arrays into one array
        state = np.concatenate((dangers, direction, food_location))
        state = np.reshape(state, newshape=[1, state.size])
        return state

    def get_distance(self, object_1, object_2):
        object_1_coords = np.array(object_1)
        object_2_coords = np.array(object_2)

        # Calculating Euclidian distance between two points
        delta = object_1_coords - object_2_coords
        distance = np.linalg.norm(delta)

        return distance

    def get_min_distance(self, object_1, object_2):
        distances = np.array([])
        object_1_coords = self.coords(object_1)
        object_2_coords = self.coords(object_2)

        square_map = {
            "current": np.array([0, 0]),
            "up": np.array([0, -1*self.height]),
            "down": np.array([0, self.height]),
            "left": np.array([-1*self.width, 0]),
            "right": np.array([self.width, 0]),
        }

        for key in square_map:
            distances = np.append(distances, self.get_distance(object_1_coords, object_2_coords + square_map[key]))
        min_distance = np.min(distances)
        return min_distance

    def get_food_relative_location(self):
        """Getting an apple position based on snake's head position
        return array [upper, lower, left, right]"""
        apple = self.find_withtag('apple')
        apple_coords = np.array(self.coords(apple))
        head = self.find_withtag('head')
        head_coords = np.array(self.coords(head))
        delta = apple_coords - head_coords
        # [upper, lower, left, right]
        res = np.array([0, 0, 0, 0], dtype=float)

        # Checking X position
        if delta[0] > 0:
            res += np.array([0, 0, 0, 1], dtype=float)
        elif delta[0] < 0:
            res += np.array([0, 0, 1, 0], dtype=float)
        else:
            res += np.array([0, 0, 0.5, 0.5], dtype=float)

        # Checking Y position
        if delta[1] > 0:
            res += np.array([0, 1, 0, 0], dtype=float)
        elif delta[1] < 0:
            res += np.array([1, 0, 0, 0], dtype=float)
        else:
            res += np.array([0.5, 0.5, 0, 0], dtype=float)

        return res

    def get_danger_direction(self):
        """Checking dangers from next positions, based on current moving parameters
        returns array with bool variables in format [Straight, Left, Right] dangers"""

        head = self.find_withtag("head")
        head_coords = self.coords(head)

        straight_move_x, straight_move_y = self.direction_map[(self.moveX, self.moveY)][0]
        left_move_x, left_move_y = self.direction_map[(self.moveX, self.moveY)][1]
        right_move_x, right_move_y = self.direction_map[(self.moveX, self.moveY)][2]

        new_straight_coords = (
            head_coords[0] + straight_move_x,
            head_coords[1] + straight_move_y,
        )

        new_left_coords = (
            head_coords[0] + left_move_x,
            head_coords[1] + left_move_y,
        )

        new_right_coords = (
            head_coords[0] + right_move_x,
            head_coords[1] + right_move_y,
        )

        straight_danger = self.is_danger(new_straight_coords[0], new_straight_coords[1], ['dot', 'border'])
        left_danger = self.is_danger(new_left_coords[0], new_left_coords[1], ['dot', 'border'])
        right_danger = self.is_danger(new_right_coords[0], new_right_coords[1], ['dot', 'border'])

        """Getting moving direction based on current moving parameters"""
        straight, right, left = False, False, False
        if (self.moveX, self.moveY) == self.direction:
            straight = True
        if ((self.moveX, self.moveY) == (0, 8) and self.direction == (8, 0)) or \
                ((self.moveX, self.moveY) == (-8, 0) and self.direction == (0, 8)) or \
                ((self.moveX, self.moveY) == (0, -8) and self.direction == (-8, 0)) or \
                ((self.moveX, self.moveY) == (8, 0) and self.direction == (0, -8)):
            right = True

        if ((self.moveX, self.moveY) == (0, -8) and self.direction == (8, 0)) or \
                ((self.moveX, self.moveY) == (-8, 0) and self.direction == (0, -8)) or \
                ((self.moveX, self.moveY) == (0, 8) and self.direction == (-8, 0)) or \
                ((self.moveX, self.moveY) == (8, 0) and self.direction == (0, 8)):
            left = True
        return [straight, right, left]

    def is_danger(self, x, y, dangerous_objects_name: list | tuple | np.ndarray):
        """Checking actual danger based on given object position and names of dangerous objects
        return True if there is danger (collision) and False if not."""
        for dangerous_object_name in dangerous_objects_name:
            dangerous_objects = self.find_withtag(str(dangerous_object_name))  # Getting dangerous objects
            for dangerous_object in dangerous_objects:
                coords = self.coords(dangerous_object)
                if coords == [x, y]:
                    return True
        return False

    def create_objects(self):
        """Creates objects on Canvas"""
        self.create_text(30, 10, text="Score: {0}".format(self.score), tag="score", fill="white")
        self.create_text(100, 10, text=f"Step: {self.game_step}", tag="step", fill="white")
        self.create_text(170, 10, text=f"Reward: {self._reward_sum}", tag="reward", fill="white")

        self.create_image(self.appleX, self.appleY, image=self.apple, anchor=CENTER, tag="apple")
        self.create_image(Cons.START_COORD_X - 2 * Cons.DOT_SIZE, Cons.START_COORD_Y, image=self.dot, anchor=CENTER,
                          tag="dot")
        self.create_image(Cons.START_COORD_X - 1 * Cons.DOT_SIZE, Cons.START_COORD_Y, image=self.dot, anchor=CENTER,
                          tag="dot")
        self.create_image(Cons.START_COORD_X, Cons.START_COORD_Y, image=self.head, anchor=CENTER, tag="head")

        if self.check_mode:
            self.x, self.y = self.custom_coords

            for i in range(len(self.x)):
                coord_x = self.x[i]
                coord_y = self.y[i]
                self.create_image(coord_x, coord_y, image=self.border, anchor=CENTER, tag="border")

            self.check_mode = False

    def checkAppleCollision(self):
        """Creating the apple collision"""
        apple = self.find_withtag("apple")
        head = self.find_withtag("head")
        dots = self.find_withtag("dot")
        self.apple_collision_status = False

        reward = 0
        x1_h, y1_h, x2_h, y2_h = self.bbox(head)
        overlap_head = self.find_overlapping(x1_h, y1_h, x2_h, y2_h)

        for over_head in overlap_head:
            if apple[0] == over_head:
                self.score += 1
                x, y = self.coords(apple)
                self.create_image(x, y, image=self.dot, anchor=CENTER, tag="dot")
                self.create_image(x, y, image=self.eaten_dot, anchor=CENTER, tag="eaten_dot")
                self.locate_apple()
                self.apple_collision_status = True
                reward = 5

        apple = self.find_withtag("apple")
        x1_a, y1_a, x2_a, y2_a = self.bbox(apple)
        overlap_apple = self.find_overlapping(x1_a, y1_a, x2_a, y2_a)
        for dot in dots:
            for over_apple in overlap_apple:
                if dot == over_apple:
                    self.locate_apple()
                    reward = 5
                    self.apple_collision_status = True
        return reward

    def checkEatenAppleCollision(self):
        """Convert eaten apple into snake body"""
        eaten_dot = self.find_withtag("eaten_dot")

        dots = self.find_withtag("dot")
        i = 0
        while i < len(dots):
            i += 1
        if eaten_dot:
            for i in range(len(eaten_dot)):
                x1, y1, x2, y2 = self.bbox(dots[0])
                overlap = self.find_overlapping(x1, y1, x2, y2)
                for over in overlap:

                    if eaten_dot:
                        if eaten_dot[0] == over:
                            self.delete(eaten_dot[i])

    def moveSnake(self):
        """Moving the snake"""
        dots = self.find_withtag("dot")
        head = self.find_withtag("head")
        items = dots + head
        z = 0

        if not self.check_pause:
            while z < len(items) - 1:
                c1 = self.coords(items[z])
                c2 = self.coords(items[z + 1])

                self.move(items[z], c2[0] - c1[0], c2[1] - c1[1])
                z += 1

            self.move(head, self.moveX, self.moveY)
            self.direction = (self.moveX, self.moveY)
        else:
            pass

    def checkCollision(self):
        """Checking for collisions"""
        dots = self.find_withtag("dot")
        head = self.find_withtag("head")
        borders = self.find_withtag("border")

        reward = 0

        x1, y1, x2, y2 = self.bbox(head)

        head_coords = (x1, y1, x2, y2)
        temp_coords = self.coords(head)

        # Checking collisions of head object with body (dot) object
        for dot_num, dot in enumerate(dots):
            dot_coords = self.bbox(dot)

            if head_coords == dot_coords:
                self.inGame = False
                self.game_is_over = True
                reward = -100

        # Checking collisions of head object with border object
        for border in borders:
            border_coords = self.bbox(border)
            if head_coords == border_coords:
                self.inGame = False
                self.game_is_over = True
                reward = -100

        # Checking collision with board borders
        if x1 < 0:
            self.moveY = 0
            self.moveX = Cons.BOARD_WIDTH + 0.5 * Cons.DOT_SIZE
            self.move(head, self.moveX, self.moveY)
            self.moveX = -Cons.DOT_SIZE
            self.inGame = True
            self.game_is_over = False

        if x1 > Cons.BOARD_WIDTH:
            self.moveY = 0
            self.moveX = -(Cons.BOARD_WIDTH + 0.5 * Cons.DOT_SIZE)
            self.move(head, self.moveX, self.moveY)
            self.moveX = Cons.DOT_SIZE
            self.inGame = True
            self.game_is_over = False


        if y1 < 0:
            self.moveX = 0
            self.moveY = Cons.BOARD_HEIGHT + 0.5 * Cons.DOT_SIZE
            self.move(head, self.moveX, self.moveY)
            self.moveY = -Cons.DOT_SIZE
            self.inGame = True
            self.game_is_over = False

        if y1 > Cons.BOARD_HEIGHT:
            self.moveX = 0
            self.moveY = -(Cons.BOARD_HEIGHT + 0.5 * Cons.DOT_SIZE)
            self.move(head, self.moveX, self.moveY)
            self.moveY = Cons.DOT_SIZE
            self.inGame = True
            self.game_is_over = False
        return reward

    def locate_apple(self):
        """places the apple object on Canvas"""
        apple = self.find_withtag("apple")
        self.delete(apple[0])

        if Cons.i == 0:
            self.appleX = self.appleX
            self.appleY = self.appleY
            Cons.i += 1
        else:

            r = random.randint(1, int((Cons.BOARD_WIDTH - 0.5 * Cons.DOT_SIZE) / Cons.DOT_SIZE) - 2)
            self.appleX = r * Cons.DOT_SIZE
            r = random.randint(1, int((Cons.BOARD_HEIGHT - 0.5 * Cons.DOT_SIZE) / Cons.DOT_SIZE) - 2)
            self.appleY = r * Cons.DOT_SIZE

        self.create_image(self.appleX, self.appleY, anchor=CENTER, image=self.apple, tag="apple")

    def onKeyPressed(self, e):
        """Controls direction variables with cursors keys"""
        key = e.keysym
        self.general_direction = "right"

        # Arrows controls
        if not self.checkpress:
            LEFT_CURSOR_KEY = "Left"
            if key == LEFT_CURSOR_KEY and self.moveX <= 0:
                self.checkpress = True
                self.check_pause = False
                self.general_direction = "left"

        if not self.checkpress:
            RIGHT_CURSOR_KEY = "Right"
            if key == RIGHT_CURSOR_KEY and self.moveX >= 0:
                self.checkpress = True
                self.check_pause = False
                self.general_direction = "right"

        if not self.checkpress:
            UP_CURSOR_KEY = "Up"
            if key == UP_CURSOR_KEY and self.moveY <= 0:
                self.checkpress = True
                self.check_pause = False
                self.general_direction = "up"

        if not self.checkpress:
            DOWN_CURSOR_KEY = "Down"
            if key == DOWN_CURSOR_KEY and self.moveY >= 0:
                self.checkpress = True
                self.check_pause = False
                self.general_direction = "down"

        # WASD controls
        if not self.checkpress:
            A_CONTROL_KEY = "a"
            if key == A_CONTROL_KEY and self.moveX <= 0:
                self.checkpress = True
                self.check_pause = False
                self.general_direction = "left"

        if not self.checkpress:
            B_CONTROL_KEY = "d"
            if key == B_CONTROL_KEY and self.moveX >= 0:
                self.checkpress = True
                self.check_pause = False
                self.general_direction = "right"

        if not self.checkpress:
            W_CONTROL_KEY = "w"
            if key == W_CONTROL_KEY and self.moveY <= 0:
                self.checkpress = True
                self.check_pause = False
                self.general_direction = "up"

        if not self.checkpress:
            S_CONTROL_KEY = "s"
            if key == S_CONTROL_KEY and self.moveY >= 0:

                self.checkpress = True
                self.check_pause = False
                self.general_direction = "down"

        PAUSE_1 = "p"
        if key == PAUSE_1:
            self.check_pause = True

        SPEED_UP = "plus"
        if key == SPEED_UP:
            print(Cons.DELAY)
            if Cons.DELAY <= 10:
                Cons.DELAY = 10

            else:
                Cons.DELAY -= 10

        SPEED_DOWN = "minus"
        if key == SPEED_DOWN:
            print(Cons.DELAY)
            if Cons.DELAY >= 1000:
                Cons.DELAY = 1000
            else:
                Cons.DELAY += 10

        self.moveX, self.moveY = self.movement_map[f'{self.general_direction}'][0]

        if self.mode[0] == "onAction":
            self.onAction(self.moveX, self.moveY)

    def play_step(self, movement=None, direction=None):
        # Updating rewarding system

        head = self.find_withtag("head")
        apples = self.find_withtag("apple")


        if movement is not None:
            assert len(movement) == 2
            try:
                self.moveX, self.moveY = movement
            except ValueError:
                print("Movement array shall be [moveX, moveY]")

        if direction is not None:
            assert len(direction) == 3 or 4
            try:
                self.moveX, self.moveY = self.convert_direction_to_movement(movement=movement,
                                                                            direction=direction)
            except ValueError:
                print(f"Convertion hasn't been done. Direction should be relative or general. Got {direction}")

        self.game_step += 1
        if self.inGame:
            self.game_is_over = False
            self.drawScore()
            self.reward = 0

            old_distance = self.get_min_distance(head, apples)
            self.moveSnake()
            new_distance = self.get_min_distance(head, apples)
            distance_delta = new_distance - old_distance
            if distance_delta <= 0:
                # Small bonus for moving in right direction
                self.reward += 1
            elif self.apple_collision_status and distance_delta > 0:
                # Prevents wrong situation, when reward is negative right after eating an apple
                self.reward += 1
            else:
                # Small punishment for moving in wrong direction
                self.reward -= 1


            self.reward += self.checkCollision()
            self.reward += self.checkAppleCollision()

            self.checkEatenAppleCollision()


            if self.checkpress:
                self.checkpress = False

            if self.mode[0] == "onTimer":
                self.onTimer()

        else:

            self.gameOver()

        self.state = self.get_state()


        return self.reward, self.game_is_over, self.score

    def onAction(self, moveX, moveY, direction: tuple | list | np.ndarray | None = None):
        self.play_step(movement=(moveX, moveY),
                       direction=direction)

    def onTimer(self):
        """creates a game cycle each timer event"""
        if self.inGame:
            self.after(Cons.DELAY, self.play_step)
        else:
            self.gameOver()

    def drawScore(self):
        """draws score"""
        score = self.find_withtag("score")
        step = self.find_withtag("step")
        reward = self.find_withtag("reward")

        self._reward_sum += self.reward

        self.itemconfig(score, text="Score: {0}".format(self.score))
        self.itemconfig(step, text=f"Step: {self.game_step}")
        self.itemconfig(reward, text=f"Reward: {self._reward_sum}")

    def gameOver(self):
        """deletes all objects and draws game over message"""

        self.delete(ALL)
        self.create_text(self.winfo_width() / 2, self.winfo_height() / 2,
                         text="Game OVER with score {0}".format(self.score), fill="white")
        self.create_text(self.winfo_width() / 2, self.winfo_height() / 2 + 50, text="Press RESTART?", fill="white")
        self.game_step = 0
        self.gameScore()
        self._reward_sum = 0

    def gameScore(self):
        score_txt = open("score.txt", "r")
        score_stored = score_txt.read()
        score_txt.close()

        if self.score > int(score_stored):
            score_txt = open("score.txt", "w+")
            score_txt.write("{0}".format(self.score))
            score_txt.close()
            self.create_text(self.winfo_width() / 2, self.winfo_height() / 4,
                             text="The best score is {0}".format(self.score), fill="white")
        else:
            self.create_text(self.winfo_width() / 2, self.winfo_height() / 4,
                             text="The best score is {0}".format(score_stored), fill="white")

    def moveSnake_control_mode(self):
        """Moving the snake"""

        dots = self.find_withtag("dot")
        head = self.find_withtag("head")
        items = dots + head
        z = 0
        while z < len(items) - 1:
            c1 = self.coords(items[z])
            c2 = self.coords(items[z + 1])
            self.move(items[z], c2[0] - c1[0], c2[1] - c1[1])
            z += 1

        self.move(head, self.moveX, self.moveY)
        self.moveX = 0
        self.moveY = 0

    def convert_movement_to_direction(self,
                                      old_movement: list | tuple | np.ndarray,
                                      new_movement: list | tuple | np.ndarray):
        """Converting movement to direction based on current snake's head."""
        new_moveX, new_moveY = new_movement
        old_moveX, old_moveY = old_movement
        straight, left, right = 0, 0, 0

        old_straight_move_x, old_straight_move_y = self.direction_map[(old_moveX, old_moveY)][0]
        old_left_move_x, old_left_move_y = self.direction_map[(old_moveX, old_moveY)][1]
        old_right_move_x, old_right_move_y = self.direction_map[(old_moveX, old_moveY)][2]

        if (old_straight_move_x, old_straight_move_y) == (new_moveX, new_moveY):
            straight = 1
        elif (old_left_move_x, old_left_move_y) == (new_moveX, new_moveY):
            left = 1
        elif (old_right_move_x, old_right_move_y) == (new_moveX, new_moveY):
            right = 1

        return [straight, left, right]

    def convert_general_direction_to_movement(self, direction: list | tuple | np.ndarray) -> [float, float]:
        new_gdm_moveX, new_gdm_moveY = None, None
        assert len(direction) == 4
        for key in self.revert_map:
            if direction == list(key):
                new_gdm_moveX, new_gdm_moveY = self.revert_map[key][0]
        return  new_gdm_moveX, new_gdm_moveY

    def convert_relative_direction_to_movement(self,
                                               old_movement: list | tuple | np.ndarray,
                                               relative_direction: list | tuple | np.ndarray) -> [float, float]:
        assert len(relative_direction) == 3
        assert len(old_movement) == 2
        old_rd_moveX, old_rd_moveY = old_movement
        new_rd_moveX, new_rd_moveY = old_movement

        if relative_direction == [1, 0, 0]:
            pass
        elif relative_direction == [0, 1, 0]:
            new_rd_moveX, new_rd_moveY = self.direction_map[(old_rd_moveX, old_rd_moveY)][1]
        elif relative_direction == [0, 0, 1]:
            new_rd_moveX, new_rd_moveY = self.direction_map[(old_rd_moveX, old_rd_moveY)][2]
        else:
            temp_rand = random.randint(0, 2)
            new_rd_moveX, new_rd_moveY = self.direction_map[(old_rd_moveX, old_rd_moveY)][temp_rand]

        del old_rd_moveX, old_rd_moveY
        return  new_rd_moveX, new_rd_moveY

    def convert_direction_to_movement(self,
                                      movement: list | tuple | np.ndarray | None = None,
                                      direction: list | tuple | np.ndarray = None) -> [float, float]:
        new_dm_moveX, new_dm_moveY = None, None
        if movement is None:
            movement = (self.moveX, self.moveY)

        if direction is not None:
            if len(direction) == 3:
                new_dm_moveX, new_dm_moveY = self.convert_relative_direction_to_movement(old_movement=movement,
                                                                                   relative_direction=direction)
            elif len(direction) == 4:
                new_dm_moveX, new_dm_moveY = self.convert_general_direction_to_movement(direction=direction)
            else:
                pass
        else:
            raise ValueError(f"Movement or Direction has been assigned wrong."
                             f"\nMovement should be [moveX, moveY]."
                             f"\nDirection should be [straight, left, right] or [up, left, down, right]")

        return new_dm_moveX, new_dm_moveY

    def train(self):

        # getting old state
        state_old = self.get_state()
        # Predicting action
        final_move = self.agent.get_action(state_old)
        self.
        # do game step, based on action
        reward, done, score = self.play_step(direction=final_move)

        # getting new state and result
        state_new = self.get_state()

        # Training shor memory
        self.agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # Remembering the decision and result
        self.agent.remember((state_old, final_move, reward, state_new, done))

        if done:
            self.agent.n_games += 1
            self.agent.train_long_memory()

            if self.score > self.record:
                self.record = self.score
                self.agent.model.save()

            self.gameOver()



class Building:
    def __init__(self, root):
        self.var_x, self.var_y = None, None

        # Creating main window
        self.root = root
        self.root.title("Snake")
        self.root.resizable(False, False)

        # Loading snake AI agent
        # self.agent = Agent()

        # Checking game mode
        self.check_mode = True
        self.lb = lb.Load_borders()
        self.border_listVAR = tk.StringVar()

        # Creating interface (buttons, text, etc)
        self.create_items()
        self.root.bind("<Key>", self.keysym_func)
        self.root.mainloop()

    def create_items(self, *args):
        """Creating main frame"""

        self.frame = ttk.LabelFrame(self.root, text="SnakeGame", width=500, height=500)
        self.frame.grid(column=0, row=0)

        self.board = Board(self.frame, *args)
        self.board.grid(column=0, row=0, columnspan=3, rowspan=6)

        # Creating buttons
        self.button_close = ttk.Button(self.frame, text="Close")
        self.button_close.grid(column=0, row=6, sticky=tk.N)

        self.button_restart = ttk.Button(self.frame, text="Restart")
        self.button_restart.grid(column=1, row=6, sticky=tk.N)

        self.borders_list = self.lb.load_list_func()
        self.combobox_load_borders = ttk.Combobox(self.frame, textvariable=self.border_listVAR)
        self.combobox_load_borders["values"] = self.borders_list
        self.combobox_load_borders.current(0)
        self.combobox_load_borders.grid(column=3, row=4)

        self.button_load_borders = ttk.Button(self.frame, text="Load")
        self.button_load_borders.grid(column=3, row=5)

        self.button_mode = ttk.Button(self.frame, text="Change mode", state="disabled")
        self.button_mode.grid(column=3, row=6)

        # Loading and attaching buttons commands
        self.buttons_commands()

    def load_borders(self):
        """Loading borders"""
        variable = self.border_listVAR.get()
        print(f"Map {variable.split('.')[0]} has been loaded.")
        coords = self.lb.load_coords(variable)
        self.var_x, self.var_y = coords
        self.button_mode["state"] = "enabled"
        return coords

    def mode(self):
        if not self.check_mode:
            self.check_mode = True
        coords = self.load_borders()
        self.restart(self.check_mode, coords)
        self.check_mode = False

    def _quit(self):
        self.root.destroy()
        self.root.quit()

    def restart(self, check_mode: bool = False, coords: list | tuple = None):
        self.board.destroy()
        self.button_restart.destroy()
        self.button_close.destroy()
        self.frame.destroy()
        if coords is not None:
            self.create_items(check_mode, coords)
        else:
            self.create_items(check_mode)

    def buttons_commands(self):
        self.button_close.configure(command=self._quit)
        self.button_restart.configure(command=self.restart)
        self.button_load_borders.configure(command=self.load_borders)
        self.button_mode.configure(command=self.mode)

    def keysym_func(self, event):
        x = 1

if __name__ == "__main__":
    root_window = Tk()
    Building(root_window)
