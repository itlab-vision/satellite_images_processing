"""
Image preparation code
"""
import os
import math
from PIL import Image

#input_path = 'LC08_L1TP_169024_20210301_20210311_01_T2_B1.TIF'
#output_path = ''

def image_pre(input_path, output_path):
    """
    Script for image preparation
    """
    data = Image.open(input_path)
    pics = data.load()
    width, height = data.size
    flag = 0
    # Ищем углы изображения для поворота картинки
    for j in range(height):
        for i in range(width):
            if (pics[i, j] != 0):
                angl1 = (i, j)
                flag = 1
                break
        if flag:
            break
    k = 1
    flag = 0
    if angl1[0] < width / 2:
        for i in range(width - 1, -1, -1):
            for j in range(height):
                if (pics[i, j] != 0):
                    angl2 = (i, j)
                    flag = 1
                    break
            if flag:
                break
    else:
        k = -1
        for i in range(width):
            for j in range(height):
                if (pics[i, j] != 0):
                    angl2 = (i, j)
                    flag = 1
                    break
            if flag:
                break
    # Поворот картинки
    data = data.rotate(k * math.degrees(math.atan(abs((angl1[1] - angl2[1])/(angl1[0] - angl2[0])))), expand = True)
    pics = data.load()
    width, height = data.size
    flag = 0
    # Снова ищем углы изображения. На этот раз, чтобы обрезать чёрные полосы
    for j in range(height):
        for i in range(width):
            if ((i == width - 1) or (pics[i + 1, j])) and (pics[i, j + 1]):
                angl1 = (i, j)
                flag = 1
                break
        if flag:
            break
    flag = 0
    for j in range(height - 1, - 1, - 1):
        for i in range(width - 1, -1, -1):
            if ((i == 0) or (pics[i - 1, j])) and (pics[i, j - 1]):
                angl2 = (i, j)
                flag = 1
                break
        if flag:
            break
    # Удаляем чёрные полосы
    data = data.crop((angl1[0], angl1[1], angl2[0], angl2[1]))
    width, height = data.size
    # Режем на куски 300x300
    for i in range(math.ceil(width / 300)):
        for j in range(math.ceil(height / 300)):
            edited = data.crop((300 * i, 300 * j, 300* (i + 1), 300 * (j + 1)))
            edited.save(os.path.join(output_path, 'edited_' + str(i) + '_' + str(j) + '.TIF'))
    data.close()
