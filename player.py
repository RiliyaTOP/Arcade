import arcade

class Player:
    def __init__(self, tile_size, map_width, map_height):
        self.tile_size = tile_size
        self.map_width = map_width
        self.map_height = map_height
        
        self.textures = []
        self.load_animations()
        
        if self.textures:
            self.sprite = arcade.Sprite()
            self.sprite.scale = 0.5
            self.sprite.texture = self.textures[0]
        else:
            self.sprite = arcade.SpriteSolidColor(
                tile_size // 2,
                tile_size // 2,
                arcade.color.BLUE
            )
            
        self.sprite.center_x = map_width * tile_size // 2
        self.sprite.center_y = map_height * tile_size // 2
        
        self.speed = 300
        self.move_up = False
        self.move_down = False
        self.move_left = False
        self.move_right = False
        
        self.is_moving = False
        self.direction = "down"
        self.animation_timer = 0
        self.animation_speed = 0.15
        self.current_animation_frame = 0

    def load_animations(self):
        try:
            texture_paths = [
                ":resources:images/animated_characters/female_person/femalePerson_idle.png",
                ":resources:images/animated_characters/female_person/femalePerson_walk0.png",
                ":resources:images/animated_characters/female_person/femalePerson_walk1.png",
                ":resources:images/animated_characters/female_person/femalePerson_walk2.png",
                ":resources:images/animated_characters/female_person/femalePerson_walk3.png",
                ":resources:images/animated_characters/female_person/femalePerson_walk4.png",
                ":resources:images/animated_characters/female_person/femalePerson_walk5.png",
                ":resources:images/animated_characters/female_person/femalePerson_walk6.png",
                ":resources:images/animated_characters/female_person/femalePerson_walk7.png",
            ]
            
            for path in texture_paths:
                texture = arcade.load_texture(path)
                self.textures.append(texture)
        except Exception as e:
            try:
                colors = [arcade.color.BLUE, arcade.color.LIGHT_BLUE, arcade.color.BLUE]
                for color in colors:
                    texture = arcade.make_circle_texture(30, color)
                    self.textures.append(texture)
            except:
                pass

    def update_animation(self, delta_time):
        self.animation_timer += delta_time
        
        if self.is_moving:
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                
                if len(self.textures) > 2:
                    self.current_animation_frame = (self.current_animation_frame + 1) % 2
                    texture_index = self.current_animation_frame + 1
                    if texture_index < len(self.textures):
                        self.sprite.texture = self.textures[texture_index]
        else:
            self.current_animation_frame = 0
            if self.textures and len(self.textures) > 0:
                self.sprite.texture = self.textures[0]

    def update_position(self, delta_time, obstacle_sprites):
        dx = 0
        dy = 0
        if self.move_up:
            dy += self.speed * delta_time
            self.direction = "up"
            self.is_moving = True
        if self.move_down:
            dy -= self.speed * delta_time
            self.direction = "down"
            self.is_moving = True
        if self.move_left:
            dx -= self.speed * delta_time
            self.direction = "left"
            self.is_moving = True
        if self.move_right:
            dx += self.speed * delta_time
            self.direction = "right"
            self.is_moving = True
        
        if not (self.move_up or self.move_down or self.move_left or self.move_right):
            self.is_moving = False

        old_x = self.sprite.center_x
        old_y = self.sprite.center_y

        self.sprite.center_x += dx
        self.sprite.center_y += dy

        collisions = arcade.check_for_collision_with_list(self.sprite, obstacle_sprites)
        if collisions:
            self.sprite.center_x = old_x
            self.sprite.center_y = old_y

    def get_position(self):
        return (self.sprite.center_x, self.sprite.center_y)

    def set_position(self, x, y):
        self.sprite.center_x = x
        self.sprite.center_y = y

    def draw(self):
        if hasattr(self.sprite, 'draw'):
            self.sprite.draw()
        else:
            if hasattr(self.sprite, 'texture') and self.sprite.texture:
                arcade.draw_texture_rect(
                    self.sprite.texture,
                    arcade.LBWH(
                        self.sprite.center_x - self.sprite.width / 2,
                        self.sprite.center_y - self.sprite.height / 2,
                        self.sprite.width,
                        self.sprite.height
                    )
                )
            else:
                arcade.draw_rectangle_filled(
                    self.sprite.center_x,
                    self.sprite.center_y,
                    self.sprite.width,
                    self.sprite.height,
                    arcade.color.BLUE
                )