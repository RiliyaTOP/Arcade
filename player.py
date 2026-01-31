import arcade


def load_frames(folder, prefix, count):
    return [arcade.load_texture(f"{folder}/{prefix}_{i}.png") for i in range(count)]


class Hero(arcade.Sprite):
    def __init__(self, x, y, scale=1.0):
        super().__init__()

        base = "resources/mainChatacter/frames"

        self.idle_r = load_frames(f"{base}/idle", "idle", 6)
        self.walk_r = load_frames(f"{base}/walk", "walk", 8)
        self.run_r = load_frames(f"{base}/run", "run", 8)
        self.atk_r = load_frames(f"{base}/attack1", "attack", 6)

        self.idle_l = [t.flip_left_right() for t in self.idle_r]
        self.walk_l = [t.flip_left_right() for t in self.walk_r]
        self.run_l = [t.flip_left_right() for t in self.run_r]
        self.atk_l = [t.flip_left_right() for t in self.atk_r]

        self.scale = scale
        self.center_x = x
        self.center_y = y

        self.face_right = True
        self.state = "idle"
        self.frame = 0
        self.t = 0.0

        self.idle_dt = 0.12
        self.walk_dt = 0.10
        self.run_dt = 0.08
        self.atk_dt = 0.07

        self.texture = self.idle_r[0]

    def start_attack(self):
        if self.state == "attack":
            return
        self.state = "attack"
        self.frame = 0
        self.t = 0.0
        self.texture = (self.atk_r if self.face_right else self.atk_l)[0]

    def update_anim(self, dt, dx, dy, speed):
        if dx < 0:
            self.face_right = False
        elif dx > 0:
            self.face_right = True

        moving = abs(dx) + abs(dy) > 0.01

        if self.state == "attack":
            frames = self.atk_r if self.face_right else self.atk_l
            if self.frame >= len(frames):
                self.frame = 0

            self.t += dt
            if self.t >= self.atk_dt:
                self.t = 0.0
                self.frame += 1
                if self.frame >= len(frames):
                    self.state = "move" if moving else "idle"
                    self.frame = 0
                else:
                    self.texture = frames[self.frame]
            else:
                self.texture = frames[self.frame]
            return

        if not moving:
            self.state = "idle"
            frames = self.idle_r if self.face_right else self.idle_l
            if not frames:
                frames = self.walk_r if self.face_right else self.walk_l

            if self.frame >= len(frames):
                self.frame = 0

            self.t += dt
            if self.t >= self.idle_dt:
                self.t = 0.0
                self.frame = (self.frame + 1) % len(frames)

            self.texture = frames[self.frame]
            return

        self.state = "move"
        running = speed >= 8
        frames = (self.run_r if self.face_right else self.run_l) if running else (
            self.walk_r if self.face_right else self.walk_l)
        fdt = self.run_dt if running else self.walk_dt

        if self.frame >= len(frames):
            self.frame = 0

        self.t += dt
        if self.t >= fdt:
            self.t = 0.0
            self.frame = (self.frame + 1) % len(frames)

        self.texture = frames[self.frame]