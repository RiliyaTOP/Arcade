import arcade
import random
from enemy import Enemy
import math

class EnemyManager:
    def __init__(self, game_view):
        self.game_view = game_view
        self.enemies = []
        self.enemy_sprites = arcade.SpriteList()
        self.enemy_count = 3
        
    def create_enemies(self):
        self.enemies.clear()
        self.enemy_sprites.clear()
        for i in range(self.enemy_count):
            random_speed = random.uniform(1.5, 3.0)
            enemy_obj = Enemy(0, 0, 10, random_speed, 10)
            enemy_obj.stop_distance = 0
            self.enemies.append(enemy_obj)
        self.game_view.level.spawn_enemy(self.enemies)
        self.create_enemy_sprites()
        for enemy in self.enemies:
            self.find_initial_path(enemy)
        
    def create_enemy_sprites(self):
        self.enemy_sprites.clear()
        tile_size = self.game_view.tile_size
        for e in self.enemies:
            try:
                sprite = arcade.Sprite("media/рыцарь.png", scale=0.5)
            except:
                sprite = arcade.SpriteSolidColor(30, 30, arcade.color.RED)
            sprite.center_x = e.x * tile_size + tile_size // 2
            sprite.center_y = e.y * tile_size + tile_size // 2
            e.sprite = sprite
            self.enemy_sprites.append(sprite)
    
    def find_initial_path(self, enemy_obj):
        enemy_x, enemy_y = enemy_obj.get_coords()
        if self.game_view.map_level[int(enemy_x)][int(enemy_y)] == 1:
            return
        closest_road = None
        min_distance = float('inf')
        for x in range(self.game_view.map_width):
            for y in range(self.game_view.map_height):
                cell_type = self.game_view.map_level[x][y]
                if cell_type in [1, 3]:
                    distance = abs(x - enemy_x) + abs(y - enemy_y)
                    if distance < min_distance:
                        min_distance = distance
                        closest_road = (x, y)
    
    def move_enemies(self, delta_time):
        for e in self.enemies:
            if not e.has_reached_fortress and e.is_moving:
                self.move_enemy_towards_fortress(e, delta_time)
            if e.sprite:
                e.x = e.sprite.center_x / self.game_view.tile_size
                e.y = e.sprite.center_y / self.game_view.tile_size
    
    def move_enemy_towards_fortress(self, enemy_obj, delta_time):
        if enemy_obj.has_reached_fortress or not enemy_obj.is_moving:
            return
        if self.game_view.fortress_coords:
            fortress_x, fortress_y = self.game_view.fortress_coords
            fortress_pixel_x = fortress_x * self.game_view.tile_size + self.game_view.tile_size // 2
            fortress_pixel_y = fortress_y * self.game_view.tile_size + self.game_view.tile_size // 2
            if enemy_obj.sprite:
                distance_to_fortress = math.sqrt((enemy_obj.sprite.center_x - fortress_pixel_x)**2 + (enemy_obj.sprite.center_y - fortress_pixel_y)**2)
                if distance_to_fortress <= 30:
                    enemy_obj.set_reached_fortress(True)
                    return
                enemy_obj.move_towards(fortress_pixel_x, fortress_pixel_y, delta_time, self.game_view.obstacle_sprites)
    
    def draw(self):
        self.enemy_sprites.draw()
    
    def get_enemy_sprites(self):
        return self.enemy_sprites
    
    def get_enemies(self):
        return self.enemies
    
    def recalculate_all_paths(self):
        pass