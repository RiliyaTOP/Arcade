import arcade
from game_view import GameView  # Импортируем GameView из game_view

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Название вашей игры"
BACKGROUND_COLOR = (180, 190, 200)
HOVER_SCALE = 1.1

class SettingsView(arcade.View):
    def __init__(self, main_menu_view):
        super().__init__()
        self.main_menu = main_menu_view
        self.volume = 0.5
        self.slider_dragging = False
        
        try:
            self.background_texture = arcade.load_texture("media/фон.png")
            self.background_available = True
        except FileNotFoundError:
            self.background_available = False
        
        try:
            self.scroll_texture = arcade.load_texture("media/свиток.png")
            self.scroll_available = True
        except FileNotFoundError:
            self.scroll_available = False
    
    def on_show_view(self):
        arcade.set_background_color(BACKGROUND_COLOR)
    
    def on_resize(self, width, height):
        pass
        
    def on_draw(self):
        self.clear()
        
        width = self.window.width
        height = self.window.height
        
        if self.background_available:
            arcade.draw_texture_rect(self.background_texture, arcade.LBWH(0, 0, width, height))
        
        arcade.draw_lrbt_rectangle_filled(0, width, 0, height, (0, 0, 0, 128))
        
        scroll_width = 500
        scroll_height = 500
        
        if self.scroll_available:
            arcade.draw_texture_rect(self.scroll_texture, arcade.LBWH(width // 2 - scroll_width // 2, height // 2 - scroll_height // 2, scroll_width, scroll_height))
        else:
            arcade.draw_lrbt_rectangle_filled(width // 2 - scroll_width // 2, width // 2 + scroll_width // 2, height // 2 - scroll_height // 2, height // 2 + scroll_height // 2, (222, 184, 135))
            arcade.draw_lrbt_rectangle_outline(width // 2 - scroll_width // 2, width // 2 + scroll_width // 2, height // 2 - scroll_height // 2, height // 2 + scroll_height // 2, arcade.color.DARK_BROWN, border_width=4)
        
        arcade.draw_text("Настройки", width // 2, height // 2 + 170, arcade.color.BLACK, font_size=24, anchor_x="center", anchor_y="center", font_name="Nineteen Ninety Three")
        
        arcade.draw_text("Громкость", width // 2 - 100, height // 2 + 100, arcade.color.BLACK, font_size=16, anchor_x="left", anchor_y="center")
        
        slider_x = width // 2 - 80
        slider_y = height // 2 + 70
        slider_width = 160
        slider_height = 10
        
        arcade.draw_lrbt_rectangle_filled(slider_x, slider_x + slider_width, slider_y - slider_height // 2, slider_y + slider_height // 2, arcade.color.DARK_GRAY)
        
        arcade.draw_lrbt_rectangle_filled(slider_x, slider_x + slider_width * self.volume, slider_y - slider_height // 2, slider_y + slider_height // 2, arcade.color.ORANGE)
        
        knob_x = slider_x + slider_width * self.volume
        arcade.draw_circle_filled(knob_x, slider_y, 8, arcade.color.WHITE)
        arcade.draw_circle_outline(knob_x, slider_y, 8, arcade.color.BLACK, 2)
        
        arcade.draw_text(f"{int(self.volume * 100)}%", width // 2, height // 2 + 30, arcade.color.BLACK, font_size=14, anchor_x="center", anchor_y="center")
        
    def on_mouse_press(self, x, y, button, modifiers):
        width = self.window.width
        height = self.window.height
        
        slider_x = width // 2 - 80
        slider_y = height // 2 + 70
        slider_width = 160
        
        knob_x = slider_x + slider_width * self.volume
        knob_radius = 8
        
        distance_to_knob = ((x - knob_x) ** 2 + (y - slider_y) ** 2) ** 0.5
        
        if distance_to_knob <= knob_radius:
            self.slider_dragging = True
        
        if slider_y - 20 <= y <= slider_y + 20 and slider_x <= x <= slider_x + slider_width:
            self.volume = (x - slider_x) / slider_width
            self.volume = max(0, min(1, self.volume))
            self.slider_dragging = True
            
    def on_mouse_release(self, x, y, button, modifiers):
        self.slider_dragging = False
        
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.slider_dragging:
            width = self.window.width
            slider_x = width // 2 - 80
            slider_width = 160
            
            if slider_x <= x <= slider_x + slider_width:
                self.volume = (x - slider_x) / slider_width
                self.volume = max(0, min(1, self.volume))
                
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.main_menu)
        elif key == arcade.key.F11:
            self.window.set_fullscreen(not self.window.fullscreen)


class MainMenuView(arcade.View):
    def __init__(self):
        super().__init__()
        
        self.background_texture = self.safe_load_texture("media/фон.png", "Фон")
        
        self.hero_texture = self.safe_load_texture("media/hero.png", "Герой")
        self.knight_texture = self.safe_load_texture("media/рыцарь.png", "Рыцарь")
        self.play_button_texture = self.safe_load_texture("media/play.png", "Кнопка PLAY")
        self.settings_button_texture = self.safe_load_texture("media/настройки.png", "Кнопка SETTINGS")
        self.cloud_texture = self.safe_load_texture("media/облако.png", "Облако")
        
        self.play_button_hover = False
        self.settings_button_hover = False
        
        self.cloud1_x = 150
        self.cloud2_x = 250
        self.cloud3_x = 200
        
    def safe_load_texture(self, path, name):
        try:
            return arcade.load_texture(path)
        except FileNotFoundError:
            return None
    
    def on_resize(self, width, height):
        pass
        
    def on_show_view(self):
        arcade.set_background_color(BACKGROUND_COLOR)
        
    def on_update(self, delta_time):
        width = self.window.width
        
        self.cloud1_x += 10 * delta_time
        self.cloud2_x += 15 * delta_time
        self.cloud3_x += 8 * delta_time
        
        if self.cloud1_x > width + 50:
            self.cloud1_x = -50
        if self.cloud2_x > width + 50:
            self.cloud2_x = -50
        if self.cloud3_x > width + 50:
            self.cloud3_x = -50
    
    def on_mouse_motion(self, x, y, dx, dy):
        width = self.window.width
        height = self.window.height
        scale_x = width / SCREEN_WIDTH
        scale_y = height / SCREEN_HEIGHT
        scale = min(scale_x, scale_y)
        
        play_width = 200 * scale
        play_height = 80 * scale
        play_x = width // 2 - play_width // 2
        play_y = height // 2 - play_height // 2
        
        self.play_button_hover = (play_x <= x <= play_x + play_width and play_y <= y <= play_y + play_height)
        
        settings_width = 140 * scale
        settings_height = 60 * scale
        settings_x = width - settings_width - 20
        settings_y = height - settings_height - 20
        
        self.settings_button_hover = (settings_x <= x <= settings_x + settings_width and settings_y <= y <= settings_y + settings_height)
        
    def on_draw(self):
        self.clear()
        
        width = self.window.width
        height = self.window.height
        
        scale_x = width / SCREEN_WIDTH
        scale_y = height / SCREEN_HEIGHT
        scale = min(scale_x, scale_y)
        
        if self.background_texture:
            arcade.draw_texture_rect(self.background_texture, arcade.LBWH(0, 0, width, height))
        
        if self.cloud_texture:
            arcade.draw_texture_rect(self.cloud_texture, arcade.LBWH(self.cloud1_x - 40, height - 130 * scale_y, 80 * scale, 50 * scale))
            arcade.draw_texture_rect(self.cloud_texture, arcade.LBWH(self.cloud2_x - 50, height - 180 * scale_y, 100 * scale, 60 * scale))
            arcade.draw_texture_rect(self.cloud_texture, arcade.LBWH(self.cloud3_x - 35, height - 110 * scale_y, 70 * scale, 45 * scale))
        
        hero_width = 300 * scale
        hero_height = 300 * scale
        if self.hero_texture:
            arcade.draw_texture_rect(self.hero_texture, arcade.LBWH(width * 0.01, height * 0.14, hero_width, hero_height))
        else:
            arcade.draw_lrbt_rectangle_filled(width * 0.1, width * 0.1 + hero_width, height * 0.15, height * 0.15 + hero_height, arcade.color.GREEN)
            arcade.draw_text("HERO", width * 0.1 + hero_width/2, height * 0.15 + hero_height/2, arcade.color.WHITE, 14, anchor_x="center", anchor_y="center")
        
        play_width = 200 * scale
        play_height = 80 * scale
        play_x = width // 2 - play_width // 2
        play_y = height // 2 - play_height // 2
        
        if self.play_button_hover:
            play_width *= HOVER_SCALE
            play_height *= HOVER_SCALE
            play_x = width // 2 - play_width // 2
            play_y = height // 2 - play_height // 2
        
        if self.play_button_texture:
            arcade.draw_texture_rect(self.play_button_texture, arcade.LBWH(play_x, play_y, play_width, play_height))
        else:
            arcade.draw_lrbt_rectangle_filled(play_x, play_x + play_width, play_y, play_y + play_height, arcade.color.DARK_BROWN)
            arcade.draw_text("PLAY", play_x + play_width/2, play_y + play_height/2, arcade.color.WHITE, 16, anchor_x="center", anchor_y="center")
        
        knight_width = 350 * scale
        knight_height = 300 * scale
        if self.knight_texture:
            arcade.draw_texture_rect(self.knight_texture, arcade.LBWH(width * 0.65, height * 0.12, knight_width, knight_height))
        else:
            arcade.draw_lrbt_rectangle_filled(width * 0.65, width * 0.65 + knight_width, height * 0.15, height * 0.15 + knight_height, arcade.color.GRAY)
            arcade.draw_text("KNIGHT", width * 0.65 + knight_width/2, height * 0.15 + knight_height/2, arcade.color.WHITE, 12, anchor_x="center", anchor_y="center")
        
        settings_width = 140 * scale
        settings_height = 60 * scale
        settings_x = width - settings_width - 20
        settings_y = height - settings_height - 20
        
        if self.settings_button_hover:
            settings_width *= 1.05
            settings_height *= 1.05
            settings_x = width - settings_width - 20
            settings_y = height - settings_height - 20
        
        if self.settings_button_texture:
            arcade.draw_texture_rect(self.settings_button_texture, arcade.LBWH(settings_x, settings_y, settings_width, settings_height))
        else:
            arcade.draw_lrbt_rectangle_filled(settings_x, settings_x + settings_width, settings_y, settings_y + settings_height, arcade.color.DARK_BROWN)
            arcade.draw_text("SETTINGS", settings_x + settings_width/2, settings_y + settings_height/2, arcade.color.WHITE, 12, anchor_x="center", anchor_y="center")
        
    def on_mouse_press(self, x, y, button, modifiers):
        width = self.window.width
        height = self.window.height
        scale_x = width / SCREEN_WIDTH
        scale_y = height / SCREEN_HEIGHT
        scale = min(scale_x, scale_y)
        
        play_width = 200 * scale
        play_height = 80 * scale
        play_x = width // 2 - play_width // 2
        play_y = height // 2 - play_height // 2
        
        if (play_x <= x <= play_x + play_width and play_y <= y <= play_y + play_height):
            game_view = GameView(self)
            self.window.show_view(game_view)
            
        settings_width = 140 * scale
        settings_height = 60 * scale
        settings_x = width - settings_width - 20
        settings_y = height - settings_height - 20
        
        if (settings_x <= x <= settings_x + settings_width and settings_y <= y <= settings_y + settings_height):
            settings_view = SettingsView(self)
            self.window.show_view(settings_view)
            
    def on_key_press(self, key, modifiers):
        if key == arcade.key.F11:
            self.window.set_fullscreen(not self.window.fullscreen)
        elif key == arcade.key.ESCAPE:
            arcade.close_window()