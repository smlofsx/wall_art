import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

# Создаем случайное изображение (можно заменить на ваш массив)
image = np.random.rand(100, 100)  # 100x100 случайных значений

# Создаем окно и отображаем изображение
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.2)  # Оставляем место для кнопки
img_display = ax.imshow(image, cmap='gray')

# Функция, которая будет вызываться при нажатии кнопки
def on_button_click(event):
    print("Кнопка нажата!")
    # Меняем изображение (например, инвертируем цвета)
    new_image = 1 - image  # Инверсия
    img_display.set_data(new_image)
    fig.canvas.draw()  # Обновляем отображение

# Создаем кнопку
button_ax = plt.axes([0.7, 0.05, 0.2, 0.075])  # [x, y, ширина, высота]
button = Button(button_ax, 'Инвертировать')

# Привязываем событие нажатия кнопки к функции
button.on_clicked(on_button_click)

plt.show()