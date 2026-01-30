import arcade



class R:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h


class GameOverView(arcade.View):
    def __init__(self, stats, on_restart):
        super().__init__()
        self.stats = stats
        self.on_restart = on_restart

        self.btn_w = 420
        self.btn_h = 80
        self.btn_x = 0
        self.btn_y = 0
        self._hover = False

        self.skull_tex = arcade.load_texture("resources/skull007.png")

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        self.on_resize(self.window.width, self.window.height)

    def on_resize(self, width, height):
        self.btn_x = (width - self.btn_w) / 2
        self.btn_y = height * 0.18

    def _in_btn(self, x, y):
        return self.btn_x <= x <= self.btn_x + self.btn_w and self.btn_y <= y <= self.btn_y + self.btn_h

    def on_mouse_motion(self, x, y, dx, dy):
        self._hover = self._in_btn(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if self._in_btn(x, y):
            self.on_restart()

    def on_draw(self):
        self.clear()

        w = self.window.width
        h = self.window.height

        skull_size = 96
        arcade.draw_texture_rect(
            self.skull_tex,
            R(w / 2, h * 0.78, skull_size, skull_size)
        )

        arcade.draw_text(
            "ВЫ ПРОИГРАЛИ!",
            w / 2,
            h * 0.70,
            arcade.color.RED,
            56,
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )

        t = float(self.stats.get("time_s", 0.0))
        kills = int(self.stats.get("kills", 0))
        lvl = int(self.stats.get("level", 1))

        mm = int(t // 60)
        ss = int(t % 60)
        time_str = f"{mm:02d}:{ss:02d}"

        arcade.draw_text(f"Время: {time_str}", w / 2, h * 0.55, arcade.color.WHITE, 24, anchor_x="center", anchor_y="center")
        arcade.draw_text(f"Убито слаймов: {kills}", w / 2, h * 0.50, arcade.color.WHITE, 24, anchor_x="center", anchor_y="center")
        arcade.draw_text(f"Уровень: {lvl}", w / 2, h * 0.45, arcade.color.WHITE, 24, anchor_x="center", anchor_y="center")

        col = arcade.color.DARK_GREEN if self._hover else arcade.color.GREEN
        arcade.draw_lrbt_rectangle_filled(
            self.btn_x,
            self.btn_x + self.btn_w,
            self.btn_y,
            self.btn_y + self.btn_h,
            col
        )

        arcade.draw_text(
            "НАЧАТЬ ЗАНОВО",
            self.btn_x + self.btn_w / 2,
            self.btn_y + self.btn_h / 2,
            arcade.color.WHITE,
            26,
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )
