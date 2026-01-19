class Enemy:
    def __init__(self, x: float, y: float,hp: int, speed: float, coin: int):
        self.x = x
        self.y = y
        self.maxhp = hp
        self.hp = hp
        self.speed = speed #Во сколько раз медленнее персонажа
        self.coin = coin
        self.sprite = None

    def move(self, time: int):
        pass

    def damage(self, damage: int):
        self.hp -= damage

    def set_coords(self, a: list):
        self.x = a[0]
        self.y = a[1]

    def get_coords(self):
        return [self.x, self.y]

    def get_speed(self):
        return self.speed