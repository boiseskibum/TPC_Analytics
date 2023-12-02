from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt6.QtCore import Qt

class ImageWithLineWidget(QLabel):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image = QPixmap(image_path)
        self.line_x = 50

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.image)

        pen = QPen(QColor("red"))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(self.line_x, 0, self.line_x, self.height())

    def moveLine(self, offset):
        self.line_x += offset
        self.update()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.image_widget = ImageWithLineWidget("graph.png", self)
        layout.addWidget(self.image_widget)

        self.move_button = QPushButton("Move Line")
        self.move_button.clicked.connect(self.onMoveButtonClicked)
        layout.addWidget(self.move_button)

        self.setLayout(layout)

    def onMoveButtonClicked(self):
        self.image_widget.moveLine(20)

app = QApplication([])
window = MainWindow()
window.show()
app.exec()
