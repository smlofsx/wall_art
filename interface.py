from work_alg import func
from WallArtGenerate import Ui_MainWindow

import sys
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox, QMainWindow
from PyQt5.QtGui import QImage, QPixmap
from PIL import Image


class MyApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Подключение кнопок к функциям
        self.loadImageButton.clicked.connect(self.load_image)
        self.loadPaletteButton.clicked.connect(self.load_palette)
        self.generateButton.clicked.connect(self.generate)


        self.width = None
        self.height = None
        self.path = None
        self.input_colors = []

    def load_image(self):
        # Открываем проводник для выбора изображения
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "JPEG Files (*.jpg)")
        if file_name:
            # Загружаем изображение и получаем его размеры
            image = Image.open(file_name)
            self.width, self.height = image.size
            self.path = file_name
            # Выводим информацию о загруженном изображении
            #self.imageLabel.setText(f"Loaded Image: {file_name}\nWidth: {self.width}, Height: {self.height}")

    def load_palette(self):
        # Открываем проводник для выбора файла с палитрой
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Palette File", "", "Text Files (*.txt)")
        if file_name:
            # Читаем цвета из файла
            with open(file_name, 'r') as file:
                lines = file.readlines()
                self.input_colors = [tuple(map(int, line.strip().split())) for line in lines]
            # Выводим информацию о загруженной палитре
            #self.paletteLabel.setText(f"Loaded Palette: {file_name}\nColors: {self.input_colors}")

    def generate(self):
        # Проверяем, загружены ли изображение и палитра
        if not all([self.width, self.height, self.path, self.input_colors]):
            QMessageBox.warning(self, "Error", "Please load both image and palette before generating.")
            return
        # Вызываем функцию генерации
        func(self.width, self.height, self.path, self.input_colors)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_app = MyApp()
    my_app.show()
    sys.exit(app.exec_())
