import random
import pprint

def level(number_level: int) -> list[int]:
    """Создание матрицы уровня"""
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
    cave_col = -2

    matrixLevel[heart_row][1] = heart #Расположение кристала

    a = number_level // 7 + 1 #Примерное колличество cave
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

        if 0 <= row < len(matrixLevel) and mirror_row != row:
            matrixLevel[row][cave_col] = cave
            b = random.randint(1, a) + 1 #Случайное смещение
            rotation.append((row, (width - max(a - i, i - a) * a1 - b)))

        if 0 <= mirror_row < len(matrixLevel) and mirror_row != row:
            matrixLevel[mirror_row][cave_col] = cave
            b = random.randint(1, a) + 1# Случайное смещение
            rotation.append((mirror_row, (width - max(a - i, i - a) * a1 - b)))

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

    return matrixLevel

a = level(7)
for i in a:
    print()
    for j in i:
        print(j, end=' ')