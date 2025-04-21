import math
from typing import override
from palette import show_palette, show_palette_nonblocking
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.backend_bases import MouseButton
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox, QMainWindow
import csv
import sys
import config

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
global_input_colors=[]
size_of_button=14 # высота кнопок на итоговой картинке
size_of_line = 2


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

def show_color(size, x1, y1, block): # вывод блока по цвету

        x1 = math.floor(x1)
        y1 = math.floor(y1)

        res = np.zeros((size, size, 3), dtype=np.uint8)
        col = block[y1, x1]  # цвет, который был нажат
        for i in range(size):
            for j in range(size):
                if not np.array_equal(block[j, i], col):  # если не тот цвет, красим в черный
                    res[j][i] = (0, 0, 0)
                else:
                    res[j][i] = block[j][i]  # иначе сохраняеем цвет

        plt.figure(figsize=(5, 5), facecolor='lightgray')
        plt.imshow(res, extent=[0, size, size, 0])

        plt.gca().xaxis.set_ticks_position('top')  # Метки оси X наверх
        plt.gca().xaxis.set_label_position('top')  # Подпись оси X наверх
        plt.gca().spines['bottom'].set_visible(False)  # Скрываем нижнюю ось X
        plt.gca().spines['top'].set_visible(True)

        plt.show(block=False)

def get_square_by_coordinate(x, y, height, width, size_of_square, img):
    x_real_coord = x*size_of_square
    y_real_coord = y*size_of_square
    rgb_image = np.zeros((size_of_square, size_of_square, 3), dtype=np.uint8)
    color_counts = {}
    for y_real in range(size_of_square):
        for x_real in range (size_of_square):
            if x_real+x_real_coord>=0 and x_real+x_real_coord<width and y_real+y_real_coord<height: # проверка на выход за границы изображения
                rgb_image[y_real, x_real] = img[y_real+y_real_coord, x_real + x_real_coord]
                color = tuple(img[y_real + y_real_coord, x_real + x_real_coord])  # RGB-кортеж
                if color not in color_counts:
                    color_counts[color] = 0
                color_counts[color] += 1
            else:
                rgb_image[y_real, x_real] = (0,0,0)

    def on_click_square(event):
        if event.button == MouseButton.LEFT:
            show_color(size_of_square, event.xdata, event.ydata, rgb_image)


    fig=plt.figure(figsize=(5, 5), facecolor='lightgray')
    plt.imshow(rgb_image, extent=[0, size_of_square, size_of_square, 0])

    plt.gca().xaxis.set_ticks_position('top')  # Метки оси X наверх
    plt.gca().xaxis.set_label_position('top')  # Подпись оси X наверх
    plt.gca().spines['bottom'].set_visible(False)  # Скрываем нижнюю ось X
    plt.gca().spines['top'].set_visible(True)

    fig.canvas.mpl_connect('button_press_event', on_click_square)
    plt.show(block=False)

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
    ymin_new=(size_of_button+size_of_line)/(size_of_button+size_of_line+h)
    for x in range(0, w, size):
        plt.axvline(x=x, ymin=ymin_new, ymax=1,
                color="#db2c2c")
    for y in range(0, h, size):
        plt.axhline(y=y, xmin=0, xmax=1, color="#db2c2c")


def show_main_pic(height, rgb_image, size_of_square, width, input_colors):
    def on_click_main(event):

        if event.button is MouseButton.LEFT:
            if event.xdata != None and event.ydata != None and event.xdata > 0 and event.ydata > 0:
                if (event.ydata<=height):
                    get_square_by_coordinate(
                        int(event.xdata // size_of_square),
                        int(event.ydata // size_of_square),
                        height, width,
                        size_of_square,
                        rgb_image)

                else: # кнопки
                    global_h = height
                    global_w = width
                    global_img = rgb_image
                    if (event.xdata < int(width/2)-1):
                        # Создаем QApplication если его нет
                        app = QApplication.instance() or QApplication([])
                        show_palette_nonblocking(input_colors)
                        # Периодически обрабатываем события Qt
                        from PyQt5.QtCore import QTimer
                        timer = QTimer()
                        timer.timeout.connect(lambda: app.processEvents())
                        timer.start(100)  # Обновляем каждые 100 мс

                    elif (event.xdata > int(width/2)+1):
                        print("save")
                        #show_pic_by_color(rgb_image[1,1], rgb_image, width, height)

    width1=0 # левая кнопка
    width2 = 0 # правая кнопка
    width3=0 # разделитель
    if width%2==0:
        width1 =width/2-1
        width2 = width/2-1
        width3=2
    else:
        width1 = int(width / 2)-1
        width2 = int(width / 2)-1
        width3=3
    but1 = np.zeros((size_of_button, width1, 3), dtype=np.uint8)
    for i in but1:
        for j in i:
            j[0] = 151
            j[1] = 94
            j[2] = 89
    sep=np.zeros((size_of_button, width3, 3), dtype=np.uint8)
    for i in sep:
        for j in i:
            j[0] = 211
            j[1] = 211
            j[2] = 211
    tmp=np.concatenate((but1, sep), axis=1)
    but2 = np.zeros((size_of_button, width2, 3), dtype=np.uint8)
    for i in but2:
        for j in i:
            j[0] = 151
            j[1] = 94
            j[2] = 89

    save_or_color = np.concatenate((tmp, but2), axis=1)

    line = np.zeros((size_of_line, width, 3), dtype=np.uint8)
    for i in line:
        for j in i:
            j[0] = 211
            j[1] = 211
            j[2] = 211
    save_or_color=np.concatenate((line, save_or_color), axis=0)

    result_img = np.concatenate((rgb_image, save_or_color), axis=0)

    plt.figure(figsize=(8, 9), facecolor='lightgray')
    plt.connect('button_press_event', on_click_main)

    drow_grid(width, height, size_of_square)  # отображаем сетку блоков


    #result_img=rgb_image
    plt.imshow(result_img, extent=[0, width, height+size_of_button+size_of_line, 0])

    plt.gca().xaxis.set_ticks_position('top')  # Метки оси X наверх
    plt.gca().xaxis.set_label_position('top')  # Подпись оси X наверх
    plt.gca().spines['bottom'].set_visible(False)  # Скрываем нижнюю ось X
    plt.gca().spines['top'].set_visible(True)

    plt.show(block=False)


#Вот эта функция типа итоговая она привязана к кнопке generate - т.е. вы можете менять тут че хотите но генерация
#изображения должна оставаться здесь
#!!!добавила переменные отвечающие за размер блока и формат вывода - ".cvc"/".txt"
def func(width, height, path, input_colors, format_to_save, block_size):

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

    config.global_img = rgb_image
    config.global_w = width
    config.global_h = height

    ### таблицы тоже должны создаваться по требованию а не каждый раз ###
    ###save_tile_info(info_table)
    ###save_tile_info(info_table, 'csv')
    ###print(img_array)


    ### размер блока должен подаваться как входные данные
    ### добавила сюда размер блока из входных данных
    size_of_square = block_size

    result_img = np.concatenate((img_array, rgb_image), axis=1)

    white_line = np.zeros((2, width*2, 3), dtype=np.uint8)
    for i in white_line:
        for j in i:
            j[0] = 211
            j[1] = 211
            j[2] = 211 #я не знаю почему если написать = [255, 255, 255] оно не приравнивается нормально
    # добавим белую линию после изображения
    result_img = np.concatenate((result_img,white_line), axis = 0)
    green_half = np.zeros((16, width, 3), dtype=np.uint8)
    for i in green_half:
        for j in i:
            j[0] = 211
            j[1] = 211
            j[2] = 211
    red_half = np.zeros((16, width, 3), dtype=np.uint8)
    for i in red_half:
        for idx, j in enumerate(i):
            if idx > width/2 + 1:
                j[0] = 175
                j[1] = 64
                j[2] = 53
            elif idx < width / 2 - 1:
                j[0] = 122
                j[1] = 169
                j[2] = 82
            else:
                j[0] = 211
                j[1] = 211
                j[2] = 211
    yes_or_no = np.concatenate((green_half, red_half), axis = 1)

    result_img = np.concatenate((result_img,yes_or_no), axis = 0)
    plt.figure(figsize=(14, 7), facecolor='lightgray')

    #plt.axis([0, width * 2, 0, height])

    def on_click(event):
        if event.button is MouseButton.LEFT:
            if event.xdata!=None and event.ydata!=None and event.xdata>width and event.ydata>0:
                if event.ydata <= 13 and event.xdata > width and event.xdata < width+ width/2 -1:
                    plt.close("all")
                    show_main_pic(height, rgb_image, size_of_square, width, input_colors)

                if event.ydata <= 13 and event.xdata > width + width/2 + 1 and event.xdata < width *2:
                    plt.close("all")


    plt.connect('button_press_event', on_click)
    plt.imshow(result_img, extent=[0, width*2, 0, height+4])
    #drow_grid(width, height, size_of_square) #отображаем сетку блоков
    plt.axis('off')
    plt.show(block=False)

