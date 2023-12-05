import random
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.dates import DateFormatter

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

jt_colors = [colors_seismic[2],
             colors_icefire[4],
             colors_icefire[7],
             colors_grey[9],
             colors_grey[6]]


# logging configuration - the default level if not set is DEBUG
log = util.jt_logging()

class JT_plot:
    def __init__(self, title, xAxisLabel, yAxisLabel, data ):
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
        self.output_filepath = None

        #optional data
        self.yMin = None
        self.yMax = None
        self.yBounds = None
        self.debug = False
        self.marker = 'o'

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

    def set_marker_none(self):
        self.marker = None

    def set_output_filepath(self, filepath):
        self.output_filepath = filepath

    #used to show the graph - generally only for debug


    def draw_on_pyqt(self, ax, figure= None):
        log.debug(f'title: {self.title}')

        #increase the space for the x axis if figure defined
        if figure is not None:
#            figure.set_size_inches(6, 4)
            figure.subplots_adjust(bottom=0.2)
#            figure.set_constrained_layout(True)d

        plt.tight_layout()

        # start with clear the existing graph
        ax.clear()

        # creating labels
        ax.set_title(self.title, fontsize=14)
        ax.set_xlabel(self.xAxisLabel, fontsize=12)
        ax.set_ylabel(self.yAxisLabel, fontsize=12)

        x_ticks_temp = []  # defined so it can be set down below

        # plotting data for each line passed in
        for my_dict in self.data:
            x = my_dict.get("x")
            x_ticks_temp = x  # this is used further down to
            y = my_dict.get("y")
            label = my_dict.get("label")
            try:
                lineColor = jt_colors[my_dict.get("color")]
            except:
                lineColor = jt_colors[0]

            if x is not None:
                ax.plot(x, y, linestyle='-', marker=self.marker, label=label, mfc='w', color=lineColor, markersize=5)
            else:
                ax.plot(y, linestyle='-', marker=self.marker, label=label, mfc='w', color=lineColor, markersize=5)

        # create bounding lines (this can be 1 or more)
        if self.yBounds is not None:
            for bounding_line in self.yBounds:
                ax.axhline(bounding_line, color='k', linestyle='--')

        ax.legend()

        # if x values were passed in
        if x is not None:
            ax.tick_params(axis='x', labelsize=8)
            ax.set_xticks(x_ticks_temp)
            ax.set_xticklabels(x, rotation=45)
            ax.xaxis.set_major_formatter(DateFormatter('%m-%d-%y'))

        ax.set_ylim(self.yMin, self.yMax)

        plt.close()

    # save file to disk  (unless debugging
    def save_plot_to_file(self, debug_it=False):

        # if filename isn't specified then get it from the local variable
        filepath = self.output_filepath

        # if filepath still isn't specifid then error out.
        if filepath == None:
            log.error(f'Save_plot_to_file - filepath to save is not specified')
            return

        # start with clear the existing graph
        plt.clf()
        plt.tight_layout()

        # this sets the size of the graph if it is not an axes (ie, it is plt)
#        plt.figure(1, figsize=(6, 3))

        # creating labels
        plt.title(self.title, fontsize=14)
        plt.xlabel(self.xAxisLabel, fontsize=12)
        plt.ylabel(self.yAxisLabel, fontsize=12)

        plt.xticks(fontsize=8, rotation=45)

        x_ticks_temp = []  # defined so it can be set down below

        # plotting data for each line passed in
        for my_dict in self.data:
            x = my_dict.get("x")
            x_ticks_temp = x  # this is used further down to
            y = my_dict.get("y")
            label = my_dict.get("label")
            try:
                lineColor = jt_colors[my_dict.get("color")]
            except:
                lineColor = jt_colors[0]


            if x is not None:
                plt.plot(x, y, linestyle='-', marker=self.marker, label=label, mfc='w', color=lineColor, markersize=5)
            else:
                plt.plot(y, linestyle='-', marker=self.marker, label=label, mfc='w', color=lineColor, markersize=5)

        # create bounding lines (this can be 1 or more)
        if self.yBounds is not None:
            for bounding_line in self.yBounds:
                plt.axhline(bounding_line, color='k', linestyle='--')

        plt.legend()

        # Adjust the margins
#        plt.subplots_adjust(bottom=0.2)  # Adjust the bottom margin

        ax = plt.gca()  # returns current active axis
        if x is not None:
            ax.tick_params(axis='x', labelsize=8)
            ax.set_xticks(x_ticks_temp)
            ax.set_xticklabels(x, rotation=45)
            ax.xaxis.set_major_formatter(DateFormatter('%m-%d-%y'))

        ax.set_ylim(self.yMin, self.yMax)

        if debug_it == False:
            if (len(filepath) > 0):
#                print(f"  ### saving image: {filepath}")
                plt.savefig(filepath,
                            transparent=False,
                            facecolor='white', dpi=200,
                            bbox_inches="tight")
                log.debug(f'Saved Graph: {filepath}')
            else:
                log.error(f'jt_plot - no file path specified: {filepath}')
                return ''
        else:
            log.error(f'****** SHOULD NOT BE HERE- about to plt.show: debug_it: {debug_it}  file_path: {filepath}')
            plt.show()
            pass

        plt.close()

        return filepath

# test plots for others to use like the PDF creation
def test_plots(num_plots = 5):
    plots = []
    lineX = [10, 20, 30, 40, 50, 60, 70, 80]
    line1 = [1, 2, 3, 4, 5, 6, 7, 8]
    line2 = [8, 7, 6, 5, 4, 3, 2, 1]
    line3 = [8, 7, 6, 5, 4, 3, 2, 2]
    line4 = [8, 7, 6, 5, 4, 5, 2, 3]
    line5 = [8, 7, 3, 5, 4, 6, 2, 4]
    line6 = [8, 7, 2, 5, 4, 6, 2, 4]

    list_of_lines = [line1, line2, line3, line4, line5, line6]

    line_data = [
        {'x': lineX, 'y': line1, 'label': 'line1', 'color': 0},
        {'x': lineX, 'y': line2, 'label': 'line2', 'color': 1}]
    plot = JT_plot('graph1', 'my X Label', 'my Y Label', line_data)
    plot.set_output_filepath('testing/line_data0.png')
    plots.append( plot )

    # no x value
    line_data = [
        {'y': line3, 'label': 'line1', 'color': 2}]
    plot = JT_plot('graph2', 'my X Label G3', 'my Y Label G3', line_data)
    plot.set_output_filepath('testing/line_data1.png')
    plots.append( plot )

    #always have 2 and then add on even more plots
    for i in range(2, num_plots):    #the plus 2 is for the fixed ones above
        line_num = len(list_of_lines) % i
        rando_num = random.randint(0, len(list_of_lines) -1)
        print(f'num_plots = {num_plots}, i: {i}, line_num: {line_num}, rando_num: {rando_num}, len_list_of_lines{len(list_of_lines)}')

        line_data = [
            {'x': list_of_lines[rando_num], 'y': line4, 'label': f'line-{line_num}', 'color': 0},
            {'x': lineX, 'y': line5, 'label': f'lineX', 'color': 1}]
        plot = JT_plot(f'graph - {i}', 'my X Label', 'my Y Label', line_data)
        plot.set_output_filepath(f'testing/line_data_{i}.png')
        plots.append( plot )


    return (plots)

if __name__ == "__main__":
    # set up colors to make easier


    class Window(QWidget):
        def __init__(self):
            super().__init__()

            self.lineX = [10, 20, 30, 40, 50, 60, 70, 80]
            self.line1 = [1, 2, 3, 4, 5, 6, 7, 8]
            self.line2 = [8, 7, 6, 5, 4, 3, 2, 1]
            self.line3 = [8, 7, 6, 5, 4, 3, 2, 1]

            line_data1 = [
                {'x': self.lineX, 'y': self.line1, 'label': 'line1', 'color': 0},
                {'x': self.lineX, 'y': self.line2, 'label': 'line2', 'color': 1}]
            self.my_plot1 = JT_plot('graph1', 'my X Label', 'my Y Label', line_data1)

            line_data2 = [
                {'x': self.lineX, 'y': self.line3, 'label': 'line1', 'color': 2}]
            self.my_plot2 = JT_plot('graph2', 'my X Label G2', 'my Y Label G2', line_data2)

            # no x value
            line_data3 = [
                {'y': self.line3, 'label': 'line1', 'color': 2}]
            self.my_plot3 = JT_plot('graph3', 'my X Label G3', 'my Y Label G3', line_data3)

            self.canvas = FigureCanvasQTAgg(plt.Figure())

            layout = QGridLayout()

            self.button1 = QPushButton('Plot 1')
            self.button1.clicked.connect(self.plot1)
            layout.addWidget(self.button1, 0, 0)

            self.button2 = QPushButton('Plot 2')
            self.button2.clicked.connect(self.plot2)
            layout.addWidget(self.button2, 0, 1)

            self.button3 = QPushButton('Plot 3')
            self.button3.clicked.connect(self.plot3)
            layout.addWidget(self.button3, 0, 2)

            self.button4 = QPushButton('Save Plot 2 to disk')
            self.button4.clicked.connect(self.savePlot2)
            layout.addWidget(self.button4, 0, 3)

            layout.addWidget(self.canvas, 1, 0, 1, 2)

            layout.setRowStretch(1, 1)
            layout.setColumnStretch(0, 1)
            layout.setColumnStretch(1, 1)

            self.setLayout(layout)

        def plot1(self):

            self.canvas.figure.clear()
            ax = self.canvas.figure.add_subplot(111)
            self.my_plot1.draw_on_pyqt(ax, self.canvas.figure)

            self.canvas.draw()

        def plot2(self):
            self.canvas.figure.clear()
            ax = self.canvas.figure.add_subplot(111)
            self.my_plot2.draw_on_pyqt(ax, self.canvas.figure)

            self.canvas.draw()

        def plot3(self):
            self.canvas.figure.clear()
            ax = self.canvas.figure.add_subplot(111)
            self.my_plot3.draw_on_pyqt(ax, self.canvas.figure)

            self.canvas.draw()

        def savePlot2(self):
            self.my_plot2.output_filepath = "testing/plot2_test.png"
            self.my_plot2.save_plot_to_file(True)   #shows the plot
            self.my_plot2.save_plot_to_file(False)    # saves plot to disk


    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec()
