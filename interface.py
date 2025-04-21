from work_alg import func
from WallArtGenerate import Ui_MainWindow
from palette import ColorVisualizer

import sys
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox, QMainWindow
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from PIL import Image




class MyApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.visualizer_window = None  # Добавляем атрибут для хранения ссылки на окно визуализатора

        # Подключение кнопок к функциям
        self.loadImageButton.clicked.connect(self.load_image)
        self.loadPaletteButton.clicked.connect(self.load_palette)
        self.block_size.clicked.connect(self.enter_size_click)
        self.select_format.activated.connect(self.current_format)
        self.generateButton.clicked.connect(self.generate)
        self.size = None
        self.width = None
        self.height = None
        self.path = None
        self.input_colors = []
        self.format_to_save = ".cvs"  # может быть еще .txt

    def load_image(self):
        # Открываем проводник для выбора изображения
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "JPEG Files (*.jpg)")
        if file_name:
            # Загружаем изображение и получаем его размеры
            image = Image.open(file_name)
            self.width, self.height = image.size
            self.path = file_name

    def is_valid_color_line(self, line: str) -> bool:
        # Требуемый формат строки палитры - 3 числа от 0 до 256
        parts = line.split()
        if len(parts) != 3:
            return False
        # Все числа целые
        try:
            r, g, b = map(int, parts)
        except ValueError:
            return False
        # Верный диапазон
        return all(0 <= num <= 256 for num in (r, g, b))

    def load_palette(self):
        # Открываем проводник для выбора файла с палитрой
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Palette File", "", "Text Files (*.txt)")

        if not file_name:
            return

        try:
            with open(file_name, 'r') as file:
                lines = file.readlines()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"File read error: {str(e)}")
            return

        error_lines = []
        for i, line in enumerate(lines, 1):
            stripped_line = line.strip()
            # пустые строки
            if not stripped_line:
                continue
            # непустые
            if not self.is_valid_color_line(stripped_line):
                error_lines.append(i)

        # есть ошибки - показываем и прерываем
        if error_lines:
            error_msg = "Invalid data in lines: " + ", ".join(map(str, error_lines))
            QMessageBox.critical(self, "Format Error", error_msg)
            return

        # все ок - парсим
        self.input_colors = []
        for line in lines:
            stripped_line = line.strip()
            if stripped_line:
                r, g, b = map(int, stripped_line.split())
                self.input_colors.append((r, g, b))

        # Выводим инфу о загруженной палитре
        if self.visualizer_window:
            self.visualizer_window.close()  # Закрываем предыдущее окно, если оно было

        self.visualizer_window = ColorVisualizer(self.input_colors)
        self.visualizer_window.setAttribute(Qt.WA_DeleteOnClose, False)  # Не удалять объект при закрытии
        self.visualizer_window.show()

    def enter_size_click(self):
        text = self.lineEdit.text()
        if text.isdigit():
            self.size = int(text)
            info_msg = "Success enter size"
            QMessageBox.information(self, "Success", info_msg)
        else:
            error_msg = "Invalid number"
            QMessageBox.critical(self, "Format Error", error_msg)
            return

    def current_format(self, _):
        ctext = self.select_format.currentText()
        self.format_to_save = ctext

    def generate(self):
        # Проверяем, загружены ли изображение и палитра
        if not all([self.width, self.height, self.path, self.input_colors, self.size]):
            QMessageBox.warning(self, "Error", "Please load all things before generating.")
            return
        # Вызываем функцию генерации

        func(self.width, self.height, self.path, self.input_colors, self.format_to_save, self.size)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_app = MyApp()
    my_app.show()
    sys.exit(app.exec_())