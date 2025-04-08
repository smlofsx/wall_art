import math

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.backend_bases import MouseButton
import csv

#input_colors = [
        #(255, 0, 0),
        #(0, 255, 0),
        #(0, 0, 255),
        #(128, 128, 128)
    #]
#path='cat.jpg'
#width=512
#height=367

##on_click()

def process_rgb(r1, g1, b1, r2, g2, b2):
    y1 = 0.299 * r1 + 0.587 * g1 + 0.114 * b1
    i1 = 0.569 * r1 + 0.274 * g1 + 0.321 * b1
    q1 = 0.211 * r1 + 0.526 * g1 + 0.311 * b1

    y2 = 0.299 * r2 + 0.587 * g2 + 0.114 * b2
    i2 = 0.569 * r2 + 0.274 * g2 + 0.321 * b2
    q2 = 0.211 * r2 + 0.526 * g2 + 0.311 * b2
    return y1-y2, i1-i2, q1-q2

# Функция для нахождения ближайшего значения из массива results
def find_nearest_value(r1, g1, b1, results):

    minimal_distance = 2000
    index_of_color = 0
    for idx, color in enumerate(results):
        r2, g2, b2 = color
        current = np.linalg.norm(process_rgb(r2, g2, b2, r1, g1, b1))
        if minimal_distance > current:
            minimal_distance = current
            index_of_color = idx

    return results[index_of_color]

def get_index_by_value(arr, value):
    # Возвращает индекс первого вхождения value в массиве arr
    indices = np.where(arr == value)[0]  # np.where возвращает кортеж, берем первый элемент
    if len(indices) > 0:
        return indices[0]  # Возвращаем первый индекс
    else:
        return -1  # Если значение не найдено, возвращаем -1


def save_tile_info(info_table, file_type='txt'):
    file_name = f"info_table.{file_type}"
    if file_type == "txt":
        with open(file_name, 'w') as file:
            for color, info in info_table.items():
                r, g, b = color
                count = info['count']
                coordinates = "; ".join([f"({x}, {y})" for x, y in info['coordinates']])
                file.write(f"Color: ({r}, {g}, {b})\nCount: {count}\nCoordinates: {coordinates}\n\n")

    elif file_type == "csv":
        with open(file_name, 'w') as file:
            for color, info in info_table.items():
                r, g, b = color
                count = info['count']
                coordinates = "; ".join([f"({x}, {y})" for x, y in info['coordinates']])
                file.write(f"Color:\n ({r}, {g}, {b})\nCount:\n {count}\nCoordinates:\n {coordinates}\n\n")

def show_color(size, x1, y1, block):
    res = np.zeros((size, size, 3), dtype=np.uint8)
    block= block[::-1, :] # костыль
    col = block[y1, x1] # цвет, который был нажат
    print(x1, y1)
    print(col)
    for i in range(size):
        for j in range(size):
            #print(block[j][i])
            if not np.array_equal(block[j, i], col): # если не тот цвет, красим в черный
                res[j][i] = (0, 0, 0)
            else:
                res[j][i] = block[j][i] # иначе сохраняеем цвет

    res = res[::-1, :] # костыль, не спрашивайте...

    plt.figure(figsize=(5, 5), facecolor='lightgray')
    plt.imshow(res, extent=[0, size, 0, size])
    plt.show()



def get_square_by_coordinate(x, y, height, width, size_of_square, img):
    x_real_coord = x*size_of_square
    y_real_coord = y*size_of_square
    print(x_real_coord, y_real_coord)
    img = img[::-1, :] ### костыль тк из-за extent[0,width*2, 0, height] поменялись координаты y
    rgb_image = np.zeros((size_of_square, size_of_square, 3), dtype=np.uint8)
    #one_color_img = np.zeros((size_of_square, size_of_square, 3), dtype=np.uint8)
    color_counts = {}
    for y_real in range(size_of_square):
        for x_real in range (size_of_square):
            if x_real+x_real_coord>=width and x_real+x_real_coord<2*width and y_real+y_real_coord<height: # проверка на выход за границы изображения
                rgb_image[y_real, x_real] = img[y_real+y_real_coord, x_real + x_real_coord]
                color = tuple(img[y_real + y_real_coord, x_real + x_real_coord])  # RGB-кортеж
                if color not in color_counts:
                    color_counts[color] = 0
                color_counts[color] += 1
            else:
                rgb_image[y_real, x_real] = (0,0,0)

    rgb_image = rgb_image[::-1, :] ### костыль тк из-за extent[0,width*2, 0, height] поменялись координаты y

    def on_click_square(event):
        if event.button == MouseButton.LEFT:
            print(event.xdata, event.ydata)
            show_color(size_of_square, math.floor(event.xdata), math.floor(event.ydata), rgb_image)

    fig=plt.figure(figsize=(5, 5), facecolor='lightgray')
    plt.imshow(rgb_image, extent=[0, size_of_square, 0, size_of_square])
    fig.canvas.mpl_connect('button_press_event', on_click_square)
    plt.show()

    ### файлы должны создаваться только по потребности ###
    """
    file_name = f"tile_info_{x}_{y}.csv"
    with open(file_name, 'w') as file:
        for color, count in color_counts.items():
            r, g, b = color
            # Собираем координаты для этого цвета в выделенной области
            coordinates = "; ".join([f"({x_real}, {y_real})"
                    for x_real in range(size_of_square)
                    for y_real in range(size_of_square)
                    if tuple(img[y_real + y_real_coord, x_real + x_real_coord]) == color])

            # Записываем информацию о цвете, количестве и координатах в файл
            file.write(f"Color:\n ({r}, {g}, {b})\nCount:\n {count}\nCoordinates:\n {coordinates}\n\n")

    # Также можно вывести информацию в консоль или вернуть результат
    print(f"Information for tile ({x}, {y}) saved to {file_name}.")
    """

def drow_grid(w, h, size):
    w=(w//size+1)*size
    for x in range(w, w*2, size):
        plt.axvline(x=x, ymin=0, ymax=1,
                color='red')
    for y in range(0, h, size):
        plt.axhline(y=y, xmin=0.5, xmax=1, color='red')

#Вот эта функция типа итоговая она привязана к кнопке generate - т.е. вы можете менять тут че хотите но генерация
#изображения должна оставаться здесь
def func(width, height, path, input_colors):

    img_array = np.array(Image.open(path))  # Загрузка RGB-изображения и преобразование в массив
    rgb_image = np.zeros((height, width, 3), dtype=np.uint8) # массив для нового изображения в формате RGB

    info_table = {} #словарь для хранения инфы о плиточках(цвет, количество и координаты)

    #создаем картину
    for y in range(height):
        for x in range(width):
            r, g, b = img_array[y, x] # Получаем значения R, G, B
            #rgb_image[y, x] = find_nearest_value(r, g, b, input_colors)
            nearest_color = tuple(find_nearest_value(r, g, b, input_colors))
            rgb_image[y, x] = nearest_color

            if nearest_color not in info_table:
                info_table[nearest_color] = {"count": 0, "coordinates": []}
            info_table[nearest_color]["count"] += 1
            info_table[nearest_color]["coordinates"].append((x, y))

    ### таблицы тоже должны создаваться по требованию а не каждый раз ###
    ###save_tile_info(info_table)
    ###save_tile_info(info_table, 'csv')
    ###print(img_array)


    ### размер блока должен подаваться как входные данные ###
    size_of_square = 10

    result_img = np.concatenate((img_array, rgb_image), axis=1)
    plt.figure(figsize=(14, 7), facecolor='lightgray')

    #plt.axis([0, width * 2, 0, height])

    def on_click(event):
        if event.button is MouseButton.LEFT:
            if event.xdata!=None and event.ydata!=None and event.xdata>width and event.ydata>0:
                print(event.xdata, event.ydata)
                get_square_by_coordinate(
                    int (event.xdata//size_of_square),
                    int (event.ydata//size_of_square),
                    height, width,
                    size_of_square,
                    result_img)


    plt.connect('button_press_event', on_click)
    plt.imshow(result_img, extent=[0, width*2, 0, height])
    drow_grid(width, height, size_of_square) #отображаем сетку блоков
    plt.show()

