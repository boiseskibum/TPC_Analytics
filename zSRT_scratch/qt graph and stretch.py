import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.canvas = FigureCanvasQTAgg(plt.Figure())

        layout = QGridLayout()

        self.button1 = QPushButton('Plot 1')
        self.button1.clicked.connect(self.plot1)
        layout.addWidget(self.button1, 0, 0)

        self.button2 = QPushButton('Plot 2')
        self.button2.clicked.connect(self.plot2)
        layout.addWidget(self.button2, 0, 1)

        layout.addWidget(self.canvas, 1, 0, 1, 2)

        layout.setRowStretch(1, 1)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)

        self.setLayout(layout)

    def plot1(self):
        self.canvas.figure.clear()
        axes = self.canvas.figure.add_subplot(111)
        axes.plot([1, 2, 3, 4, 5, 6, 7, 8])
        self.canvas.draw()

    def plot2(self):
        self.canvas.figure.clear()
        axes = self.canvas.figure.add_subplot(111)
        axes.plot([8, 7, 6, 5, 4, 3, 2, 1])
        self.canvas.draw()


app = QApplication(sys.argv)
window = Window()
window.show()
app.exec()