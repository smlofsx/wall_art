import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

#input_colors = [
        #(255, 0, 0),
        #(0, 255, 0),
        #(0, 0, 255),
        #(128, 128, 128)
    #]
#path='cat.jpg'
#width=512
#height=367


def process_rgb(r,g,b):
    return int(0.3*r+0.59*g+0.11*b)

# Функция для нахождения ближайшего значения из массива results
def find_nearest_value(value, results):
    differences = np.abs(results - value)# Вычисляем абсолютную разницу между value и всеми элементами results
    nearest_index = np.argmin(differences)# Находим индекс минимальной разницы
    return results[nearest_index]# Возвращаем ближайшее значение

def number_to_rgb(value, colors, results):
    pass



def get_index_by_value(arr, value):
    # Возвращает индекс первого вхождения value в массиве arr
    indices = np.where(arr == value)[0]  # np.where возвращает кортеж, берем первый элемент
    if len(indices) > 0:
        return indices[0]  # Возвращаем первый индекс
    else:
        return -1  # Если значение не найдено, возвращаем -1


#Вот эта функция типа итоговая она привязана к кнопке generate - т.е. вы можете менять тут че хотите но генерация
#изображения должна оставаться здесь
def func(width, height, path, input_colors):
    img_array = np.array(Image.open(path))  # Загрузка RGB-изображения и преобразование в массив
    results = np.array([process_rgb(r, g, b) for r, g, b in input_colors])

    arr = np.zeros([height, width, 1], dtype=int)  # вспомогательный массив

    # переводим ргб
    for y in range(height):
        for x in range(width):
            r, g, b = img_array[y, x]  # Получаем значения R, G, B
            arr[y, x, 0] = process_rgb(r, g, b)  # Применяем функцию и сохраняем результат

    # Проходим по массиву arr и заменяем значения на ближайшие из results
    for y in range(height):
        for x in range(width):
            current_value = arr[y, x, 0]  # Получаем текущее значение из arr
            nearest_value = find_nearest_value(current_value, results)  # Находим ближайшее значение из results
            arr[y, x, 0] = nearest_value  # Заменяем значение в arr

    # Создаем массив для нового изображения в формате RGB
    rgb_image = np.zeros((height, width, 3), dtype=np.uint8)

    for y in range(height):
        for x in range(width):
            value = arr[y, x, 0]
            index = get_index_by_value(results, value)
            r, g, b = input_colors[index]
            rgb_image[y, x] = r, g, b

    # отобразить
    result_img = np.concatenate((img_array, rgb_image), axis=1)
    plt.figure(figsize=(5, 5))
    plt.imshow(result_img)
    plt.show()

    # img = Image.fromarray(array)
    # img.save('imrgb.png')
    print(img_array)


