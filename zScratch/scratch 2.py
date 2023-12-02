import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class PlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plot(self, x, y):
        self.ax.clear()
        self.ax.plot(x, y)
        self.canvas.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_plot_index = 0
        self.initUI()

    def initUI(self):
        self.plot_data = [
            ([j for j in range(10)], [j * (i + 1) for j in range(10)]) for i in range(4)
        ]

        self.plot_widget = PlotWidget()
        self.plot_widget.plot(*self.plot_data[self.current_plot_index])

        next_button = QPushButton('Next', self)
        next_button.clicked.connect(self.showNextPlot)

        prev_button = QPushButton('Previous', self)
        prev_button.clicked.connect(self.showPreviousPlot)

        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)
        layout.addWidget(next_button)
        layout.addWidget(prev_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Multiple Plots Example')
        self.show()

    def showNextPlot(self):
        self.current_plot_index = (self.current_plot_index + 1) % len(self.plot_data)
        self.plot_widget.plot(*self.plot_data[self.current_plot_index])

    def showPreviousPlot(self):
        self.current_plot_index = (self.current_plot_index - 1) % len(self.plot_data)
        self.plot_widget.plot(*self.plot_data[self.current_plot_index])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
