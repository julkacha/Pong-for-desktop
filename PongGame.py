from kivy.config import Config

Config.set('graphics', 'width', '1000')
Config.set('graphics', 'height', '700')

from kivy import platform
from kivy.core.window import Window
from kivy.app import App
from kivy.graphics.vertex_instructions import Ellipse, Rectangle
from kivy.properties import StringProperty, Clock, ListProperty, BooleanProperty, NumericProperty
from kivy.uix.widget import Widget


class PongGameApp(App):
    pass


class BallMovement(Widget):

    _counter_left = StringProperty("0")
    _counter_right = StringProperty("0")
    winner = StringProperty("player 0")
    pause_state = False
    restart_button = BooleanProperty(True)
    countdown_text = StringProperty("4")
    countdown_visible = NumericProperty(0)
    winner_visible = NumericProperty(0)
    pause_visible = ListProperty([0, 0, 0, 0])
    right_speed_y = 0
    left_speed_y = 0
    board_speed = 10
    starting_speed = 5.0
    ball_speed = 5.0

    def __init__(self, **kwargs):
        super(BallMovement, self).__init__(**kwargs)
        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
            self._keyboard.bind(on_key_down=self._on_keyboard_down)
            self._keyboard.bind(on_key_up=self._on_keyboard_up)
        self.game = 0
        self.walls = 0
        self.pos_history = []
        self.up = lambda m: m + self.ball_speed
        self.down = lambda m: m - self.ball_speed
        self.movement = {0: [self.up, self.up], 1: [self.up, self.down],
                         2: [self.down, self.down], 3: [self.down, self.up]}
        with self.canvas:
            self.ball = Ellipse(pos=self.center, size=(20, 20))
            self.left_board = Rectangle(pos=self.center, size=(5, 160))
            self.right_board = Rectangle(pos=self.center, size=(5, 160))

        self.countdown_on()

    def is_desktop(self):
        if platform in ('linux', 'win', 'macosx'):
            return True
        return False

    def on_size(self, *args):
        w, h = self.ball.size
        self.left_board.pos = (25, self.height / 2 - self.left_board.size[1] / 2)
        self.right_board.pos = (self.width - 25, self.height / 2 - self.left_board.size[1] / 2)
        if self.game == 0:
            self.ball.pos = ((self.width - w) / 2, (self.height - h) / 2)
        else:
            y = (self.height - h) / 2
            if self.game == 1:
                x = self.right_board.pos[0] - self.ball.size[0]
            elif self.game == -1:
                x = self.left_board.pos[0] + self.left_board.size[0]
            self.ball.pos = (x, y)
        self.ball_speed = self.starting_speed
        self.game = 0

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'w':
            self.left_speed_y = self.board_speed
        elif keycode[1] == 's':
            self.left_speed_y = -self.board_speed
        elif keycode[1] == 'up':
            self.right_speed_y = self.board_speed
        elif keycode[1] == 'down':
            self.right_speed_y = -self.board_speed
        elif keycode[1] == 'spacebar':
            self.pause()
        elif keycode[1] == "enter":
            self.restart_game()
        return True

    def _on_keyboard_up(self, keyboard, keycode):
        if keycode[1] == "w" and self.left_speed_y == self.board_speed:
            self.left_speed_y = 0
        if keycode[1] == "s" and self.left_speed_y == -self.board_speed:
            self.left_speed_y = 0
        if keycode[1] == "up" and self.right_speed_y == self.board_speed:
            self.right_speed_y = 0
        if keycode[1] == "down" and self.right_speed_y == -self.board_speed:
            self.right_speed_y = 0
        return True

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if touch.x < self.width / 2 and touch.y > self.height / 2:
                self.left_speed_y = self.board_speed
            elif touch.x < self.width / 2 and touch.y < self.height / 2:
                self.left_speed_y = -self.board_speed
            if touch.x > self.width / 2 and touch.y > self.height / 2:
                self.right_speed_y = self.board_speed
            elif touch.x > self.width / 2 and touch.y < self.height / 2:
                self.right_speed_y = -self.board_speed
            return super(BallMovement, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        self.left_speed_y = 0
        self.right_speed_y = 0

    def pause(self):
        if self.winner_visible == 0:
            if self.pause_state:
                self.pause_visible = [0, 0, 0, 0]
                self.pause_state = False
                self.countdown_on()
            else:
                self.pause_visible = [1, 1, 1, 1]
                self.pause_state = True

    def on_pause(self): return True

    def on_resume(self): pass

    def game_resume(self): Clock.schedule_interval(self.pos_update_fun, 1 / 60)

    def countdown_on(self): Clock.schedule_interval(self.countdown, 1 / 1.5)

    def countdown(self, dt):
        if self.pause_state:
            return False
        num = int(self.countdown_text)
        if num == 4:
            num -= 1
            self.countdown_visible = 1
        elif num == 0:
            self.countdown_text = str(4)
            self.countdown_visible = 0
            self.game_resume()
            return False
        else:
            num -= 1
        self.countdown_text = str(num)

    def end_game(self):
        self.winner = self.winner + " wins!"
        self.winner_visible = 1
        self.restart_button = False

    def restart_game(self):
        PongGameApp().stop()
        PongGameApp().run()

    def pos_update_fun(self, dt):
        if self.pause_state:
            return False

        x, y = self.ball.pos
        x_left, y_left = self.left_board.pos
        x_right, y_right = self.right_board.pos

        if (self.width / 2 - 10) < x < (self.width / 2 + 10):
            self.ball_speed += 0.1

        if self.left_speed_y == -self.board_speed and y_left <= 0:
            self.left_speed_y = 0
        elif self.left_speed_y == self.board_speed and (y_left + self.left_board.size[1]) >= self.height:
            self.left_speed_y = 0
        y_left += self.left_speed_y

        if self.right_speed_y == -self.board_speed and y_right <= 0:
            self.right_speed_y = 0
        elif self.right_speed_y == self.board_speed and (y_right + self.right_board.size[1]) >= self.height:
            self.right_speed_y = 0
        y_right += self.right_speed_y

        self.left_board.pos = (x_left, y_left)
        self.right_board.pos = (x_right, y_right)

        '''When ball meets borders or board'''
        if self.height - y <= self.ball.size[1]:
            self.walls = 1
        elif x_right - x <= self.ball.size[0] and (y_right <= y <= (y_right + self.right_board.size[1])):
            self.walls = 2
        elif self.width - x <= self.ball.size[0]:
            self.ball_speed = self.starting_speed
            left_num = int(self._counter_left)
            left_num += 1
            self._counter_left = str(left_num)
            self.game = -1
            self.on_size()
            if left_num == 11:
                self.winner = "player 1"
                self.end_game()
            else:
                self.countdown_on()
            return False
        elif y <= 0:
            self.walls = 3
        elif x <= x_left and (y_left <= y <= (y_left + self.left_board.size[1])):
            self.walls = 0
        elif x <= 0:
            self.ball_speed = self.starting_speed
            right_num = int(self._counter_right)
            right_num += 1
            self._counter_right = str(right_num)
            self.game = 1
            self.on_size()
            if right_num == 11:
                self.winner = "player 2"
                self.end_game()
            else:
                self.countdown_on()
            return False

        '''Changing direction of the ball if it wants to go the same way it came from'''
        if len(self.pos_history) < 2:
            self.ball.pos = (self.movement[self.walls][0](x), self.movement[self.walls][1](y))
            self.pos_history.append(self.ball.pos)
        else:
            p1 = (round(self.pos_history[0][0], 1), round(self.pos_history[0][1], 1))
            p2 = (round(self.pos_history[0][0] + 0.1, 1), round(self.pos_history[0][1] + 0.1, 1))
            p3 = (round(self.pos_history[0][0] + 0.1, 1), round(self.pos_history[0][1] - 0.1, 1))
            p4 = (round(self.pos_history[0][0] - 0.1, 1), round(self.pos_history[0][1] + 0.1, 1))
            p5 = (round(self.pos_history[0][0] - 0.1, 1), round(self.pos_history[0][1] - 0.1, 1))
            pos_changes = [p1, p2, p3, p4, p5]
            if (round(self.movement[self.walls][0](x), 1), round(self.movement[self.walls][1](y), 1)) in pos_changes:
                if self.walls == 1 or self.walls == 3:
                    x_new = self.movement[self.walls][0](x)
                    if x_new > x:
                        x_change = self.down
                    else:
                        x_change = self.up
                    self.movement[self.walls] = [x_change, self.movement[self.walls][1]]
                else:
                    y_new = self.movement[self.walls][1](y)
                    if y_new > y:
                        y_change = self.down
                    else:
                        y_change = self.up
                    self.movement[self.walls] = [self.movement[self.walls][0], y_change]
            self.ball.pos = (self.movement[self.walls][0](x), self.movement[self.walls][1](y))
            self.pos_history[0] = self.pos_history[1]
            self.pos_history[1] = self.ball.pos


if __name__ == "__main__":
    PongGameApp().run()
