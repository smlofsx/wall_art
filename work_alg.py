import math
from typing import override
from palette import show_palette, show_palette_nonblocking
import numpy as np

import matplotlib
matplotlib.use('Qt5Agg')

import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from PIL import Image
from matplotlib.backend_bases import MouseButton
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox, QMainWindow
import sys
import config
import pandas as pd
import os


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
global_block=0
global_bl_col=0
global_img_col=0


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


def save_tile_info(info_table, file_type='xlsx', file_name='info_table.xlsx'):
    color_data = []

    for color, info in info_table.items():
        r, g, b = color
        # Если info - это просто количество, это ошибка, нужно подправить.
        if isinstance(info, int):  # Проверка, если info — это количество
            count = info  # Просто количество, без дополнительных данных
            coordinates = []  # Координат не будет
        else:
            count = info.get('count', 0)  # Получаем количество
            coordinates = info.get('coordinates', [])  # Получаем координаты

        # Добавляем первую строку с count
        first = True
        for coord in coordinates:
            color_data.append({
                'Color': f"({r}, {g}, {b})",
                'Coordinate': f"({coord[0]}, {coord[1]})",
                'Count': count if first else ""
            })
            first = False

    df = pd.DataFrame(color_data)

    if file_type == 'xlsx':
        with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
            worksheet = writer.sheets['Sheet1']
            worksheet.column_dimensions['A'].width = 20  # Color
            worksheet.column_dimensions['B'].width = 15  # Coordinate
            worksheet.column_dimensions['C'].width = 10  # Count

    #elif file_type == 'csv':
        #df.to_csv(file_name, index=False)

    elif file_type == 'txt':
        with open(file_name, 'w', encoding='utf-8') as file:
            # Заголовок таблицы
            file.write(f"{'Color':<20} {'Coordinate':<15} {'Count':<10}\n")
            file.write(f"{'-'*20} {'-'*15} {'-'*10}\n")

            for _, row in df.iterrows():
                file.write(f"{row['Color']:<20} {row['Coordinate']:<15} {str(row['Count']):<10}\n")


def show_color(size, x1, y1, block): # вывод блока по цвету
        plt.close('all')
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

        fig, ax=plt.subplots(figsize=(5, 5), facecolor='lightgray')
        plt.imshow(res, extent=[0, size, size, 0])

        plt.gca().xaxis.set_ticks_position('top')  # Метки оси X наверх
        plt.gca().xaxis.set_label_position('top')  # Подпись оси X наверх
        plt.gca().spines['bottom'].set_visible(False)  # Скрываем нижнюю ось X
        plt.gca().spines['top'].set_visible(True)

        # Создание кнопок
        plt.subplots_adjust(bottom=0.3)  # Освобождаем место для кнопок

        # Обработчики кнопок
        def go_back(event):
            print("Back")
            plt.close('all')

        def save_image(event):
            print("Save")

        # Создаем первую кнопку (Show Palette)
        ax_btn_back = plt.axes([0.2, 0.1, 0.3, 0.1])  # [left, bottom, width, height]
        show_palette_button = Button(ax_btn_back, 'Go back', color='lightblue')
        show_palette_button.on_clicked(go_back)

        # Создаем вторую кнопку (Save)
        ax_btn_save = plt.axes([0.5, 0.1, 0.3, 0.1])  # [left, bottom, width, height]
        save_button = Button(ax_btn_save, 'Save', color='lightgreen')
        save_button.on_clicked(save_image)

        plt.show()

        while plt.fignum_exists(fig.number):  # Пока окно не закрыто
            plt.pause(0.1)

def get_square_by_coordinate(x, y, height, width, size_of_square, img):
    plt.close('all')
    x_real_coord = x*size_of_square
    y_real_coord = y*size_of_square
    rgb_image = np.zeros((size_of_square, size_of_square, 3), dtype=np.uint8)
    color_counts = {}
    for y_real in range(size_of_square):
        for x_real in range(size_of_square):
            if x_real + x_real_coord >= 0 and x_real + x_real_coord < width and y_real + y_real_coord < height:
                rgb_image[y_real, x_real] = img[y_real + y_real_coord, x_real + x_real_coord]

                # Преобразуем np.uint8 цвета в обычный кортеж из целых чисел
                color = tuple(map(int, img[y_real + y_real_coord, x_real + x_real_coord]))

                # Инициализация словаря для каждого цвета, если его нет в color_counts
                if color not in color_counts:
                    color_counts[color] = {'count': 0, 'coordinates': []}

                # Обновляем количество и добавляем координаты
                color_counts[color]['count'] += 1
                color_counts[color]['coordinates'].append((x_real + x_real_coord, y_real + y_real_coord))
            else:
                rgb_image[y_real, x_real] = (0, 0, 0)

    global_block=rgb_image.copy()
    #!!!вот отсюда вывод по блокам как только на него тыкнем
    """block_filename_base = f"block_{y}_{x}"
    save_tile_info(color_counts, file_type='txt', file_name=f"{block_filename_base}.txt")
    save_tile_info(color_counts, file_type='xlsx', file_name=f"{block_filename_base}.xlsx")"""


    #это для вывода матрицы тхт конкретного цвета
    def save_block_info(rgb_image, color, size_of_square, x, y):
        # Формируем матрицу 0 и 1
        matrix = np.zeros((size_of_square, size_of_square), dtype=int)
        for i in range(size_of_square):
            for j in range(size_of_square):
                if np.array_equal(rgb_image[i, j], color):
                    matrix[i, j] = 1

        r, g, b = color
        color_str = f"({r}, {g}, {b})"

        txt_filename = f"block_matrix_{y}_{x}.txt"
        with open(txt_filename, 'w') as file:
            file.write(f"Color: {color_str}\n")
            file.write("Matrix:\n")

            # Заголовок с номерами столбцов
            file.write("    " + " ".join(f"{j:>3}" for j in range(size_of_square)) + "\n")

            # Каждая строка с номером строки и выровненными значениями
            for i, row in enumerate(matrix):
                file.write(f"{i:>3} " + " ".join(f"{val:>3}" for val in row) + "\n")


    def on_click_square(event):
        if event.button == MouseButton.LEFT:
            #для вывода конкретного цвета блока
            '''x_coord = math.floor(event.xdata)  # Получаем координаты клика
            y_coord = math.floor(event.ydata)

            # Получаем цвет пикселя по этим координатам
            color = tuple(rgb_image[y_coord, x_coord])  # Цвет пикселя
            save_block_info(rgb_image, color, size_of_square, x_coord, y_coord)  # Сохраняем информацию
            '''
            if event.inaxes == ax:
                show_color(size_of_square, event.xdata, event.ydata, rgb_image)


    fig, ax = plt.subplots(figsize=(5,5), facecolor='lightgray')
    plt.imshow(rgb_image, extent=[0, size_of_square, size_of_square, 0])

    plt.gca().xaxis.set_ticks_position('top')  # Метки оси X наверх
    plt.gca().xaxis.set_label_position('top')  # Подпись оси X наверх
    plt.gca().spines['bottom'].set_visible(False)  # Скрываем нижнюю ось X
    plt.gca().spines['top'].set_visible(True)

    # Создание кнопок
    plt.subplots_adjust(bottom=0.3)  # Освобождаем место для кнопок

    # Обработчики кнопок
    def go_back(event):
        print("Back")
        plt.close('all')

    def save_image(event):
        print("Save")

    # Создаем первую кнопку (Show Palette)
    ax_btn_back = plt.axes([0.2, 0.1, 0.3, 0.1])   # [left, bottom, width, height]
    show_palette_button = Button(ax_btn_back, 'Go back', color='lightblue')
    show_palette_button.on_clicked(go_back)

    # Создаем вторую кнопку (Save)
    ax_btn_save = plt.axes([0.5, 0.1, 0.3, 0.1])  # [left, bottom, width, height]
    save_button = Button(ax_btn_save, 'Save', color='lightgreen')
    save_button.on_clicked(save_image)

    fig.canvas.mpl_connect('button_press_event', on_click_square)
    plt.show()

    while plt.fignum_exists(fig.number):  # Пока окно не закрыто
        plt.pause(0.1)



def draw_grid(w, h, size):
    #ymin_new=(size_of_button+size_of_line)/(size_of_button+size_of_line+h)
    for x in range(0, w, size):
        plt.axvline(x=x, ymin=0, ymax=1,
                color="#db2c2c")
    for y in range(0, h, size):
        plt.axhline(y=y, xmin=0, xmax=1, color="#db2c2c")


def show_main_pic(height, rgb_image, size_of_square, width, input_colors):
    def on_click_main(event):
        if event.button is MouseButton.LEFT:
            if event.inaxes == ax and event.xdata != None and event.ydata != None and event.xdata > 0 and event.ydata > 0:
                if (event.ydata<=height):
                    get_square_by_coordinate(
                        int(event.xdata // size_of_square),
                        int(event.ydata // size_of_square),
                        height, width,
                        size_of_square,
                        rgb_image)

    '''width1=0 # левая кнопка
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

    result_img = np.concatenate((rgb_image, save_or_color), axis=0)'''

    fig, ax = plt.subplots(figsize=(8, 9))
    plt.subplots_adjust(bottom=0.2)

    draw_grid(width, height, size_of_square)  # отображаем сетку блоков
    img_display = ax.imshow(rgb_image, extent=[0, width, height, 0])

    #result_img=rgb_image
    #plt.imshow(rgb_image, extent=[0, width, height, 0])

    plt.gca().xaxis.set_ticks_position('top')  # Метки оси X наверх
    plt.gca().xaxis.set_label_position('top')  # Подпись оси X наверх
    plt.gca().spines['bottom'].set_visible(False)  # Скрываем нижнюю ось X
    plt.gca().spines['top'].set_visible(True)

    # Привязываем обработчик кликов
    fig.canvas.mpl_connect('button_press_event', on_click_main)

    def on_show_palette(event):
        print("Show Palette button clicked")
        plt.close('all')
        app = QApplication.instance() or QApplication([])
        show_palette_nonblocking(input_colors)
        # Периодически обрабатываем события Qt
        from PyQt5.QtCore import QTimer
        timer = QTimer()
        timer.timeout.connect(lambda: app.processEvents())
        timer.start(100)
        #matplotlib
        '''size=len(input_colors)
        palette = np.zeros((10, size*10, 3), dtype=np.uint8)
        for i, color in enumerate(input_colors):
            x_start = i * 10
            x_end = x_start + 10
            palette[:, x_start:x_end] = color
        fig = plt.figure(figsize=(5, 5), facecolor='lightgray')
        plt.imshow(palette)
        ax.axis('off')
        plt.show()'''



    def on_save(event):
        print("Save button clicked")
        # Здесь можно добавить логику сохранения изображения
        # Например: plt.savefig("output.png")

    # Создаем первую кнопку (Show Palette)
    show_palette_ax = plt.axes([0.2, 0.05, 0.2, 0.075])  # [left, bottom, width, height]
    show_palette_button = Button(show_palette_ax, 'Show Palette', color='lightblue')
    show_palette_button.on_clicked(on_show_palette)

    # Создаем вторую кнопку (Save)
    save_ax = plt.axes([0.6, 0.05, 0.2, 0.075])  # [left, bottom, width, height]
    save_button = Button(save_ax, 'Save', color='lightgreen')
    save_button.on_clicked(on_save)

    plt.show()
    while plt.fignum_exists(fig.number):  # Пока окно не закрыто
        plt.pause(0.1)



#Вот эта функция типа итоговая она привязана к кнопке generate - т.е. вы можете менять тут че хотите но генерация
#изображения должна оставаться здесь
#!!!добавила переменные отвечающие за размер блока и формат вывода - ".cvc"/".txt"
def func(width, height, path, input_colors, format_to_save, block_size):

    img_array = np.array(Image.open(path))  # Загрузка RGB-изображения и преобразование в массив
    rgb_image = np.zeros((height, width, 3), dtype=np.uint8) # массив для нового изображения в формате RGB

    global_block = np.zeros((block_size, block_size, 3), dtype=np.uint8)
    global_bl_col=np.zeros((block_size, block_size, 3), dtype=np.uint8)
    global_img_col = np.zeros((height, width, 3), dtype=np.uint8)

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
    config.global_info_table = info_table
    ### таблицы тоже должны создаваться по требованию а не каждый раз ###
    #сто проц работает правильно
    ### save_tile_info(info_table, 'xlsx')
    ### save_tile_info(info_table, 'txt')
    ### теперь при нажатии кнопки вызывать(только хз работает ли):
    ### save_tile_info(config.global_info_table, 'xlsx')
    ### save_tile_info(config.global_info_table, 'txt')
    ###print(img_array)


    ### размер блока должен подаваться как входные данные
    ### добавила сюда размер блока из входных данных
    size_of_square = block_size

    result_img = np.concatenate((img_array, rgb_image), axis=1)

    '''white_line = np.zeros((2, width*2, 3), dtype=np.uint8)
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

    result_img = np.concatenate((result_img,yes_or_no), axis = 0)'''
    #plt.figure(figsize=(14, 7), facecolor='lightgray')

    '''def on_click(event):
        if event.button is MouseButton.LEFT:
            if event.xdata!=None and event.ydata!=None and event.xdata>width and event.ydata>0:
                if event.ydata <= 13 and event.xdata > width and event.xdata < width+ width/2 -1: # условие нажатия кнопки ок
                    plt.close("all")
                    show_main_pic(height, rgb_image, size_of_square, width, input_colors)

                if event.ydata <= 13 and event.xdata > width + width/2 + 1 and event.xdata < width *2: # условие нажатия кнопки regeneretion
                    plt.close("all")


    plt.connect('button_press_event', on_click)
    plt.imshow(result_img, extent=[0, width*2, 0, height])
    plt.axis('off')'''

    fig, ax = plt.subplots(figsize=(14, 7))
    plt.subplots_adjust(bottom=0.2)

    img_display = ax.imshow(result_img)
    ax.axis('off')

    def on_continue(event):
        print("continue")
        plt.close("all")
        show_main_pic(height, rgb_image, size_of_square, width, input_colors)

    def on_goback(event):
        print("go back")
        plt.close("all")

    # Создаем первую кнопку (Continue)
    continue_ax = plt.axes([0.2, 0.05, 0.2, 0.075])  # [left, bottom, width, height]
    continue_button = Button(continue_ax, 'Continue', color='lightgreen')
    continue_button.on_clicked(on_continue)

    # Создаем вторую кнопку (Go Back)
    goback_ax = plt.axes([0.6, 0.05, 0.2, 0.075])  # [left, bottom, width, height]
    goback_button = Button(goback_ax, 'Go Back', color='lightcoral')
    goback_button.on_clicked(on_goback)

    plt.show()
    while plt.fignum_exists(fig.number):  # Пока окно не закрыто
        plt.pause(0.1)

