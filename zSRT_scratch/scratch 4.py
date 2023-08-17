import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor

class ImageWidget(QWidget):
    def __init__(self, image_path):
        super().__init__()
        self.image = QPixmap(image_path)
        self.lines = []

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.image)

        pen = QPen()
        pen.setColor(QColor("red"))
        pen.setWidth(2)
        painter.setPen(pen)

        for line in self.lines:
            painter.drawLine(*line)

    def add_line(self, start_x, start_y, end_x, end_y):
        self.lines.append((start_x, start_y, end_x, end_y))
        self.update()

class ImageDisplayApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image Display with Lines")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = ImageWidget("gear_icon.png")
        self.setCentralWidget(self.central_widget)

        self.central_widget.add_line(100, 100, 300, 200)  # Example line coordinates

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageDisplayApp()
    window.show()
    sys.exit(app.exec())
