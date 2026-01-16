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
        self.fortress_sprites = arcade.SpriteList()
        self.obstacle_sprites = arcade.SpriteList()

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

        self.show_inventory = False
        
        self.inventory_items = []
        self.inventory_slots_count = 20
        self.inventory_slot_size = 60
        self.inventory_slot_spacing = 10
        self.inventory_width = 5
        self.inventory_height = 4
        
        self.quick_slots_count = 6
        self.quick_slots = [None] * (self.quick_slots_count - 1)
        self.slot_size = 50
        self.slot_spacing = 10

        self.balance = 100

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

        try:
            self.fortress_image = arcade.load_texture("media/крепость.png")
            self.fortress_loaded = True
        except FileNotFoundError:
            self.fortress_loaded = False

        self.shop_button_width = 150
        self.shop_button_height = 60
        self.shop_button_padding = 20

        self.player_position_x = 0
        self.player_position_y = 0

        self.tile_sprites = arcade.SpriteList()

        self.generate_sprites()
        self.create_fortress()
        
        self.last_click_time = 0
        self.double_click_delay = 0.3
        self.last_clicked_slot = None

    def create_fortress(self):
        if self.fortress_loaded:
            fortress_x, fortress_y = None, None
            for x in range(self.map_width):
                for y in range(self.map_height):
                    if self.level[x][y] == 3:
                        fortress_x = x
                        fortress_y = y
                        break
                if fortress_x is not None:
                    break
            
            if fortress_x is not None:
                tile_center_x = fortress_x * self.tile_size + self.tile_size // 2
                tile_center_y = fortress_y * self.tile_size + self.tile_size // 2
                
                fortress_sprite = arcade.Sprite(
                    "media/крепость.png",
                    scale=1.0
                )
                
                fortress_sprite.center_x = tile_center_x
                fortress_sprite.center_y = tile_center_y
                
                self.fortress_sprites.append(fortress_sprite)
                self.obstacle_sprites.append(fortress_sprite)
            else:
                fortress_x = self.map_width - 1
                fortress_y = 0
                tile_center_x = fortress_x * self.tile_size + self.tile_size // 2
                tile_center_y = fortress_y * self.tile_size + self.tile_size // 2
                
                fortress_sprite = arcade.Sprite(
                    "media/крепость.png",
                    scale=1.0
                )
                fortress_sprite.center_x = tile_center_x
                fortress_sprite.center_y = tile_center_y
                self.fortress_sprites.append(fortress_sprite)
                self.obstacle_sprites.append(fortress_sprite)

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

        total_width = self.quick_slots_count * self.slot_size + (self.quick_slots_count - 1) * self.slot_spacing
        first_x = (screen_width - total_width) // 2

        slots = []
        for i in range(self.quick_slots_count):
            slot_x = first_x + i * (self.slot_size + self.slot_spacing)
            slot_left = slot_x
            slot_right = slot_x + self.slot_size
            slot_bottom = 20
            slot_top = 20 + self.slot_size
            slots.append((slot_left, slot_right, slot_bottom, slot_top, i))

        return slots
    
    def get_inventory_area(self):
        screen_width = self.window.width
        screen_height = self.window.height
        
        inv_width = screen_width * 0.7
        inv_height = screen_height * 0.7
        
        inv_left = (screen_width - inv_width) // 2
        inv_right = inv_left + inv_width
        inv_bottom = (screen_height - inv_height) // 2
        inv_top = inv_bottom + inv_height
        
        return inv_left, inv_right, inv_bottom, inv_top
    
    def get_inventory_slots(self):
        inv_left, inv_right, inv_bottom, inv_top = self.get_inventory_area()
        
        padding = 20
        
        slots_left = inv_left + padding
        slots_right = inv_right - padding
        slots_bottom = inv_bottom + padding + 40
        slots_top = inv_top - padding
        
        available_width = slots_right - slots_left
        available_height = slots_top - slots_bottom
        
        columns = self.inventory_width
        rows = self.inventory_height
        
        slot_width = min(self.inventory_slot_size, (available_width - (columns - 1) * self.inventory_slot_spacing) // columns)
        slot_height = min(self.inventory_slot_size, (available_height - (rows - 1) * self.inventory_slot_spacing) // rows)
        
        total_grid_width = columns * slot_width + (columns - 1) * self.inventory_slot_spacing
        total_grid_height = rows * slot_height + (rows - 1) * self.inventory_slot_spacing
        
        grid_start_x = slots_left + (available_width - total_grid_width) // 2
        grid_start_y = slots_bottom + (available_height - total_grid_height) // 2
        
        slots = []
        for row in range(rows):
            for col in range(columns):
                slot_index = row * columns + col
                if slot_index >= self.inventory_slots_count:
                    break
                    
                slot_x = grid_start_x + col * (slot_width + self.inventory_slot_spacing)
                slot_y = grid_start_y + row * (slot_height + self.inventory_slot_spacing)
                
                slot_left = slot_x
                slot_right = slot_x + slot_width
                slot_bottom = slot_y
                slot_top = slot_y + slot_height
                
                slots.append((slot_left, slot_right, slot_bottom, slot_top, slot_index))
        
        return slots, slot_width, slot_height

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

    def draw_inventory(self):
        inv_left, inv_right, inv_bottom, inv_top = self.get_inventory_area()
        
        arcade.draw_lrbt_rectangle_filled(
            inv_left, inv_right, inv_bottom, inv_top,
            arcade.color.WHITE
        )
        
        title_x = (inv_left + inv_right) // 2
        title_y = inv_top - 25
        arcade.draw_text(
            "ИНВЕНТАРЬ", title_x, title_y,
            arcade.color.BLACK, font_size=24,
            anchor_x="center", anchor_y="center",
            bold=True
        )
        
        balance_text = f"Баланс: {self.balance}"
        balance_x = inv_left + 20
        balance_y = inv_top - 25
        arcade.draw_text(
            balance_text, balance_x, balance_y,
            arcade.color.DARK_GREEN, font_size=18,
            anchor_x="left", anchor_y="center"
        )
        
        slots, slot_width, slot_height = self.get_inventory_slots()
        
        for slot_left, slot_right, slot_bottom, slot_top, slot_index in slots:
            arcade.draw_lrbt_rectangle_filled(
                slot_left, slot_right, slot_bottom, slot_top,
                arcade.color.LIGHT_GRAY
            )
            arcade.draw_lrbt_rectangle_outline(
                slot_left, slot_right, slot_bottom, slot_top,
                arcade.color.DARK_GRAY, 2
            )
            
            slot_center_x = (slot_left + slot_right) // 2
            slot_center_y = (slot_bottom + slot_top) // 2
            
            if slot_index < len(self.inventory_items):
                item = self.inventory_items[slot_index]
                
                if item['name'].startswith('Камни'):
                    color = (169, 169, 169)
                elif item['name'].startswith('Банан'):
                    color = arcade.color.YELLOW
                elif item['name'].startswith('Костер'):
                    color = arcade.color.ORANGE_RED
                else:
                    color = arcade.color.BLUE
                
                item_width = slot_width * 0.8
                item_height = slot_height * 0.8
                item_left = slot_left + (slot_width - item_width) / 2
                item_bottom = slot_bottom + (slot_height - item_height) / 2
                
                arcade.draw_lrbt_rectangle_filled(
                    item_left, item_left + item_width,
                    item_bottom, item_bottom + item_height,
                    color
                )
                
                name_y = slot_bottom - 15
                arcade.draw_text(
                    item['name'], slot_center_x, name_y,
                    arcade.color.BLACK, font_size=10,
                    anchor_x="center", anchor_y="top"
                )
            else:
                arcade.draw_text(
                    str(slot_index + 1), slot_center_x, slot_center_y,
                    arcade.color.DARK_GRAY, font_size=12,
                    anchor_x="center", anchor_y="center"
                )
        
        close_button_size = 30
        close_button_left = inv_right - close_button_size - 10
        close_button_right = close_button_left + close_button_size
        close_button_bottom = inv_top - close_button_size - 10
        close_button_top = close_button_bottom + close_button_size
        
        arcade.draw_lrbt_rectangle_filled(
            close_button_left, close_button_right, close_button_bottom, close_button_top,
            arcade.color.RED
        )
        arcade.draw_text(
            "X", (close_button_left + close_button_right) // 2, 
            (close_button_bottom + close_button_top) // 2,
            arcade.color.WHITE, font_size=18,
            anchor_x="center", anchor_y="center", bold=True
        )
        
        self.close_button_area = (close_button_left, close_button_right, 
                                 close_button_bottom, close_button_top)

    def add_item_to_inventory(self, item):
        if len(self.inventory_items) < self.inventory_slots_count:
            self.inventory_items.append(item)
            return True
        return False
    
    def add_item_to_quick_slot(self, item, slot_index):
        if 0 <= slot_index < len(self.quick_slots) - 1:
            self.quick_slots[slot_index] = item
            return True
        return False
    
    def remove_item_from_inventory(self, slot_index):
        if 0 <= slot_index < len(self.inventory_items):
            return self.inventory_items.pop(slot_index)
        return None

    def update_balance(self, amount):
        if self.balance + amount >= 0:
            self.balance += amount
            return True
        return False

    def on_draw(self):
        self.clear()
        screen_width = self.window.width
        screen_height = self.window.height
        
        if self.map_loaded:
            arcade.draw_texture_rect(self.map_image, arcade.LBWH(0, 0, screen_width, screen_height))
        else:
            arcade.draw_lrbt_rectangle_filled(0, screen_width, 0, screen_height, arcade.color.DARK_GREEN)
            arcade.draw_text("КАРТА НЕ ЗАГРУЖЕНА", screen_width // 2, screen_height // 2, 
                           arcade.color.WHITE, font_size=20, anchor_x="center", 
                           anchor_y="center", multiline=True, width=400, align="center")

        self.world_camera.use()
        self.tile_sprites.draw()
        self.fortress_sprites.draw()
        self.player_list.draw()

        self.ui_camera.use()

        if self.shop_button_loaded:
            left, right, bottom, top = self.get_shop_button_area()
            arcade.draw_texture_rect(self.shop_button_image, 
                                   arcade.LBWH(left, bottom, self.shop_button_width, 
                                              self.shop_button_height))
        else:
            left, right, bottom, top = self.get_shop_button_area()
            arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, arcade.color.ORANGE)
            arcade.draw_text("МАГАЗИН", (left + right) / 2, (bottom + top) / 2, 
                           arcade.color.BLACK, font_size=14, anchor_x="center", 
                           anchor_y="center", bold=True)

        slots = self.get_slots_area()
        for slot_left, slot_right, slot_bottom, slot_top, slot_index in slots:
            arcade.draw_lrbt_rectangle_outline(slot_left, slot_right, slot_bottom, 
                                             slot_top, arcade.color.WHITE, 2)
            
            if slot_index == self.quick_slots_count - 1:
                arcade.draw_text("+", (slot_left + slot_right) / 2, 
                               (slot_bottom + slot_top) / 2,
                               arcade.color.WHITE, font_size=24, 
                               anchor_x="center", anchor_y="center", bold=True)
            else:
                if self.quick_slots[slot_index] is not None:
                    item = self.quick_slots[slot_index]
                    if item['name'].startswith('Камни'):
                        color = (169, 169, 169)
                    elif item['name'].startswith('Банан'):
                        color = arcade.color.YELLOW
                    elif item['name'].startswith('Костер'):
                        color = arcade.color.ORANGE_RED
                    else:
                        color = arcade.color.BLUE
                    
                    arcade.draw_lrbt_rectangle_filled(
                        slot_left + 5, slot_right - 5,
                        slot_bottom + 5, slot_top - 5,
                        color
                    )
                    
                    arcade.draw_text(
                        str(slot_index + 1), 
                        (slot_left + slot_right) / 2, slot_top + 10,
                        arcade.color.WHITE, font_size=10,
                        anchor_x="center", anchor_y="center"
                    )
                else:
                    arcade.draw_text(
                        str(slot_index + 1), 
                        (slot_left + slot_right) / 2, (slot_bottom + slot_top) / 2,
                        arcade.color.WHITE, font_size=16,
                        anchor_x="center", anchor_y="center"
                    )
        
        if self.show_inventory:
            arcade.draw_lrbt_rectangle_filled(0, screen_width, 0, screen_height,
                                            (0, 0, 0, 180))
            self.draw_inventory()

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

        old_x = self.player_sprite.center_x
        old_y = self.player_sprite.center_y
        
        self.player_sprite.center_x += dx
        self.player_sprite.center_y += dy
        
        collisions = arcade.check_for_collision_with_list(self.player_sprite, self.obstacle_sprites)
        if collisions:
            self.player_sprite.center_x = old_x
            self.player_sprite.center_y = old_y
        
        position = (
            self.player_sprite.center_x,
            self.player_sprite.center_y
        )
        self.world_camera.position = arcade.math.lerp_2d(
            self.world_camera.position,
            position,
            1,
        )
        
        if self.last_click_time > 0:
            self.last_click_time -= delta_time
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            if self.show_inventory:
                self.show_inventory = False
            else:
                self.window.show_view(self.main_menu)
        elif key == arcade.key.F11:
            self.window.set_fullscreen(not self.window.fullscreen)
        elif key == arcade.key.I or key == arcade.key.TAB:
            self.show_inventory = not self.show_inventory
        elif key == arcade.key.UP or key == arcade.key.W:
            self.move_up = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.move_down = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.move_left = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.move_right = True
        elif key == arcade.key.KEY_1:
            self.use_quick_slot_item(0)
        elif key == arcade.key.KEY_2:
            self.use_quick_slot_item(1)
        elif key == arcade.key.KEY_3:
            self.use_quick_slot_item(2)
        elif key == arcade.key.KEY_4:
            self.use_quick_slot_item(3)
        elif key == arcade.key.KEY_5:
            self.use_quick_slot_item(4)

    def use_quick_slot_item(self, slot_index):
        if 0 <= slot_index < len(self.quick_slots) and self.quick_slots[slot_index] is not None:
            item = self.quick_slots[slot_index]
            print(f"Используется предмет из быстрого слота {slot_index + 1}: {item['name']}")

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
        import time
        
        if self.show_inventory:
            if hasattr(self, 'close_button_area'):
                close_left, close_right, close_bottom, close_top = self.close_button_area
                if close_left <= x <= close_right and close_bottom <= y <= close_top:
                    self.show_inventory = False
                    return
            
            slots, _, _ = self.get_inventory_slots()
            for slot_left, slot_right, slot_bottom, slot_top, slot_index in slots:
                if slot_left <= x <= slot_right and slot_bottom <= y <= slot_top:
                    current_time = time.time()
                    
                    if (self.last_clicked_slot == slot_index and 
                        current_time - self.last_click_time < self.double_click_delay):
                        
                        if slot_index < len(self.inventory_items):
                            item = self.inventory_items[slot_index]
                            self.move_item_to_quick_slot(item, slot_index)
                    
                    self.last_click_time = current_time
                    self.last_clicked_slot = slot_index
                    return
            
            inv_left, inv_right, inv_bottom, inv_top = self.get_inventory_area()
            if inv_left <= x <= inv_right and inv_bottom <= y <= inv_top:
                return
        else:
            slots = self.get_slots_area()
            for slot_left, slot_right, slot_bottom, slot_top, slot_index in slots:
                if slot_left <= x <= slot_right and slot_bottom <= y <= slot_top:
                    if slot_index == self.quick_slots_count - 1:
                        self.show_inventory = True
                    else:
                        if self.quick_slots[slot_index] is not None:
                            item = self.quick_slots[slot_index]
                            print(f"Клик по быстрому слоту {slot_index + 1}: {item['name']}")
                    return
        
        left, right, bottom, top = self.get_shop_button_area()
        if left <= x <= right and bottom <= y <= top:
            shop_view = ShopView(self)
            self.window.show_view(shop_view)
            return

    def move_item_to_quick_slot(self, item, inventory_slot_index):
        for i in range(len(self.quick_slots) - 1):
            if self.quick_slots[i] is None:
                self.quick_slots[i] = {
                    'name': item['name'],
                    'production': item['production'],
                    'price': item['price']
                }
                print(f"Предмет '{item['name']}' перемещен в быстрый слот {i + 1}")
                return True
        
        print("Нет свободных быстрых слотов!")
        return False