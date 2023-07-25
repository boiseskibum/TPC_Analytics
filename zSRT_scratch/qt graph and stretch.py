import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.lines import Line2D

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
        ax = self.canvas.figure.add_subplot(111)
        ax.plot([1, 2, 3, 4, 5, 6, 7, 8], label="line1")
        ax.plot([8, 7, 6, 5, 4, 3, 2, 1], label="line2")
        ax.legend()
        self.canvas.draw()

    def plot2(self):
        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(111)
        ax.plot([8, 7, 6, 5, 4, 3, 2, 1], label="line11")
        ax.legend()
        ax.set_xlabel('X-Axis')
        ax.set_ylabel('Y-Axis')
        ax.set_title('Matplotlib Graph with Legend')

        self.canvas.draw()


app = QApplication(sys.argv)
window = Window()
window.show()
app.exec()