# controls.py
import arcade

class MoveController:
    def __init__(self, speed: float, sprint_mult: float = 1.8):
        self.speed = speed
        self.sprint_mult = sprint_mult

        self.up = False
        self.down = False
        self.left = False
        self.right = False
        self.sprint = False

    def on_press(self, key: int):
        if key == arcade.key.W:
            self.up = True
        elif key == arcade.key.S:
            self.down = True
        elif key == arcade.key.A:
            self.left = True
        elif key == arcade.key.D:
            self.right = True
        elif key in (arcade.key.LSHIFT, arcade.key.RSHIFT):
            self.sprint = True

    def on_release(self, key: int):
        if key == arcade.key.W:
            self.up = False
        elif key == arcade.key.S:
            self.down = False
        elif key == arcade.key.A:
            self.left = False
        elif key == arcade.key.D:
            self.right = False
        elif key in (arcade.key.LSHIFT, arcade.key.RSHIFT):
            self.sprint = False

    def vector(self):
        dx = 0
        dy = 0

        if self.left and not self.right:
            dx = -1
        elif self.right and not self.left:
            dx = 1

        if self.down and not self.up:
            dy = -1
        elif self.up and not self.down:
            dy = 1

        mult = self.sprint_mult if self.sprint else 1.0
        sp = self.speed * mult

        if dx != 0 and dy != 0:
            k = 0.7071067811865476
            return dx * sp * k, dy * sp * k

        return dx * sp, dy * sp