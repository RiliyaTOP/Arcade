import math
import arcade
from arcade.camera import Camera2D
from controls import MoveController
from enemy import Enemy
from menu_view import SETTINGS, SettingsView
from player import Hero
import time
from game_over_view import GameOverView





class DeathPuff(arcade.Sprite):
    def __init__(self, x, y, textures, scale=1.0):
        super().__init__()
        self.textures = textures
        self.texture = textures[0]
        self.center_x = x
        self.center_y = y
        self.scale = scale
        self.i = 0
        self.t = 0.0
        self.dt = 0.06

    def update_animation(self, delta_time: float = 1 / 60):
        self.t += delta_time
        if self.t < self.dt:
            return
        self.t = 0.0
        self.i += 1
        if self.i >= len(self.textures):
            self.remove_from_sprite_lists()
            return
        self.texture = self.textures[self.i]




class R:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h


MAP_PATH = "maps/1map.tmx"
L_WALLS = "walls"
L_OBJECTS = "objects"
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


class ShopView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
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
        head_h = 90
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

        arcade.draw_lrbt_rectangle_filled(
            0, self.window.width, 0, self.window.height,
            (0, 0, 0, 140)
        )

        left, right, bottom, top = self._panel_rect()
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (30, 30, 40, 220))
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, arcade.color.WHITE, 2)

        arcade.draw_text(
            "МАГАЗИН",
            self.window.width / 2,
            top - 46,
            arcade.color.WHITE,
            30,
            anchor_x="center",
        )

        arcade.draw_text(
            f"Золото: {self.gv.coins}",
            right - 40,
            top - 52,
            arcade.color.GOLD,
            22,
            anchor_x="right",
        )

        left, right, bottom, top = self._panel_rect()

        labels = ["ИГРОК", "ИНВЕНТАРЬ", "ЗАМОК"]

        for col in range(3):
            l, r, b, t = self._cell_rect_3cols_2rows(left, top, col, 0)
            arcade.draw_text(
                labels[col],
                (l + r) / 2,
                top - 92,
                arcade.color.WHITE,
                18,
                anchor_x="center",
            )

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
                    iw = 64
                    ih = 64
                    icx = l + 52
                    icy = b + 64
                    arcade.draw_texture_rect(icon, R(icx, icy, iw, ih))

                lvl = self.gv.upg_levels.get(item["id"], 0)
                arcade.draw_text(
                    f"x{lvl}",
                    r - 12,
                    t - 30,
                    arcade.color.WHITE,
                    18,
                    anchor_x="right",
                )
            else:
                sq = 56
                icx = (l + r) / 2
                icy = (b + t) / 2 + 6
                arcade.draw_lrbt_rectangle_filled(
                    icx - sq / 2, icx + sq / 2,
                    icy - sq / 2, icy + sq / 2,
                    arcade.color.RED
                )

            price = item["price"]
            price_color = arcade.color.WHITE if can_buy else arcade.color.LIGHT_GRAY

            coin_size = 26
            px = r - 18
            py = b + 18

            arcade.draw_texture_rect(self.gv.coin_tex, R(px - 70, py + 10, coin_size, coin_size))
            arcade.draw_text(
                str(price),
                px - 40,
                py,
                price_color,
                18,
                anchor_x="right",
            )

        self.gv.draw_inventory_bar()

        arcade.draw_text(
            "Клик по лоту — купить. ESC — выйти",
            self.window.width / 2,
            bottom - 34,
            arcade.color.LIGHT_GRAY,
            18,
            anchor_x="center",
        )

    def on_mouse_press(self, x, y, button, modifiers):
        for (l, r, b, t), item in self._iter_cells():
            if l <= x <= r and b <= y <= t:
                self.gv.try_buy_item(item)
                return

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.gv)
            self.gv.on_shop_closed()


class GameView(arcade.View):
    def __init__(self, menu_view):
        super().__init__()
        self.menu_view = menu_view
        self.t0 = time.time()
        self.kills = 0
        self.level = 1
        self.game_over = False

        self.tm = arcade.load_tilemap(
            MAP_PATH,
            scaling=SCALING,
            layer_options={L_WALLS: {"use_spatial_hash": True}},
        )
        self.scene = arcade.Scene.from_tilemap(self.tm)

        walls = scene_list(self.scene, L_WALLS)
        self.walls = walls if walls is not None else arcade.SpriteList(use_spatial_hash=True)

        self.map_w = int(self.tm.width * self.tm.tile_width * SCALING)
        self.map_h = int(self.tm.height * self.tm.tile_height * SCALING)
        self.sad_bgm = arcade.load_sound("resources/music/sad.m4a")
        self.sad_player = None
        self.is_sad_music = False



        self.spawn_points = []
        self.player_spawn = (self.map_w / 2, self.map_h / 2)
        self.castle_pos = (self.map_w / 2, self.map_h / 2)

        self.castle_hp_max = 100
        self.castle_hp = 100

        self.wave_plan = [10, 15, 20]

        self.wave = 1
        self.wave_left = self.wave_plan[0]
        self.wave_alive = 0

        self.spawn_delay = 1.2
        self.spawn_timer = 0.0

        self.kills = 0
        self.level_time = 0.0
        self.game_won = False

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
            self.spawn_points = [
                (cx, self.map_h - m),
                (cx, m),
                (m, cy),
                (self.map_w - m, cy),
            ]

        self.castle_radius = 70
        self.atk_dmg = 10
        self.atk_radius = 90
        self.atk_cd = 0.35
        self.atk_t = 0.0

        self.castle_target_offset_y = 80
        self.castle_target = (self.castle_pos[0], self.castle_pos[1] + self.castle_target_offset_y)

        px, py = self.player_spawn
        self.player = Hero(px, py, scale=2.0)

        self.players = arcade.SpriteList()
        self.players.append(self.player)

        self.enemies = arcade.SpriteList()
        self.spawn_i = 0


        self.fx = arcade.SpriteList()
        self.puff_tex = [arcade.load_texture(f"resources/fx/death_puff/puff_{i}.png") for i in range(8)]

        self.speed = 7
        self.ctrl = MoveController(self.speed)

        self.camera = Camera2D()
        self.ui_camera = Camera2D()

        self._astar_dummy = arcade.SpriteSolidColor(1, 1, arcade.color.BLACK)
        grid = int(self.tm.tile_width * SCALING)
        self.barriers = arcade.AStarBarrierList(
            self._astar_dummy,
            self.walls,
            grid_size=grid,
            left=0,
            right=self.map_w,
            bottom=0,
            top=self.map_h,
        )

        self.coins = 0
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

        self.shop_icons = {
            "damage": arcade.load_texture("resources/shop/damage.png"),
            "speed": arcade.load_texture("resources/shop/speedometer.png"),
            "heal": arcade.load_texture("resources/shop/health-normal.png"),
            "maxhp": arcade.load_texture("resources/shop/health-increase.png"),
        }

        self.shop_sections = {"player": [], "inv": [], "castle": []}
        self._make_shop_items()

    def _make_shop_items(self):
        self.shop_sections["player"] = [
            {"kind": "player_upgrade", "id": "damage", "title": "Урон +2", "price": 3},
            {"kind": "player_upgrade", "id": "speed", "title": "Скорость +1", "price": 3},
        ]

        self.shop_sections["inv"] = [
            {"kind": "inv_item", "id": "inv_1", "title": "Предмет", "price": 4},
            {"kind": "inv_item", "id": "inv_2", "title": "Предмет", "price": 5},
        ]

        self.shop_sections["castle"] = [
            {"kind": "castle_upgrade", "id": "heal", "title": "Хил +25", "price": 4},
            {"kind": "castle_upgrade", "id": "maxhp", "title": "MaxHP +25", "price": 6},
        ]

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
            except Exception:
                pass

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        self._center_camera()

        if self.bgm_player is None:
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
            except Exception:
                pass
            self.bgm_player = None

    def stop_sad_music(self):
        if self.sad_player is not None:
            try:
                self.sad_player.pause()
            except Exception:
                pass
            self.sad_player = None
        self.is_sad_music = False

    def start_sad_music(self):
        if self.sad_player is not None:
            return
        self.stop_main_music()
        self.sad_player = self.sad_bgm.play(volume=SETTINGS["volume"] / 100, loop=True)
        self.is_sad_music = True

    def draw_world_no_ui(self):
        self.camera.use()
        self.scene.draw()
        self.enemies.draw()
        self.fx.draw()
        self.players.draw()

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

            arcade.draw_lrbt_rectangle_filled(l, r, b, t, (0, 0, 0, 200))
            arcade.draw_lrbt_rectangle_outline(l, r, b, t, arcade.color.WHITE, 2)

            if self.inventory[i] is not None:
                w = 44
                h = 44
                arcade.draw_lrbt_rectangle_filled(
                    cx - w / 2, cx + w / 2,
                    cy - h / 2, cy + h / 2,
                    arcade.color.RED
                )

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

    def on_draw(self):
        self.clear()


        self.draw_world_no_ui()
        self.ui_camera.use()

        arcade.draw_text(
            f"wave: {self.wave}   left: {self.wave_left + self.wave_alive}   castle hp: {self.castle_hp}/{self.castle_hp_max}",
            20,
            self.window.height - 40,
            arcade.color.WHITE,
            16,
        )

        bx = 20
        by = self.window.height - 70
        w = 220
        h = 16

        arcade.draw_lrbt_rectangle_outline(bx, bx + w, by, by + h, arcade.color.WHITE, 2)
        p = max(0.0, min(1.0, self.castle_hp / self.castle_hp_max))
        arcade.draw_lrbt_rectangle_filled(bx, bx + w * p, by, by + h, arcade.color.GREEN)

        pad = 20
        size = 90
        right = self.window.width - pad
        top = self.window.height - pad

        arcade.draw_texture_rect(self.coin_tex, R(right - size / 2, top - size / 2, size, size))
        arcade.draw_text(str(self.coins), right - size - 14, top - size / 2 - 14, arcade.color.GOLD, 28, bold=True, anchor_x="right")

        self.draw_inventory_bar()

        if self.shop_active:
            cx = self.window.width / 2
            cy = self.window.height / 2

            arcade.draw_text(
                "ПОРА ЗАКУПАТЬСЯ!",
                cx,
                cy + 170,
                arcade.color.WHITE,
                30,
                anchor_x="center",
            )

            t = max(0, int(math.ceil(self.shop_time_left)))
            arcade.draw_text(
                f"Осталось: {t} сек",
                cx,
                cy + 130,
                arcade.color.LIGHT_GRAY,
                22,
                anchor_x="center",
            )

            bw = self.shop_btn_tex.width
            bh = self.shop_btn_tex.height
            arcade.draw_texture_rect(self.shop_btn_tex, R(cx, cy, bw, bh))

        if self.game_won:
            arcade.draw_text(
                "LEVEL COMPLETE",
                self.window.width / 2,
                self.window.height / 2,
                arcade.color.WHITE,
                36,
                anchor_x="center",
                anchor_y="center",
            )

    def on_mouse_press(self, x, y, button, modifiers):
        if self.shop_active:
            cx = self.window.width / 2
            cy = self.window.height / 2
            bw = self.shop_btn_tex.width
            bh = self.shop_btn_tex.height

            if (cx - bw / 2 <= x <= cx + bw / 2) and (cy - bh / 2 <= y <= cy + bh / 2):
                self.window.show_view(ShopView(self))
                return

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(SettingsView(self.menu_view, self))
            return

        if self.game_won:
            return

        if key == arcade.key.SPACE:
            self.player.start_attack()
            self.try_attack()
            return

        self.ctrl.on_press(key)

    def on_key_release(self, key, modifiers):
        self.ctrl.on_release(key)

    def spawn_enemy(self):
        if not self.spawn_points:
            return

        x, y = self.spawn_points[self.spawn_i % len(self.spawn_points)]
        self.spawn_i += 1

        e = Enemy(x, y)

        tx, ty = self.castle_target
        path = arcade.astar_calculate_path((x, y), (tx, ty), self.barriers, diagonal_movement=False)
        e.set_path(path)

        self.enemies.append(e)
        self.wave_alive += 1

    def try_attack(self):
        if self.atk_t < self.atk_cd:
            return

        self.atk_t = 0.0

        px = self.player.center_x
        py = self.player.center_y

        dead = []
        for e in self.enemies:
            d = math.hypot(px - e.center_x, py - e.center_y)
            if d <= self.atk_radius:
                dead_now = e.take_damage(self.atk_dmg)
                if dead_now:
                    dead.append(e)
                    self.kills += 1
                    self.fx.append(DeathPuff(e.center_x, e.center_y, self.puff_tex, scale=1.5))
                    self.coins += 1
                    self.wave_alive -= 1

        for e in dead:
            e.remove_from_sprite_lists()

    def on_update(self, dt):

        self.fx.update_animation(dt)
        self.apply_volume()

        if self.shop_active:
            self.shop_time_left -= dt
            if self.shop_time_left <= 0:
                self.shop_time_left = 0
                self.finish_shop_and_start_next_wave()
            self._center_camera()
            return

        if not self.game_won and self.castle_hp > 0:
            self.level_time += dt

        self.atk_t += dt
        for e in self.enemies:
            e.tick(dt)

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
                    else:
                        self.start_shop_window()

        if self.castle_hp <= 0 and not self.game_over:
            self.game_over = True
            self.start_sad_music()
            self.open_game_over()

        dx, dy = self.ctrl.vector()
        self.player.update_anim(dt, dx, dy, self.speed)

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
                d = math.hypot(tx - e.center_x, ty - e.center_y)
                if d <= self.castle_radius:
                    self.castle_hp -= e.attack(dt)
                else:
                    e.step(dt, tx, ty)

            if self.castle_hp < 0:
                self.castle_hp = 0

        self._center_camera()

    def open_game_over(self):
        t = time.time() - self.t0
        stats = {
            "time_s": t,
            "kills": self.kills,
            "level": self.wave,
        }

        def restart():
            self.stop_sad_music()
            v = GameView(self.menu_view)
            self.window.show_view(v)

        self.window.show_view(GameOverView(stats, restart))

