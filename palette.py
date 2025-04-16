import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QColor, QPainter, QPalette, QFont, QPainterPath
from PyQt5.QtCore import Qt, QRectF


class ColorBox(QLabel):
    def __init__(self, color):
        super().__init__()
        self.color = QColor(*color)
        self.setFixedSize(100, 100)
        self.setAlignment(Qt.AlignCenter)

        font = QFont()
        font.setFamily("Candara")
        font.setPointSize(12)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(15)
        self.setFont(font)

        # Отображаем значения RGB
        self.setText(f"{color[0]}, {color[1]}, {color[2]}")

        # Устанавливаем цвет текста в зависимости от яркости фона
        r, g, b = color
        if (r * 0.299 + g * 0.587 + b * 0.114) > 150:
            self.setStyleSheet("color: black; background: transparent;")
        else:
            self.setStyleSheet("color: white; background: transparent;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Создаем путь с закругленными углами
        path = QPainterPath()
        rect = QRectF(0, 0, self.width(), self.height())
        path.addRoundedRect(rect, 15, 15)  # 15 - радиус закругления

        # Заливаем прямоугольник цветом
        painter.fillPath(path, self.color)

        # Рисуем текст
        painter.drawText(rect, Qt.AlignCenter, self.text())


class ColorVisualizer(QWidget):
    def __init__(self, colors):
        super().__init__()
        self.colors = colors
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Визуализатор цветов RGB')
        self.setGeometry(100, 100, 600, 400)
        self.setStyleSheet("background-color: #fbf8f4;")  # Серый фон окна

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)  # Отступ между рядами
        main_layout.setContentsMargins(15, 15, 15, 15)  # Отступы от краев окна

        # Создаем строки по 5 цветов в каждой
        row_layout = None
        for i, color in enumerate(self.colors):
            if i % 5 == 0:
                row_layout = QHBoxLayout()
                row_layout.setSpacing(15)  # Отступ между цветами
                main_layout.addLayout(row_layout)

            color_box = ColorBox(color)
            row_layout.addWidget(color_box)

        # Добавляем кнопку закрытия
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

        # Добавляем возможность перемещения окна
        self.drag_position = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
