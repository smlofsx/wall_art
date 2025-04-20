import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel)
from PyQt5.QtGui import QColor, QPainter, QFont, QPainterPath
from PyQt5.QtCore import Qt, QRectF


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
        self.colors = colors
        self.flag = flag_to_button
        self.color_buttons = {}  # Словарь для хранения кнопок
        self.initUI()

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
        close_btn = QPushButton("OK")
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
        """Обработчик нажатия на цветную кнопку"""
        button = self.color_buttons[brightness_key]
        r, g, b = button.color.red(), button.color.green(), button.color.blue()
        if self.flag == 0:
            print(f"Clicked color: RGB({r}, {g}, {b}), Brightness key: {brightness_key}")
        else:
            #вот тут надо типа вызвать новое окошко с выводом по конкретному цвету
            return



    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()


if __name__ == '__main__':
    input_colors = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (128, 128, 128),
        (255, 255, 0),
        (255, 0, 255),
        (0, 255, 255),
        (192, 192, 192),
        (128, 0, 0),
        (0, 128, 0),
        (0, 0, 0),
        (255, 255, 255)
    ]

    app = QApplication(sys.argv)
    visualizer = ColorVisualizer(input_colors)
    visualizer.show()
    sys.exit(app.exec_())