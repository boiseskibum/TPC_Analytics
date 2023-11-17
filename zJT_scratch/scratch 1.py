import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

    def plot(self, data, plot_type='line'):
        ax = self.figure.add_subplot(111)
        if plot_type == 'line':
            ax.plot(data)
        elif plot_type == 'scatter':
            ax.scatter(np.arange(len(data)), data)
        ax.set_title('PyQt6 Matplotlib Example')
        self.draw()


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'PyQt6 Matplotlib Example'
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 400
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Create tab widget
        tab_widget = QTabWidget()
        tab1 = QWidget()
        tab2 = QWidget()

        # Add tabs
        tab_widget.addTab(tab1, "Line Plot")
        tab_widget.addTab(tab2, "Scatter Plot")

        # Create first plot
        layout1 = QVBoxLayout()
        self.plot1 = PlotCanvas(tab1, width=5, height=4)
        self.plot1.plot([2, 4, 6, 8, 10], plot_type='line')
        layout1.addWidget(self.plot1)
        tab1.setLayout(layout1)

        # Create second plot
        layout2 = QVBoxLayout()
        self.plot2 = PlotCanvas(tab2, width=5, height=4)
        self.plot2.plot(np.random.rand(50), plot_type='scatter')
        layout2.addWidget(self.plot2)
        tab2.setLayout(layout2)

        # Set main widget
        self.setCentralWidget(tab_widget)
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec())
