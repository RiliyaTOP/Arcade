import arcade
import os
from pathlib import Path

WIN_W = 1280
WIN_H = 720

DESIGN_W = 1280
DESIGN_H = 720

MENU_DIR = Path("resources") / "menu"
MUSIC_PATH = Path("resources") / "music" / "Garoslaw - Star of Providence Soundtrack vol. 1 - 03 Before the Dawn.mp3"
LOGO_PATH = Path("resources") / "menu" / "Mega-Ultra-Game.png"

SETTINGS = {"volume": 40}

SETTINGS_PATH = "settings.txt"


def _clamp_int(v, a, b):
    try:
        v = int(v)
    except Exception:
        return a
    if v < a:
        return a
    if v > b:
        return b
    return v


def load_settings():
    try:
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                line = f.read().strip()
            if line:
                SETTINGS["volume"] = _clamp_int(line, 0, 100)
    except Exception:
        pass


def save_settings():
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            f.write(str(_clamp_int(SETTINGS.get("volume", 40), 0, 100)))
    except Exception:
        pass


load_settings()


load_settings()


def tex(name):
    return arcade.load_texture(str(MENU_DIR / name))


class R:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h


class MainMenuView(arcade.View):
    def __init__(self):
        super().__init__()

        self.music = arcade.Sound(str(MUSIC_PATH))
        self.music_player = None
        self.music_loop_supported = True

        self.bg = tex("фон.png")
        self.hero = tex("hero.png")
        self.knight = tex("рыцарь.png")
        self.play = tex("play.png")
        self.settings = tex("настройки.png")
        self.cloud = tex("облако.png")

        self.logo = arcade.load_texture(str(LOGO_PATH))
        self.logo_base_scale = 1.0

        self.h_play = False
        self.h_set = False

        self.clouds = [
            {"x": 380.0, "y": 600.0, "s": 1.15, "v": 26.0},
            {"x": 720.0, "y": 560.0, "s": 0.90, "v": 18.0},
            {"x": 980.0, "y": 635.0, "s": 1.05, "v": 32.0},
        ]

    def _fit(self):
        ww = self.window.width
        wh = self.window.height
        sc = min(ww / DESIGN_W, wh / DESIGN_H)
        ox = (ww - DESIGN_W * sc) / 2
        oy = (wh - DESIGN_H * sc) / 2
        return sc, ox, oy

    def _v(self, x, y, sc, ox, oy):
        return ox + x * sc, oy + y * sc

    def _btn_hit(self, x, y, cx, cy, w, h):
        return (cx - w / 2 <= x <= cx + w / 2) and (cy - h / 2 <= y <= cy + h / 2)

    def _music_volume(self):
        return max(0.0, min(1.0, SETTINGS["volume"] / 100))

    def start_music(self):
        if self.music_player is not None and getattr(self.music_player, "playing", False):
            return

        vol = self._music_volume()

        try:
            self.music_player = self.music.play(volume=vol, loop=True)
            self.music_loop_supported = True
        except TypeError:
            self.music_player = self.music.play(volume=vol)
            self.music_loop_supported = False

    def stop_music(self):
        if self.music_player is not None:
            try:
                self.music_player.pause()
            except Exception:
                pass
            self.music_player = None

    def apply_volume(self):
        if self.music_player is not None and hasattr(self.music_player, "volume"):
            self.music_player.volume = self._music_volume()

    def on_show_view(self):
        arcade.set_background_color((20, 20, 30))
        self.start_music()
        max_width = DESIGN_W * 0.7
        self.logo_base_scale = min(1.0, max_width / self.logo.width)

    def on_hide_view(self):
        self.stop_music()

    def on_update(self, dt):
        for c in self.clouds:
            c["x"] += c["v"] * dt
            if c["x"] > DESIGN_W + 220:
                c["x"] = -220

        if self.music_player is not None and not self.music_loop_supported:
            if hasattr(self.music_player, "playing") and not self.music_player.playing:
                self.start_music()

    def on_mouse_motion(self, x, y, dx, dy):
        sc, ox, oy = self._fit()

        play_cx, play_cy = self._v(640, 410, sc, ox, oy)
        set_cx, set_cy = self._v(640, 520, sc, ox, oy)

        play_w = self.play.width * sc
        play_h = self.play.height * sc

        set_w = self.settings.width * sc
        set_h = self.settings.height * sc

        self.h_play = self._btn_hit(x, y, play_cx, play_cy, play_w, play_h)
        self.h_set = self._btn_hit(x, y, set_cx, set_cy, set_w, set_h)

    def on_mouse_press(self, x, y, button, modifiers):
        sc, ox, oy = self._fit()

        play_cx, play_cy = self._v(640, 410, sc, ox, oy)
        set_cx, set_cy = self._v(640, 520, sc, ox, oy)

        play_w = self.play.width * sc
        play_h = self.play.height * sc

        set_w = self.settings.width * sc
        set_h = self.settings.height * sc

        if self._btn_hit(x, y, play_cx, play_cy, play_w, play_h):
            import traceback
            from game_view import GameView
            try:
                gv = GameView(self)
            except Exception:
                traceback.print_exc()
                return
            self.window.show_view(gv)
            return

        if self._btn_hit(x, y, set_cx, set_cy, set_w, set_h):
            self.window.show_view(SettingsView(self, self))
            return

    def on_draw(self):
        self.clear()
        sc, ox, oy = self._fit()

        bg_cx, bg_cy = self._v(DESIGN_W / 2, DESIGN_H / 2, sc, ox, oy)
        arcade.draw_texture_rect(self.bg, R(bg_cx, bg_cy, DESIGN_W * sc, DESIGN_H * sc))

        for c in self.clouds:
            cx, cy = self._v(c["x"], c["y"], sc, ox, oy)
            w = self.cloud.width * sc * c["s"]
            h = self.cloud.height * sc * c["s"]
            arcade.draw_texture_rect(self.cloud, R(cx, cy, w, h))

        logo_cx, logo_cy = self._v(640, 640, sc, ox, oy)
        lw = self.logo.width * self.logo_base_scale * sc
        lh = self.logo.height * self.logo_base_scale * sc
        arcade.draw_texture_rect(self.logo, R(logo_cx, logo_cy, lw, lh))

        hero_cx, hero_cy = self._v(210, 210, sc, ox, oy)
        arcade.draw_texture_rect(self.hero, R(hero_cx, hero_cy, self.hero.width * sc, self.hero.height * sc))

        k_cx, k_cy = self._v(1085, 205, sc, ox, oy)
        arcade.draw_texture_rect(self.knight, R(k_cx, k_cy, self.knight.width * sc, self.knight.height * sc))

        play_cx, play_cy = self._v(640, 410, sc, ox, oy)
        k = 1.05 if self.h_play else 1.0
        arcade.draw_texture_rect(self.play, R(play_cx, play_cy, self.play.width * sc * k, self.play.height * sc * k))

        set_cx, set_cy = self._v(640, 520, sc, ox, oy)
        k2 = 1.05 if self.h_set else 1.0
        arcade.draw_texture_rect(self.settings, R(set_cx, set_cy, self.settings.width * sc * k2, self.settings.height * sc * k2))


class SettingsView(arcade.View):
    def __init__(self, menu_view, back_view):
        super().__init__()
        self.menu_view = menu_view
        self.back_view = back_view
        self.ui_camera = arcade.Camera2D()

        self.logo = arcade.load_texture(str(LOGO_PATH))
        self.logo_base_scale = 1.0

        self.drag = False
        self.bar_x = 0
        self.bar_y = 0
        self.bar_w = 520
        self.bar_h = 16
        self.knob_r = 16

    def _fit(self):
        ww = self.window.width
        wh = self.window.height
        sc = min(ww / DESIGN_W, wh / DESIGN_H)
        ox = (ww - DESIGN_W * sc) / 2
        oy = (wh - DESIGN_H * sc) / 2
        return sc, ox, oy

    def _v(self, x, y, sc, ox, oy):
        return ox + x * sc, oy + y * sc

    def _clamp(self, v, a, b):
        return a if v < a else b if v > b else v

    def _set_from_mouse(self, mx):
        left = self.bar_x - self.bar_w / 2
        t = (mx - left) / self.bar_w
        t = self._clamp(t, 0.0, 1.0)
        vol = int(round(t * 100))
        SETTINGS["volume"] = self._clamp(vol, 0, 100)
        save_settings()

        bv = self.back_view
        if hasattr(bv, "apply_volume"):
            bv.apply_volume()

    def on_show_view(self):
        arcade.set_background_color((20, 20, 30))
        max_w = DESIGN_W * 0.55
        self.logo_base_scale = min(1.0, max_w / self.logo.width)

    def on_draw(self):
        self.ui_camera.use()
        self.clear()
        sc, ox, oy = self._fit()

        logo_cx, logo_cy = self._v(640, 620, sc, ox, oy)
        lw = self.logo.width * self.logo_base_scale * sc
        lh = self.logo.height * self.logo_base_scale * sc
        arcade.draw_texture_rect(self.logo, R(logo_cx, logo_cy, lw, lh))

        arcade.draw_text(
            "НАСТРОЙКИ",
            self.window.width / 2,
            self.window.height / 2 + 190 * sc,
            arcade.color.WHITE,
            int(34 * sc),
            anchor_x="center",
        )

        self.bar_x, self.bar_y = self._v(640, 360, sc, ox, oy)

        left = self.bar_x - self.bar_w / 2
        right = self.bar_x + self.bar_w / 2
        bottom = self.bar_y - self.bar_h / 2
        top = self.bar_y + self.bar_h / 2

        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (60, 60, 75))
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, arcade.color.WHITE, 2)

        vol = SETTINGS["volume"]
        t = self._clamp(vol / 100.0, 0.0, 1.0)
        fill_r = left + self.bar_w * t

        arcade.draw_lrbt_rectangle_filled(left, fill_r, bottom, top, (200, 170, 80))

        knob_x = fill_r
        knob_y = self.bar_y

        arcade.draw_circle_filled(knob_x, knob_y, self.knob_r, arcade.color.WHITE)
        arcade.draw_circle_outline(knob_x, knob_y, self.knob_r, arcade.color.BLACK, 2)

        arcade.draw_text(
            f"Громкость: {vol}",
            self.window.width / 2,
            self.window.height / 2 + 70 * sc,
            arcade.color.WHITE,
            int(24 * sc),
            anchor_x="center",
        )

        arcade.draw_text(
            "ESC — назад",
            self.window.width / 2,
            self.window.height / 2 - 190 * sc,
            arcade.color.LIGHT_GRAY,
            int(18 * sc),
            anchor_x="center",
        )

    def on_mouse_press(self, x, y, button, modifiers):
        left = self.bar_x - self.bar_w / 2
        right = self.bar_x + self.bar_w / 2
        bottom = self.bar_y - 28
        top = self.bar_y + 28

        if left <= x <= right and bottom <= y <= top:
            self.drag = True
            self._set_from_mouse(x)

    def on_mouse_release(self, x, y, button, modifiers):
        self.drag = False

    def on_mouse_motion(self, x, y, dx, dy):
        if self.drag:
            self._set_from_mouse(x)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.back_view)
