import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget
#from matplotlib.backends.backend_qt6agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

class GraphApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Matplotlib Line Graph with PyQt6")
        self.setGeometry(100, 100, 800, 600)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.ax = self.figure.add_subplot(111)
        self.line, = self.ax.plot([], [])

        self.button = QPushButton("Move Line")
        self.button.clicked.connect(self.move_line)
        layout.addWidget(self.button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.plot_graph()

    def plot_graph(self):
        x = np.linspace(0, 100, 500)
        y = np.sin(x)
        self.ax.clear()
        self.ax.plot(x, y)
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_title("Sine Wave")

        self.line_position = 20
        self.vertical_line = self.ax.axvline(x=self.line_position, color='r', linestyle='--')
        self.canvas.draw()

    def move_line(self):
        self.line_position += 20
        self.vertical_line.set_xdata(self.line_position)
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GraphApp()
    window.show()
    sys.exit(app.exec())
