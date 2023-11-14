
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QComboBox, QPushButton

try:
    from . import jt_config as jtc
    from . import jt_util as util
except:
    import jt_config as jtc
    import jt_util as util


class MyMainWindow(QMainWindow):
    def __init__(self, jt_config, plots=None):
        super().__init__()

        self.config_obj = jt_config
        self.plots = plots
        self.initUI()

    def initUI(self):
        # Set initial size of the window
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Reporting and Analytics Viewer')

        # Create central widget and main layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create combo box
        combo_box = QComboBox()
        main_layout.addWidget(combo_box)

        # Create Matplotlib canvas
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(self.canvas)

        # Create navigation buttons
        button_layout = QHBoxLayout()
        previous_button = QPushButton('Previous')
        previous_button.clicked.connect(self.showPreviousGraph)
        button_layout.addWidget(previous_button)

        next_button = QPushButton('Next')
        next_button.clicked.connect(self.showNextGraph)
        button_layout.addWidget(next_button)

        quit_button = QPushButton('Quit')
        quit_button.clicked.connect(self.close)
        button_layout.addWidget(quit_button)

        main_layout.addLayout(button_layout)

        # Initialize graph data
        self.graph_data = [np.random.rand(10), np.random.rand(10), np.random.rand(10)]
        self.current_graph_index = 0
        self.plotGraph()

        self.show()

    def plotGraph(self):
        self.ax.clear()
        self.ax.plot(self.graph_data[self.current_graph_index])
        self.ax.set_xlabel('X-Axis')
        self.ax.set_ylabel('Y-Axis')
        self.canvas.draw()

    def showPreviousGraph(self):
        self.current_graph_index = (self.current_graph_index - 1) % len(self.graph_data)
        self.plotGraph()

    def showNextGraph(self):
        self.current_graph_index = (self.current_graph_index + 1) % len(self.graph_data)
        self.plotGraph()


if __name__ == '__main__':
    config_obj = jtc.JT_Config('taylor performance', 'TPC')
    app = QApplication(sys.argv)
    mainWindow = MyMainWindow(config_obj)
    sys.exit(app.exec())
