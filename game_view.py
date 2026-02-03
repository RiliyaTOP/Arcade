import math
import arcade
import random
import os
from arcade.camera import Camera2D
from controls import MoveController
from enemy import Enemy
from menu_view import SETTINGS, SettingsView
from player import Hero
from pathlib import Path




def load_frames_from_dir(folder, prefix, count):
    folder = Path(folder)
    return [arcade.load_texture(str(folder / f"{prefix}_{i}.png")) for i in range(count)]


class OneShotFX(arcade.Sprite):
    def __init__(self, textures, x, y, scale=1.0, frame_time=0.06):
        super().__init__(textures[0], scale=scale)
        self.textures = list(textures)
        self.center_x = x
        self.center_y = y
        self.frame_time = frame_time
        self.t = 0.0
        self.i = 0
        self.done = False

    def update_animation(self, dt=1/60):
        if self.done:
            return
        self.t += dt
        if self.t >= self.frame_time:
            self.t = 0.0
            self.i += 1
            if self.i >= len(self.textures):
                self.done = True
                return
            self.set_texture(self.i)




class R:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h

MAPS = [
    "maps/1map.tmx",
    "maps/2map.tmx",
]

LEVELS = [
    {"enemy_variant": "default", "wave_plan": [10, 15, 20]},
    {"enemy_variant": "warrior", "wave_plan": [10, 15, 20]},
]

L_WALLS = "walls"
L_OBJECTS = "objects"
L_PLACED_ITEMS = "placed_items"
SCALING = 1.0

def props(s):
    p = getattr(s, "properties", None)
    return p if isinstance(p, dict) else {}



def scene_list(scene, name):
    try:
        return scene[name]
    except Exception:
        try:
            return scene.get_sprite_list(name)
        except Exception:
            return None

def safe_prop_name(s):
    n = getattr(s, "name", "") or ""
    if n:
        return str(n).lower()
    p = props(s)
    for k in ("name", "id", "type"):
        v = p.get(k)
        if v:
            return str(v).lower()
    return ""

class PhysicsEngine:
    HERO_RADIUS = 22
    ENEMY_RADIUS = 18
    BARRIER_HALF = 20
    REBOUND_MULT = 1.8
    DAMPING = 0.92
    MIN_OVERLAP = 0.5

    @staticmethod
    def _ensure_phys(enemy):
        if not hasattr(enemy, '_phys_vx'):
            enemy._phys_vx = 0.0
            enemy._phys_vy = 0.0

    @staticmethod
    def _vec(ax, ay, bx, by):
        dx, dy = bx - ax, by - ay
        d = math.hypot(dx, dy)
        return (dx, dy, d)

    @staticmethod
    def _circle_vs_aabb(cx, cy, cr, ax, ay, ahw, ahh):
        px = max(ax - ahw, min(cx, ax + ahw))
        py = max(ay - ahh, min(cy, ay + ahh))
        dx, dy = cx - px, cy - py
        d = math.hypot(dx, dy)
        if d < cr:
            if d < 0.001:
                sides = [
                    (cx - (ax - ahw), -1,  0),
                    ((ax + ahw) - cx,  1,  0),
                    (cy - (ay - ahh),  0, -1),
                    ((ay + ahh) - cy,  0,  1),
                ]
                sides.sort(key=lambda s: s[0])
                return cr - sides[0][0], sides[0][1], sides[0][2]
            return cr - d, dx / d, dy / d
        return None

    def resolve(self, enemies, hero, placed_items, castle_cx, castle_cy, castle_hw, castle_hh):
        hx, hy = hero.center_x, hero.center_y
        hr = self.HERO_RADIUS
        er = self.ENEMY_RADIUS
        contact = hr + er

        res = self._circle_vs_aabb(hx, hy, hr, castle_cx, castle_cy, castle_hw, castle_hh)
        if res:
            pen, nx, ny = res
            hero.center_x += nx * pen
            hero.center_y += ny * pen

        for e in enemies:
            self._ensure_phys(e)

            res = self._circle_vs_aabb(e.center_x, e.center_y, er, castle_cx, castle_cy, castle_hw, castle_hh)
            if res:
                pen, nx, ny = res
                e.center_x += nx * pen
                e.center_y += ny * pen
                e._phys_vx += nx * pen * self.REBOUND_MULT
                e._phys_vy += ny * pen * self.REBOUND_MULT

            dx, dy, d = self._vec(hx, hy, e.center_x, e.center_y)
            if d < contact and d > 0.001:
                overlap = contact - d
                if overlap > self.MIN_OVERLAP:
                    nx, ny = dx / d, dy / d
                    e.center_x += nx * overlap
                    e.center_y += ny * overlap
                    e._phys_vx += nx * overlap * self.REBOUND_MULT
                    e._phys_vy += ny * overlap * self.REBOUND_MULT

            for item in placed_items:
                if not isinstance(item, PlacedItem) or item.destroyed:
                    continue
                bh = self.BARRIER_HALF
                res2 = self._circle_vs_aabb(e.center_x, e.center_y, er, item.center_x, item.center_y, bh, bh)
                if res2:
                    pen2, nx2, ny2 = res2
                    if pen2 > self.MIN_OVERLAP:
                        e.center_x += nx2 * pen2
                        e.center_y += ny2 * pen2
                        e._phys_vx += nx2 * pen2 * self.REBOUND_MULT
                        e._phys_vy += ny2 * pen2 * self.REBOUND_MULT

        enemy_list = list(enemies)
        n = len(enemy_list)
        contact_ee = er * 2
        for i in range(n):
            for j in range(i + 1, n):
                ei, ej = enemy_list[i], enemy_list[j]
                dx, dy, d = self._vec(ei.center_x, ei.center_y, ej.center_x, ej.center_y)
                if d < contact_ee and d > 0.001:
                    overlap = contact_ee - d
                    if overlap > self.MIN_OVERLAP:
                        nx, ny = dx / d, dy / d
                        half = overlap * 0.5
                        ei.center_x -= nx * half
                        ei.center_y -= ny * half
                        ej.center_x += nx * half
                        ej.center_y += ny * half

        for e in enemies:
            self._ensure_phys(e)
            e.center_x += e._phys_vx
            e.center_y += e._phys_vy
            e._phys_vx *= self.DAMPING
            e._phys_vy *= self.DAMPING
            if abs(e._phys_vx) < 0.05:
                e._phys_vx = 0.0
            if abs(e._phys_vy) < 0.05:
                e._phys_vy = 0.0

class Particle:
    def __init__(self, x, y, dx, dy, color, size=5, lifetime=1.0):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.alpha = 255

    def update(self, dt):
        self.lifetime -= dt
        self.x += self.dx * dt * 60
        self.y += self.dy * dt * 60
        self.dy -= 0.2
        self.alpha = int(255 * (self.lifetime / self.max_lifetime))

    def draw(self):
        if self.lifetime > 0:
            arcade.draw_circle_filled(
                self.x, self.y, self.size,
                (self.color[0], self.color[1], self.color[2], self.alpha)
            )

    def is_alive(self):
        return self.lifetime > 0

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def create_placement_particles(self, x, y, color=(100, 200, 255)):
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            size = random.uniform(3, 7)
            lifetime = random.uniform(0.5, 1.2)
            self.particles.append(Particle(x, y, dx, dy, color, size, lifetime))

    def create_destruction_particles(self, x, y, color=(255, 100, 50)):
        for _ in range(25):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(80, 200)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            size = random.uniform(4, 8)
            lifetime = random.uniform(0.7, 1.5)
            self.particles.append(Particle(x, y, dx, dy, color, size, lifetime))

    def update(self, dt):
        alive_particles = []
        for particle in self.particles:
            particle.update(dt)
            if particle.is_alive():
                alive_particles.append(particle)
        self.particles = alive_particles

    def create_death_particles(self, x, y):
        for _ in range(18):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(70, 180)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            self.particles.append(Particle(x, y, dx, dy, (220, 40, 40), size=random.uniform(3, 7), lifetime=random.uniform(0.4, 1.0)))
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(40, 100)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            self.particles.append(Particle(x, y, dx, dy, (255, 150, 100), size=random.uniform(2, 4), lifetime=random.uniform(0.3, 0.7)))

    def create_hit_particles(self, x, y):
        for _ in range(6):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(30, 80)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            self.particles.append(Particle(x, y, dx, dy, (255, 180, 80), size=random.uniform(2, 4), lifetime=random.uniform(0.2, 0.5)))

    def create_coin_particles(self, x, y):
        for _ in range(10):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(40, 100)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            self.particles.append(Particle(x, y, dx, dy, (255, 215, 0), size=random.uniform(2, 5), lifetime=random.uniform(0.3, 0.8)))

    def draw(self):
        for particle in self.particles:
            particle.draw()

class ShopView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.res_path = Path(__file__).resolve().parent / "res.txt"
        self.gv = game_view
        self.panel_w = 920
        self.panel_h = 620
        self.cell_w = 240
        self.cell_h = 150
        self.gap = 18

    def _panel_rect(self):
        cx = self.window.width / 2
        cy = self.window.height / 2 + 10
        left = cx - self.panel_w / 2
        right = cx + self.panel_w / 2
        bottom = cy - self.panel_h / 2
        top = cy + self.panel_h / 2
        return left, right, bottom, top

    def _cell_rect_3cols_2rows(self, left, top, col, row):
        pad_l = 40
        pad_r = 40
        head_h = 120
        gap_x = 26
        gap_y = 18
        grid_top = top - head_h
        w = self.panel_w - pad_l - pad_r
        cell_w = (w - gap_x * 2) / 3
        cell_h = 150
        l = left + pad_l + col * (cell_w + gap_x)
        r = l + cell_w
        t = grid_top - row * (cell_h + gap_y)
        b = t - cell_h
        return l, r, b, t

    def _iter_cells(self):
        left, right, bottom, top = self._panel_rect()
        cols = [
            self.gv.shop_sections["player"],
            self.gv.shop_sections["inv"],
            self.gv.shop_sections["castle"],
        ]
        for col in range(3):
            items = cols[col]
            for row in range(2):
                idx = row
                if idx >= len(items):
                    continue
                yield self._cell_rect_3cols_2rows(left, top, col, row), items[idx]

    def on_show_view(self):
        arcade.set_background_color((0, 0, 0))

    def on_draw(self):
        self.clear()
        self.gv.draw_world_no_ui()
        self.gv.ui_camera.use()
        arcade.draw_lrbt_rectangle_filled(0, self.window.width, 0, self.window.height, (0, 0, 0, 140))
        left, right, bottom, top = self._panel_rect()
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (30, 30, 40, 220))
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, arcade.color.WHITE, 2)
        arcade.draw_text("МАГАЗИН", self.window.width / 2, top - 46, arcade.color.WHITE, 30, anchor_x="center", font_name="Nineteen Ninety Three")
        arcade.draw_text(f"Золото: {self.gv.coins}", right - 40, top - 52, arcade.color.GOLD, 22, anchor_x="right", font_name="Nineteen Ninety Three")
        left, right, bottom, top = self._panel_rect()
        labels = ["ИГРОК", "ИНВЕНТАРЬ", "ЗАМОК"]
        for col in range(3):
            l, r, b, t = self._cell_rect_3cols_2rows(left, top, col, 0)
            arcade.draw_text(labels[col], (l + r) / 2, top - 108, arcade.color.WHITE, 18, anchor_x="center", font_name="Nineteen Ninety Three")
        for (l, r, b, t), item in self._iter_cells():
            can_buy = self.gv.can_buy(item)
            bg = (15, 15, 20, 220) if can_buy else (15, 15, 20, 150)
            bd = (220, 220, 240) if can_buy else (140, 140, 150)
            arcade.draw_lrbt_rectangle_filled(l, r, b, t, bg)
            arcade.draw_lrbt_rectangle_outline(l, r, b, t, bd, 2)
            title = item.get("title", "")
            if title:
                arcade.draw_text(title, l + 12, t - 30, arcade.color.WHITE, 16)
            if item["kind"] in ("player_upgrade", "castle_upgrade"):
                icon = self.gv.shop_icons.get(item["id"])
                if icon is not None:
                    iw = 70
                    ih = 70
                    icx = l + 52
                    icy = b + 64
                    arcade.draw_texture_rect(icon, R(icx, icy, iw, ih))
                lvl = self.gv.upg_levels.get(item["id"], 0)
                arcade.draw_text(f"x{lvl}", r - 12, t - 30, arcade.color.WHITE, 18, anchor_x="right")
            elif item["kind"] == "inv_item":
                icon = self.gv.inv_icons.get(item["id"])
                if icon is not None:
                    sq = 110
                    icx = (l + r) / 2
                    icy = (b + t) / 2 + 6
                    arcade.draw_texture_rect(icon, R(icx, icy, sq, sq))
                else:
                    sq = 70
                    icx = (l + r) / 2
                    icy = (b + t) / 2 + 6
                    arcade.draw_lrbt_rectangle_filled(icx - sq / 2, icx + sq / 2, icy - sq / 2, icy + sq / 2, arcade.color.RED)
            price = item["price"]
            price_color = arcade.color.WHITE if can_buy else arcade.color.LIGHT_GRAY
            coin_size = 26
            px = r - 18
            py = b + 18
            arcade.draw_texture_rect(self.gv.coin_tex, R(px - 70, py + 10, coin_size, coin_size))
            arcade.draw_text(str(price), px - 40, py, price_color, 18, anchor_x="right")
        self.gv.draw_inventory_bar()
        arcade.draw_text("Клик по лоту — купить. ESC — выйти", self.window.width / 2, bottom - 34, arcade.color.LIGHT_GRAY, 18, anchor_x="center", font_name="Nineteen Ninety Three")

    def on_mouse_press(self, x, y, button, modifiers):
        for (l, r, b, t), item in self._iter_cells():
            if l <= x <= r and b <= y <= t:
                self.gv.try_buy_item(item)
                return

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.gv)
            self.gv.on_shop_closed()

class PlacedItem(arcade.Sprite):
    def __init__(self, item_id, x, y, texture, max_health=20):
        super().__init__(texture, scale=1.0)
        self.item_id = item_id
        self.center_x = x
        self.center_y = y
        self.max_health = max_health
        self.health = max_health
        self.effect_applied = False
        self.destroyed = False
        self.hit_timer = 0.0
        self.health_colors = [
            (255, 50, 50),
            (255, 150, 50),
            (255, 255, 50),
            (150, 255, 50),
            (50, 255, 50),
        ]
        self.barrier = arcade.SpriteSolidColor(40, 40, arcade.color.TRANSPARENT_BLACK)
        self.barrier.center_x = x
        self.barrier.center_y = y
        self.barrier.alpha = 0

    def draw(self):
        if not self.destroyed:
            super().draw()
            self.draw_health_bar()

    def draw_health_bar(self):
        if self.destroyed:
            return
        health_percent = self.health / self.max_health
        color_index = min(4, max(0, int(health_percent * 5)))
        color = self.health_colors[color_index]
        bar_width = max(4, int(40 * health_percent))
        bar_x = self.center_x - bar_width / 2
        bar_y = self.center_y - 25
        arcade.draw_lrbt_rectangle_filled(bar_x, bar_x + bar_width, bar_y, bar_y + 4, color)

    def take_damage(self, damage):
        if self.destroyed:
            return True
        self.health -= damage
        self.hit_timer = 0.3
        if self.health <= 0:
            return True
        return False

    def destroy(self, particle_system=None):
        self.destroyed = True
        self.alpha = 0
        self.barrier.alpha = 0
        self.barrier.width = 0
        self.barrier.height = 0
        if particle_system:
            particle_system.create_destruction_particles(self.center_x, self.center_y)

    def update(self, dt):
        if self.hit_timer > 0:
            self.hit_timer -= dt
            if self.hit_timer <= 0:
                self.color = (255, 255, 255)
            else:
                self.color = (255, 150, 150) if int(self.hit_timer * 10) % 2 == 0 else (255, 255, 255)

class GameView(arcade.View):
    def __init__(self, menu_view, level_index=0, coins=0):
        super().__init__()
        self.menu_view = menu_view
        self.level_index = level_index
        self.scaling = SCALING
        base_dir = Path(__file__).resolve().parent
        map_path = base_dir / "maps" / f"{self.level_index + 1}map.tmx"

        cfg = LEVELS[self.level_index]
        self.enemy_variant = cfg["enemy_variant"]
        self.wave_plan = cfg["wave_plan"]

        cfg = LEVELS[self.level_index]
        self.enemy_variant = cfg["enemy_variant"]
        self.wave_plan = cfg["wave_plan"]

        map_path = MAPS[self.level_index]
        base_dir = Path(__file__).resolve().parent
        map_path = base_dir / "maps" / f"{self.level_index + 1}map.tmx"
        self.tm = arcade.load_tilemap(
            str(map_path),
            scaling=self.scaling,  # или scaling=SCALING
            layer_options={L_WALLS: {"use_spatial_hash": True}},
        )

        self.scene = arcade.Scene.from_tilemap(self.tm)

        self.placed_items = scene_list(self.scene, L_PLACED_ITEMS)
        if self.placed_items is None:
            self.placed_items = arcade.SpriteList()
            self.scene.add_sprite_list(L_PLACED_ITEMS, self.placed_items)

        walls = scene_list(self.scene, L_WALLS)
        self.walls = walls if walls is not None else arcade.SpriteList(use_spatial_hash=True)

        self.map_w = int(self.tm.width * self.tm.tile_width * SCALING)
        self.map_h = int(self.tm.height * self.tm.tile_height * SCALING)

        self.sad_bgm = arcade.load_sound("resources/music/sad.m4a")
        self.sad_player = None
        self.is_sad_music = False

        self.spawn_points = []
        self.hit_knockback = 8

        self.player_spawn = (self.map_w / 2, self.map_h / 2)
        self.castle_pos = (self.map_w / 2, self.map_h / 2)

        self.castle_hp_max = 100
        self.castle_hp = 100

        self.wave = 1
        self.wave_left = self.wave_plan[0]
        self.wave_alive = 0

        self.spawn_delay = 1.2
        self.spawn_timer = 0.0

        self.kills = 0
        self.level_time = 0.0

        self.game_won = False
        self.game_over = False
        self.paused = False

        objs = scene_list(self.scene, L_OBJECTS)
        if objs is not None:
            for s in objs:
                n = safe_prop_name(s)
                if n.startswith("spawn_"):
                    self.spawn_points.append((s.center_x, s.center_y))
                if n == "player_spawn":
                    self.player_spawn = (s.center_x, s.center_y)
                if n == "castle":
                    self.castle_pos = (s.center_x, s.center_y)

        if not self.spawn_points:
            cx, cy = self.castle_pos
            m = 32
            self.spawn_points = [(cx, self.map_h - m), (cx, m), (m, cy), (self.map_w - m, cy)]

        self.castle_radius = 110

        self.atk_dmg = 10
        self.atk_radius = 90
        self.atk_cd = 0.35
        self.atk_t = 0.0

        self.castle_target_offset_y = 140
        self.castle_target = (self.castle_pos[0], self.castle_pos[1] + self.castle_target_offset_y)
        self.castle_hw = 80
        self.castle_hh = 80

        px, py = self.player_spawn
        self.player = Hero(px, py, scale=2.0)

        self.shadow_off_y = -37
        self.shadow_w = 44
        self.shadow_h = 16
        self.shadow_a = 120

        self.players = arcade.SpriteList()
        self.players.append(self.player)

        self.enemies = arcade.SpriteList()
        self.spawn_i = 0

        self.speed = 7
        self.ctrl = MoveController(self.speed)

        self.camera = Camera2D()
        self.ui_camera = Camera2D()

        self._astar_dummy = arcade.SpriteSolidColor(1, 1, arcade.color.BLACK)
        self._barrier_dirty = True
        self._update_barriers()

        self.coins = coins
        self.coin_tex = arcade.load_texture(
            "resources/Tiny Swords (Free Pack)/Terrain/Resources/Gold/Gold Resource/Gold_Resource.png"
        )

        self.bgm = arcade.load_sound("resources/music/Garoslaw - Star of Providence Soundtrack vol. 1 - 10 Point Zero.mp3")
        self.bgm_player = None

        self.shop_btn_tex = arcade.load_texture("resources/menu/магазин.png")
        self.shop_active = False
        self.shop_time_left = 0.0
        self.shop_return_wave = None

        self.inventory = [None, None, None]
        self.upg_levels = {"damage": 0, "speed": 0, "heal": 0, "maxhp": 0}
        self.selected_item_slot = None
        self.placing_mode = False

        self.shop_icons = {
            "damage": arcade.load_texture("resources/shop/damage.png"),
            "speed": arcade.load_texture("resources/shop/speedometer.png"),
            "heal": arcade.load_texture("resources/shop/health-normal.png"),
            "maxhp": arcade.load_texture("resources/shop/health-increase.png"),
        }

        self.inv_icons = {
            "inv_1": arcade.load_texture("resources/Tiny Swords (Free Pack)/Terrain/Resources/Wood/Trees/Stump 1.png"),
            "inv_2": arcade.load_texture("resources/Tiny Swords (Free Pack)/Terrain/Resources/Wood/Wood Resource/Wood Resource.png"),
        }

        self.placed_item_textures = {
            "inv_1": arcade.load_texture("resources/Tiny Swords (Free Pack)/Terrain/Resources/Wood/Trees/Stump 1.png"),
            "inv_2": arcade.load_texture("resources/Tiny Swords (Free Pack)/Terrain/Resources/Wood/Wood Resource/Wood Resource.png"),
        }

        try:
            self.game_over_bg = arcade.load_texture("resources/menu/свиток1.png")
        except:
            self.game_over_bg = None

        self.item_effects = {
            "inv_1": {"type": "slow_enemies", "radius": 150, "slow_factor": 0.5, "max_health": 30, "attack_damage": 3},
            "inv_2": {"type": "damage_area", "radius": 120, "damage": 2, "interval": 1.0, "max_health": 20, "attack_damage": 4},
        }

        self.enemy_item_attack_timers = {}
        self.item_effect_timers = {}

        self.particle_system = ParticleSystem()

        self.fx = arcade.SpriteList()
        self.death_fx_textures = load_frames_from_dir("resources/_cache_fx/dust01", "dust", 8)

        self.physics = PhysicsEngine()

        self.shop_sections = {"player": [], "inv": [], "castle": []}
        self._make_shop_items()

        self.res_path = Path(__file__).resolve().parent / "res.txt"
        self.record = self.load_record()


    def _make_shop_items(self):
        self.shop_sections["player"] = [
            {"kind": "player_upgrade", "id": "damage", "title": "Урон +2", "price": 3},
            {"kind": "player_upgrade", "id": "speed", "title": "Скорость +1", "price": 3},
        ]
        self.shop_sections["inv"] = [
            {"kind": "inv_item", "id": "inv_1", "title": "Пень (замедление) - 30HP", "price": 4},
            {"kind": "inv_item", "id": "inv_2", "title": "Колючки (урон) - 20HP", "price": 5},
        ]
        self.shop_sections["castle"] = [
            {"kind": "castle_upgrade", "id": "heal", "title": "Хил +25", "price": 4},
            {"kind": "castle_upgrade", "id": "maxhp", "title": "MaxHP +25", "price": 6},
        ]

    def _request_barrier_rebuild(self):
        self._barrier_dirty = True

    def draw_player_shadow(self):
        x = self.player.center_x
        y = self.player.center_y + self.shadow_off_y
        arcade.draw_ellipse_filled(x, y, self.shadow_w, self.shadow_h, (0, 0, 0, self.shadow_a))

    def _update_barriers(self):
        all_barriers = arcade.SpriteList()
        for wall in self.walls:
            all_barriers.append(wall)
        for item in self.placed_items:
            if isinstance(item, PlacedItem) and not item.destroyed:
                all_barriers.append(item.barrier)
        grid = int(self.tm.tile_width * SCALING)
        self.barriers = arcade.AStarBarrierList(
            self._astar_dummy,
            all_barriers,
            grid_size=grid,
            left=0,
            right=self.map_w,
            bottom=0,
            top=self.map_h,
        )

    def spawn_enemy(self):
        if not self.spawn_points or self.game_over:
            return
        x, y = self.spawn_points[self.spawn_i % len(self.spawn_points)]
        self.spawn_i += 1
        e = Enemy(x, y, variant=self.enemy_variant)
        tx, ty = self.castle_target
        path = arcade.astar_calculate_path((x, y), (tx, ty), self.barriers, diagonal_movement=False)
        e.set_path(path)
        self.enemies.append(e)
        self.wave_alive += 1

    def can_buy(self, item):
        price = item["price"]
        if self.coins < price:
            return False
        if item["kind"] == "inv_item":
            return self.inv_free_slot() is not None
        return True

    def apply_volume(self):
        if self.bgm_player is not None:
            try:
                self.bgm_player.volume = SETTINGS["volume"] / 100
            except:
                pass
        if self.sad_player is not None:
            try:
                self.sad_player.volume = SETTINGS["volume"] / 100
            except:
                pass

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        self._center_camera()
        if self.bgm_player is None and not self.is_sad_music:
            self.bgm_player = self.bgm.play(volume=SETTINGS["volume"] / 100, loop=True)
        else:
            self.apply_volume()

    def on_shop_closed(self):
        if not self.shop_active:
            return
        if self.shop_time_left <= 0:
            self.finish_shop_and_start_next_wave()

    def start_shop_window(self):
        self.shop_active = True
        self.shop_time_left = 5.0 if self.wave == 1 else 10.0
        self.shop_return_wave = self.wave + 1

    def finish_shop_and_start_next_wave(self):
        self.shop_active = False
        self.shop_time_left = 0.0
        self.wave = self.shop_return_wave
        self.shop_return_wave = None
        self.wave_left = self.wave_plan[self.wave - 1]
        self.wave_alive = 0
        self.spawn_timer = 0.0

    def _center_camera(self):
        half_w = self.window.width / 2
        half_h = self.window.height / 2
        cx = self.player.center_x
        cy = self.player.center_y
        if cx < half_w:
            cx = half_w
        if cy < half_h:
            cy = half_h
        max_cx = self.map_w - half_w
        max_cy = self.map_h - half_h
        if cx > max_cx:
            cx = max_cx
        if cy > max_cy:
            cy = max_cy
        self.camera.position = (cx, cy)

    def stop_main_music(self):
        if self.bgm_player is not None:
            try:
                self.bgm_player.pause()
            except:
                pass
            self.bgm_player = None

    def start_sad_music(self):
        if self.sad_player is not None:
            return
        self.stop_main_music()
        self.sad_player = self.sad_bgm.play(volume=SETTINGS["volume"] / 100, loop=True)
        self.is_sad_music = True

    def stop_sad_music(self):
        if self.sad_player is not None:
            try:
                self.sad_player.pause()
            except:
                pass
            self.sad_player = None
        self.is_sad_music = False

    def show_game_over_screen(self):
        self.game_over = True
        self.update_and_save_record()
        self.start_sad_music()

    def update_and_save_record(self):
        try:
            if self.kills > self.record:
                self.record = self.kills
            self.res_path.write_text(str(self.record), encoding="utf-8")
        except:
            pass

    def load_record(self):
        try:
            if self.res_path.exists():
                text = self.res_path.read_text(encoding="utf-8").strip()
                return int(text) if text else 0
            return 0
        except:
            return 0

    def draw_world_no_ui(self):
        self.camera.use()
        self.scene.draw()
        self.draw_player_shadow()
        self.enemies.draw()
        self.players.draw()
        self.fx.draw()
        self.placed_items.draw()
        self.particle_system.draw()

        if self.placing_mode and self.selected_item_slot is not None:
            mouse_x = self.window.mouse.x if self.window.mouse else 0
            mouse_y = self.window.mouse.y if self.window.mouse else 0
            mouse_pos = self.camera.unproject((mouse_x, mouse_y))
            item_id = self.inventory[self.selected_item_slot]
            if item_id in self.item_effects:
                effect = self.item_effects[item_id]
                arcade.draw_circle_outline(mouse_pos[0], mouse_pos[1], effect["radius"], arcade.color.YELLOW, 2)

    def spawn_death_fx(self, x, y):
        fx = OneShotFX(self.death_fx_textures, x, y, scale=2.0, frame_time=0.05)
        self.fx.append(fx)

    def draw_inventory_bar(self):
        y = 70
        slot_w = 110
        slot_h = 90
        gap = 12
        total_w = slot_w * 3 + gap * 2
        start_x = self.window.width / 2 - total_w / 2 + slot_w / 2
        for i in range(3):
            cx = start_x + i * (slot_w + gap)
            cy = y
            l = cx - slot_w / 2
            r = cx + slot_w / 2
            b = cy - slot_h / 2
            t = cy + slot_h / 2

            if i == self.selected_item_slot:
                arcade.draw_lrbt_rectangle_filled(l, r, b, t, (50, 50, 100, 200))
                arcade.draw_lrbt_rectangle_outline(l, r, b, t, arcade.color.CYAN, 3)
            else:
                arcade.draw_lrbt_rectangle_filled(l, r, b, t, (0, 0, 0, 200))
                arcade.draw_lrbt_rectangle_outline(l, r, b, t, arcade.color.WHITE, 2)

            if self.inventory[i] is not None:
                icon = self.inv_icons.get(self.inventory[i])
                if icon is not None:
                    arcade.draw_texture_rect(icon, R(cx, cy, 60, 60))
                else:
                    arcade.draw_lrbt_rectangle_filled(cx - 30, cx + 30, cy - 30, cy + 30, arcade.color.RED)
                arcade.draw_text(str(i + 1), cx - slot_w / 2 + 10, b + 10, arcade.color.WHITE, 14)

    def inv_free_slot(self):
        for i in range(len(self.inventory)):
            if self.inventory[i] is None:
                return i
        return None

    def apply_upgrade(self, item_id):
        if item_id == "damage":
            self.atk_dmg += 2
            self.upg_levels["damage"] = self.upg_levels.get("damage", 0) + 1
            return
        if item_id == "speed":
            self.speed += 1
            if hasattr(self.ctrl, "speed"):
                self.ctrl.speed = self.speed
            else:
                self.ctrl = MoveController(self.speed)
            self.upg_levels["speed"] = self.upg_levels.get("speed", 0) + 1
            return
        if item_id == "heal":
            self.castle_hp = min(self.castle_hp_max, self.castle_hp + 25)
            self.upg_levels["heal"] = self.upg_levels.get("heal", 0) + 1
            return
        if item_id == "maxhp":
            self.castle_hp_max += 25
            self.castle_hp += 25
            self.upg_levels["maxhp"] = self.upg_levels.get("maxhp", 0) + 1
            return

    def try_buy_item(self, item):
        if not self.can_buy(item):
            return
        price = item["price"]
        if self.coins < price:
            return
        if item["kind"] == "inv_item":
            slot = self.inv_free_slot()
            if slot is None:
                return
            self.coins -= price
            self.inventory[slot] = item["id"]
            return
        self.coins -= price
        self.apply_upgrade(item["id"])

    def apply_item_effect(self, item_id, item_sprite):
        if item_sprite.effect_applied or item_sprite.destroyed:
            return
        effect = self.item_effects.get(item_id)
        if not effect:
            return
        if effect["type"] == "slow_enemies":
            for enemy in self.enemies:
                dist = math.hypot(item_sprite.center_x - enemy.center_x, item_sprite.center_y - enemy.center_y)
                if dist <= effect["radius"]:
                    enemy.speed = enemy.speed * effect["slow_factor"]
        item_sprite.effect_applied = True

    def update_item_effects(self, dt):
        for item in self.placed_items:
            if not isinstance(item, PlacedItem) or item.destroyed:
                continue
            item.update(dt)
            effect = self.item_effects.get(item.item_id)
            if not effect:
                continue
            if effect["type"] == "damage_area":
                k = f"{item.item_id}_{id(item)}"
                if k not in self.item_effect_timers:
                    self.item_effect_timers[k] = 0.0
                self.item_effect_timers[k] += dt
                if self.item_effect_timers[k] >= effect["interval"]:
                    self.item_effect_timers[k] = 0.0
                    for enemy in self.enemies:
                        if math.hypot(item.center_x - enemy.center_x, item.center_y - enemy.center_y) <= effect["radius"]:
                            enemy.take_damage(effect["damage"])

    def handle_enemy_item_collisions(self, dt):
        destroyed_items = []
        for enemy in self.enemies:
            item_collided = False
            for item in self.placed_items:
                if not isinstance(item, PlacedItem) or item.destroyed:
                    continue
                if arcade.check_for_collision(enemy, item.barrier):
                    item_collided = True
                    timer_key = f"{id(enemy)}_{id(item)}"
                    if timer_key not in self.enemy_item_attack_timers:
                        self.enemy_item_attack_timers[timer_key] = 0.0
                    self.enemy_item_attack_timers[timer_key] += dt
                    if self.enemy_item_attack_timers[timer_key] >= 1.0:
                        self.enemy_item_attack_timers[timer_key] = 0.0
                        effect = self.item_effects.get(item.item_id)
                        if effect:
                            damage = effect.get("attack_damage", 1)
                            self.particle_system.create_hit_particles(item.center_x, item.center_y)
                            destroyed = item.take_damage(damage)
                            if destroyed:
                                destroyed_items.append((timer_key, item))
                    enemy.set_mode("attack")
                    break

        for timer_key, item in destroyed_items:
            if timer_key in self.enemy_item_attack_timers:
                del self.enemy_item_attack_timers[timer_key]
            item.destroy(self.particle_system)
            self._request_barrier_rebuild()
            item.effect_applied = False

    def place_item(self, x, y):
        if self.selected_item_slot is None:
            return False
        item_id = self.inventory[self.selected_item_slot]
        if item_id is None:
            return False

        test_sprite = arcade.SpriteSolidColor(40, 40, arcade.color.TRANSPARENT_BLACK)
        test_sprite.center_x = x
        test_sprite.center_y = y
        if arcade.check_for_collision_with_list(test_sprite, self.walls):
            return False

        for item in self.placed_items:
            if isinstance(item, PlacedItem) and not item.destroyed:
                if math.hypot(x - item.center_x, y - item.center_y) < 40:
                    return False

        texture = self.placed_item_textures.get(item_id)
        if not texture:
            return False

        effect = self.item_effects.get(item_id, {})
        max_health = effect.get("max_health", 20)
        placed_item = PlacedItem(item_id, x, y, texture, max_health)
        self.placed_items.append(placed_item)

        self._request_barrier_rebuild()
        self.particle_system.create_placement_particles(x, y)
        self.apply_item_effect(item_id, placed_item)

        self.inventory[self.selected_item_slot] = None
        self.selected_item_slot = None
        self.placing_mode = False
        return True

    def on_mouse_press(self, x, y, button, modifiers):
        if self.game_over or self.game_won:
            return
        if self.paused:
            return

        if self.shop_active:
            cx = self.window.width / 2
            cy = self.window.height / 2
            bw = self.shop_btn_tex.width
            bh = self.shop_btn_tex.height
            if (cx - bw / 2 <= x <= cx + bw / 2) and (cy - bh / 2 <= y <= cy + bh / 2):
                self.window.show_view(ShopView(self))
                return

        if not self.placing_mode and not self.shop_active:
            y_slot = 70
            slot_w = 110
            slot_h = 90
            gap = 12
            total_w = slot_w * 3 + gap * 2
            start_x = self.window.width / 2 - total_w / 2 + slot_w / 2
            for i in range(3):
                cx = start_x + i * (slot_w + gap)
                cy = y_slot
                l = cx - slot_w / 2
                r = cx + slot_w / 2
                b = cy - slot_h / 2
                t = cy + slot_h / 2
                if l <= x <= r and b <= y <= t:
                    if self.inventory[i] is not None:
                        self.selected_item_slot = i
                        self.placing_mode = True
                    else:
                        self.selected_item_slot = None
                        self.placing_mode = False
                    return

        if self.placing_mode and button == arcade.MOUSE_BUTTON_LEFT:
            world_pos = self.camera.unproject((x, y))
            if 0 <= world_pos[0] <= self.map_w and 0 <= world_pos[1] <= self.map_h:
                self.place_item(world_pos[0], world_pos[1])

        if self.placing_mode and button == arcade.MOUSE_BUTTON_RIGHT:
            self.selected_item_slot = None
            self.placing_mode = False

    def on_key_press(self, key, modifiers):
        if self.game_won:
            if key in (arcade.key.ENTER, arcade.key.SPACE):
                self.stop_sad_music()
                self.stop_main_music()
                if self.level_index + 1 < len(MAPS):
                    self.window.show_view(GameView(self.menu_view, self.level_index + 1, self.coins))
                else:
                    self.window.show_view(self.menu_view)
            if key == arcade.key.ESCAPE:
                self.stop_sad_music()
                self.stop_main_music()
                self.window.show_view(self.menu_view)
            return

        if self.game_over:
            if key == arcade.key.ESCAPE:
                self.stop_sad_music()
                self.stop_main_music()
                self.window.show_view(self.menu_view)
            return

        if key == arcade.key.P and not self.shop_active:
            self.paused = not self.paused
            return

        if self.paused:
            if key == arcade.key.P:
                self.paused = False
                return
            if key == arcade.key.ESCAPE:
                self.paused = False
                self.update_and_save_record()
                self.window.show_view(SettingsView(self.menu_view, self))
                return
            return

        if key == arcade.key.ESCAPE:
            if self.placing_mode:
                self.selected_item_slot = None
                self.placing_mode = False
                return
            self.update_and_save_record()
            self.window.show_view(SettingsView(self.menu_view, self))
            return

        if key == arcade.key.SPACE:
            self.player.start_attack()
            self.try_attack()
            return

        if key in (arcade.key.KEY_1, arcade.key.KEY_2, arcade.key.KEY_3):
            slot_index = key - arcade.key.KEY_1
            if 0 <= slot_index < len(self.inventory) and self.inventory[slot_index] is not None:
                self.selected_item_slot = slot_index
                self.placing_mode = True
            return

        self.ctrl.on_press(key)

    def on_key_release(self, key, modifiers):
        if self.game_won or self.game_over or self.paused:
            return
        self.ctrl.on_release(key)

    def try_attack(self):
        if self.atk_t < self.atk_cd:
            return

        self.atk_t = 0.0
        px = self.player.center_x
        py = self.player.center_y

        dead = []
        for e in self.enemies:
            dx = e.center_x - px
            dy = e.center_y - py
            dist = math.hypot(dx, dy)

            if dist <= self.atk_radius and dist > 0.001:
                dead_now = e.take_damage(self.atk_dmg)

                nx = dx / dist
                ny = dy / dist

                if not hasattr(e, "_phys_vx"):
                    e._phys_vx = 0.0
                    e._phys_vy = 0.0

                e._phys_vx += nx * self.hit_knockback
                e._phys_vy += ny * self.hit_knockback

                if dead_now:
                    dead.append(e)
                    self.coins += 1
                    self.spawn_death_fx(e.center_x, e.center_y)
                    self.wave_alive -= 1

        for e in dead:
            e.remove_from_sprite_lists()
            self.kills += 1
            if self.kills > self.record:
                self.record = self.kills
                self.update_and_save_record()


    def fmt_time(self, t):
        s = int(t)
        m = s // 60
        s = s % 60
        return f"{m:02d}:{s:02d}"

    def draw_game_over_panel(self):
        cx = self.window.width / 2
        cy = self.window.height / 2

        arcade.draw_lrbt_rectangle_filled(0, self.window.width, 0, self.window.height, (0, 0, 0, 180))

        if self.game_over_bg is not None:
            arcade.draw_texture_rect(
                self.game_over_bg,
                R(cx, cy, self.game_over_bg.width, self.game_over_bg.height)
            )

        title_y = cy + 165
        arcade.draw_text(
            "GAME OVER",
            cx,
            title_y,
            arcade.color.BLACK,
            52,
            anchor_x="center",
            font_name="Nineteen Ninety Three",
        )

        lvl = self.level_index + 1
        killed = self.kills
        t = self.fmt_time(self.level_time)
        rec = self.record

        cx = self.window.width / 2
        cy = self.window.height / 2

        title_y = cy + 145

        x_label = cx - 130
        x_value = cx + 150

        y0 = cy + 55
        dy = 34


        arcade.draw_text("УБИТО:", x_label, y0, arcade.color.BLACK, 26, anchor_x="left", font_name="Nineteen Ninety Three")
        arcade.draw_text(str(killed), x_value, y0, arcade.color.BLACK, 26, anchor_x="right", font_name="Nineteen Ninety Three")

        arcade.draw_text("ВРЕМЯ:", x_label, y0 - dy, arcade.color.BLACK, 26, anchor_x="left", font_name="Nineteen Ninety Three")
        arcade.draw_text(t, x_value, y0 - dy, arcade.color.BLACK, 26, anchor_x="right", font_name="Nineteen Ninety Three")

        arcade.draw_text("УРОВЕНЬ:", x_label, y0 - dy * 2, arcade.color.BLACK, 26, anchor_x="left", font_name="Nineteen Ninety Three")
        arcade.draw_text(str(lvl), x_value, y0 - dy * 2, arcade.color.BLACK, 26, anchor_x="right", font_name="Nineteen Ninety Three")

        arcade.draw_text("РЕКОРД:", x_label, y0 - dy * 3, arcade.color.BLACK, 26, anchor_x="left", font_name="Nineteen Ninety Three")
        arcade.draw_text(str(rec), x_value, y0 - dy * 3, arcade.color.BLACK, 26, anchor_x="right", font_name="Nineteen Ninety Three")

        arcade.draw_text(
            "ESC — в меню",
            cx,
            cy - 165,
            arcade.color.BLACK,
            22,
            anchor_x="center",
            font_name="Nineteen Ninety Three",
        )


    def on_update(self, dt):
        if self.paused:
            return

        self.apply_volume()

        if self.game_over or self.game_won:
            for fx in list(self.fx):
                fx.update_animation(dt)
                if fx.done:
                    fx.remove_from_sprite_lists()
            return

        if self.shop_active:
            self.shop_time_left -= dt
            if self.shop_time_left <= 0:
                self.shop_time_left = 0
                self.finish_shop_and_start_next_wave()
            self._center_camera()
            return

        if self.castle_hp > 0:
            self.level_time += dt

        self.atk_t += dt
        self.particle_system.update(dt)

        for fx in list(self.fx):
            fx.update_animation(dt)
            if fx.done:
                fx.remove_from_sprite_lists()

        if self._barrier_dirty:
            self._update_barriers()
            self._barrier_dirty = False

        self.update_item_effects(dt)
        self.handle_enemy_item_collisions(dt)

        self.physics.resolve(
            self.enemies,
            self.player,
            self.placed_items,
            self.castle_target[0],
            self.castle_target[1],
            self.castle_hw,
            self.castle_hh,
        )

        if self.castle_hp > 0:
            if self.wave_left > 0:
                self.spawn_timer += dt
                if self.spawn_timer >= self.spawn_delay:
                    self.spawn_timer = 0.0
                    self.spawn_enemy()
                    self.wave_left -= 1
            else:
                if self.wave_alive <= 0:
                    if self.wave >= len(self.wave_plan):
                        self.game_won = True
                        self.stop_main_music()
                    else:
                        self.start_shop_window()
        else:
            if not self.game_over:
                self.show_game_over_screen()

        dx, dy = self.ctrl.vector()
        ox, oy = self.player.center_x, self.player.center_y

        self.player.center_x = ox + dx
        if arcade.check_for_collision_with_list(self.player, self.walls):
            self.player.center_x = ox

        self.player.center_y = oy + dy
        if arcade.check_for_collision_with_list(self.player, self.walls):
            self.player.center_y = oy

        self.player.update_anim(dt, dx, dy, self.speed)

        tx, ty = self.castle_target
        if self.castle_hp > 0:
            for e in self.enemies:
                is_attacking_item = False
                for item in self.placed_items:
                    if isinstance(item, PlacedItem) and not item.destroyed:
                        if arcade.check_for_collision(e, item.barrier):
                            is_attacking_item = True
                            break

                if is_attacking_item:
                    if e.mode != "attack":
                        e.set_mode("attack")

                else:
                    d = math.hypot(tx - e.center_x, ty - e.center_y)
                    if d <= self.castle_radius:
                        self.castle_hp -= e.attack(dt)
                    else:
                        e.step(dt, tx, ty)
        for e in self.enemies:
            e.tick(dt)

        if self.castle_hp < 0:
            self.castle_hp = 0

        self._center_camera()

    def draw_top_right_hud(self):
        self.ui_camera.use()

        pad = 14
        x_right = self.window.width - pad
        y_top = self.window.height - pad

        icon = 96
        gap = 8

        bg_w = icon + 160
        bg_h = icon + 44

        left = x_right - bg_w
        right = x_right
        top = y_top
        bottom = y_top - bg_h

        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (0, 0, 0, 120))

        coin_cx = x_right - icon / 2 - 10
        coin_cy = y_top - icon / 2 - 10

        if self.coin_tex is not None:
            arcade.draw_texture_rect(self.coin_tex, R(coin_cx, coin_cy, icon, icon))

        arcade.draw_text(
            str(self.coins),
            coin_cx - icon / 2 - gap,
            coin_cy - 18,
            arcade.color.WHITE,
            44,
            anchor_x="right",
            font_name="Nineteen Ninety Three"
        )

        arcade.draw_text(
            f"Рекорд: {self.record}",
            x_right - 12,
            bottom + 14,
            arcade.color.WHITE,
            26,
            anchor_x="right",
            font_name="Nineteen Ninety Three"
        )

    def on_draw(self):
        self.clear()
        self.draw_world_no_ui()

        self.ui_camera.use()
        arcade.draw_text(f"HP ЗАМКА: {self.castle_hp}/{self.castle_hp_max}", 20, self.window.height - 40,
                         arcade.color.WHITE, 18)
        arcade.draw_text(f"KILLS: {self.kills}", 20, self.window.height - 70, arcade.color.WHITE, 18)
        arcade.draw_text(f"WAVE: {self.wave}", 20, self.window.height - 100, arcade.color.WHITE, 18)

        self.draw_top_right_hud()

        self.draw_inventory_bar()

        self.ui_camera.use()

        arcade.draw_text(f"HP ЗАМКА: {self.castle_hp}/{self.castle_hp_max}", 20, self.window.height - 40, arcade.color.WHITE, 18)
        arcade.draw_text(f"KILLS: {self.kills}", 20, self.window.height - 70, arcade.color.WHITE, 18)
        arcade.draw_text(f"WAVE: {self.wave}", 20, self.window.height - 100, arcade.color.WHITE, 18)

        if self.shop_active:
            cx = self.window.width / 2
            cy = self.window.height / 2

            arcade.draw_text(
                "ПОРА ЗАКУПАТЬСЯ!!!",
                cx,
                cy + 140,
                arcade.color.WHITE,
                52,
                anchor_x="center",
                font_name="Nineteen Ninety Three",
            )

            arcade.draw_texture_rect(self.shop_btn_tex, R(cx, cy, self.shop_btn_tex.width, self.shop_btn_tex.height))
            arcade.draw_text(f"{int(self.shop_time_left)}", cx, cy - 120, arcade.color.WHITE, 26, anchor_x="center")

        self.draw_inventory_bar()

        if self.game_over:
            self.draw_game_over_panel()

        if self.game_won:
            arcade.draw_lrbt_rectangle_filled(0, self.window.width, 0, self.window.height, (0, 0, 0, 170))
            arcade.draw_text("ПОБЕДА!", self.window.width / 2, self.window.height / 2 + 40, arcade.color.WHITE, 46, anchor_x="center", font_name="Nineteen Ninety Three")
            arcade.draw_text("ENTER/SPACE — дальше", self.window.width / 2, self.window.height / 2 - 10, arcade.color.LIGHT_GRAY, 22, anchor_x="center", font_name="Nineteen Ninety Three")
            arcade.draw_text("ESC — в меню", self.window.width / 2, self.window.height / 2 - 50, arcade.color.LIGHT_GRAY, 22, anchor_x="center", font_name="Nineteen Ninety Three")

