import arcade

class ShopView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        self.balance = 0
        self.scroll_position = 0
        self.scroll_speed = 50
        
        try:
            self.background = arcade.load_texture("media/фон.png")
            self.background_available = True
        except:
            self.background_available = False
        
        try:
            self.header = arcade.load_texture("media/магазин_шапка.png")
            self.header_available = True
        except:
            self.header_available = False
        
        try:
            self.footer = arcade.load_texture("media/магазин_футер.png")
            self.footer_available = True
        except:
            self.footer_available = False
        
        self.shop_items = [
            {'name': 'Камни', 'image': 'media/камни.png', 'production': 1, 'price': 10},
            {'name': 'Банан', 'image': 'media/банан.png', 'production': 3, 'price': 25},
            {'name': 'Костер', 'image': 'media/костер.png', 'production': 5, 'price': 50},
            {'name': 'Банан 2', 'image': 'media/банан.png', 'production': 3, 'price': 30},
            {'name': 'Камни 2', 'image': 'media/камни.png', 'production': 1, 'price': 15},
            {'name': 'Банан 3', 'image': 'media/банан.png', 'production': 3, 'price': 35},
            {'name': 'Костер 2', 'image': 'media/костер.png', 'production': 5, 'price': 60},
            {'name': 'Банан 4', 'image': 'media/банан.png', 'production': 3, 'price': 40},
            {'name': 'Камни 3', 'image': 'media/камни.png', 'production': 1, 'price': 20},
            {'name': 'Банан 5', 'image': 'media/банан.png', 'production': 3, 'price': 45},
            {'name': 'Костер 3', 'image': 'media/костер.png', 'production': 5, 'price': 75},
            {'name': 'Банан 6', 'image': 'media/банан.png', 'production': 3, 'price': 50},
            {'name': 'Камни 4', 'image': 'media/камни.png', 'production': 1, 'price': 25},
            {'name': 'Банан 7', 'image': 'media/банан.png', 'production': 3, 'price': 55},
            {'name': 'Костер 4', 'image': 'media/костер.png', 'production': 5, 'price': 90},
            {'name': 'Банан 8', 'image': 'media/банан.png', 'production': 3, 'price': 60},
        ]
        
        for item in self.shop_items:
            try:
                item['texture'] = arcade.load_texture(item['image'])
            except:
                item['texture'] = None
        
        self.cards_in_row = 4
        self.visible_rows = 2
        self.card_width = 170
        self.card_height = 240
        self.card_margin = 20
        self.header_size = 80
        self.footer_size = 0

    def on_show_view(self):
        arcade.set_background_color(arcade.color.SKY_BLUE)
        self.scroll_position = 0
    
    def on_resize(self, width, height):
        max_scroll = self.get_max_scroll()
        self.scroll_position = max(-max_scroll, min(self.scroll_position, max_scroll))
    
    def get_total_content_height(self):
        total_rows = (len(self.shop_items) + self.cards_in_row - 1) // self.cards_in_row
        return total_rows * (self.card_height + self.card_margin) + self.card_margin
    
    def get_max_scroll(self):
        content_height = self.get_total_content_height()
        window_height = self.window.height
        visible_height = window_height - self.header_size - 40
        
        total_rows = (len(self.shop_items) + self.cards_in_row - 1) // self.cards_in_row
        visible_rows = int(visible_height / (self.card_height + self.card_margin))
        
        if total_rows <= visible_rows:
            return 0
        
        hidden_rows = total_rows - visible_rows
        max_scroll = hidden_rows * (self.card_height + self.card_margin)
        
        return max_scroll
        
    def on_draw(self):
        self.clear()
        
        screen_width = self.window.width
        screen_height = self.window.height
        
        if self.background_available:
            arcade.draw_texture_rect(self.background, arcade.LBWH(0, 0, screen_width, screen_height))
        else:
            arcade.draw_lrbt_rectangle_filled(0, screen_width, 0, screen_height, arcade.color.SKY_BLUE)
        
        content_top = screen_height - self.header_size
        content_bottom = 40
        
        total_width = self.cards_in_row * self.card_width + (self.cards_in_row - 1) * self.card_margin
        start_x = (screen_width - total_width) // 2
        start_y = content_top - self.card_margin
        
        for index, item in enumerate(self.shop_items):
            row = index // self.cards_in_row
            col = index % self.cards_in_row
            
            x = start_x + col * (self.card_width + self.card_margin)
            y = start_y - (row + 1) * (self.card_height + self.card_margin) - self.scroll_position
            
            if y + self.card_height >= content_bottom and y <= content_top:
                self.draw_product_card(x, y, item)
        
        if self.header_available:
            arcade.draw_texture_rect(self.header, arcade.LBWH(0, screen_height - self.header_size, screen_width, self.header_size))
        else:
            arcade.draw_lrbt_rectangle_filled(0, screen_width, screen_height - self.header_size, screen_height, (218, 165, 32))
            arcade.draw_lrbt_rectangle_outline(0, screen_width, screen_height - self.header_size, screen_height, arcade.color.DARK_GOLDENROD, border_width=4)
            arcade.draw_text("МАГАЗИН", screen_width // 2, screen_height - self.header_size // 2, arcade.color.BLACK, font_size=28, anchor_x="center", anchor_y="center", bold=True)
        
        balance_x = 20
        balance_y = screen_height - 30
        
        arcade.draw_text(f"Баланс: {self.balance}", balance_x, balance_y, arcade.color.WHITE, font_size=16, anchor_x="left", anchor_y="center", bold=True)
        
        coin_x = balance_x + 100
        arcade.draw_circle_filled(coin_x, balance_y, 8, arcade.color.GOLD)
        arcade.draw_circle_outline(coin_x, balance_y, 8, arcade.color.DARK_GOLDENROD, 2)
    
    def draw_product_card(self, x, y, item):
        corner_radius = 10
        
        arcade.draw_lrbt_rectangle_filled(x + corner_radius, x + self.card_width - corner_radius, y, y + self.card_height, arcade.color.WHITE)
        arcade.draw_lrbt_rectangle_filled(x, x + self.card_width, y + corner_radius, y + self.card_height - corner_radius, arcade.color.WHITE)
        
        arcade.draw_circle_filled(x + corner_radius, y + corner_radius, corner_radius, arcade.color.WHITE)
        arcade.draw_circle_filled(x + self.card_width - corner_radius, y + corner_radius, corner_radius, arcade.color.WHITE)
        arcade.draw_circle_filled(x + corner_radius, y + self.card_height - corner_radius, corner_radius, arcade.color.WHITE)
        arcade.draw_circle_filled(x + self.card_width - corner_radius, y + self.card_height - corner_radius, corner_radius, arcade.color.WHITE)
        
        image_size = 100
        image_x = x + self.card_width // 2
        image_y = y + self.card_height - 70
        
        arcade.draw_lrbt_rectangle_filled(image_x - image_size // 2, image_x + image_size // 2, image_y - image_size // 2, image_y + image_size // 2, (169, 169, 169))
        
        if item['texture']:
            arcade.draw_texture_rect(item['texture'], arcade.LBWH(image_x - image_size // 2, image_y - image_size // 2, image_size, image_size))
        else:
            arcade.draw_text("?", image_x, image_y, arcade.color.BLACK, font_size=48, anchor_x="center", anchor_y="center", bold=True)
        
        prod_y = y + 110
        arcade.draw_text("Производит:", x + self.card_width // 2, prod_y, arcade.color.BLACK, font_size=10, anchor_x="center", anchor_y="center")
        
        coin_y = prod_y - 20
        self.draw_coins(x + self.card_width // 2, coin_y, item['production'])
        
        price_y = y + 65
        arcade.draw_text(f"Цена:", x + self.card_width // 2 - 20, price_y, arcade.color.DARK_GRAY, font_size=11, anchor_x="center", anchor_y="center", bold=True)
        arcade.draw_text(f"{item['price']}", x + self.card_width // 2 + 10, price_y, arcade.color.DARK_GRAY, font_size=11, anchor_x="center", anchor_y="center", bold=True)
        
        coin_icon_x = x + self.card_width // 2 + 30
        arcade.draw_circle_filled(coin_icon_x, price_y, 6, arcade.color.GOLD)
        arcade.draw_circle_outline(coin_icon_x, price_y, 6, arcade.color.DARK_GOLDENROD, 2)
        
        button_width = 120
        button_height = 35
        button_x = x + (self.card_width - button_width) // 2
        button_y = y + 15
        button_radius = 8
        
        arcade.draw_lrbt_rectangle_filled(button_x + button_radius, button_x + button_width - button_radius, button_y, button_y + button_height, (128, 128, 128))
        arcade.draw_lrbt_rectangle_filled(button_x, button_x + button_width, button_y + button_radius, button_y + button_height - button_radius, (128, 128, 128))
        
        arcade.draw_circle_filled(button_x + button_radius, button_y + button_radius, button_radius, (128, 128, 128))
        arcade.draw_circle_filled(button_x + button_width - button_radius, button_y + button_radius, button_radius, (128, 128, 128))
        arcade.draw_circle_filled(button_x + button_radius, button_y + button_height - button_radius, button_radius, (128, 128, 128))
        arcade.draw_circle_filled(button_x + button_width - button_radius, button_y + button_height - button_radius, button_radius, (128, 128, 128))
        
        arcade.draw_text("КУПИТЬ", button_x + button_width // 2, button_y + button_height // 2, arcade.color.BLACK, font_size=12, anchor_x="center", anchor_y="center", bold=True)
    
    def draw_coins(self, center_x, center_y, count):
        coin_radius = 8
        spacing = 20
        
        total_width = count * spacing
        start_x = center_x - total_width // 2 + spacing // 2
        
        for i in range(count):
            x = start_x + i * spacing
            arcade.draw_circle_filled(x, center_y, coin_radius, arcade.color.GOLD)
            arcade.draw_circle_outline(x, center_y, coin_radius, arcade.color.DARK_GOLDENROD, 2)
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.game_view)
        elif key == arcade.key.DOWN:
            max_scroll = self.get_max_scroll()
            self.scroll_position = max(self.scroll_position - self.scroll_speed, -max_scroll)
        elif key == arcade.key.UP:
            max_scroll = self.get_max_scroll()
            self.scroll_position = min(self.scroll_position + self.scroll_speed, max_scroll)
    
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.scroll_position += scroll_y * self.scroll_speed
        max_scroll = self.get_max_scroll()
        self.scroll_position = max(-max_scroll, min(self.scroll_position, max_scroll))