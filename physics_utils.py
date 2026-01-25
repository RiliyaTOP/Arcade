import pymunk
import math

def create_physics_box(space, x, y, width, height, mass=1, body_type=pymunk.Body.DYNAMIC):
    """Создание физического прямоугольника"""
    moment = pymunk.moment_for_box(mass, (width, height))
    body = pymunk.Body(mass, moment, body_type=body_type)
    body.position = pymunk.Vec2d(x, y)
    
    shape = pymunk.Poly.create_box(body, (width, height))
    shape.elasticity = 0.3
    shape.friction = 0.5
    
    space.add(body, shape)
    return body, shape

def create_physics_circle(space, x, y, radius, mass=1, body_type=pymunk.Body.DYNAMIC):
    """Создание физического круга"""
    moment = pymunk.moment_for_circle(mass, 0, radius)
    body = pymunk.Body(mass, moment, body_type=body_type)
    body.position = pymunk.Vec2d(x, y)
    
    shape = pymunk.Circle(body, radius)
    shape.elasticity = 0.3
    shape.friction = 0.5
    
    space.add(body, shape)
    return body, shape

def sync_sprite_with_physics(sprite, physics_body):
    """Синхронизация спрайта с физическим телом"""
    sprite.center_x = physics_body.position.x
    sprite.center_y = physics_body.position.y
    sprite.angle = math.degrees(physics_body.angle)