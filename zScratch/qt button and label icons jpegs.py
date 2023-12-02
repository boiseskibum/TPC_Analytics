import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtGui import QPixmap, QIcon


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image Buttons and Labels")

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        w = 100
        h = 100

        # Icon
        ico_image = QPixmap("jt.ico").scaled(w, h)
        ico_image = QPixmap("gear_icon.png").scaled(w, h)
        ico_icon = QIcon(ico_image)

        # jpeg
        jpeg_image = QPixmap("KallieAndSteve.jpg").scaled(w, h)
        jpeg_icon = QIcon(jpeg_image)

        # Create the ico image button
        self.ico_button = QPushButton("ICO Button")
        self.ico_button.setIcon(ico_icon)
        self.ico_button.setIconSize(ico_image.size())
        layout.addWidget(self.ico_button)

        # Create the jpeg image button
        self.jpeg_button = QPushButton("JPEG Button")
        self.jpeg_button.setIcon(jpeg_icon)
        self.jpeg_button.setIconSize(jpeg_image.size())
        layout.addWidget(self.jpeg_button)

        # Create the ico label
        ico_label = QLabel(self)
        ico_label.setPixmap(ico_image)
        layout.addWidget(ico_label)

        # Create the jpeg label
        jpeg_label = QLabel(self)
        jpeg_label.setPixmap(jpeg_image)
        layout.addWidget(jpeg_label)

        # Connect button signals to callback functions
        self.ico_button.clicked.connect(self.on_ico_button_clicked)
        self.jpeg_button.clicked.connect(self.on_jpeg_button_clicked)
    def on_ico_button_clicked(self):
        print("ICO Button Clicked!")

    def on_jpeg_button_clicked(self):
        print("JPEG Button Clicked!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
