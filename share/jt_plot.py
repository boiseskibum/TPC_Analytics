
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

import matplotlib.pyplot as plt
import seaborn as sns
colors_blue = sns.color_palette('Blues', 10)
colors_grey = sns.color_palette('Greys', 10)
colors = sns.color_palette('rocket', 10)
colors_icefire = sns.color_palette('icefire', 10)
colors3 = sns.color_palette('rainbow', 5)
colors_seismic = sns.color_palette('seismic', 10)

try:
    from . import jt_util as util
except:
    import jt_util as util

# logging configuration - the default level if not set is DEBUG
log = util.jt_logging()

class JT_plot:
    def __init__(self, title, xAxisLabel, yAxisLabel, data=None ):
        # title - graph title
        # xAxisLabel
        # yAxisLabel
        # data -  List of dictionaries that holds data for a single line, ALL are required
        #         looks like {x (1 dimensional array of data), y (ditto), lineLable, color}
        #         Example {'x': [1,2,3], 'y': [dates...], 'lineLable': "force", 'color': colors_seismic[2]}

        self.title = title
        self.xAxisLabel = xAxisLabel
        self.yAxisLabel = yAxisLabel
        self.data = data

        #optional data
        self.yMin = None
        self.yMax = None
        self.yBounds = None
        self.debug = False

    # sets the min and max values of the graph
    # yMin - this is for setting the axis
    # yMax - ditto

    def set_yminmax(self, yMin, yMax):
        self.yMin = yMin
        self.yMax = yMax

    #Vertical Bounds - allows horizontal lines to be drawn at each position in list [-40, 50, 120]
    # yBounds - List that contains y coordinate for horizonatal line (bounds)
    #         Example yBounds = [15, -15]
    def set_yBounds(self, yBounds):
        self.yBounds = yBounds

    #used to show the graph - generally only for debug
    def show_graph(self):
        plt.show()

    # save filename to disk
    # filename - filename to write out
    def save_to_file(self, filename):
        self._setup_plt()
        if (len(filename) > 0):
            plt.savefig(filename,
                        transparent=False,
                        facecolor='white', dpi=300,
                        bbox_inches="tight")
            log.debug(f'Saved Graph: {filename}')
        plt.close()

    def draw_on_pyqt(self, ):
        self._setup_plt()
        if (len(filename) > 0):
            plt.savefig(filename,
                        transparent=False,
                        facecolor='white', dpi=300,
                        bbox_inches="tight")
            log.debug(f'Saved Graph: {filename}')
        plt.close()

    # core work of setting up plt
    def _setup_plt(self):
        log.f(f'title: {self.title}')
        plt.figure(1, figsize=(8, 4))

        # creating labels
        plt.title(self.title, fontsize=14)
        plt.xlabel(self.xAxisLabel, fontsize=12)
        plt.ylabel(self.yAxisLabel, fontsize=12)

        x_ticks_temp = []  # defined so it can be set down below

        # plotting data for each line passed in
        for my_dict in self.data:
            x = my_dict.get("x")
            x_ticks_temp = x  # this is used further down to
            y = my_dict.get("y")
            label = my_dict.get("label")
            lineColor = my_dict.get("color")
            plt.plot(x, y, linestyle='-', marker='o', label=label, mfc='w', color=lineColor, markersize=5)

        # create bounding lines (this can be 1 or more)
        if self.yBounds is not None:
            for bounding_line in self.yBounds:
                plt.axhline(bounding_line, color='k', linestyle='--')

        plt.legend()
        plt.xticks(fontsize=8)
        plt.xticks(rotation=90)

        ax = plt.gca()  # returns current active axis
        ax.set_xticks(x_ticks_temp)

        # when ymin or ymax is None then it let it self determine
        ax.set_ylim(self.yMin, self.yMax)


if __name__ == "__main__":
    # set up colors to make easier
    jt_color1 = colors_seismic[2]
    jt_color2 = colors_icefire[4]

    class Window(QWidget):
        def __init__(self):
            super().__init__()

            self.lineX = [1, 2, 3, 4, 5, 6, 7, 8]
            self.line1 = [1, 2, 3, 4, 5, 6, 7, 8]
            self.line2 = [8, 7, 6, 5, 4, 3, 2, 1]
            self.line3 = [8, 7, 6, 5, 4, 3, 2, 1]

            line_data1 = [
                {'x': self.lineX, 'y': self.line1, 'label': 'line1', 'color': jt_color1},
                {'x': self.lineX, 'y': self.line2, 'label': 'line1', 'color': jt_color2}]
            output_filename = 'line1_test_case.png'
            self.my_plot1 = JT_plot('graph1', 'my X Label', 'my Y Label', line_data1)
#            self.my_plot1.save_to_file(output_filename)

            line_data2 = [
                {'x': self.lineX, 'y': self.line3, 'label': 'line1', 'color': jt_color1}]
            output_filename = 'line2_test_case.png'
            self.my_plot1 = JT_plot('graph2', 'my X Label', 'my Y Label', line_data2)
#            self.my_plot1.save_to_file(output_filename)

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
            ax.plot(self.line1, label="line1")
            ax.plot(self.line2, label="line2")
            ax.legend()
            self.canvas.draw()

        def plot2(self):
            self.canvas.figure.clear()
            ax = self.canvas.figure.add_subplot(111)
            ax.plot(self.line3, label="line11")
            ax.legend()
            ax.set_xlabel('X-Axis')
            ax.set_ylabel('Y-Axis')
            ax.set_title('Matplotlib Graph with Legend')

            self.canvas.draw()


    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec()