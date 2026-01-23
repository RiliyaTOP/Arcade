import arcade
from shop_view import ShopView
import generate_level
from arcade.camera import Camera2D
import enemy
import os
import time
from enemy_manager import EnemyManager
from player import Player

class GameView(arcade.View):
    def __init__(self, main_menu_view):
        super().__init__()
        number_level = 7
        self.level = generate_level.Level(number_level)
        self.map_level = self.level.generate_level()
        self.main_menu = main_menu_view
        self.map_width = len(self.map_level)
        self.map_height = len(self.map_level[0])
        self.tile_size = 64
        
        self.custom_font = self.load_custom_font()
        
        self.enemy_manager = EnemyManager(self)
        self.enemy_manager.create_enemies()
        
        self.tile_sprites = arcade.SpriteList()
        self.fortress_sprites = arcade.SpriteList()
        self.obstacle_sprites = arcade.SpriteList()
        
        self.placed_items = []
        self.placed_items_sprites = arcade.SpriteList()

        self.world_camera = Camera2D()
        self.ui_camera = Camera2D()
        
        self.player = Player(self.tile_size, self.map_width, self.map_height)
        
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

        self.item_to_place = None
        self.placing_slot_index = None
        self.show_placement_hint = False
        self.placement_hint_timer = 0

        self.item_textures = {}
        self.load_item_textures()

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

        self.fortress_coords = self.find_fortress_coords()
        
        self.add_test_items_to_inventory()
        
        self.add_static_obstacles()
        
        self.enemy_collision_timer = 0
        self.collision_threshold = 5.0
        self.is_colliding_with_enemy = False

    def add_static_obstacles(self):
        for item_sprite in self.placed_items_sprites:
            self.obstacle_sprites.append(item_sprite)
    
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

    def add_test_items_to_inventory(self):
        test_items = [
            {'name': 'Камни', 'production': 1, 'price': 10},
            {'name': 'Банан', 'production': 3, 'price': 25},
            {'name': 'Костер', 'production': 5, 'price': 50},
        ]
        for item in test_items:
            self.add_item_to_inventory(item)

    def load_item_textures(self):
        items = {
            'Камни': 'media/камни.png',
            'Камни 2': 'media/камни.png',
            'Камни 3': 'media/камни.png',
            'Камни 4': 'media/камни.png',
            'Банан': 'media/банан.png',
            'Банан 2': 'media/банан.png',
            'Банан 3': 'media/банан.png',
            'Банан 4': 'media/банан.png',
            'Банан 5': 'media/банан.png',
            'Банан 6': 'media/банан.png',
            'Банан 7': 'media/банан.png',
            'Банан 8': 'media/банан.png',
            'Костер': 'media/костер.png',
            'Костер 2': 'media/костер.png',
            'Костер 3': 'media/костер.png',
            'Костер 4': 'media/костер.png'
        }
        
        for item_name, texture_path in items.items():
            try:
                if os.path.exists(texture_path):
                    self.item_textures[item_name] = arcade.load_texture(texture_path)
                else:
                    self.item_textures[item_name] = None
            except:
                self.item_textures[item_name] = None

    def find_fortress_coords(self):
        for x in range(self.map_width):
            for y in range(self.map_height):
                if self.map_level[x][y] == 3:
                    return (x, y)
        return None

    def create_fortress(self):
        if self.fortress_loaded:
            fortress_x, fortress_y = None, None
            for x in range(self.map_width):
                for y in range(self.map_height):
                    if self.map_level[x][y] == 3:
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

        slot_width = min(self.inventory_slot_size,
                         (available_width - (columns - 1) * self.inventory_slot_spacing) // columns)
        slot_height = min(self.inventory_slot_size,
                          (available_height - (rows - 1) * self.inventory_slot_spacing) // rows)

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
            return (255, 255, 255, 0)
        elif value == 1:
            return (255, 255, 255, 0)
        elif value == 2:
            return (255, 255, 255, 0)
        elif value == 3:
            return (255, 255, 255, 0)
        else:
            return arcade.color.BLACK

    def generate_sprites(self):
        self.tile_sprites.clear()

        for y in range(self.map_height):
            for x in range(self.map_width):
                tile_value = self.map_level[x][y]
                
                if tile_value in [1, 2, 3]:
                    continue
                
                if tile_value == 0:
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
            if self.item_to_place and slot_index == self.placing_slot_index:
                arcade.draw_lrbt_rectangle_filled(
                    slot_left, slot_right, slot_bottom, slot_top,
                    (255, 255, 200, 200)
                )
            else:
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
                
                item_width = slot_width * 0.8
                item_height = slot_height * 0.8
                item_left = slot_left + (slot_width - item_width) / 2
                item_bottom = slot_bottom + (slot_height - item_height) / 2
                
                texture = self.item_textures.get(item['name'])
                if texture:
                    arcade.draw_texture_rect(
                        texture,
                        arcade.LBWH(item_left, item_bottom, item_width, item_height)
                    )
                else:
                    if item['name'].startswith('Камни'):
                        color = (169, 169, 169)
                    elif item['name'].startswith('Банан'):
                        color = arcade.color.YELLOW
                    elif item['name'].startswith('Костер'):
                        color = arcade.color.ORANGE_RED
                    else:
                        color = arcade.color.BLUE
                    
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
            if isinstance(item, dict) and 'name' in item:
                self.inventory_items.append(item)
            else:
                item_dict = {
                    'name': str(item),
                    'production': 0,
                    'price': 0
                }
                self.inventory_items.append(item_dict)
            return True
        return False

    def add_item_to_quick_slot(self, item, slot_index):
        if 0 <= slot_index < len(self.quick_slots):
            self.quick_slots[slot_index] = item
            return True
        return False

    def remove_item_from_inventory(self, slot_index):
        if 0 <= slot_index < len(self.inventory_items):
            removed = self.inventory_items.pop(slot_index)
            return removed
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
        
        self.placed_items_sprites.draw()
        
        self.enemy_manager.draw()
        
        self.player.draw()

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
                if slot_index < len(self.quick_slots) and self.quick_slots[slot_index] is not None:
                    item = self.quick_slots[slot_index]
                    
                    item_width = self.slot_size * 0.8
                    item_height = self.slot_size * 0.8
                    item_left = slot_left + (self.slot_size - item_width) / 2
                    item_bottom = slot_bottom + (self.slot_size - item_height) / 2
                    
                    texture = self.item_textures.get(item['name'])
                    if texture:
                        arcade.draw_texture_rect(
                            texture,
                            arcade.LBWH(item_left, item_bottom, item_width, item_height)
                        )
                    else:
                        if item['name'].startswith('Камни'):
                            color = (169, 169, 169)
                        elif item['name'].startswith('Банан'):
                            color = arcade.color.YELLOW
                        elif item['name'].startswith('Костер'):
                            color = arcade.color.ORANGE_RED
                        else:
                            color = arcade.color.BLUE

                        arcade.draw_lrbt_rectangle_filled(
                            item_left, item_left + item_width,
                            item_bottom, item_bottom + item_height,
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
            
        if self.is_colliding_with_enemy:
            remaining_time = self.collision_threshold - self.enemy_collision_timer
            
            if int(self.enemy_collision_timer * 2) % 2 == 0:
                arcade.draw_text(
                    "ОПАСНОСТЬ!",
                    screen_width // 2, screen_height - 80,
                    arcade.color.RED, font_size=32,
                    anchor_x="center", anchor_y="center",
                    bold=True,
                    font_name=self.custom_font
                )
            
            arcade.draw_text(
                f"Отойдите от врага: {remaining_time:.1f} сек",
                screen_width // 2, screen_height - 120,
                arcade.color.ORANGE, font_size=18,
                anchor_x="center", anchor_y="center",
                bold=True,
                font_name=self.custom_font
            )
            
            bar_width = 300
            bar_height = 20
            bar_x = screen_width // 2 - bar_width // 2
            bar_y = screen_height - 150
            
            arcade.draw_lrbt_rectangle_filled(
                bar_x, bar_x + bar_width,
                bar_y, bar_y + bar_height,
                arcade.color.DARK_RED
            )
            
            fill_width = bar_width * (self.enemy_collision_timer / self.collision_threshold)
            arcade.draw_lrbt_rectangle_filled(
                bar_x, bar_x + fill_width,
                bar_y, bar_y + bar_height,
                arcade.color.RED
            )
            
            arcade.draw_lrbt_rectangle_outline(
                bar_x, bar_x + bar_width,
                bar_y, bar_y + bar_height,
                arcade.color.WHITE, 2
            )

    def select_item_for_placement(self, slot_index):
        if 0 <= slot_index < len(self.quick_slots) and self.quick_slots[slot_index] is not None:
            self.item_to_place = self.quick_slots[slot_index]
            self.placing_slot_index = slot_index
            self.show_placement_hint = False

    def cancel_item_selection(self):
        self.item_to_place = None
        self.placing_slot_index = None

    def place_item_on_map(self, world_x, world_y):
        if not self.item_to_place:
            return False
        
        tile_x = int(world_x // self.tile_size)
        tile_y = int(world_y // self.tile_size)
        
        if not (0 <= tile_x < self.map_width and 0 <= tile_y < self.map_height):
            return False
        
        for enemy_obj in self.enemy_manager.get_enemies():
            enemy_tile_x = int(enemy_obj.x)
            enemy_tile_y = int(enemy_obj.y)
            if enemy_tile_x == tile_x and enemy_tile_y == tile_y:
                return False
        
        for placed_item in self.placed_items:
            if placed_item[0] == tile_x and placed_item[1] == tile_y:
                return False
        
        tile_value = self.map_level[tile_x][tile_y]
        
        if tile_value == 3:
            return False
        elif tile_value == 2:
            return False
        elif tile_value == 0:
            pass
        elif tile_value == 1:
            pass
        
        texture = self.item_textures.get(self.item_to_place['name'])
        sprite = None
        
        if texture:
            sprite = arcade.Sprite()
            sprite.texture = texture
            sprite.scale = 1.0
        else:
            if self.item_to_place['name'].startswith('Камни'):
                color = (169, 169, 169)
            elif self.item_to_place['name'].startswith('Банан'):
                color = arcade.color.YELLOW
            elif self.item_to_place['name'].startswith('Костер'):
                color = arcade.color.ORANGE_RED
            else:
                color = arcade.color.BLUE
            
            sprite = arcade.SpriteSolidColor(
                self.tile_size // 2, 
                self.tile_size // 2, 
                color
            )
        
        if sprite is None:
            return False
        
        sprite.center_x = tile_x * self.tile_size + self.tile_size // 2
        sprite.center_y = tile_y * self.tile_size + self.tile_size // 2
        
        self.placed_items_sprites.append(sprite)
        self.placed_items.append((tile_x, tile_y, self.item_to_place['name'], sprite))
        
        if self.placing_slot_index is not None and 0 <= self.placing_slot_index < len(self.quick_slots):
            self.quick_slots[self.placing_slot_index] = None
        
        self.obstacle_sprites.append(sprite)
        
        self.enemy_manager.recalculate_all_paths()
        
        self.cancel_item_selection()
        
        return True

    def on_update(self, delta_time):
        self.player.update_animation(delta_time)
        self.player.update_position(delta_time, self.obstacle_sprites)
        
        if self.show_placement_hint:
            self.placement_hint_timer -= delta_time
            if self.placement_hint_timer <= 0:
                self.show_placement_hint = False
        
        self.enemy_manager.move_enemies(delta_time)

        position = self.player.get_position()
        self.world_camera.position = arcade.math.lerp_2d(
            self.world_camera.position,
            position,
            1,
        )

        if self.last_click_time > 0:
            self.last_click_time -= delta_time
        
        self.check_enemy_collision(delta_time)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            if self.item_to_place:
                self.cancel_item_selection()
            elif self.show_inventory:
                self.show_inventory = False
            else:
                self.window.show_view(self.main_menu)
        elif key == arcade.key.F11:
            self.window.set_fullscreen(not self.window.fullscreen)
        elif key == arcade.key.I or key == arcade.key.TAB:
            if self.item_to_place:
                self.cancel_item_selection()
            self.show_inventory = not self.show_inventory
        elif key == arcade.key.UP or key == arcade.key.W:
            self.player.move_up = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player.move_down = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player.move_left = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player.move_right = True
        elif key == arcade.key.KEY_1:
            self.select_item_for_placement(0)
        elif key == arcade.key.KEY_2:
            self.select_item_for_placement(1)
        elif key == arcade.key.KEY_3:
            self.select_item_for_placement(2)
        elif key == arcade.key.KEY_4:
            self.select_item_for_placement(3)
        elif key == arcade.key.KEY_5:
            self.select_item_for_placement(4)

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.W, arcade.key.UP):
            self.player.move_up = False
        elif key in (arcade.key.S, arcade.key.DOWN):
            self.player.move_down = False
        elif key in (arcade.key.A, arcade.key.LEFT):
            self.player.move_left = False
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.player.move_right = False

    def on_mouse_press(self, x, y, button, modifiers):
        import time

        if self.item_to_place and button == arcade.MOUSE_BUTTON_LEFT and not self.show_inventory:
            try:
                world_x, world_y = self.world_camera.mouse_to_world(x, y)
                self.place_item_on_map(world_x, world_y)
            except Exception as e:
                camera_x, camera_y = self.world_camera.position
                screen_width = self.window.width
                screen_height = self.window.height
                
                world_x = (x - screen_width / 2) + camera_x
                world_y = (y - screen_height / 2) + camera_y
                
                self.place_item_on_map(world_x, world_y)
            return
        
        if self.item_to_place and button == arcade.MOUSE_BUTTON_RIGHT:
            self.cancel_item_selection()
            return

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
                            moved = self.move_item_to_quick_slot(item, slot_index)
                            if moved:
                                self.show_placement_hint = True
                                self.placement_hint_timer = 3.0

                    else:
                        pass

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
                        if slot_index < len(self.quick_slots) and self.quick_slots[slot_index] is not None:
                            self.select_item_for_placement(slot_index)
                        else:
                            self.show_placement_hint = True
                            self.placement_hint_timer = 3.0
                    return

        left, right, bottom, top = self.get_shop_button_area()
        if left <= x <= right and bottom <= y <= top:
            shop_view = ShopView(self)
            self.window.show_view(shop_view)
            return

    def move_item_to_quick_slot(self, item, inventory_slot_index):
        for i in range(len(self.quick_slots)):
            if self.quick_slots[i] is None:
                self.quick_slots[i] = {
                    'name': item['name'],
                    'production': item['production'],
                    'price': item['price']
                }
                if 0 <= inventory_slot_index < len(self.inventory_items):
                    self.inventory_items.pop(inventory_slot_index)
                    return True
        return False
    
    def check_enemy_collision(self, delta_time):
        collision_detected = False
        
        for enemy_obj in self.enemy_manager.get_enemies():
            if enemy_obj.sprite and arcade.check_for_collision(self.player.sprite, enemy_obj.sprite):
                collision_detected = True
                break
        
        if collision_detected:
            if not self.is_colliding_with_enemy:
                self.is_colliding_with_enemy = True
                self.enemy_collision_timer = 0
            else:
                self.enemy_collision_timer += delta_time
                
                if self.enemy_collision_timer >= self.collision_threshold:
                    self.game_over()
        else:
            self.is_colliding_with_enemy = False
            self.enemy_collision_timer = 0
    
    def game_over(self):
        from game_over_view import GameOverView
        game_over_view = GameOverView(self.main_menu)
        self.window.show_view(game_over_view)