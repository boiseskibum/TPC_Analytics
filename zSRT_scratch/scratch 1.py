import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget
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
        self.initUI()

    def initUI(self):
        tab_widget = QTabWidget()

        for i in range(4):
            x = [j for j in range(10)]  # Sample x data
            y = [j * (i + 1) for j in range(10)]  # Sample y data
            plot_widget = PlotWidget()
            plot_widget.plot(x, y)
            tab_widget.addTab(plot_widget, f'Plot {i + 1}')

        self.setCentralWidget(tab_widget)
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Multiple Plots Example')
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
