import arcade
from arcade import PhysicsEngineSimple
import random
import math

class Enemy:
    def __init__(self, x: float, y: float, hp: int, speed: float, coin: int):
        self.x = x
        self.y = y
        self.maxhp = hp
        self.hp = hp
        self.speed = speed
        self.coin = coin
        self.sprite = None
        self.has_reached_fortress = False
        self.is_moving = True
        self.stop_distance = 0  # Дистанция остановки
        
        # Физический движок
        self.physics_engine = None
        
        # Атрибуты для атаки предметов
        self.current_target_item = None
        self.attack_timer = 0
        self.attack_threshold = 5.0  # Время для уничтожения предмета (секунд)
        
        # Для предотвращения залипания
        self.stuck_timer = 0
        self.last_position = (x, y)
        self.stuck_threshold = 2.0  # 2 секунды
        
        # Для анимации атаки
        self.is_attacking = False
        self.attack_animation_timer = 0
        self.original_texture = None

    def init_physics_engine(self, obstacle_sprites):
        """Инициализация физического движка"""
        if self.sprite:
            self.physics_engine = PhysicsEngineSimple(
                self.sprite,
                obstacle_sprites
            )

    def move_towards(self, target_x, target_y, delta_time, obstacle_sprites):
        """Движение к цели с использованием физики"""
        if not self.is_moving or self.has_reached_fortress or self.is_attacking:
            return
        
        if self.sprite:
            # Проверяем, не застрял ли враг
            current_pos = (self.sprite.center_x, self.sprite.center_y)
            if abs(current_pos[0] - self.last_position[0]) < 1 and abs(current_pos[1] - self.last_position[1]) < 1:
                self.stuck_timer += delta_time
            else:
                self.stuck_timer = 0
                self.last_position = current_pos
            
            # Если враг застрял, пытаемся обойти
            if self.stuck_timer > self.stuck_threshold:
                self.try_avoid_stuck(target_x, target_y, delta_time)
                return
            
            # Вычисляем направление
            dx = target_x - self.sprite.center_x
            dy = target_y - self.sprite.center_y
            
            # Нормализуем
            distance = (dx**2 + dy**2)**0.5
            if distance > 0:
                # Уменьшаем скорость при приближении к цели
                speed_multiplier = 1.0
                if distance < 100:  # Если близко к цели
                    speed_multiplier = distance / 100
                
                dx = dx / distance * self.speed * delta_time * 60 * speed_multiplier
                dy = dy / distance * self.speed * delta_time * 60 * speed_multiplier
                
                # Сохраняем старую позицию
                old_x = self.sprite.center_x
                old_y = self.sprite.center_y
                
                # Пытаемся двигаться
                self.sprite.center_x += dx
                self.sprite.center_y += dy
                
                # Обновляем физический движок
                if self.physics_engine:
                    self.physics_engine.update()
                
                # Проверяем, двигается ли враг
                if abs(self.sprite.center_x - old_x) < 0.1 and abs(self.sprite.center_y - old_y) < 0.1:
                    # Враг не двигается, возможно, столкнулся
                    self.try_avoid_stuck(target_x, target_y, delta_time)

    def try_avoid_stuck(self, target_x, target_y, delta_time):
        """Попытка обойти препятствие"""
        # Случайное небольшое смещение
        random_angle = random.uniform(0, 3.14159 * 2)
        avoid_distance = 50 * delta_time * 60
        
        self.sprite.center_x += avoid_distance * random.uniform(0.5, 1.5) * self.speed * delta_time * 60
        self.sprite.center_y += avoid_distance * random.uniform(0.5, 1.5) * self.speed * delta_time * 60
        
        # Обновляем физический движок
        if self.physics_engine:
            self.physics_engine.update()
        
        self.stuck_timer = 0

    def damage(self, damage: int):
        """Нанесение урона врагу"""
        self.hp -= damage

    def set_coords(self, a: list):
        """Установка координат врага"""
        self.x = a[0]
        self.y = a[1]
        if self.sprite:
            # Предполагаем, что размер тайла 64
            tile_size = 64
            self.sprite.center_x = self.x * tile_size + tile_size // 2
            self.sprite.center_y = self.y * tile_size + tile_size // 2

    def get_coords(self):
        """Получение координат врага"""
        return [self.x, self.y]

    def get_speed(self):
        """Получение скорости врага"""
        return self.speed

    def set_reached_fortress(self, reached: bool):
        """Установка флага достижения крепости"""
        self.has_reached_fortress = reached
        if reached:
            self.is_moving = False
            if self.physics_engine:
                # Останавливаем врага
                self.sprite.change_x = 0
                self.sprite.change_y = 0

    def set_stop_distance(self, distance: float):
        """Установка дистанции остановки"""
        self.stop_distance = distance
    
    def get_sprite(self):
        """Получение спрайта врага"""
        return self.sprite
    
    # Методы для атаки предметов
    def set_current_target(self, item_sprite):
        """Установка текущей цели для атаки"""
        self.current_target_item = item_sprite
        self.attack_timer = 0
        self.is_attacking = True
        # Сохраняем оригинальную текстуру для анимации
        if self.sprite and hasattr(self.sprite, 'texture'):
            self.original_texture = self.sprite.texture
        
        # Останавливаем врага при атаке
        self.is_moving = False
        if self.sprite:
            self.sprite.change_x = 0
            self.sprite.change_y = 0
    
    def clear_current_target(self):
        """Очистка текущей цели"""
        self.current_target_item = None
        self.attack_timer = 0
        self.is_attacking = False
        # Восстанавливаем оригинальную текстуру
        if self.sprite and self.original_texture:
            self.sprite.texture = self.original_texture
        
        # Возобновляем движение
        self.is_moving = True
    
    def update_attack_timer(self, delta_time):
        """Обновление таймера атаки"""
        if self.current_target_item:
            self.attack_timer += delta_time
            
            # Анимация атаки
            self.attack_animation_timer += delta_time
            if self.attack_animation_timer > 0.2:  # Мерцание каждые 0.2 секунды
                self.attack_animation_timer = 0
                if hasattr(self.sprite, 'color'):
                    # Меняем цвет для эффекта атаки
                    import random
                    self.sprite.color = (random.randint(200, 255), random.randint(0, 100), random.randint(0, 100))
            
            return self.attack_timer >= self.attack_threshold
        return False