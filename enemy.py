# enemy.py
import math
import os
import arcade
from PIL import Image

WALK_PATH = "resources/enemies/1/D_Walk.png"
ATK_PATH = "resources/enemies/1/D_Special.png"

FRAME_W = 48
FRAME_H = 48
SCALE = 3

CACHE_DIR = "resources/_cache_enemy"


def sheet_count(path, fw):
    img = Image.open(path)
    return max(1, img.width // fw)


def load_row_textures(path, fw, fh):
    os.makedirs(CACHE_DIR, exist_ok=True)

    base = os.path.splitext(os.path.basename(path))[0]
    cnt = sheet_count(path, fw)
    cache_paths = [os.path.join(CACHE_DIR, f"{base}_{fw}x{fh}_{i}.png") for i in range(cnt)]

    need_cut = False
    for cp in cache_paths:
        if not os.path.exists(cp) or os.path.getsize(cp) < 10:
            need_cut = True
            break

    if need_cut:
        img = Image.open(path).convert("RGBA")
        for i, cp in enumerate(cache_paths):
            crop = img.crop((i * fw, 0, (i + 1) * fw, fh))
            crop.save(cp)

    return [arcade.load_texture(cp) for cp in cache_paths]


class Enemy(arcade.Sprite):
    def __init__(self, x, y, speed=130):
        self.walk_textures = load_row_textures(WALK_PATH, FRAME_W, FRAME_H)
        self.atk_textures = load_row_textures(ATK_PATH, FRAME_W, FRAME_H)

        super().__init__(self.walk_textures[0], SCALE)

        self.textures = []
        for t in self.walk_textures:
            self.textures.append(t)
        self.set_texture(0)

        self.center_x = x
        self.center_y = y

        self.speed = speed

        self.hp = 20

        self.dmg = 6
        self.cd = 0.5
        self.t = 0.0

        self.anim_t = 0.0
        self.anim_i = 0

        self.hurt_t = 0.0

        self.path = []
        self.pi = 0

        self.mode = "walk"

    def set_path(self, path):
        self.path = path or []
        self.pi = 0

    def set_mode(self, mode):
        if self.mode == mode:
            return
        self.mode = mode
        self.anim_t = 0.0
        self.anim_i = 0

        src = self.walk_textures if mode == "walk" else self.atk_textures
        self.textures = []
        for t in src:
            self.textures.append(t)
        self.set_texture(0)

    def tick(self, dt):
        if self.hurt_t > 0:
            self.hurt_t -= dt
            if self.hurt_t <= 0:
                self.color = (255, 255, 255)

    def take_damage(self, dmg):
        self.hp -= dmg
        self.hurt_t = 0.12
        self.color = (255, 120, 120)
        return self.hp <= 0

    def _animate(self, dt):
        self.anim_t += dt
        if self.anim_t >= 0.11:
            self.anim_t = 0.0
            self.anim_i = (self.anim_i + 1) % len(self.textures)
            self.set_texture(self.anim_i)

    def _step_to(self, dt, tx, ty):
        dx = tx - self.center_x
        dy = ty - self.center_y
        d = math.hypot(dx, dy)
        if d < 1:
            return

        self.center_x += (dx / d) * self.speed * dt
        self.center_y += (dy / d) * self.speed * dt

    def step(self, dt, tx, ty):
        self.set_mode("walk")
        self._animate(dt)

        if self.path and self.pi < len(self.path):
            px, py = self.path[self.pi]
            self._step_to(dt, px, py)
            if math.hypot(px - self.center_x, py - self.center_y) < 10:
                self.pi += 1
            return

        self._step_to(dt, tx, ty)

    def attack(self, dt):
        self.set_mode("attack")
        self._animate(dt)

        self.t += dt
        if self.t >= self.cd:
            self.t = 0.0
            return self.dmg
        return 0