import random

class Level:
    def __init__(self, number_level: int):
        self.number_level = number_level
        self.matrixLevel = [[0 for _ in range(number_level)] for _ in range(number_level)]
        self.enemyMatrix = [[0 for _ in range(number_level)] for _ in range(number_level)]
        self.caves = []
        self.rotation = []
        self.enemy = []


    def generate_level(self) -> list[int]:
        """Создание матрицы уровня"""
        number_level = self.number_level
        random.seed(number_level) #Сид для генерации одинаковых уровней

        n = random.randint(1, number_level)
        height = number_level // 2 * 2 + 3
        width = n + 10 * (number_level // 7 + 1)

        matrixLevel = [[0 for _ in range(width)] for _ in range(height)] #Создание пустой матрицы

        heart = 3
        cave = 2
        road = 1

        rotation = []  #Список координат поворота для дороги

        heart_row = number_level // 2 + 1
        cave_col = width - 2

        matrixLevel[heart_row][1] = heart #Расположение кристала

        a = number_level // 7 + 1 #Примерное количество cave
        a1 = (width - 4) // (a + 1) #Разбитие поля для создания поворотов

        #Расчёт координат поворота и пещер
        for i in range(number_level // 7 + 1):
            if i * 4 > heart_row:
                break

            row = i * 4
            mirror_row = 2 * heart_row - row

            if row == heart_row or row == mirror_row or mirror_row == heart_row:
                matrixLevel[mirror_row][cave_col] = cave
                rotation.append((mirror_row, width - 3))
                self.caves.append((mirror_row, cave_col))

            if 0 <= row < len(matrixLevel) and mirror_row != row:
                matrixLevel[row][cave_col] = cave
                b = random.randint(1, a) + 1 #Случайное смещение
                rotation.append((row, (width - max(a - i, i - a) * a1 - b)))
                self.caves.append((row, cave_col))

            if 0 <= mirror_row < len(matrixLevel) and mirror_row != row:
                matrixLevel[mirror_row][cave_col] = cave
                b = random.randint(1, a) + 1# Случайное смещение
                rotation.append((mirror_row, (width - max(a - i, i - a) * a1 - b)))
                self.caves.append((mirror_row, cave_col))


        #Проставление дороги
        for i in range(len(rotation)):
            for j in range(rotation[i][1], width - 2):
                matrixLevel[rotation[i][0]][j] = road
            for j in range(min(rotation[i][0], heart_row), max(rotation[i][0], heart_row)):
                matrixLevel[j][rotation[i][1]] = road

        if len(rotation) % 2 == 1:
            num = width - 2
        else:
            num = max(rotation, key=lambda x: x[1])[1] + 1
        for i in range(2, num):
            matrixLevel[heart_row][i] = road

        self.matrixLevel = matrixLevel
        self.rotation = rotation
        return self.matrixLevel

    def spawn_enemy(self, enemies: list):
        self.enemy = enemies
        for e in self.enemy:
            e.set_coords(self.caves[random.randint(0, len(self.caves) - 1)])

    def get_enemy_coords(self):
        coords = []
        for i in self.enemy:
            coords.append(i.get_coords())
        return coords

    def move_enemy(self, delta_time):
        for i in self.enemy:
            x, y = i.get_coords()
            if self.matrixLevel[int(x + 1)][int(y)] == 1:
                i.set_coords((x + delta_time / i.get_speed(), y))
            elif self.matrixLevel[int(x)][int(y + 1)] == 1:
                i.set_coords((x, y + delta_time / i.get_speed()))
            elif self.matrixLevel[int(x)][int(y - 1)] == 1:
                i.set_coords((x, y - delta_time / i.get_speed()))