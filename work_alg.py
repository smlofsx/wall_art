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

def number_to_rgb(value, colors, results):
    pass

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


def get_square_by_coordinate(x, y, height, width, size_of_square, img):
    x_real_coord = x*size_of_square
    y_real_coord = y*size_of_square
    print(x_real_coord, y_real_coord)
    rgb_image = np.zeros((size_of_square, size_of_square, 3), dtype=np.uint8)
    color_counts = {}
    for x_real in range(size_of_square):
        for y_real in range (size_of_square):
            rgb_image[y_real, x_real] = img[y_real+y_real_coord, x_real + x_real_coord]

            color = tuple(img[y_real + y_real_coord, x_real + x_real_coord])  # RGB-кортеж

            if color not in color_counts:
                color_counts[color] = 0
            color_counts[color] += 1


    plt.figure(figsize=(5, 5))
    plt.imshow(rgb_image)
    plt.show()

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

#Вот эта функция типа итоговая она привязана к кнопке generate - т.е. вы можете менять тут че хотите но генерация
#изображения должна оставаться здесь
def func(width, height, path, input_colors):

    img_array = np.array(Image.open(path))  # Загрузка RGB-изображения и преобразование в массив
    # массив для нового изображения в формате RGB
    rgb_image = np.zeros((height, width, 3), dtype=np.uint8)

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


    # отобразить
    #result_img = np.concatenate((img_array, rgb_image), axis=1)
    #plt.figure(figsize=(5, 5))
    #plt.imshow(result_img)
    #plt.show()

    save_tile_info(info_table)
    save_tile_info(info_table, 'csv')

    # img = Image.fromarray(array)
    # img.save('imrgb.png')
    print(img_array)


    # отобразить
    size_of_square = 5

    result_img = np.concatenate((img_array, rgb_image), axis=1)
    plt.figure(figsize=(14, 7))

    def on_click(event):
        if event.button is MouseButton.LEFT:
            if event.xdata>0 and event.ydata>0:
                print(event.xdata)
                print(event.ydata)
                print(event.xdata//size_of_square)
                print(event.ydata//size_of_square)
                get_square_by_coordinate(
                    int (event.xdata//size_of_square),
                    int (event.ydata//size_of_square),
                    height, width,
                    size_of_square,
                    result_img)

    plt.connect('button_press_event', on_click)
    plt.imshow(result_img)
    plt.show()

    # img = Image.fromarray(array)
    # img.save('imrgb.png')
    # print(img_array)