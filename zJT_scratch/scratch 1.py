import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
import pandas as pd


class MatplotlibWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        # Example data with datetime objects
        dates = pd.date_range('2023-01-01', periods=5, freq='D')
        values = [1, 3, 2, 5, 4]

        # Plotting
        self.ax.plot(dates, values)

        # Formatting the dates on the x-axis to display only the date
        self.ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
        self.ax.xaxis.set_major_locator(mdates.DayLocator())

        # Rotate x-axis labels to 45 degrees
        for label in self.ax.get_xticklabels():
            label.set_rotation(45)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.matplotlib_widget = MatplotlibWidget()
        self.setCentralWidget(self.matplotlib_widget)
        self.setWindowTitle("Matplotlib Date Plot Example")
        self.setGeometry(100, 100, 800, 600)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainApp = App()
    mainApp.show()
    sys.exit(app.exec())
