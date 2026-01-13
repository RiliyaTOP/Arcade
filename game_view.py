import arcade
from shop_view import ShopView

class GameView(arcade.View):
    def __init__(self, main_menu_view):
        super().__init__()
        self.main_menu = main_menu_view
        
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
        
    def on_draw(self):
        self.clear()
        
        screen_width = self.window.width
        screen_height = self.window.height
        
        if self.map_loaded:
            arcade.draw_texture_rect(self.map_image, arcade.LBWH(0, 0, screen_width, screen_height))
        else:
            arcade.draw_lrbt_rectangle_filled(0, screen_width, 0, screen_height, arcade.color.DARK_GREEN)
            arcade.draw_text("КАРТА НЕ ЗАГРУЖЕНА", screen_width // 2, screen_height // 2, arcade.color.WHITE, font_size=20, anchor_x="center", anchor_y="center", multiline=True, width=400, align="center")
        
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
        pass
        
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.main_menu)
        elif key == arcade.key.F11:
            self.window.set_fullscreen(not self.window.fullscreen)
        elif key == arcade.key.UP or key == arcade.key.W:
            print("Вверх")
        elif key == arcade.key.DOWN or key == arcade.key.S:
            print("Вниз")
        elif key == arcade.key.LEFT or key == arcade.key.A:
            print("Влево")
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            print("Вправо")
        
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