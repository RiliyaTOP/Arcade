# particle_effects.py - Простая система частиц для Arcade 3.3.3
import arcade
import random
import math

class SimpleParticleSystem:
    """Простая система частиц для версий Arcade без поддержки эмиттеров"""
    
    def __init__(self):
        self.particles = []
    
    def create_explosion(self, x, y, color, count=25, speed_min=50, speed_max=150):
        """Создание взрыва частиц"""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(speed_min, speed_max)
            
            self.particles.append({
                'x': x,
                'y': y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'size': random.uniform(3, 8),
                'color': color,
                'lifetime': random.uniform(0.5, 1.5),
                'timer': 0.0,
                'gravity': random.uniform(50, 150)
            })
    
    def create_smoke(self, x, y, color=arcade.color.GRAY, count=10):
        """Создание дыма"""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(10, 40)
            
            self.particles.append({
                'x': x,
                'y': y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed + 20,  # Поднимается
                'size': random.uniform(5, 15),
                'color': color,
                'lifetime': random.uniform(1.0, 2.0),
                'timer': 0.0,
                'fade': True
            })
    
    def create_sparks(self, x, y, count=15):
        """Создание искр"""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(100, 250)
            
            self.particles.append({
                'x': x,
                'y': y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'size': random.uniform(2, 6),
                'color': arcade.color.YELLOW,
                'lifetime': random.uniform(0.3, 0.7),
                'timer': 0.0,
                'gravity': 200
            })
    
    def create_healing_effect(self, x, y, count=15):
        """Эффект лечения"""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(30, 80)
            
            self.particles.append({
                'x': x,
                'y': y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed + 50,  # В основном вверх
                'size': random.uniform(4, 8),
                'color': arcade.color.GREEN,
                'lifetime': random.uniform(0.8, 1.2),
                'timer': 0.0
            })
    
    def update(self, delta_time):
        """Обновление всех частиц"""
        for particle in self.particles[:]:
            particle['timer'] += delta_time
            
            # Удаляем старые частицы
            if particle['timer'] >= particle['lifetime']:
                self.particles.remove(particle)
                continue
            
            # Обновляем позицию
            particle['x'] += particle['dx'] * delta_time
            particle['y'] += particle['dy'] * delta_time
            
            # Применяем гравитацию
            if 'gravity' in particle:
                particle['dy'] -= particle['gravity'] * delta_time
            
            # Замедление
            particle['dx'] *= 0.97
            particle['dy'] *= 0.97
            
            # Уменьшение размера для эффекта исчезновения
            if 'fade' in particle and particle['fade']:
                particle['size'] *= 0.99
    
    def draw(self):
        """Отрисовка всех частиц"""
        for particle in self.particles:
            # Вычисляем прозрачность
            alpha = int(255 * (1 - particle['timer'] / particle['lifetime']))
            
            # Рисуем частицу
            arcade.draw_circle_filled(
                particle['x'], particle['y'],
                particle['size'],
                (particle['color'][0], particle['color'][1], particle['color'][2], alpha)
            )
    
    def clear(self):
        """Очистка всех частиц"""
        self.particles.clear()

# Функции для обратной совместимости
def create_smoke_effect(x, y, color=arcade.color.GRAY):
    """Создание эффекта дыма (для обратной совместимости)"""
    system = SimpleParticleSystem()
    system.create_smoke(x, y, color)
    return system

def create_healing_effect(x, y):
    """Создание эффекта лечения (для обратной совместимости)"""
    system = SimpleParticleSystem()
    system.create_healing_effect(x, y)
    return system