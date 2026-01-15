import arcade
from shop_view import ShopView
from generate_level import level
from arcade.camera import Camera2D


class GameView(arcade.View):
    def __init__(self, main_menu_view):
        super().__init__()
        self.main_menu = main_menu_view
        self.level = level(7)
        self.map_width = len(self.level)
        self.map_height = len(self.level[0])
        self.tile_size = 64

        self.tile_sprites = arcade.SpriteList()
        self.player_list = arcade.SpriteList()

        self.world_camera = Camera2D()
        self.ui_camera = Camera2D()

        self.player_sprite = arcade.Sprite(
            ":resources:images/animated_characters/female_person/femalePerson_idle.png",
            scale=0.5
        )
        self.player_sprite.center_x = self.map_width * self.tile_size // 2
        self.player_sprite.center_y = self.map_height * self.tile_size // 2
        self.player_list.append(self.player_sprite)

        self.player_speed = 300
        self.move_up = False
        self.move_down = False
        self.move_left = False
        self.move_right = False

        try:
            self.map_image = arcade.load_texture("media/карта.png")
            self.map_loaded = True
        except FileNotFoundError:
            self.map_loaded = False

        try:
            self.shop_button_image = arcade.load_texture("media/магазин_кнопка.png")
            self.shop_button_loaded = True
        except FileNotFoundError:
            self.shop_button_loaded = False

        self.shop_button_width = 150
        self.shop_button_height = 60
        self.shop_button_padding = 20

        self.player_position_x = 0
        self.player_position_y = 0

        self.slots_count = 6
        self.slot_size = 50
        self.slot_spacing = 10

        self.tile_sprites = arcade.SpriteList()


        self.generate_sprites()  # <-- добавь это!


    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_GREEN)

    def on_resize(self, width, height):
        pass

    def get_shop_button_area(self):
        left = self.shop_button_padding
        bottom = self.shop_button_padding
        right = left + self.shop_button_width
        top = bottom + self.shop_button_height
        return left, right, bottom, top

    def get_slots_area(self):
        screen_width = self.window.width
        screen_height = self.window.height

        total_width = self.slots_count * self.slot_size + (self.slots_count - 1) * self.slot_spacing
        first_x = (screen_width - total_width) // 2

        slots = []
        for i in range(self.slots_count):
            slot_x = first_x + i * (self.slot_size + self.slot_spacing)
            slot_left = slot_x
            slot_right = slot_x + self.slot_size
            slot_bottom = 20
            slot_top = 20 + self.slot_size
            slots.append((slot_left, slot_right, slot_bottom, slot_top))

        return slots

    def get_tile_color(self, value):
        if value == 0:
            return arcade.color.DARK_GREEN
        elif value == 1:
            return arcade.color.BROWN
        elif value == 2:
            return arcade.color.DARK_BLUE
        elif value == 3:
            return arcade.color.GRAY
        else:
            return arcade.color.BLACK

    def generate_sprites(self):
        self.tile_sprites.clear()

        for y in range(self.map_height):
            for x in range(self.map_width):
                tile_value = self.level[x][y]

                sprite = arcade.SpriteSolidColor(
                    self.tile_size,
                    self.tile_size,
                    color=self.get_tile_color(tile_value)
                )

                sprite.center_x = x * self.tile_size + self.tile_size // 2
                sprite.center_y = y * self.tile_size + self.tile_size // 2

                self.tile_sprites.append(sprite)

    def on_draw(self):
        self.clear()
        screen_width = self.window.width
        screen_height = self.window.height
        if self.map_loaded:
            arcade.draw_texture_rect(self.map_image, arcade.LBWH(0, 0, screen_width, screen_height))
        else:
            arcade.draw_lrbt_rectangle_filled(0, screen_width, 0, screen_height, arcade.color.DARK_GREEN)
            arcade.draw_text("КАРТА НЕ ЗАГРУЖЕНА", screen_width // 2, screen_height // 2, arcade.color.WHITE, font_size=20, anchor_x="center", anchor_y="center", multiline=True, width=400, align="center")

        self.world_camera.use()
        self.tile_sprites.draw()
        self.player_list.draw()

        self.ui_camera.use()

        if self.shop_button_loaded:
            left, right, bottom, top = self.get_shop_button_area()
            arcade.draw_texture_rect(self.shop_button_image, arcade.LBWH(left, bottom, self.shop_button_width, self.shop_button_height))
        else:
            left, right, bottom, top = self.get_shop_button_area()
            arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, arcade.color.ORANGE)
            arcade.draw_text("МАГАЗИН", (left + right) / 2, (bottom + top) / 2, arcade.color.BLACK, font_size=14, anchor_x="center", anchor_y="center", bold=True)

        slots = self.get_slots_area()
        for i, (slot_left, slot_right, slot_bottom, slot_top) in enumerate(slots):
            arcade.draw_lrbt_rectangle_outline(slot_left, slot_right, slot_bottom, slot_top, arcade.color.WHITE, 2)

            if i == self.slots_count - 1:
                arcade.draw_text("+", (slot_left + slot_right) / 2, (slot_bottom + slot_top) / 2,
                               arcade.color.WHITE, font_size=24, anchor_x="center", anchor_y="center", bold=True)

    def on_update(self, delta_time):
        dx = 0
        dy = 0
        if self.move_up:
            dy += self.player_speed * delta_time
        if self.move_down:
            dy -= self.player_speed * delta_time
        if self.move_left:
            dx -= self.player_speed * delta_time
        if self.move_right:
            dx += self.player_speed * delta_time

        self.player_sprite.center_x += dx
        self.player_sprite.center_y += dy
        position = (
            self.player_sprite.center_x,
            self.player_sprite.center_y
        )
        self.world_camera.position = arcade.math.lerp_2d(
            self.world_camera.position,
            position,
            1,  # Плавность следования камеры
        )
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.main_menu)
        elif key == arcade.key.F11:
            self.window.set_fullscreen(not self.window.fullscreen)
        elif key == arcade.key.UP or key == arcade.key.W:
            self.move_up = True
            print("Вверх")
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.move_down = True
            print("Вниз")
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.move_left = True
            print("Влево")
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.move_right = True
            print("Вправо")

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.W, arcade.key.UP):
            self.move_up = False
        elif key in (arcade.key.S, arcade.key.DOWN):
            self.move_down = False
        elif key in (arcade.key.A, arcade.key.LEFT):
            self.move_left = False
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.move_right = False


    def on_mouse_press(self, x, y, button, modifiers):
        left, right, bottom, top = self.get_shop_button_area()
        if left <= x <= right and bottom <= y <= top:
            self.window.show_view(ShopView(self))
            return

        slots = self.get_slots_area()
        for i, (slot_left, slot_right, slot_bottom, slot_top) in enumerate(slots):
            if slot_left <= x <= slot_right and slot_bottom <= y <= slot_top:
                if i == self.slots_count - 1:
                    print("Клик по квадратику с плюсом")
                else:
                    print(f"Клик по пустому слоту {i + 1}")
                return

        print(f"Клик по координатам: {x}, {y}")
