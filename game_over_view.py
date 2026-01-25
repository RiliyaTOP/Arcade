import arcade
import os

class GameOver(arcade.View):
    def __init__(self, main_menu_view):
        super().__init__()
        self.main_menu = main_menu_view
        
        self.custom_font = self.load_custom_font()
        
        try:
            self.background_texture = arcade.load_texture("media/фон.png")
            self.background_available = True
        except FileNotFoundError:
            self.background_available = False
        
        try:
            self.restart_button_texture = arcade.load_texture("media/play.png")
            self.restart_button_available = True
        except FileNotFoundError:
            self.restart_button_available = False
        
        try:
            self.menu_button_texture = arcade.load_texture("media/магазин_кнопка.png")
            self.menu_button_available = True
        except FileNotFoundError:
            self.menu_button_available = False
        
        self.restart_button_hover = False
        self.menu_button_hover = False
    
    def load_custom_font(self):
        possible_font_paths = [
            "media/Nineteen Ninety Three.ttf",
        ]
        
        for font_path in possible_font_paths:
            if os.path.exists(font_path):
                return font_path
        
        try:
            available_fonts = arcade.get_font_names()
            for font in available_fonts:
                if "nineteen" in font.lower() or "ninety" in font.lower() or "93" in font:
                    return font
        except:
            pass
        
        return "Arial"
        
    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
    
    def on_resize(self, width, height):
        pass
    
    def on_mouse_motion(self, x, y, dx, dy):
        width = self.window.width
        height = self.window.height
        
        restart_width = 250
        restart_height = 80
        restart_x = width // 2 - restart_width // 2
        restart_y = height // 2 - 50
        
        self.restart_button_hover = (restart_x <= x <= restart_x + restart_width and 
                                     restart_y <= y <= restart_y + restart_height)
        
        menu_width = 250
        menu_height = 80
        menu_x = width // 2 - menu_width // 2
        menu_y = height // 2 - 150
        
        self.menu_button_hover = (menu_x <= x <= menu_x + menu_width and 
                                  menu_y <= y <= menu_y + menu_height)
    
    def on_draw(self):
        self.clear()
        
        width = self.window.width
        height = self.window.height
        
        if self.background_available:
            arcade.draw_texture_rect(self.background_texture, arcade.LBWH(0, 0, width, height))
        else:
            arcade.draw_lrbt_rectangle_filled(0, width, 0, height, arcade.color.BLACK)
        
        arcade.draw_lrbt_rectangle_filled(0, width, 0, height, (0, 0, 0, 180))
        
        arcade.draw_text(
            "ВЫ ПРОИГРАЛИ",
            width // 2, height // 2 + 150,
            arcade.color.RED, font_size=48,
            anchor_x="center", anchor_y="center",
            bold=True,
            font_name=self.custom_font
        )
        
        arcade.draw_text(
            "Враг настиг вас!",
            width // 2, height // 2 + 100,
            arcade.color.WHITE, font_size=24,
            anchor_x="center", anchor_y="center",
            font_name=self.custom_font
        )
        
        restart_width = 250
        restart_height = 80
        restart_x = width // 2 - restart_width // 2
        restart_y = height // 2 - 50
        
        if self.restart_button_hover:
            restart_width = int(restart_width * 1.1)
            restart_height = int(restart_height * 1.1)
            restart_x = width // 2 - restart_width // 2
            restart_y = height // 2 - 50
        
        if self.restart_button_available:
            arcade.draw_texture_rect(
                self.restart_button_texture,
                arcade.LBWH(restart_x, restart_y, restart_width, restart_height)
            )
            arcade.draw_text(
                "НАЧАТЬ ЗАНОВО",
                width // 2, restart_y + restart_height // 2,
                arcade.color.WHITE, font_size=18,
                anchor_x="center", anchor_y="center",
                bold=True,
                font_name=self.custom_font
            )
        else:
            arcade.draw_lrbt_rectangle_filled(
                restart_x, restart_x + restart_width,
                restart_y, restart_y + restart_height,
                arcade.color.DARK_GREEN
            )
            arcade.draw_lrbt_rectangle_outline(
                restart_x, restart_x + restart_width,
                restart_y, restart_y + restart_height,
                arcade.color.WHITE, 3
            )
            arcade.draw_text(
                "НАЧАТЬ ЗАНОВО",
                width // 2, restart_y + restart_height // 2,
                arcade.color.WHITE, font_size=18,
                anchor_x="center", anchor_y="center",
                bold=True,
                font_name=self.custom_font
            )
        
        menu_width = 250
        menu_height = 80
        menu_x = width // 2 - menu_width // 2
        menu_y = height // 2 - 150
        
        if self.menu_button_hover:
            menu_width = int(menu_width * 1.1)
            menu_height = int(menu_height * 1.1)
            menu_x = width // 2 - menu_width // 2
            menu_y = height // 2 - 150
        
        if self.menu_button_available:
            arcade.draw_texture_rect(
                self.menu_button_texture,
                arcade.LBWH(menu_x, menu_y, menu_width, menu_height)
            )
            arcade.draw_text(
                "ГЛАВНОЕ МЕНЮ",
                width // 2, menu_y + menu_height // 2,
                arcade.color.WHITE, font_size=18,
                anchor_x="center", anchor_y="center",
                bold=True,
                font_name=self.custom_font
            )
        else:
            arcade.draw_lrbt_rectangle_filled(
                menu_x, menu_x + menu_width,
                menu_y, menu_y + menu_height,
                arcade.color.DARK_BLUE
            )
            arcade.draw_lrbt_rectangle_outline(
                menu_x, menu_x + menu_width,
                menu_y, menu_y + menu_height,
                arcade.color.WHITE, 3
            )
            arcade.draw_text(
                "ГЛАВНОЕ МЕНЮ",
                width // 2, menu_y + menu_height // 2,
                arcade.color.WHITE, font_size=18,
                anchor_x="center", anchor_y="center",
                bold=True,
                font_name=self.custom_font
            )
    
    def on_mouse_press(self, x, y, button, modifiers):
        width = self.window.width
        height = self.window.height
        
        restart_width = 250
        restart_height = 80
        restart_x = width // 2 - restart_width // 2
        restart_y = height // 2 - 50
        
        if (restart_x <= x <= restart_x + restart_width and 
            restart_y <= y <= restart_y + restart_height):
            from game_view import GameView
            game_view = GameView(self.main_menu)
            self.window.show_view(game_view)
            return
        
        menu_width = 250
        menu_height = 80
        menu_x = width // 2 - menu_width // 2
        menu_y = height // 2 - 150
        
        if (menu_x <= x <= menu_x + menu_width and 
            menu_y <= y <= menu_y + menu_height):
            self.window.show_view(self.main_menu)
            return
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.main_menu)
        elif key == arcade.key.F11:
            self.window.set_fullscreen(not self.window.fullscreen)
        elif key == arcade.key.ENTER or key == arcade.key.SPACE:
            from game_view import GameView
            game_view = GameView(self.main_menu)
            self.window.show_view(game_view)