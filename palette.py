import sys
from functools import lru_cache

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel)
from PyQt5.QtGui import QColor, QPainter, QFont, QPainterPath
from PyQt5.QtCore import Qt, QRectF
import numpy as np
import matplotlib.pyplot as plt
import config


def show_pic_by_color(color, img, width, height):
    # Проверяем, есть ли уже открытое окно
    if hasattr(show_pic_by_color, 'window') and plt.fignum_exists(show_pic_by_color.window.number):
        # Если окно существует, просто обновляем его содержимое
        ax = show_pic_by_color.window.axes[0]
        ax.clear()
    else:
        # Создаем новое окно с уникальным менеджером
        show_pic_by_color.window = plt.figure(figsize=(8, 9))
        ax = show_pic_by_color.window.add_subplot(111)
        show_pic_by_color.window.canvas.manager.set_window_title('Color View')

        # Преобразуем цвет в кортеж, если это массив

    # Оптимизированное создание изображения
    res = np.zeros((height, width, 3), dtype=np.uint8)
    color_array = np.array(color, dtype=np.uint8)  # Преобразуем кортеж в массив
    mask = np.all(img == color_array, axis=2)  # Теперь сравнение корректно
    res[mask] = color

    ax.imshow(res, extent=[0, width, height, 0])
    ax.set_title(f"Color: {color}")

    # Настройки для плавного отображения
    plt.tight_layout()
    plt.show(block=False)

    # Важно: обрабатываем события PyQt
    app = QApplication.instance()
    if app:
        app.processEvents()

    return show_pic_by_color.window


class ColorButton(QPushButton):
    def __init__(self, color):
        super().__init__()
        self.color = QColor(*color)
        self.setFixedSize(100, 100)

        # Вычисляем ключ для словаря
        r, g, b = color
        self.brightness_key = r * 0.299 + g * 0.587 + b * 0.114

        # Настраиваем шрифт
        font = QFont()
        font.setFamily("Candara")
        font.setPointSize(12)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(15)
        self.setFont(font)

        # Устанавливаем текст
        self.setText(f"{color[0]}, {color[1]}, {color[2]}")

        # Убираем стандартные стили кнопки
        self.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
            }
        """)

        # Устанавливаем цвет текста в зависимости от яркости фона
        if self.brightness_key > 150:
            self.text_color = QColor(0, 0, 0)  # черный
        else:
            self.text_color = QColor(255, 255, 255)  # белый

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Рисуем закругленный прямоугольник
        path = QPainterPath()
        rect = QRectF(0, 0, self.width(), self.height())
        path.addRoundedRect(rect, 15, 15)
        painter.fillPath(path, self.color)

        # Рисуем текст
        painter.setPen(self.text_color)
        painter.drawText(rect, Qt.AlignCenter, self.text())


class ColorVisualizer(QWidget):
    def __init__(self, colors, flag_to_button=0):
        super().__init__()
        self.setWindowFlag(Qt.WindowStaysOnTopHint)  # Окно поверх других
        self.setAttribute(Qt.WA_DeleteOnClose, False)  # Не удалять при закрытии
        self.colors = colors
        self.flag = flag_to_button
        self.color_buttons = {}  # Словарь для хранения кнопок
        self.initUI()
        self.matplotlib_figures = []  # Для хранения открытых фигур

    def initUI(self):
        self.setWindowTitle('Визуализатор цветов RGB')
        self.setGeometry(100, 100, 600, 400)
        self.setStyleSheet("background-color: #fbf8f4;")

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Создаем строки по 5 цветов в каждой
        row_layout = None
        for i, color in enumerate(self.colors):
            if i % 5 == 0:
                row_layout = QHBoxLayout()
                row_layout.setSpacing(15)
                main_layout.addLayout(row_layout)

            # Создаем кнопку и добавляем в словарь
            color_button = ColorButton(color)
            self.color_buttons[color_button.brightness_key] = color_button

            # Подключаем обработчик нажатия
            color_button.clicked.connect(
                lambda checked, key=color_button.brightness_key: self.on_color_clicked(key)
            )

            row_layout.addWidget(color_button)

        # Кнопка закрытия
        close_btn = QPushButton("CLOSE")
        close_btn.setFont(QFont("Candara", 10))
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #975e59;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        close_btn.clicked.connect(self.close)
        main_layout.addWidget(close_btn, 0, Qt.AlignCenter)

        self.setLayout(main_layout)
        self.drag_position = None

    def on_color_clicked(self, brightness_key):
        try:
            button = self.color_buttons[brightness_key]
            color = (button.color.red(), button.color.green(), button.color.blue())
            if not hasattr(config, 'global_img'):
                return

            # Закрываем предыдущее окно если оно есть
            if hasattr(self, '_current_fig') and plt.fignum_exists(self._current_fig.number):
                plt.close(self._current_fig)

            # Создаем новое окно
            self._current_fig = show_pic_by_color(color, config.global_img,
                                                  config.global_w, config.global_h)

            # Принудительно обрабатываем события
            QApplication.processEvents()

        except Exception as e:
            print(f"Error in color click: {str(e)}")

            # Можно добавить QMessageBox с предупреждением об ошибке

    def closeEvent(self, event):
        if hasattr(self, '_current_fig') and self._current_fig:
            plt.close(self._current_fig)
        event.accept()


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()


def show_palette(input_colors):
    # Проверяем, существует ли уже экземпляр QApplication
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    # Создаем окно
    visualizer = ColorVisualizer(input_colors)
    visualizer.setAttribute(Qt.WA_DeleteOnClose, False)

    # Показываем окно
    visualizer.show()

    # Если это первый вызов (нет существующего QApplication), запускаем event loop
    if not QApplication.instance():
        sys.exit(app.exec_())

from PyQt5.QtCore import QTimer


def show_palette_nonblocking(colors):
    # Проверяем существует ли QApplication
    app = QApplication.instance()
    if not app:
        app = QApplication([])

    # Создаем и настраиваем окно
    visualizer = ColorVisualizer(colors, 1)
    visualizer.setAttribute(Qt.WA_DeleteOnClose, False)

    # Сохраняем ссылку на окно глобально
    global _global_visualizer
    _global_visualizer = visualizer

    # Показываем окно
    visualizer.show()

    # Обрабатываем события Qt без блокировки
    app.processEvents()
    return visualizer

