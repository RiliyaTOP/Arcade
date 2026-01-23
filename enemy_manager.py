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
        """Создать врагов со случайной скоростью"""
        self.enemies.clear()
        self.enemy_sprites.clear()
        
        # Создаем трех врагов со случайной скоростью
        for i in range(self.enemy_count):
            # Случайная скорость от 1.5 до 3.0
            random_speed = random.uniform(1.5, 3.0)
            enemy_obj = Enemy(0, 0, 10, random_speed, 10)
            enemy_obj.set_stop_distance(0)
            self.enemies.append(enemy_obj)
        
        # Спавним врагов в пещерах
        self.game_view.level.spawn_enemy(self.enemies)
        
        # Создаем спрайты для врагов
        self.create_enemy_sprites()
        
    def create_enemy_sprites(self):
        """Создать спрайты для врагов"""
        self.enemy_sprites.clear()
        
        tile_size = self.game_view.tile_size
        
        for e in self.enemies:
            try:
                sprite = arcade.Sprite(
                    "media/рыцарь.png",
                    scale=0.5
                )
            except:
                sprite = arcade.SpriteSolidColor(
                    30, 30, 
                    arcade.color.RED
                )
            
            sprite.center_x = e.x * tile_size + tile_size // 2
            sprite.center_y = e.y * tile_size + tile_size // 2
            
            e.sprite = sprite
            self.enemy_sprites.append(sprite)
            print(f"Создан спрайт врага в координатах: {e.x}, {e.y} -> {sprite.center_x}, {sprite.center_y}, скорость: {e.speed}")
    
    def move_enemies(self, delta_time):
        """Обновить позиции всех врагов"""
        for e in self.enemies:
            if not e.has_reached_fortress:
                self.move_enemy_towards_fortress(e, delta_time)
            
            # Обновить позицию спрайта
            if e.sprite:
                e.sprite.center_x = e.x * self.game_view.tile_size + self.game_view.tile_size // 2
                e.sprite.center_y = e.y * self.game_view.tile_size + self.game_view.tile_size // 2
    
    def move_enemy_towards_fortress(self, enemy_obj, delta_time):
        """Переместить врага к крепости с улучшенной навигацией"""
        if enemy_obj.has_reached_fortress or not enemy_obj.is_moving:
            return
        
        enemy_x, enemy_y = enemy_obj.get_coords()
        
        if not self.game_view.fortress_coords:
            return
            
        fortress_x, fortress_y = self.game_view.fortress_coords
        
        # Проверяем, достиг ли враг соседней клетки с крепостью
        distance_to_fortress = abs(enemy_x - fortress_x) + abs(enemy_y - fortress_y)
        if distance_to_fortress <= 1.0:
            enemy_obj.set_reached_fortress(True)
            print(f"Враг достиг крепости!")
            return
        
        # Получаем координаты персонажа
        player_tile_x = int(self.game_view.player.sprite.center_x // self.game_view.tile_size)
        player_tile_y = int(self.game_view.player.sprite.center_y // self.game_view.tile_size)
        
        move_distance = delta_time / enemy_obj.get_speed() * 3.0
        
        current_cell_type = self.game_view.map_level[int(enemy_x)][int(enemy_y)]
        
        # Если враг на дороге или крепости
        if current_cell_type in [1, 3]:
            dx, dy = self.get_direction_to_fortress(enemy_x, enemy_y, fortress_x, fortress_y, move_distance)
        else:
            # Враг в пещере - ищем ближайшую дорогу
            dx, dy = self.get_direction_to_road(enemy_x, enemy_y, move_distance)
        
        if dx == 0 and dy == 0:
            return
        
        new_x = enemy_x + dx
        new_y = enemy_y + dy
        
        new_tile_x = int(new_x)
        new_tile_y = int(new_y)
        
        # Проверяем, не идем ли мы на клетку персонажа
        if new_tile_x == player_tile_x and new_tile_y == player_tile_y:
            print("Враг пытается перейти на клетку персонажа! Ищем альтернативный путь.")
            self.try_avoid_player(enemy_obj, delta_time, player_tile_x, player_tile_y)
            return
        
        # Проверяем границы карты
        if not (0 <= new_tile_x < self.game_view.map_width and 0 <= new_tile_y < self.game_view.map_height):
            return
        
        # Проверяем тип клетки - враги могут ходить по дорогам (1), пещерам (2), но НЕ по крепости (3)
        new_cell_type = self.game_view.map_level[new_tile_x][new_tile_y]
        
        # Разрешаем движение только по дорогам и пещерам, но не по крепости
        if new_cell_type not in [1, 2]:
            print(f"Враг пытается выйти на недопустимую клетку ({new_tile_x}, {new_tile_y}) типа {new_cell_type}")
            # Пытаемся найти обходной путь
            self.try_alternative_path(enemy_obj, delta_time, new_tile_x, new_tile_y)
            return
        
        # Проверяем столкновение со спрайтами
        if enemy_obj.sprite:
            old_x = enemy_obj.sprite.center_x
            old_y = enemy_obj.sprite.center_y
            
            enemy_obj.sprite.center_x = new_x * self.game_view.tile_size + self.game_view.tile_size // 2
            enemy_obj.sprite.center_y = new_y * self.game_view.tile_size + self.game_view.tile_size // 2
            
            # Проверяем столкновение с размещенными предметами
            if self.game_view.placed_items_sprites:
                collisions = arcade.check_for_collision_with_list(enemy_obj.sprite, self.game_view.placed_items_sprites)
                if collisions:
                    enemy_obj.sprite.center_x = old_x
                    enemy_obj.sprite.center_y = old_y
                    self.try_avoid_obstacle(enemy_obj, delta_time, new_tile_x, new_tile_y)
                    return
            
            # Проверяем столкновение с персонажем
            if arcade.check_for_collision(enemy_obj.sprite, self.game_view.player.sprite):
                enemy_obj.sprite.center_x = old_x
                enemy_obj.sprite.center_y = old_y
                self.try_avoid_player(enemy_obj, delta_time, player_tile_x, player_tile_y)
                return
            
            enemy_obj.set_coords([new_x, new_y])
        else:
            enemy_obj.set_coords([new_x, new_y])
    
    def get_direction_to_fortress(self, enemy_x, enemy_y, fortress_x, fortress_y, move_distance):
        """Получить направление движения к крепости"""
        dx = 0
        dy = 0
        
        # Сначала двигаемся по горизонтали
        if abs(enemy_x - fortress_x) > 0.1:
            if enemy_x < fortress_x:
                dx = min(move_distance, fortress_x - enemy_x)
            else:
                dx = max(-move_distance, fortress_x - enemy_x)
        # Затем по вертикали
        elif abs(enemy_y - fortress_y) > 0.1:
            if enemy_y < fortress_y:
                dy = min(move_distance, fortress_y - enemy_y)
            else:
                dy = max(-move_distance, fortress_y - enemy_y)
        
        return dx, dy
    
    def get_direction_to_road(self, enemy_x, enemy_y, move_distance):
        """Получить направление движения к ближайшей дороге"""
        # Ищем ближайшую дорогу
        closest_road = None
        min_distance = float('inf')
        
        for x in range(self.game_view.map_width):
            for y in range(self.game_view.map_height):
                cell_type = self.game_view.map_level[x][y]
                if cell_type == 1:  # Только дорога
                    distance = math.sqrt((x - enemy_x)**2 + (y - enemy_y)**2)
                    if distance < min_distance:
                        min_distance = distance
                        closest_road = (x, y)
        
        if not closest_road:
            return 0, 0
        
        road_x, road_y = closest_road
        
        dx = 0
        dy = 0
        
        # Сначала двигаемся по горизонтали
        if abs(enemy_x - road_x) > 0.1:
            if enemy_x < road_x:
                dx = min(move_distance, road_x - enemy_x)
            else:
                dx = max(-move_distance, road_x - enemy_x)
        # Затем по вертикали
        elif abs(enemy_y - road_y) > 0.1:
            if enemy_y < road_y:
                dy = min(move_distance, road_y - enemy_y)
            else:
                dy = max(-move_distance, road_y - enemy_y)
        
        return dx, dy
    
    def try_avoid_player(self, enemy_obj, delta_time, player_x, player_y):
        """Попытаться обойти игрока"""
        enemy_x, enemy_y = enemy_obj.get_coords()
        move_distance = delta_time / enemy_obj.get_speed() * 2.0
        
        # Пробуем разные направления
        directions = [
            (move_distance, 0),
            (-move_distance, 0),
            (0, move_distance),
            (0, -move_distance),
        ]
        
        for dx, dy in directions:
            new_x = enemy_x + dx
            new_y = enemy_y + dy
            new_tile_x = int(new_x)
            new_tile_y = int(new_y)
            
            if new_tile_x == player_x and new_tile_y == player_y:
                continue
            
            if (0 <= new_tile_x < self.game_view.map_width and 
                0 <= new_tile_y < self.game_view.map_height):
                cell_type = self.game_view.map_level[new_tile_x][new_tile_y]
                if cell_type in [1, 2]:  # Дорога или пещера
                    enemy_obj.set_coords([new_x, new_y])
                    if enemy_obj.sprite:
                        enemy_obj.sprite.center_x = new_x * self.game_view.tile_size + self.game_view.tile_size // 2
                        enemy_obj.sprite.center_y = new_y * self.game_view.tile_size + self.game_view.tile_size // 2
                    return
    
    def try_avoid_obstacle(self, enemy_obj, delta_time, obstacle_x, obstacle_y):
        """Попытаться обойти препятствие"""
        enemy_x, enemy_y = enemy_obj.get_coords()
        move_distance = delta_time / enemy_obj.get_speed() * 2.0
        
        directions = [
            (move_distance, 0),
            (-move_distance, 0),
            (0, move_distance),
            (0, -move_distance),
        ]
        
        for dx, dy in directions:
            new_x = enemy_x + dx
            new_y = enemy_y + dy
            new_tile_x = int(new_x)
            new_tile_y = int(new_y)
            
            if new_tile_x == obstacle_x and new_tile_y == obstacle_y:
                continue
            
            if (0 <= new_tile_x < self.game_view.map_width and 
                0 <= new_tile_y < self.game_view.map_height):
                cell_type = self.game_view.map_level[new_tile_x][new_tile_y]
                if cell_type in [1, 2]:
                    enemy_obj.set_coords([new_x, new_y])
                    if enemy_obj.sprite:
                        enemy_obj.sprite.center_x = new_x * self.game_view.tile_size + self.game_view.tile_size // 2
                        enemy_obj.sprite.center_y = new_y * self.game_view.tile_size + self.game_view.tile_size // 2
                    return
    
    def try_alternative_path(self, enemy_obj, delta_time, blocked_x, blocked_y):
        """Попытаться найти альтернативный путь"""
        if not self.game_view.fortress_coords:
            return
        
        fortress_x, fortress_y = self.game_view.fortress_coords
        enemy_x, enemy_y = enemy_obj.get_coords()
        move_distance = delta_time / enemy_obj.get_speed() * 2.0
        
        # Пробуем все направления
        directions = [
            (move_distance, 0),
            (-move_distance, 0),
            (0, move_distance),
            (0, -move_distance),
        ]
        
        best_direction = None
        best_distance = float('inf')
        
        for dx, dy in directions:
            new_x = enemy_x + dx
            new_y = enemy_y + dy
            new_tile_x = int(new_x)
            new_tile_y = int(new_y)
            
            if (0 <= new_tile_x < self.game_view.map_width and 
                0 <= new_tile_y < self.game_view.map_height):
                cell_type = self.game_view.map_level[new_tile_x][new_tile_y]
                if cell_type in [1, 2]:
                    # Вычисляем расстояние до крепости
                    distance = abs(new_x - fortress_x) + abs(new_y - fortress_y)
                    if distance < best_distance:
                        best_distance = distance
                        best_direction = (dx, dy)
        
        if best_direction:
            dx, dy = best_direction
            new_x = enemy_x + dx
            new_y = enemy_y + dy
            enemy_obj.set_coords([new_x, new_y])
            if enemy_obj.sprite:
                enemy_obj.sprite.center_x = new_x * self.game_view.tile_size + self.game_view.tile_size // 2
                enemy_obj.sprite.center_y = new_y * self.game_view.tile_size + self.game_view.tile_size // 2
    
    def draw(self):
        """Отрисовать всех врагов"""
        self.enemy_sprites.draw()
    
    def get_enemy_sprites(self):
        """Получить спрайты врагов"""
        return self.enemy_sprites
    
    def get_enemies(self):
        """Получить список объектов врагов"""
        return self.enemies