from jt_main_analytics_designer import Ui_MainAnalyticsWindow
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QTreeWidgetItem
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen, QColor
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
import sys, cv2, platform

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import seaborn as sns   # pip install seaborn

sys.path.append('./share')

# Importing Colors
colors_blue = sns.color_palette('Blues', 10)
colors_grey = sns.color_palette('Greys', 10)
colors = sns.color_palette('rocket', 10)
colors_icefire = sns.color_palette('icefire', 10)
colors3 = sns.color_palette('rainbow', 5)
colors_seismic = sns.color_palette('seismic', 10)

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

import jt_util as util

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
from share import jt_util as util
from share import jt_trial_display as jttd
from share import jt_trial_manager as jttm
from share import jt_config as jtc




trial_mgr_filename = 'all_athletes.json'

######################################################################################
# Special use QLabel class tht has a vertical line on it so that when the
# user moves the bar left and right it moves a vertical bar to indicate where time is at
class ImageWithLineWidget(QLabel):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image = QPixmap(image_path)
        self.line_x = 0

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.image)

        pen = QPen(QColor("red"))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(self.line_x, 0, self.line_x, self.height())

    def moveLine(self, new_x):
        self.line_x = new_x
        self.update()

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
        self.video1_capture = None
        self.video2_capture = None
        self.srt_label_graphic = None

        #if this is launched from parent window then grab its child mgr object
        if parent != None:
            self. trial_mgr_obj = parent.trial_mgr_obj
        else:
            self.trial_mgr_obj = jttm.JT_JsonTrialManager(self.config_obj)

        self.load_tree()

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

    def item_clicked(self, item, column):

        if item.childCount() == 0:
            parent_path = ""
            current_item = item
            item_text = item.text(0)

            while current_item.parent():
                parent_path = f"/{current_item.text(0)}{parent_path}"
                current_item = current_item.parent()
            original_filename = item.data(0, Qt.ItemDataRole.UserRole)
            trial_display = self.trial_mgr_obj.get_trial_display(original_filename, item_text)
            self.set_trial_display(trial_display)

            log.debug(f"Clicked: {item_text}, Parent Path: {parent_path}, original_filename: {original_filename}")

    def set_video1(self, filename):
        #connect to video
        self.video1_capture = cv2.VideoCapture(filename)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.current_frame = 0
        self.total_frames = int(self.video1_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.video_speed = 30   #frames per second
        self.videoSlider.setMaximum(self.total_frames)

    def set_trial_display(self, trial):
        self.current_trial = trial
        self.label_athlete_value.setText(trial.athlete)
        self.label_protocol_value.setText(trial.protocol)
        self.label_date_value.setText(trial.date_str)
        self.label_trial_value.setText(trial.trial_name)

        # add graphic to screen
        if len(trial.graph_images) > 0:
            key, image_path = next(iter(trial.graph_images.items()))

            try:

                # change out the existing QLabel button for my custom Lable Widget
                if self.srt_label_graphic is None:
                    self.srt_label_graphic = ImageWithLineWidget(image_path)
                    self.verticalLayout.replaceWidget(self.label_graphic, self.srt_label_graphic)
                    self.label_graphic.deleteLater()  # Remove the label from the layout and delete it

                pixmap = QPixmap(image_path)
                label_size = self.srt_label_graphic.size()
                w = label_size.width()
                h = label_size.height()
                w = 400  # the width is the driving factor, needs to be figured out somehow better than this hack
                h = 200
                scaled_pixmap = pixmap.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio)
                self.srt_label_graphic.setPixmap(scaled_pixmap)
            except:
                log.error(f"Failed to scale pixmap for: {image_path}")

        # add videos to screen

    def play(self):
        print(f"pressed play: {self.current_frame}")
        if self.video1_capture == None:
            return

        if self.timer.isActive():
            self.timer.stop()
        else:
            self.timer.start(self.video_speed)  #FPS

    def stop(self):
        print(f"pressed stop; {self.current_frame}")
        if self.video1_capture == None:
            return
        self.timer.stop()

    def rewind_1(self):
        print(f"pressed rewind: {self.current_frame}")
        if self.video1_capture == None:
            return

        self.timer.stop()
        self.current_frame -= 2
        if self.current_frame < 0:
            self.current_frame = -1     # this is to take into account that update frame will add one to it automatically
        self.video1_capture.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
        self.update_frame()

    def rewind_chunk(self):
        print(f"pressed rewind chunk: {self.current_frame}")
        if self.video1_capture == None:
            return

        self.timer.stop()
        self.current_frame -= self.chunk
        if self.current_frame < 0:
            self.current_frame = -1     # this is to take into account that update frame will add one to it automatically
        self.video1_capture.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
        self.update_frame()

    def rewind_to_start(self):
        print(f"pressed rewind to start: {self.current_frame}")
        if self.video1_capture == None:
            return

        self.video1_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.current_frame = -1     #update frame will move it to frame zero
        self.update_frame()

    def forward_1(self):
        print(f"pressed forward: {self.current_frame}")
        if self.video1_capture == None:
            return

        self.timer.stop()
        self.update_frame()   #this automatically moves one step forward

    def forward_chunk(self):
        print(f"pressed forward chunk: {self.current_frame}")
        if self.video1_capture == None:
            return

        self.timer.stop()
        self.current_frame += self.chunk - 1
        if self.current_frame > self.total_frames:
            self.current_frame = self.total_frames
        self.update_frame()   #this automatically moves one step forward

    def slider_value_changed(self, value):
        print(f"slider value changed: {value}")
        if self.video1_capture == None:
            return

        self.timer.stop()
        self.current_frame = value
        self.video1_capture.set(cv2.CAP_PROP_POS_FRAMES, value)
        self.update_frame()

    def update_frame(self):
        if self.video1_capture == None:
            return

        ret, frame = self.video1_capture.read()
        if ret:
            if self.current_frame > 0:
                self.video1_capture.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
            self.current_frame += 1

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            bytes_per_line = 3 * width

            resized_frame = cv2.resize(rgb_frame, (640, 480))
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

            self.srt_label_graphic.moveline()

            #update the slider position
            self.videoSlider.valueChanged.disconnect(self.slider_value_changed) # disconnect the signla
            self.videoSlider.setValue(self.current_frame)
            self.videoSlider.valueChanged.connect(self.slider_value_changed)  # Reconnect the signal


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = JT_Analytics_UI()

    path_zTest = path_app + 'zTest/'
    fp = path_zTest + 'JTSextL_Mickey_2023-08-08_17-36-53.csv'
    fp_video1 = path_zTest + 'test_video1.mp4'
    fp_graph = path_zTest + 'graph1.png'

    trial = jttd.JT_TrialDisplay(fp)
    trial.attach_video("video1", fp_video1)
    trial.attach_graph("graph1", fp_graph)

    window.set_trial_display(trial)
#    window.load_tree()

    window.set_video1('resources/testing/test_video.mp4')

    window.show()

    result = app.exec()
    sys.exit(result)
