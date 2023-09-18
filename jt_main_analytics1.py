from jt_main_analytics_designer import Ui_MainAnalyticsWindow
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QTreeWidgetItem,  QRadioButton
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QIcon, QTransform
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

import sys, cv2, platform, time
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
from share import jt_dialog as jtd
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
        self.checkBox_video1_enable.stateChanged.connect(self.checkbox_video1_enable_changed)
        self.checkBox_video1_enable.stateChanged.connect(self.checkbox_video2_enable_changed)
        self.checkBox_video1_overlay.stateChanged.connect(self.checkbox_video1_overlay_changed)
        self.checkBox_video2_overlay.stateChanged.connect(self.checkbox_video2_overlay_changed)
        self.checkBox_short_video.stateChanged.connect(self.checkBox_short_video_changed)

        # video playback speed
        self.radioButton_full.setChecked(True)
        self.radioButton_full.toggled.connect(self.radio_button_callback)
        self.radioButton_slow.toggled.connect(self.radio_button_callback)
        self.radioButton_super_slow.toggled.connect(self.radio_button_callback)

        self.videoSlider.setMinimum(0)

        self.treeWidget.itemClicked.connect(self.item_clicked)

        #player buttons
        # utility function to set icons on pushbuttons
        def add_pb_icon(image_path, pb, flip=False):
            pixmap = QPixmap(image_path)  # Replace with the path to your image
            if pixmap.isNull():
                print(f"Image '{image_path}' does not exist or is invalid.\n")
            if flip:
                pixmap = pixmap.transformed(QTransform().scale(-1, 1))
            icon = QIcon(pixmap)  # Replace with the path to your image
            pb.setIcon(icon)
            pb.setText("")

        add_pb_icon ( "resources/img/rewind-to-start.png", self.pushButton_rewind_to_start)
        add_pb_icon ( "resources/img/next-button-ff.png", self.pushButton_rewind_chunk, True)
        add_pb_icon ( "resources/img/next-button.png", self.pushButton_rewind_1, True)
        add_pb_icon ( "resources/img/stop-button.png", self.pushButton_stop)
        add_pb_icon ( "resources/img/play-button.png", self.pushButton_play)
        add_pb_icon ( "resources/img/next-button.png", self.pushButton_forward_1)
        add_pb_icon ( "resources/img/next-button-ff.png", self.pushButton_forward_chunk)

        self.chunk = 10

        self.speed_multiplier = 1

        # starting are always 0
        # min is where the video will start
        # current is where the video is at
        # max is the last point on video to show
        # total - is the furthest in the video it can go
        self.starting_data_point = 0
        self.starting_frame = 0
        self.min_data_point = 0
        self.min_frame = 0
        self.current_frame = 0
        self.current_data_point = 0
        self.max_frame = 0
        self.max_data_point = 0
        self.total_frames = 0
        self.total_data_points = 0

        self.video1_cv2 = None
        self.video2_capture = None
        self.srt_label_graphic = None
        self.video_play_timer = None

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
        self.verticalLayout_graph.addWidget(self.canvas)
        self.verticalLayout_graph.replaceWidget(self.label_graphic, self.canvas)

        #add graph
        self.ax = self.figure.add_subplot(111)
        self.video1_overlay = True
        self.video2_overlay = True
        self.video1_enabled = True
        self.video2_enabled = True
        self.short_video = False

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

            if self.video_play_timer:
                self.video_play_timer.stop()

            while current_item.parent():
                parent_path = f"/{current_item.text(0)}{parent_path}"
                current_item = current_item.parent()
            original_filename = item.data(0, Qt.ItemDataRole.UserRole)

            try:
                trial = self.trial_mgr_obj.get_trial_file_path(original_filename, item_text)

                trial.set_athletes_protocol_objects(self.athletes_obj, self.protocol_obj)
                trial.process_summary()

                trial.trial_name = item_text

                self.set_trial(trial)
            except:
                msg = f'Error processing {item_text}, limited functionality '
                jtd.JT_Dialog(parent=self, title="Exception",
                                   msg=msg,
                                   type="ok")
                log.error(f'{msg}, {original_filename}')


            log.debug(f"Clicked: {item_text}, Parent Path: {parent_path}, original_filename: {original_filename}, filepath {trial.file_path}---")

    def set_trial(self, trial):
        self.current_trial = trial
        self.label_athlete_value.setText(trial.athlete)
        self.label_protocol_value.setText(trial.protocol)
        self.label_date_value.setText(trial.date_str)
        self.label_trial_value.setText(trial.trial_name)

        self.ax.clear()

        # graph the first key value pair from the dictionary.  Probably one one key value pair but this was
        # set up to handle more in the future
        self.graph = self.current_trial.main_graph
        self.ax.set_title(self.graph.get('title', "no title set"))
        self.ax.set_xlabel(self.graph.get('xlabel', 'no xlabel'))
        self.ax.set_ylabel(self.graph.get('ylabel', 'no ylabel'))
        self.elapsed_time = self.graph.get('elapsed_time', 0)

        # draw the lines on the graph
        lines_dict = self.graph["lines"]
        color_i=0
        j = 0   # counter
        self.max_value = 0   #this is used later for drawing lines on the video
        for key, line in lines_dict.items():
            my_color = jt_color_list[color_i]
            self.total_data_points = len(line)
            self.min_data_point = 0
            self.max_data_point = self.total_data_points

            max_value = max( max(line), abs(min(line)))       # get the largest value between the abs of min and max of data points in the line
            self.max_value = max(self.max_value, max_value)   # get the largest value between of past lines if there was one

            if self.short_video == True and self.current_trial.short_start_index is not None:
                self.min_data_point = self.current_trial.short_start_index;  # change this in the future
            if self.short_video == True and self.current_trial.short_end_index is not None:
                self.max_data_point = self.current_trial.short_end_index    # change this in the future

            final_line = line[self.min_data_point:self.max_data_point]
            fl = len(final_line)
            l = len(line)
#                log.debug(f"TOTAL DATA POINTS: {self.total_data_points}")
            #calculate the min and max times to show on the graph
            start_time = self.min_data_point / self.total_data_points * self.elapsed_time
            end_time = self.max_data_point / self.total_data_points * self.elapsed_time



            # create the x values so they are in seconds
            self.graph_x_seconds = np.linspace(start_time, end_time, (self.max_data_point - self.min_data_point ) )
            lxsecs = len(self.graph_x_seconds)
            log.debug(f"line len: {l}, final_line len: {fl} graphx len {lxsecs}")
            self.ax.plot(self.graph_x_seconds, final_line, linestyle='-', label=key, color=my_color, linewidth=1)
            color_i += 1
            if color_i > len(jt_color_list):
                color_i = 0

        log.debug(f'set_trial - self.min_data_poing {self.min_data_point}. max_data_point: {self.max_data_point}, total_data_points: {self.total_data_points}')

        self.current_data_point = self.min_data_point
        self.vertical_line = self.ax.axvline(x=self.current_data_point, color='g', linestyle='--')
        self.ax.legend()
        self.canvas.draw()

        # set the video files for video 1

        self.video1_cv2 = None
        if len(trial.video_files) > 0:
            first_key, video = next(iter(trial.video_files.items()))
            if video is not None:
                self.set_video1(video)
        else:
            #should cause frame to be updated with static image
            self.update_frame()

        #adjust the number of datapoints
        self.videoSlider.setMinimum( self.min_data_point )
        self.videoSlider.setMaximum( self.max_data_point - 1)
        log.debug(f'min_data_point: {self.min_data_point}, max_data_point = {self.max_data_point}')


    def set_video1(self, filename):

        #connect to video
        if self.video_play_timer:
            self.video_play_timer.stop()

        if self.video1_cv2:
            self.video1_cv2.release()
            self.video1_cv2 = None

        if len(filename) < 1:
            # Do something to disable video
            pass

        self.video1_cv2 = cv2.VideoCapture(filename)
        self.video_play_timer = QTimer(self)
        self.video_play_timer.timeout.connect(self.update_frame)

        self.video_speed_full = int( 1000/30 )   #frames per second

        self.video_speed = int(self.video_speed_full/self.speed_multiplier)


        #set iniitial frames mins and maxes and current
        self.starting_frame = 0   # this will always be zero
        self.min_frame = self.starting_frame

        self.total_frames = int(self.video1_cv2.get(cv2.CAP_PROP_FRAME_COUNT))
        self.max_frame = self.total_frames

        # make adjustments if video is shortened
        if self.min_data_point > 0:
            self.min_frame = self.min_data_point/self.total_data_points * self.total_frames

        if self.max_data_point != self.total_data_points:
            self.max_frame = self.max_data_point/self.total_data_points * self.total_frames

        self.current_frame = self.min_frame

        log.debug(f'set_video1 - min_frame {self.min_frame}. max_starting_frame: {self.max_frame}, video_speed:{self.video_speed}')
        log.debug(f'set_video1 - elapsed_time: {self.elapsed_time}, total_frames/video_speed: {self.total_frames/self.video_speed}, video_speed: {self.video_speed}, total_frames {self.total_frames}')
        self.update_frame()

    # sets data for the next color and draws the graph

    def play(self):
#        print(f"pressed play: {self.current_frame}")
        if self.video1_cv2 == None:
            return

        if self.video_play_timer.isActive():
            self.video_play_timer.stop()
        else:
            self.video_play_timer.start(self.video_speed)  #FPS
            log.debug(f'play - milliseconds/frame: {self.video_speed}')


    def stop(self):
#        print(f"pressed stop; {self.current_frame}")
        if self.video1_cv2 == None:
            return
        self.video_play_timer.stop()

    def rewind_1(self):
#        print(f"pressed rewind: {self.current_frame}")
        if self.video1_cv2 == None:
            return

        self.video_play_timer.stop()
        self.current_data_point -= 1
        if self.current_data_point < self.min_data_point:
            self.current_data_point = self.min_data_point     # this is to take into account that update frame will add one to it automatically
        self.update_frame()

    def rewind_chunk(self):
#        print(f"pressed rewind chunk: {self.current_frame}")
        if self.video1_cv2 == None:
            return

        self.video_play_timer.stop()
        self.current_data_point -= self.chunk
        if self.current_data_point < self.min_data_point:
            self.current_data_point = self.min_data_point     # this is to take into account that update frame will add one to it automatically
        self.update_frame()

    def rewind_to_start(self):
        if self.video1_cv2 == None:
            return

        self.video_play_timer.stop()
        self.current_data_point = self.min_data_point     #update frame will move it to frame zero
        self.update_frame()

    def forward_1(self):
 #       print(f"pressed forward: {self.current_frame}")
        if self.video1_cv2 == None:
            return

        self.current_data_point += 1
        self.video_play_timer.stop()
        self.update_frame()   #this automatically moves one step forward

    def forward_chunk(self):
#        print(f"pressed forward chunk: {self.current_frame}")
        if self.video1_cv2 == None:
            return

        self.video_play_timer.stop()
        self.current_data_point += self.chunk
        if self.current_data_point > self.max_data_point:
            self.current_data_point = self.max_data_point
        if self.current_data_point > self.max_data_point:
            self.current_data_point = self.max_data_point
        self.update_frame()   #this automatically moves one step forward

    def slider_value_changed(self, value):
#        print(f"slider value changed: {value}")
        if self.video1_cv2 == None:
            return

        self.video_play_timer.stop()
        self.current_data_point = value
        self.update_frame()

    def checkbox_video1_enable_changed(self, checked):
        if checked != 0:
            self.video1_enabled = True
        else:
            self.video1_enabled = True

    def checkbox_video2_enable_changed(self, checked):
        if checked != 0:
            self.video2_enabled = True
        else:
            self.video2_enabled = True

    def checkbox_video1_overlay_changed(self, checked):
        if checked != 0:
            self.video1_overlay = True
        else:
            self.video1_overlay = False
        self.update_frame()

    def checkbox_video2_overlay_changed(self, checked):
        if checked != 0:
            self.video2_overlay = True
        else:
            self.video2_overlay = False
        self.update_frame()

    def radio_button_callback(self, sender ):
        sender = window.sender()  # Get the sender of the signal

        # ignore when something is turned off
        if sender.isChecked() == False:
            return

        if isinstance(sender, QRadioButton):
#            print(f"Radio button {sender.text()} toggled: {sender.isChecked()}")
            pass

        answer = sender.text()
        if "Full" in answer:
            self.speed_multiplier = 1
        elif "Super" in answer:
            self.speed_multiplier = .1
        else:
            self.speed_multiplier = .4

        self.video_speed = int(self.video_speed_full/self.speed_multiplier)

        if self.video_play_timer.isActive():
            self.video_play_timer.stop()
#            time.sleep(0.05)
            self.video_play_timer.start(self.video_speed)  #FPS
            log.debug(f'radio_button_speed - milliseconds/frame: {self.video_speed}')

    # def checkbox_short_video_changed(self, checked):
    def checkBox_short_video_changed(self, checked):

        if checked != 0:
            self.short_video = True
            self.set_trial(self.current_trial)
        else:
            self.short_video = False
            self.set_trial(self.current_trial)

        self.update_frame()

    def set_vertical_bar(self):

        if self.vertical_line is not None:

            # the following accounts for if we are showing a short video
            x_point = self.current_data_point - self.min_data_point

            line_pos = self.graph_x_seconds[x_point]
            self.vertical_line.set_xdata([line_pos])
            self.canvas.draw()

    def update_frame(self):
        if self.video1_cv2 == None:
            image_path = 'resources/img/camera_offline.png'
            image = QImage(image_path)
            image = image.scaledToWidth(self.label_video1.width())
            pixmap = QPixmap.fromImage(image)
            self.label_video1.setPixmap(pixmap)
            return

        #ratio is used for calculations of graph compared to video

        ratio = (self.max_frame - self.min_frame) / (self.max_data_point - self.min_data_point)

        # if timer is active move the frame forward.  If inactive we calculate which
        # frame to show
        if self.video_play_timer.isActive():
            self.current_frame += 1
            self.current_data_point = int( self.current_frame/ratio )
        else:
            # calculate which frame should be shown.  This is basically the number of
            # frames of video divided by the total points being graphed.
            self.current_frame = int( (self.current_data_point - self.min_data_point)* ratio)
            if self.current_frame < self.min_frame:
                self.current_frame = self.min_frame
            elif self.current_frame >= self.max_frame:
                self.current_frame = self.max_frame - 1

        #last check to make sure datapoints are between correct ranges.
        if self.current_data_point < self.min_data_point:
            self.current_data_point = self.min_data_point
        elif self.current_data_point >= self.max_data_point:
            self.video_play_timer.stop()
            self.current_data_point = self.max_data_point - 1

#        print(f"data: {self.current_data_point}, frame: {self.current_frame}   ---   d: {old_d}, f: {old_f}")

        # Set the frame position to the desired frame number
        self.video1_cv2.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)

        # Read the specific frame
        ret, frame = self.video1_cv2.read()
        if ret:

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w

            q_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)


            scaled_pixmap = QPixmap.fromImage(q_image).scaled(self.label_video1.size(), Qt.AspectRatioMode.KeepAspectRatio)

            #add in lines/graphics
            if(self.video1_overlay == True):
                self.frame_add_lines(scaled_pixmap)

            self.label_video1.setPixmap(scaled_pixmap)

            self.set_vertical_bar()

            #update the slider position
            self.videoSlider.valueChanged.disconnect(self.slider_value_changed) # disconnect the signla
            self.videoSlider.setValue(self.current_data_point)
            self.videoSlider.valueChanged.connect(self.slider_value_changed)  # Reconnect the signal

    def frame_add_lines(self, scaled_pixmap):

        lines_dict = self.graph["lines"]
        l_force = 100
        r_force = 100
        for key, line in lines_dict.items():
            if(key =='Left'):
                l_force = line[self.current_data_point]
            else:
                r_force = line[self.current_data_point]

        pixmap_size = scaled_pixmap.size()
        w = pixmap_size.width()
        h = pixmap_size.height()

        # Create a QPainter object to draw on the QPixmap
        painter = QPainter(scaled_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # Optional: Enable anti-aliasing for smoother lines

        # Set the line properties (e.g., color and width)

        linew = 10
        pen = QPen(Qt.GlobalColor.darkGreen)  # Red color
        pen.setWidth(linew)  # Line width
        penH = QPen(Qt.GlobalColor.white)  # Red color
        penH.setWidth(2)  # Line width

        def y_value_calc(pixmap_h, force_max, force):
            ratio = abs(pixmap_h / (force_max *2))    # Use absolute value as the +/- is accounted for below
            value = int(pixmap_h / 2 + (force * ratio * -1) )   # the times -1 is because the upper left corner of the pixmap is 0, 0
            return value

        l_scaled = y_value_calc(h, self.max_value, l_force)
        r_scaled = y_value_calc(h, self.max_value, r_force)

        if self.current_data_point % 10 == 0:
#            print(f"LINES:   h: {h}, self.max_value {self.max_value}, l_force: {l_force}, r_force: {r_force}, l_scaled: {l_scaled}, r_scaled: {r_scaled}")
            pass

#        lxpos = int(linew / 2)
        lxpos = w - int(linew / 2)
#        rxpos = w - int(linew / 2)
        rxpos = int(linew / 2)


        # Draw lines on the QPixmap
        if l_force < 0:
            pen.setColor(Qt.GlobalColor.blue)
        else:
            pen.setColor(Qt.GlobalColor.darkGreen)
        painter.setPen(pen)
        painter.drawLine(lxpos, int(h / 2), lxpos, l_scaled)

        if r_force < 0:
            pen.setColor(Qt.GlobalColor.blue)
        else:
            pen.setColor(Qt.GlobalColor.darkGreen)
        painter.setPen(pen)
        painter.drawLine(rxpos, int(h / 2), rxpos, r_scaled)

        # horizontal lilne
        painter.setPen(penH)
        painter.drawLine(lxpos, l_scaled, rxpos, r_scaled)

        # End painting
        painter.end()


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
    trial.validate_trial_path(fp)
    trial.process_summary()
    trial.trial_name = "srt test trial"
    trial.video_files["video1"]: fp_video1

    window.set_trial(trial)
#    window.load_tree()

    window.set_video1('resources/testing/test_video.mp4')

    window.show()

    result = app.exec()
    sys.exit(result)
