from jt_main_analytics_designer import Ui_MainAnalyticsWindow
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QTreeWidgetItem
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen, QColor
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

import sys, cv2, platform
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import seaborn as sns   # pip install seaborn

#sys.path.append('./share')

# Importing Colors
colors_blue = sns.color_palette('Blues', 10)
colors_grey = sns.color_palette('Greys', 10)
colors = sns.color_palette('rocket', 10)
colors_icefire = sns.color_palette('icefire', 10)
colors3 = sns.color_palette('rainbow', 5)
colors_seismic = sns.color_palette('seismic', 10)

# used for two different color of lines
jt_color_list = [colors_seismic[2], colors_icefire[4] ]

######################################################################
# set up path and debuggging

# retrieve username and platform information
import getpass as gt

my_username = gt.getuser()
my_platform = platform.system()

# appends the path to look for files to the existing path

# mount drive if in google collab()
if my_platform == "Linux":

    from google.colab import drive

    try:
        drive.mount('/gdrive')
    except:
        print("INFO: Drive already mounted")

    # required to import jt_util
    sys.path.append('/gdrive/MyDrive/Colab Notebooks')

from share import jt_util as util

# set base and application path
path_base = util.jt_path_base()  # this figures out right base path for Colab, MacOS, and Windows

# logging configuration - the default level if not set is DEBUG
log = util.jt_logging()

log.msg(f'INFO - Valid logging levels are: {util.logging_levels}')
log.set_logging_level("WARNING")  # this will show errors but not files actually processed

# setup path variables for base and misc
path_app = path_base + 'Force Plate Testing/'

# if __name__ == "__main__":
#     import jt_util as util
#     import jt_trial_display as jttd
#     import jt_trial_manager as jttm
#     import jt_config as jtc
#
# else:
#from share import jt_trial_display as jttd
from share import jt_trial as jtt
from share import jt_trial_manager as jttm
from share import jt_config as jtc
from share import jt_protocol as jtp
from share import jt_athletes as jta

trial_mgr_filename = 'all_athletes.json'

######################################################################################
######################################################################################
######################################################################################
class JT_Analytics_UI(QMainWindow, Ui_MainAnalyticsWindow):
    closed = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        # calls the setup methon instead of the python class created from the UI
        self.setupUi(self)

        # configuration object for keys and values setup
        self.config_obj = jtc.JT_Config(path_app)

        ##### Athletes #####
        try:
            # create the athletes Object
            self.athletes_obj = jta.JT_athletes(self.config_obj) # get list of valid athletes from CSV file
        except:
            log.critical(f'Could not load athletes')

        ##### Protocol #####
        # Get list of protocols, throw error message if unsuccessful at getting list
        try:
            self.protocol_obj = jtp.JT_protocol(self.config_obj)
        except:
            log.critical(f'Could not load athletes')

        # set up callbacks
        self.pushButton_play.clicked.connect(self.play)
        self.pushButton_forward_1.clicked.connect(self.forward_1)
        self.pushButton_forward_chunk.clicked.connect(self.forward_chunk)
        self.pushButton_stop.clicked.connect(self.stop)
        self.pushButton_rewind_1.clicked.connect(self.rewind_1)
        self.pushButton_rewind_chunk.clicked.connect(self.rewind_chunk)
        self.pushButton_rewind_to_start.clicked.connect(self.rewind_to_start)
        self.videoSlider.valueChanged.connect(self.slider_value_changed)

        self.videoSlider.setMinimum(0)

        self.treeWidget.itemClicked.connect(self.item_clicked)

        self.chunk = 10

        self.current_frame = 0
        self.current_data_point = 0
        self.total_frames = 0
        self.total_data_points = 0
        self.video1_capture = None
        self.video2_capture = None
        self.srt_label_graphic = None

        #if this is launched from parent window then grab its child mgr object
        if parent != None:
            self. trial_mgr_obj = parent.trial_mgr_obj
        else:
            self.trial_mgr_obj = jttm.JT_JsonTrialManager(self.config_obj)

        self.load_tree()

        #set up for graph
        # change out the existing QLabel button to canvas
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.verticalLayout.addWidget(self.canvas)
        self.verticalLayout.replaceWidget(self.label_graphic, self.canvas)

        #add graph
        self.ax = self.figure.add_subplot(111)
#        self.line, = self.ax.plot([], [])

    def closeEvent(self, event):
        self.closed.emit()


    #load tree widget
    def load_tree(self):
        df = self.trial_mgr_obj.load_all_trials()

        if len(df) < 1:
            return

        unique_athletes = df['athlete'].unique()
        for athlete in unique_athletes:
            athlete_item = QTreeWidgetItem([athlete])
            self.treeWidget.addTopLevelItem(athlete_item)

            # Filter DataFrame for the target dates
            athlete_df = df[df["athlete"] == athlete]
            unique_dates = athlete_df['date'].unique()


            for date in unique_dates:
                date_item = QTreeWidgetItem([date])
                athlete_item.addChild(date_item)

                date_df = athlete_df[athlete_df["date"] == date]
                unique_timestamps = date_df['timestamp'].unique()

                # Note that a timestamp is essentially a trial at this point
                protocol_counts = {}  # Dictionary to store counts
                for timestamp in unique_timestamps:
                    filtered_df = df[df["timestamp"] == timestamp]
                    original_filename = filtered_df.iloc[0]["original_filename"]
                    protocol = filtered_df.iloc[0]["protocol"]
                    if protocol in protocol_counts:
                        protocol_counts[protocol] += 1
                    else:
                        protocol_counts[protocol] = 1
                    trial_name = f"{protocol}-{protocol_counts[protocol]}"

                    trial_item = QTreeWidgetItem([trial_name])
                    date_item.addChild(trial_item)
                    trial_item.setData(0, Qt.ItemDataRole.UserRole, original_filename)

        self.expand_tree_widget(self.treeWidget)


    def expand_tree_widget(self, tree_widget):
        def expand_items(item):
            item.setExpanded(True)
            for i in range(item.childCount()):
                expand_items(item.child(i))

        for i in range(tree_widget.topLevelItemCount()):
            expand_items(tree_widget.topLevelItem(i))

    def item_clicked(self, item, column):

        if item.childCount() == 0:
            parent_path = ""
            current_item = item
            item_text = item.text(0)

            while current_item.parent():
                parent_path = f"/{current_item.text(0)}{parent_path}"
                current_item = current_item.parent()
            original_filename = item.data(0, Qt.ItemDataRole.UserRole)

            trial = self.trial_mgr_obj.get_trial_file_path(original_filename, item_text)

            trial.set_athletes_protocol_objects(self.athletes_obj, self.protocol_obj)
            trial.get_trial_data()
            trial.trial_name = item_text
#            log.debug(f"filepath {trial.file_path}&&&")

            self.set_trial(trial)

            log.debug(f"Clicked: {item_text}, Parent Path: {parent_path}, original_filename: {original_filename}, filepath {trial.file_path}---")

    def set_trial(self, trial):
        self.current_trial = trial
        self.label_athlete_value.setText(trial.athlete)
        self.label_protocol_value.setText(trial.protocol)
        self.label_date_value.setText(trial.date_str)
        self.label_trial_value.setText(trial.trial_name)

        self.ax.clear()

        #plot the graph, validate there is one
        if len(self.current_trial.graphs) > 0:
            # graph the first key value pair from the dictionary.  Probably one one key value pair but this was
            # set up to handle more in the future
            first_key, graph = next(iter(self.current_trial.graphs.items()))
            self.ax.set_title(graph.get('title', "no title set"))
            self.ax.set_xlabel(graph.get('xlabel', 'no xlabel'))
            self.ax.set_ylabel(graph.get('ylabel', 'no ylabel'))
            self.elapsed_time = graph.get('elapsed_time', 0)

            # draw the lines on the graph
            lines_dict = graph["lines"]
            color_i=0
            j = 0   # counter
            for key, line in lines_dict.items():
                my_color = jt_color_list[color_i]
                self.total_data_points = len(line)
                print(f"TOTAL DATA POINTS: {self.total_data_points}")
                self.graph_x_seconds = np.linspace(0, self.elapsed_time, self.total_data_points)   # create the x values so they are in seconds
                self.ax.plot(self.graph_x_seconds, line, linestyle='-', label=key, color=my_color, linewidth=1)
                color_i += 1
                if color_i > len(jt_color_list):
                    color_i = 0

            self.current_data_point = 0
            self.vertical_line = self.ax.axvline(x=self.current_data_point, color='g', linestyle='--')
            self.canvas.draw()

            # set the video files for video 1

            if len(trial.video_files) > 0:
                first_key, video = next(iter(trial.video_files.items()))
                if video is not None:
                    self.set_video1(video)

            #adjust the number of datapoints
            self.videoSlider.setMaximum(self.total_data_points - 1)


    def set_video1(self, filename):
        if len(filename) < 1:
            # Do something to disable video
            pass

        #connect to video
        self.video1_capture = cv2.VideoCapture(filename)
        self.video_play_timer = QTimer(self)
        self.video_play_timer.timeout.connect(self.update_frame)
        self.current_frame = 0
        self.total_frames = int(self.video1_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.video_speed = 30   #frames per second
        self.update_frame()
#        log.debug(f"Slider - total frames: {self.total_frames}")

    # sets data for the next color and draws the graph

    def play(self):
#        print(f"pressed play: {self.current_frame}")
        if self.video1_capture == None:
            return

        if self.video_play_timer.isActive():
            self.video_play_timer.stop()
        else:
            self.video_play_timer.start(self.video_speed)  #FPS

    def stop(self):
#        print(f"pressed stop; {self.current_frame}")
        if self.video1_capture == None:
            return
        self.video_play_timer.stop()

    def rewind_1(self):
#        print(f"pressed rewind: {self.current_frame}")
        if self.video1_capture == None:
            return

        self.video_play_timer.stop()
        self.current_data_point -= 1
        if self.current_data_point < 0:
            self.current_data_point = 0     # this is to take into account that update frame will add one to it automatically
        self.update_frame()

    def rewind_chunk(self):
#        print(f"pressed rewind chunk: {self.current_frame}")
        if self.video1_capture == None:
            return

        self.video_play_timer.stop()
        self.current_data_point -= self.chunk
        if self.current_data_point < 0:
            self.current_data_point = 0     # this is to take into account that update frame will add one to it automatically
        self.update_frame()

    def rewind_to_start(self):
        if self.video1_capture == None:
            return

        self.video_play_timer.stop()
        self.current_data_point = 0     #update frame will move it to frame zero
        self.update_frame()

    def forward_1(self):
 #       print(f"pressed forward: {self.current_frame}")
        if self.video1_capture == None:
            return

        self.current_data_point += 1
        self.video_play_timer.stop()
        self.update_frame()   #this automatically moves one step forward

    def forward_chunk(self):
#        print(f"pressed forward chunk: {self.current_frame}")
        if self.video1_capture == None:
            return

        self.video_play_timer.stop()
        self.current_data_point += self.chunk
        if self.current_data_point > self.total_data_points:
            self.current_data_point = self.total_data_points
        self.update_frame()   #this automatically moves one step forward

    def slider_value_changed(self, value):
#        print(f"slider value changed: {value}")
        if self.video1_capture == None:
            return

        self.video_play_timer.stop()
        self.current_data_point = value
        self.update_frame()

    def set_vertical_bar(self):

        if self.vertical_line is not None:
            line_pos = self.graph_x_seconds[self.current_data_point]
            self.vertical_line.set_xdata([line_pos])
            self.canvas.draw()

    def update_frame(self):
        if self.video1_capture == None:
            return

        old_d = self.current_data_point
        old_f = self.current_frame

        #ratio is used for calculations of graph compared to video
        ratio = self.total_frames / self.total_data_points

        # if timer is active move the frame forward.  If inactive we calculate which
        # frame to show
        if self.video_play_timer.isActive():
            self.current_frame += 1
            self.current_data_point = int( self.current_frame/ratio )
        else:
            # calculate which frame should be shown.  This is basically the number of
            # frames of video divided by the total points being graphed.
            ratio = self.total_frames / self.total_data_points
            self.current_frame = int(self.current_data_point * ratio)
            if self.current_frame < 0:
                self.current_frame = 0
            elif self.current_frame >= self.total_frames:
                self.current_frame = self.total_frames - 1

        #last check to make sure datapoints are between correct ranges.
        if self.current_data_point < 0:
            self.current_data_point = 0
        elif self.current_data_point >= self.total_data_points:
            self.video_play_timer.stop()
            self.current_data_point = self.total_data_points - 1


#        print(f"data: {self.current_data_point}, frame: {self.current_frame}   ---   d: {old_d}, f: {old_f}")

        # Set the frame position to the desired frame number
        self.video1_capture.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)

        # Read the specific frame
        ret, frame = self.video1_capture.read()
        if ret:

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            bytes_per_line = 3 * width

            resized_frame = cv2.resize(rgb_frame, (740, 480))
            # Display the frame in the video widget
            image = QImage(
                resized_frame,
                resized_frame.shape[1],
                resized_frame.shape[0],
                QImage.Format.Format_RGB888,
            )

#            q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)

            q_pixmap = QPixmap.fromImage(image)
            self.label_video1.setPixmap(q_pixmap)

            self.set_vertical_bar()

            #update the slider position
            self.videoSlider.valueChanged.disconnect(self.slider_value_changed) # disconnect the signla
            self.videoSlider.setValue(self.current_data_point)
            self.videoSlider.valueChanged.connect(self.slider_value_changed)  # Reconnect the signal


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = JT_Analytics_UI()

    path_zTest = path_app + 'zTest/'
    fp = path_zTest + 'JTDcmj_huey_2023-08-17_00-38-07.csv'
#    fp = path_zTest + 'JTSextL_Mickey_2023-08-08_17-36-53.csv'
    fp_video1 = path_zTest + 'test_video1.mp4'
    fp_graph = path_zTest + 'graph1.png'

#    trial = jttd.JT_TrialDisplay(fp)
#    trial.attach_video("video1", fp_video1)
#    trial.attach_graph("graph1", fp_graph)

    trial = jtt.JT_Trial()
    trial.set_athletes_protocol_objects(window.athletes_obj, window.protocol_obj)
    trial.retrieve_trial(fp)
    trial.get_trial_data()
    trial.trial_name = "srt test trial"

    trial.video_files["video1"]: fp_video1

    window.set_trial(trial)
#    window.load_tree()

    window.set_video1('resources/testing/test_video.mp4')

    window.show()

    result = app.exec()
    sys.exit(result)
