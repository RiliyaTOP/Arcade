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
        
        self.speed = 200  
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
                # Альтернативные текстуры если основные не загрузились
                colors = [arcade.color.BLUE, arcade.color.LIGHT_BLUE, arcade.color.BLUE]
                for color in colors:
                    texture = arcade.make_circle_texture(30, color)
                    self.textures.append(texture)
            except:
                pass

    def update_animation(self, delta_time):
        """Обновление анимации игрока"""
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

    def update_position(self, delta_time):
        speed = self.speed * delta_time
        
        self.is_moving = (self.move_up or self.move_down or self.move_left or self.move_right)
        
        if self.move_up:
            self.direction = "up"
        elif self.move_down:
            self.direction = "down"
        elif self.move_left:
            self.direction = "left"
        elif self.move_right:
            self.direction = "right"
        
        if self.is_moving:
            if (self.move_up or self.move_down) and (self.move_left or self.move_right):
                speed = speed * 0.7071  
            
            if self.move_up:
                self.sprite.change_y = speed
            elif self.move_down:
                self.sprite.change_y = -speed
            else:
                self.sprite.change_y = 0
                
            if self.move_left:
                self.sprite.change_x = -speed
            elif self.move_right:
                self.sprite.change_x = speed
            else:
                self.sprite.change_x = 0
        else:
            self.sprite.change_x = 0
            self.sprite.change_y = 0

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

    def get_sprite(self):
        return self.sprite