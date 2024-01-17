# TPC_analytics_UI.py

import os, sys, cv2, platform, time, threading
import numpy as np
from queue import Queue, Empty  # utilized for video frame reader

from TPC_analytics_UI_designer import Ui_MainAnalyticsWindow

from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QTreeWidgetItem,  QRadioButton
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QIcon, QTransform
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QEvent

#import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import seaborn as sns   # pip install seaborn
import getpass as gt

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
# set up logging

from share import jt_util as util

# logging configuration - the default level if not set is DEBUG
log = util.jt_logging()

# log.set_logging_level("INFO")
# log.debug(f'INFO - Valid logging levels are: {util.logging_levels}')

from share import jt_dialog as jtd
from share import jt_trial as jtt
from share import jt_trial_manager as jttm
from share import jt_config as jtc
from share import analytics_knee_extension as ake
from share import analytics_cmj as acmj
from share import jt_pdf_2_across as jtpdf2
from share import jt_videoFrameReader as jtvf

trial_mgr_filename = 'all_athletes.json'

######################################################################################
######################################################################################
######################################################################################
class TPC_Analytics_UI(QMainWindow, Ui_MainAnalyticsWindow):

    #used to handle closed event
    closed = pyqtSignal()
    def __init__(self, config_obj, parent=None):
        super().__init__(parent)

        self.video_timing_debug = False
        self.video_frame_retrieve_debug = False

        self.config_obj = config_obj
        # calls the setup method instead of the python class created from the UI
        self.setupUi(self)

        self.setWindowTitle(self.config_obj.app_name)

        ##################################################
        ### browser tab
        ##################################################
        self.video_widgets = []

        # Tree Widget
        self.treeWidget.itemClicked.connect(self.item_clicked_browser)
        self.treeWidget.currentItemChanged.connect(self.item_changed_browser)
        self.browser_tree_clicked = True

        # the following is created so that when the user uses the up or down arrow it essentially
        # clicks on that particular field assuming it is the leaf (when UserRole has data)

        self.treeWidget.installEventFilter(self)

        # clicked events for video widgets
        self.pushButton_play.clicked.connect(self.play)
        self.pushButton_forward.clicked.connect(self.forward)
        self.pushButton_forward_chunk.clicked.connect(self.forward_chunk)
        self.pushButton_stop.clicked.connect(self.stop)
        self.pushButton_rewind.clicked.connect(self.rewind)
        self.pushButton_rewind_chunk.clicked.connect(self.rewind_chunk)
        self.pushButton_rewind_to_start.clicked.connect(self.rewind_to_start)
        self.videoSlider.valueChanged.connect(self.slider_value_changed)
        self.videoAlignmentSlider.valueChanged.connect(self.videoAlignmentSlider_changed)

        # state changes video buttons
        self.checkBox_video1_enable.stateChanged.connect(self.checkbox_video1_enable_changed)
        self.checkBox_video1_overlay.stateChanged.connect(self.checkbox_video1_overlay_changed)
        self.checkBox_short_video.stateChanged.connect(self.checkBox_short_video_changed)
        self.checkBox_freeze_y_axis.stateChanged.connect(self.checkBox_freeze_y_axis_changed)

        # video playback speed
        self.radioButton_full.setChecked(True)
        self.radioButton_full.toggled.connect(self.radio_button_callback)
        self.radioButton_slow.toggled.connect(self.radio_button_callback)
        self.radioButton_super_slow.toggled.connect(self.radio_button_callback)

        self.videoSlider.setMinimum(0)

        # create list of all video widgets so that they can be turned on or off if there isn't a video with the
        # trial being displayed
        self.video_widgets.append(self.pushButton_play)
        self.video_widgets.append(self.pushButton_forward)
        self.video_widgets.append(self.pushButton_forward_chunk)
        self.video_widgets.append(self.pushButton_stop)
        self.video_widgets.append(self.pushButton_rewind)
        self.video_widgets.append(self.pushButton_rewind_chunk)
        self.video_widgets.append(self.pushButton_rewind_to_start)
        self.video_widgets.append(self.videoSlider)
        self.video_widgets.append(self.checkBox_video1_enable)
        self.video_widgets.append(self.checkBox_video1_overlay)
        # commented out because might want to see jump only even if there isn't a video
#        self.video_widgets.append(self.checkBox_short_video)
        self.video_widgets.append(self.radioButton_full)
        self.video_widgets.append(self.radioButton_slow)
        self.video_widgets.append(self.radioButton_super_slow)
        self.video_widgets.append(self.qlabel_time)
        self.video_widgets.append(self.videoAlignmentSlider)
        self.video_widgets.append(self.label_align_video)
        self.video_widgets.append(self.label_video1)

        self.videoAlignmentSlider.setMinimum(-15)
        self.videoAlignmentSlider.setMaximum( 15)


        # reports tab
        self.treeWidget_reports.itemClicked.connect(self.item_clicked_reports)
        self.pushButton_page_forward.clicked.connect(self.reports_page_forward)
        self.pushButton_page_back.clicked.connect(self.reports_page_back)
        self.pushButton_create_pdf.clicked.connect(self.reports_create_pdf)
        self.pushbutton_results_directory.clicked.connect(self.open_results_directory_in_OS)

        #player buttons
        # utility function to set icons on pushbuttons
        def add_pb_icon(image_name, pb, flip=False):
            image_path = self.config_obj.get_img_path() + image_name
#            print(f'image_path of video widgets: {image_path}')
            pixmap = QPixmap(image_path)  # Replace with the path to your image
            if pixmap.isNull():
                log.info(f"Image '{image_path}' does not exist or is invalid.\n")
            if flip:
                pixmap = pixmap.transformed(QTransform().scale(-1, 1))
            icon = QIcon(pixmap)  # Replace with the path to your image
            pb.setIcon(icon)
            pb.setText("")

        add_pb_icon ( "rewind-to-start.png", self.pushButton_rewind_to_start)
        add_pb_icon ( "next-button-ff.png", self.pushButton_rewind_chunk, True)
        add_pb_icon ( "next-button.png", self.pushButton_rewind, True)
        add_pb_icon ( "stop-button.png", self.pushButton_stop)
        add_pb_icon ( "play-button.png", self.pushButton_play)
        add_pb_icon ( "next-button.png", self.pushButton_forward)
        add_pb_icon ( "next-button-ff.png", self.pushButton_forward_chunk)


        ##########################
        # video setup
        ##########################

        # starting are always 0
        # min is where the video will start
        # current is where the video is at
        # max is the last point on video to show
        # total - is the furthest in the video it can go
        self.starting_data_point = 0
        self.starting_frame = 0
        self.min_data_point = 0
        self.min_frame = 0
        self.current_trial = None
        self.current_frame = 0
        self.current_data_point = 0
        self.max_frame = 0
        self.max_data_point = 0
        self.total_frames = 0
        self.total_data_points = 0
        self.video_tweak_x = 0
        self.freeze_y_axis = False
        self.browsing_yMin = None
        self.browsing_yMax = None

        self.video1_cv2 = None
        self.srt_label_graphic = None
        self.video_play_timer = None
        self.vertical_line = None
        self.debug_last_time = None
        self.debug_update_frame_count = 0
        self.video_starting_point = None

        self.video1_cv2_lock = threading.Lock()
        self.chunk = 10
        self.speed_multiplier = 1

        #if this is launched from parent window then grab its child mgr object
        if parent != None:
            self. trial_mgr_obj = parent.trial_mgr_obj
        else:
            self.trial_mgr_obj = jttm.JT_JsonTrialManager(self.config_obj)

        self.load_browser_tree()
        self.load_reports_tree()

        #set up for graph
        # change out the existing QLabel button to canvas
        figure_browsing = Figure()
        self.ax_browsing = figure_browsing.add_subplot(111)
        self.canvas_browsing = FigureCanvas(figure_browsing)
        self.verticalLayout_graph.addWidget(self.canvas_browsing)
        self.verticalLayout_graph.replaceWidget(self.label_graphic, self.canvas_browsing)
        self.label_graphic.deleteLater()

        #video stuff
        self.video1_overlay = True
        self.video1_enabled = True
        self.short_video = False
        self.video1_filepath = None

        self.video1_frame_buffer = None
        self.video1_frame_reader = None
        ##################################################
        ### reports tab
        ##################################################
        self.canvas_list = []   # list of places on the screen that can show a specific plot
        self.plot_list = []     # ultimately will hold the list of plots to show on the screen that can be scrolled
        self.plot_current = 0   # this variable shows what the current plot being displayed is (ie, 1 to XX plots can
                                # be scrolled through
        self.reports_protocol = None

        def canvas_define(canvas_list, label_plot ):
            figure_report = Figure()
            ax_reports = figure_report.add_subplot(111)
            canvas_report = FigureCanvas(figure_report)
            self.gridLayout_plots.addWidget(canvas_report)
            self.gridLayout_plots.replaceWidget(label_plot, canvas_report)
            label_plot.deleteLater()

            canvas_dict = {
                'ax': ax_reports,
                'canvas': canvas_report,
                'figure': figure_report
            }
            canvas_list.append(canvas_dict)


        ### call plot_define above to create each one
        canvas_define(self.canvas_list, self.label_plot1)
        canvas_define(self.canvas_list, self.label_plot2)
        canvas_define(self.canvas_list, self.label_plot3)
        canvas_define(self.canvas_list, self.label_plot4)


    # for TreeWidget get the key up or down captured and then pass it to my own handler
    def eventFilter(self, obj, event):
        try:
            if obj == self.treeWidget and event.type() == QEvent.Type.KeyPress:
                if event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down):
                    # Let the tree widget handle the event first, then follow up with the timer.  ChatGPT said
                    # use 0 milliseconds for the delay.  I have moved it to 50 to see if it helps not crash so much
                    QTimer.singleShot(50, self.treeWidget_check_current_item)
                    return False
        except:
            log.error('eventFilter for up/down key press failed')
        return super().eventFilter(obj, event)

    #this code does an item clicked for the new item in the tree view being shown
    def treeWidget_check_current_item(self):
        current_item = self.treeWidget.currentItem()
        if current_item and current_item.data(0, Qt.ItemDataRole.UserRole) is not None:
            # Perform your action here for the current item
            self.item_clicked_browser(current_item)
#            print(f"Current Item: {current_item.text(0)}")



    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)

    #load tree widget
    def load_browser_tree(self):
        df = self.trial_mgr_obj.load_all_trials()

        if len(df) < 1:
            return

        unique_athletes = df['athlete'].unique()
        unique_athletes.sort()

        for athlete in unique_athletes:
            athlete_item = QTreeWidgetItem([athlete])
            self.treeWidget.addTopLevelItem(athlete_item)

            # Filter DataFrame for the target dates
            athlete_df = df[df["athlete"] == athlete]
            unique_dates = athlete_df['date'].unique()
            unique_dates = np.sort(unique_dates)
#            log.debug(f'Unique dates\n {unique_dates}')

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
                    protocol_obj = self.config_obj.protocol_obj
                    protocol_name = protocol_obj.get_name_by_protocol(protocol)
                    trial_name = f"{protocol_name} - {protocol_counts[protocol]}"

                    trial_item = QTreeWidgetItem([trial_name])
                    date_item.addChild(trial_item)
                    trial_item.setData(0, Qt.ItemDataRole.UserRole, original_filename)

        # self.expand_tree_widget(self.treeWidget)


    def expand_tree_widget(self, tree_widget):
        def expand_items(item):
            item.setExpanded(True)
            for i in range(item.childCount()):
                expand_items(item.child(i))

        for i in range(tree_widget.topLevelItemCount()):
            expand_items(tree_widget.topLevelItem(i))

    def expand_single_item(self, item):
        def expand_items(item):
            item.setExpanded(True)
            for i in range(item.childCount()):
                expand_items(item.child(i))

        expand_items(item)

    def item_clicked_browser(self, item, column=0):

        if item.childCount() == 0:
            self.browser_tree_clicked = True
            parent_path = ""
            current_item = item
            item_text = item.text(0)

            if self.video_play_timer:
                self._stop_video()

            while current_item.parent():
                parent_path = f"/{current_item.text(0)}{parent_path}"
                current_item = current_item.parent()
            original_filename = item.data(0, Qt.ItemDataRole.UserRole)

            try:
                log.info(f'Trial Browser item clicked: {original_filename} item_text: {item_text}')
                trial = self.trial_mgr_obj.get_trial_file_path(original_filename, item_text)

                trial.process_summary()

                trial.trial_name = item_text

                log.info(f"Clicked: {item_text}, Parent Path: {parent_path}, original_filename: {original_filename}, filepath {trial.file_path}---")
            except:
                msg = f'Error processing {item_text}, limited functionality '
                jtd.JT_Dialog(parent=self, title="Exception",
                                   msg=msg,
                                   type="ok")
                log.error(f'{msg}, {original_filename}')

            # because this is a different trial being selected reset the video_tweak to 0.  Everything else that should
            # be reset happens inside of set_trial().   Video_tweak isn't reset inside of the set)trial because we want it
            # to remain the same if the user is toggling between short and full lenght video OR if the user is
            # freezing/unfreezing the axis
            self.video_tweak_x = 0
            self.videoAlignmentSlider.setValue(self.video_tweak_x)

            self.set_trial(trial)
            self.statusbar.showMessage(f"Original Filename: {original_filename}")

        else:
            log.debug(f'no item to selected, must be a folder.  item_text: {item.text(0)}')
            if item.isExpanded():
                item.setExpanded(False)
            else:
                item.setExpanded(True)
                self.expand_single_item(item)

    def item_changed_browser(self, current, previous):
        # commented out for now, current can't just be passed along to the item clicked and not worth
        # debugging at this time
        # if not self.browser_tree_clicked:
        #     self.item_clicked_browser(self, current)
        self.browser_tree_clicked = False

    ###########################################################################################
    # set_trial - allows the user to display a different trial.
    ###########################################################################################
    # 1) gets initial video information, primary purpose is determine the FPS, total frames, and therefore len of video
    # 2) does calculations to align video with timeline of values.  IE, videos are shorter by ~.5 seconds so essentially
    #    chops off the first first .5 seconds of recorded values.  It does this by adjusting the min index from 0
    #    to a higher number.
    # 3) draws the graph on the screen
    # 4) completes setup of video_frame_reader
    # 5) makes adjustments to min and max frame if it is a scenario where the video is shortened to start of jump
    def set_trial(self, trial):
        self.current_trial = trial

        #### Initial Video setup for trial
        # 1) kill old video video if it exists
        if self.video_play_timer:
            self._stop_video()

        if self.video1_cv2:
            with self.video1_cv2_lock:
                self.video1_cv2.release()
                self.video1_cv2 = None
                time.sleep(0)

        # 2) get video file and do basic setup.  The remainder is doing in (set_video1)
        if len(trial.video_files) > 0:
            first_key, video = next(iter(trial.video_files.items()))   # designed for multiple videos but hard coded for only1
            if video is not None and len(video) > 0:
                self.show_video_widgets(True)
                path_data = self.config_obj.path_data + self.current_trial.athlete + "/"
                self.video1_filepath = path_data + video

                # validate if video file exists
                if not os.path.exists(self.video1_filepath):
                    log.error(f'Video file does not seem to exist: {self.video1_filepath}')
                    return

                try:
                    if os.path.exists(self.video1_filepath):
                        with self.video1_cv2_lock:
                            self.video1_cv2 = cv2.VideoCapture(self.video1_filepath)

                    # validated if file was successfully opened
                    if not self.video1_cv2.isOpened():
                        log.error(f"Error: cv2.VideoCapture Error: Could not open video file {self.video1_filepath}")
                        with self.video1_cv2_lock:
                            self.video1_cv2.release()
                            self.video1_cv2 = None
                        self.show_video_widgets(False)
                    else:
                        # get video data
                        self.total_frames = int(self.video1_cv2.get(cv2.CAP_PROP_FRAME_COUNT))
                        self.max_frame = self.total_frames
                        self.video1_fps = self.video1_cv2.get(cv2.CAP_PROP_FPS)
                        self.video_time_freq_full = round(1000 / self.video1_fps)  # calculates milliseconds/frame

                        log.debug(f'Opened video: {self.video1_filepath}, FPS: {self.video1_fps}')
                except:
                    log.error(f'Failed to open video file: {self.video1_filepath}')
                    self.show_video_widgets(False)
        else:
            # should cause frame to be updated with static image
            #            self.update_frame()
            self.show_video_widgets(False)


        #### set up plot/ graph to display
        self.label_athlete_value.setText(trial.athlete)
        self.label_protocol_value.setText(trial.protocol)
        self.label_date_value.setText(trial.date_str)
        self.label_trial_value.setText(trial.trial_name)

        self.ax_browsing.clear()

        # graph the first key value pair from the dictionary.  Probably one one key value pair but this was
        # set up to handle more in the future
        self.graph = self.current_trial.main_graph
        self.ax_browsing.set_title(self.graph.get('title', "no title set"))
        self.ax_browsing.set_xlabel(self.graph.get('xlabel', 'no xlabel'))
        self.ax_browsing.set_ylabel(self.graph.get('ylabel', 'no ylabel'))
        self.elapsed_time = self.graph.get('elapsed_time', 0)

        # draw the lines on the graph.  There is a lot of code here and the primary purpose is
        # there are two ways to draw the lines.  First is all the points from beginning to end.  The
        # second way is to draw the lines starting a specific point on the time line to a 2nd point on
        # the timeline.  This is used for when the "short_video" flag is set.   Because ultimately time is
        # on the X axis there is a bunch of calculations to be done.   This should probably be put into
        # jt_plot but I am leaving that for another day (and maybe person)
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

            # if in short video mode then grab the "short" start and end index's
            if self.short_video == True and self.current_trial.short_start_index is not None:
                self.min_data_point = self.current_trial.short_start_index;  # change this in the future
            if self.short_video == True and self.current_trial.short_end_index is not None:
                self.max_data_point = self.current_trial.short_end_index    # change this in the future

            # the following code changes the start point to align with the beginning of the video.  Testing found that
            # generally the video was about .5 seconds to start up.  Therefore when there is video the first .5 seconds
            # worth of data needs to be "trimmed".  The following code does that by setting self.min_data_point to the
            # trimmed value
            # NOTE: technically this only needs to be run once but I am a bit lazy on and let it happen for each line
            if self.video1_cv2 is not None:
                # calculate amount of time to be trimmed:   #frames * timer/frame = video length
                trim_time = (self.total_frames * self.video_time_freq_full) - self.elapsed_time
                self.video_starting_point = trim_time / self.elapsed_time / self.total_data_points
                # check if video start is later than min_data_point and if so bump it out.  With 70hz this should
                # typically be around 35

                if self.video_starting_point > self.min_data_point:
                    self.min_data_point = int(self.video_starting_point)

            tl = len(line)
            short_line = line[self.min_data_point:self.max_data_point]
            sl = len(short_line)
#                log.debug(f"TOTAL DATA POINTS: {self.total_data_points}")
            #calculate the min and max times to show on the graph
            start_time = self.min_data_point / self.total_data_points * self.elapsed_time
            end_time = self.max_data_point / self.total_data_points * self.elapsed_time

            # create the x values so they are in seconds
            self.graph_x_seconds = np.linspace(start_time, end_time, (self.max_data_point - self.min_data_point ) )
            lxsecs = len(self.graph_x_seconds)
            log.debug(f"total line len: {tl}, short_line len: {sl} graphx len {lxsecs}")
            self.ax_browsing.plot(self.graph_x_seconds, short_line, linestyle='-', label=key, color=my_color, linewidth=1)
            # print(f'Printing line: {key} and graph_x_seconds')
            # print(self.graph_x_seconds)
            color_i += 1
            if color_i > len(jt_color_list):
                color_i = 0

        # code to debug start and end time calculations and put them on the graph correctly
        # log.msg(f'#### short_video: {self.short_video} ')
        # log.msg(f'     for reference in current trial: short_start_index: {self.current_trial.short_start_index} short_end_index: {self.current_trial.short_end_index}')
        # log.msg(f'     full length        start_time: {0} end_time:  {self.elapsed_time} total_line len: {tl}')
        # log.msg(f'     current_trial      start_time: {start_time}, end_time: {end_time}')
        # log.msg(f"     current_trial      short_line len: {sl} graphx len {lxsecs}")
        # log.msg(f'     current_trial      self.min_data_point {self.min_data_point}. max_data_point: {self.max_data_point}')

        #set the verical line at the beginning
        self.current_data_point = self.min_data_point
        self.vertical_line = self.ax_browsing.axvline(x=(start_time), color='g', linestyle='--')

        self.ax_browsing.legend()
        # will set limits if they aren't equal to None
        self.ax_browsing.set_ylim(self.browsing_yMin, self.browsing_yMax)
        self.canvas_browsing.draw()

        # finalize video setup
        if self.video1_cv2 is not None:

            # setup timers for video playback at the correct speed
            self.video_play_timer = QTimer(self)
            self.video_play_timer.timeout.connect(self.update_frame)

            # apply speed modifier (ie, if in slow motion)
            self.video_time_freq = round(self.video_time_freq_full / self.speed_multiplier)

            # set iniitial frames mins and maxes and current
            self.starting_frame = 0  # this will always be zero
            self.min_frame = self.starting_frame

            # make adjustments if video is shortened  (self.video_starting_point is a replacement for 0)
            if self.min_data_point > self.video_starting_point:
                self.min_frame = round(self.min_data_point / self.total_data_points * self.total_frames)

            if self.max_data_point != self.total_data_points:
                self.max_frame = round(self.max_data_point / self.total_data_points * self.total_frames)

            # set initial frame to zero
            self.current_frame = self.min_frame

            # calculate ratio
            self.ratio = (self.max_frame - self.min_frame) / (self.max_data_point - self.min_data_point)

            # debug stuff - full speed only
            if (self.video_timing_debug):
                video_time_duration = self.total_frames * self.video_time_freq_full / 1000  # calculates length of video in seconds
                log.info(
                    f'set trial - min_data_point {self.min_data_point}. max_data_point: {self.max_data_point}, data elapsed_time: {self.elapsed_time:.2f}')
                log.info(
                    f'   min_frame {self.min_frame}. max_frame: {self.max_frame}, video_time_freq_full(ms):{self.video_time_freq_full}, video_fps {self.video1_fps}')
                log.info(
                    f'   total_frames {self.total_frames}, videoTimeDuration: {video_time_duration:.2f}, elapsed-video: {(self.elapsed_time - video_time_duration):.2f} ')
                short_frame_cnt = self.max_frame - self.min_frame
                short_data_cnt = self.max_data_point - self.min_data_point
                log.info(
                    f'   short_frames_cnt {short_frame_cnt}, data_point_cnt {short_data_cnt}, ratio(frames/data_points) = {self.ratio:.2f}')

            # setup video frame reader and buffer
            self._setup_video_frame_reader()

        #adjust the slider for the number of datapoints
        self.videoSlider.setMinimum( self.min_frame )
        self.videoSlider.setMaximum( self.max_frame)

        #set slider to correct position
        self.videoSlider.setValue(self.min_frame)

        # update what is on the screen
        self.update_frame()

#        log.debug(f'min_data_point: {self.min_data_point}, max_data_point = {self.max_data_point}')

    def play(self):
#        print(f"pressed play: {self.current_frame}")
        self.debug_update_frame_count = 0

        if self.video1_cv2 == None:
            return

        if self.video_play_timer.isActive():
            self._stop_video()
            self.update_frame()
        else:
            self.video_play_timer.start(self.video_time_freq)  #FPS
            if (self.video_timing_debug):
                log.info(f'play - milliseconds/frame: {self.video_time_freq}')


    def stop(self):
#        print(f"pressed stop; {self.current_frame}")
        if self.video1_cv2 == None:
            return
        self._stop_video()
        self.update_frame()

    #used internally to stop both the video_play_timer (pyqt loop), the VideoFrameReader thread, and empty the buffer
    def _stop_video(self, pause_time = .0):

        #stop the pyqt video from playing
        if self.video_play_timer is not None:
            self.video_play_timer.stop()
            time.sleep(pause_time)

        # stop the buffer reader first so it doesn't overflow
        if self.video1_frame_reader is not None:
            self.video1_frame_reader.stop()
        time.sleep(pause_time)

        # empty the buffer
        try:
            while True:
                self.video1_frame_buffer.get_nowait()
        except Empty:
            pass  # Queue is now empty

    # setup VideoFrameReader which is a seperate thread that will read in the video frames on the side while
    # the main loop displays them.
    def _setup_video_frame_reader(self):
        self.video1_frame_buffer = Queue(maxsize=5)     # Adjust size as needed
        self.video1_frame_reader = jtvf.jt_VideoFrameReader(self.video1_cv2, self.video1_cv2_lock, self.video1_frame_buffer, self.video_time_freq)
        self.video1_frame_reader.start()                # go ahead and get the frame buffer loaded
        timer_wait = .0
        time.sleep(timer_wait) #give the buffer a chance to start filling

        st = time.time()
        # wait to load buffer if not at the end of the video
        while self.video1_frame_buffer.empty() and self.current_frame < self.total_frames:
            if(self.video_timing_debug):
                print(f'current frame: {self.current_frame}, self.total_frames: {self.total_frames}')
            time.sleep(timer_wait)
            ct = time.time()
            tot = ct - st
            if(self.video_timing_debug):
                print(f'    waiting to load buffer secs: {tot}')
#        print(f'   queue size: {self.video1_frame_buffer.qsize()}')

    def rewind(self):
#        print(f"pressed rewind: {self.current_frame}")
        if self.video1_cv2 == None:
            return

        self._stop_video()
        self.current_frame -= 1
        if self.current_frame < self.min_frame:
            self.current_frame = self.min_frame     # this is to take into account that update frame will add one to it automatically
        self.update_frame()

    def rewind_chunk(self):
#        print(f"pressed rewind chunk: {self.current_frame}")
        if self.video1_cv2 == None:
            return

        self._stop_video()
        self.current_frame -= self.chunk
        if self.current_frame < self.min_frame:
            self.current_frame = self.min_frame     # this is to take into account that update frame will add one to it automatically
        self.update_frame()

    def rewind_to_start(self):
        if self.video1_cv2 == None:
            return

        self._stop_video()
        self.current_frame = self.min_frame     #update frame will move it to frame zero
        self.update_frame()

    def forward(self):
 #       print(f"pressed forward: {self.current_frame}")
        if self.video1_cv2 == None:
            return

        self.current_frame += 1
        self._stop_video()
        self.update_frame()   #this automatically moves one step forward

    def forward_chunk(self):
#        print(f"pressed forward chunk: {self.current_frame}")
        if self.video1_cv2 == None:
            return

        self._stop_video()
        self.current_frame += self.chunk
        if self.current_frame > self.max_frame:
            self.current_frame = self.max_frame
        self.update_frame()   #this automatically moves one step forward

    # the slider value comes in which is really the new_frame_number
    def slider_value_changed(self, new_frame_number):
#        print(f"##### slider value changed: {new_frame_number}")
        if self.video1_cv2 == None:
            return

        # this is the only place we need super fast action on the stop video function.
        self._stop_video(.01)

        # calculate the current frame to be diplayed
        tweaked_frame = new_frame_number - self.video_tweak_x

        self.current_frame = new_frame_number
#        print(f'    slider changed:  slider_value(new_frame_number/current_frame): {new_frame_number}  tweaked_frame: {tweaked_frame}, tweak_x: {self.video_tweak_x}')

        self.update_frame()

    # function to tweak the video left or right to align with the graph
    def videoAlignmentSlider_changed(self, value):
#        print(f'video slider: {value}')
        if self.video1_cv2 == None:
            return

        self._stop_video()
        self.video_tweak_x = value
        #self.current_frame = self.current_frame + self.video_tweak_x


        if (self.video_timing_debug):
            print(f'          AlignmentSlider: {value}, tweak_x: {self.video_tweak_x}, current_frame: {self.current_frame}')

        self.update_frame()

    def checkbox_video1_enable_changed(self, checked):

        if checked != 0:
            self.video1_enabled = True
        else:
            self.video1_enabled = True

    def checkbox_video1_overlay_changed(self, checked):
        if self.video1_cv2 == None:
            return

        self._stop_video()
        if checked != 0:
            self.video1_overlay = True
        else:
            self.video1_overlay = False
        self.update_frame()

    # Video Speed control (normal, slow, superslow
    def radio_button_callback(self, sender ):
        sender = self.sender()  # Get the sender of the signal

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
            self.speed_multiplier = .05
        else:
            self.speed_multiplier = .3

        # apply speed modifier (ie, if in slow motion)
        self.video_time_freq = round(self.video_time_freq_full/self.speed_multiplier)
        log.info(f'radio_button_speed - milliseconds/frame: {self.video_time_freq}')

        # after changing speed stop the video if it is active and restart it.
        if self.video_play_timer.isActive():
            self._stop_video()
            time.sleep(0)
            self.update_frame()
            self.video_play_timer.start(self.video_time_freq)  #FPS

    # def checkbox_short_video_changed(self, checked):
    def checkBox_short_video_changed(self, checked):

        if (self.video_frame_retrieve_debug):
            print('##### beggining of short video stopped')

        if self.video1_cv2 == None:
            return

        self._stop_video()

        if (self.video_frame_retrieve_debug):
            print('##### made it here, checkbox for short video after video stopped')

        if checked != 0:
            self.short_video = True
        else:
            self.short_video = False

        self.set_trial(self.current_trial)

    # handles freezing the y-axis to better see difference between different jumps
    def checkBox_freeze_y_axis_changed(self, checked):

        if self.video_play_timer.isActive():
            self._stop_video()

        if checked != 0:
            self.freeze_y_axis = True
            if self.current_trial is not None:
                self.browsing_yMin, self.browsing_yMax = self.ax_browsing.get_ylim()

        else:
            self.freeze_y_axis = False
            self.browsing_yMin = None
            self.browsing_yMax = None

        # this should force a redraw of the graph
        if self.current_trial is not None:
            self.set_trial(self.current_trial)

    # positions the vertical bar along the timeline
    def set_vertical_bar(self):

        if self.vertical_line is not None:

            # the following accounts for if we are showing a short video
            x_point = self.current_data_point - self.min_data_point
            if x_point >= len(self.graph_x_seconds):
                x_point = len(self.graph_x_seconds) - 1

            line_pos = self.graph_x_seconds[x_point]
            self.vertical_line.set_xdata([line_pos])
            self.canvas_browsing.draw()
            if(self.video_timing_debug):
                print(f'    --Vertical Bar || Data min/cur/max: {self.min_data_point}, {self.current_data_point}, {self.max_data_point}  x_point: {x_point} line_pos: {line_pos}')

    def update_frame(self):

        if (self.video_frame_retrieve_debug):
            print(f'update_frame: {self.current_frame}')
        # debugging stuff
        self.debug_update_frame_count += 1
        #debug timer to see how fast this function is being run
        current_time = time.time()
        if self.debug_last_time is not None:
            # only print out every tenth value
            if self.current_frame % 20 == 0:
                elapsed = current_time - self.debug_last_time
                if self.video_timing_debug:
                    print(f'  update_frame cnt: {self.debug_update_frame_count-1}, current_frame: {self.current_frame}, elapsed: {elapsed:.3f}')

        self.debug_last_time = current_time

        # No Video
        if self.video1_cv2 == None:
            image_path = self.config_obj.get_img_path() + 'camera_offline.png'
            image = QImage(image_path)
            image = image.scaledToWidth(self.label_video1.width())
            pixmap = QPixmap.fromImage(image)
            self.label_video1.setPixmap(pixmap)
            return

        # Calculate current_data_point
        self.current_data_point = round( ((self.current_frame - self.min_frame) / self.ratio) + self.min_data_point )
#        print (f'    ## data point: {self.current_data_point}: ratio: {self.ratio} current_frame: {self.current_frame} min_frame: {self.min_frame}')

        # check to make sure datapoints are between correct ranges.
        if self.current_data_point < self.min_data_point:
            self.current_data_point = self.min_data_point
        elif self.current_data_point > self.max_data_point:
            self.current_data_point = self.max_data_point - 1

        if self.video_timing_debug:
            print(f"     ## Data min/cur/max: {self.min_data_point}, {self.current_data_point}, {self.max_data_point} || Frame min/cur/max: {self.min_frame}, {self.current_frame}, {self.max_frame} | tweak: {self.video_tweak_x}")

        # Set the video frame
        # the cv2.set command is not needed if video is being played live as the cv2.read command automatically
        # goes to the next frame.  If the video isn't being played then set the location to the current_frame
        s_time = time.time() # debug timer
        if self.video_play_timer.isActive() is False:
            if (self.video_frame_retrieve_debug):
                print(f'    cv2 prior to video_cv2.set')
            try:
                # handle the boundry cases which.  They were handled before but this takes into account the tweak value
                frame_num = self.current_frame + self.video_tweak_x
                if frame_num < 0:
                    frame_num = 0
                elif frame_num >= self.total_frames:
                    frame_num = self.total_frames -1

                with self.video1_cv2_lock:
                    self.video1_cv2.set(cv2.CAP_PROP_POS_FRAMES,frame_num )

            except:
                print(f'    ############### failed to set position of frame')

            if (self.video_frame_retrieve_debug):
                print(f'    cv2.set  current_frame: {self.current_frame} tweak_x: {self.video_tweak_x}')
            # reset the video frame reader
            self._setup_video_frame_reader()
            if (self.video_frame_retrieve_debug):
                print(f'    cv2 completed _setup_video_frame_reader')
        else:
            self.current_frame += 1

            # check if video is trying to play beyond max_frame, if so then stop it
        if self.current_frame > self.max_frame:
            self.current_frame = self.max_frame
            self._stop_video()

        m_time = time.time() # debug timer

        # read video frame from buffer
        frame = None
        if not self.video1_frame_buffer.empty():
            frame = self.video1_frame_buffer.get()

        f_time = time.time() # debug timer

        #debug timing information
        if self.current_frame % 10 == 0:
            set_elapsed = m_time - s_time
            read_elapsed = f_time - m_time
            total_elapsed = f_time - s_time
#                print(f'      cv2.set: {set_elapsed:.3f}, cv2.read {read_elapsed:.3f}, cv2-total {total_elapsed:.3f}')

        ### update display the video frame
        if frame is not None:

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w

            q_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

            scaled_pixmap = QPixmap.fromImage(q_image).scaled(self.label_video1.size(), Qt.AspectRatioMode.KeepAspectRatio)

            #add in lines/graphics
            if(self.video1_overlay == True):
                self.frame_add_lines(scaled_pixmap)

            self.label_video1.setPixmap(scaled_pixmap)

        #### Update Misc screen elements
        # update when video play back is inactive or read the other two statements.  Goal is to skip some updates
        # when running at full speed
        skip_count = 1
        # if  (self.video_play_timer.isActive() is False) or \
        #     (self.video_play_timer.isActive() is True and self.speed_multiplier != 1) or \
        #     (self.speed_multiplier == 1 and self.current_frame % skip_count == 0):
        if skip_count == 1:
            # # sets the vertical bar on the graph
            self.set_vertical_bar()
            #
            # update the slider position
            self.videoSlider.valueChanged.disconnect(self.slider_value_changed) # disconnect the signal
            self.videoSlider.setValue(self.current_frame)
            self.videoSlider.valueChanged.connect(self.slider_value_changed)  # Reconnect the signal

            # update time for display on the screen
            # the following accounts for if we are showing a short video
            # make sure we don't go beyond end of time graph
            x_point = self.current_data_point - self.min_data_point
            if x_point >= len(self.graph_x_seconds):
                x_point = len(self.graph_x_seconds) - 1

            graph_time = self.graph_x_seconds[x_point]
            graph_time = f'Time: {graph_time:.2f}'

            # display the current time into the video in the label
    #        print(f'graph_time: {graph_time}')
            self.qlabel_time.setText(graph_time)

        # if in play mode then increment to the next frame for the next time around
        if self.video_play_timer.isActive():
            pass


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
            ratio = abs(pixmap_h / (force_max * 2))    # Use absolute value as the +/- is accounted for below
            value = int(pixmap_h / 2 + (force * ratio * -1) )   # the times -1 is because the upper left corner of the pixmap is 0, 0
            return value

        l_scaled = y_value_calc(h, self.max_value, l_force)
        r_scaled = y_value_calc(h, self.max_value, r_force)

        if self.current_data_point % 10 == 0:
#            print(f"LINES:   h: {h}, self.max_value {self.max_value}, l_force: {l_force}, r_force: {r_force}, l_scaled: {l_scaled}, r_scaled: {r_scaled}")
            pass

        lxpos = w - int(linew / 2)
        rxpos = int(linew / 2)


        # Draw lines on the QPixmap
        pen.setColor(Qt.GlobalColor.blue)
        painter.setPen(pen)

        # commented out code was to make the color change when positive force versus negagive relative to
        # body weight
        # left side
        # if l_force < 0:
        #     pen.setColor(Qt.GlobalColor.blue)
        # else:
        #     pen.setColor(Qt.GlobalColor.darkGreen)
        # painter.setPen(pen)
#        painter.drawLine(lxpos, int(h / 2), lxpos, l_scaled)
        painter.drawLine(lxpos, int(h), lxpos, l_scaled)

        # right side
        # if r_force < 0:
        #     pen.setColor(Qt.GlobalColor.blue)
        # else:
        #     pen.setColor(Qt.GlobalColor.darkGreen)
        # painter.setPen(pen)
#        painter.drawLine(rxpos, int(h / 2), rxpos, r_scaled)
        painter.drawLine(rxpos, int(h), rxpos, r_scaled)

        # horizontal line
        painter.setPen(penH)
        painter.drawLine(lxpos, l_scaled, rxpos, r_scaled)

        # End painting
        painter.end()

    # iterates over all video widgets and hides them if there isn't a video associated with the trial
    def show_video_widgets(self, show = True):
        for widget in self.video_widgets:
            if show:
                widget.show()
            else:
                widget.hide()


    ###############################################################
    #### Tab Reports
    ###############################################################

    def load_reports_tree(self):
        df = self.trial_mgr_obj.load_all_trials()

        if len(df) < 1:
            return

        list_of_combos = self.trial_mgr_obj.get_athletes_and_protocols_combinations()
#        print(f'list of combos \n {list_of_combos}')

        if len(list_of_combos) < 1:
            log.info(f'No data has been retrieved for any athletes')
            return

        # Using a set to get unique values from the first element of each tuple
        unique_athletes = list_of_combos['athlete'].unique()
        unique_athletes.sort()

        #load all athletes
        for athlete in unique_athletes:
            athlete_item = QTreeWidgetItem([athlete])
            self.treeWidget_reports.addTopLevelItem(athlete_item)

            # get protocols that are valid for a given athlete
            protocols_for_athlete = list_of_combos[list_of_combos['athlete'] == athlete]['short_protocol'].unique().tolist()
            protocols_for_athlete.sort()

            # for specific athlete, load protocols that they have done
            for protocol in protocols_for_athlete:
                short_name = self.config_obj.protocol_obj.get_short_name_by_short_protocol(protocol)
                if short_name is not None:
                    protocol_item = QTreeWidgetItem([short_name])
                    athlete_item.addChild(protocol_item)
                    protocol_item.setData(0, Qt.ItemDataRole.UserRole, athlete + '||' + protocol)
#                    print (f'***** athlete: {athlete}  protocol: {protocol} short_name: {short_name}')
        self.expand_tree_widget(self.treeWidget_reports)

    def item_clicked_reports(self, item, column):

        if item.childCount() == 0:
            parent_path = ""
            current_item = item
            item_text = item.text(0)

            athlete_protocol_combo = item.data(0, Qt.ItemDataRole.UserRole)
            split_list = athlete_protocol_combo.split('||')
            self.reports_athlete = split_list[0]
            self.reports_protocol = split_list[1]

            log.debug(f"childcount Clicked: {item_text}, Parent Path: {parent_path}---")
            log.debug(f"report selected - athlete: {self.reports_athlete}  protocol: {self.reports_protocol}")

            self.plot_current = 0
            if self.reports_protocol == 'JTDcmj':
                self.reports_protocol_athlete_analytics = acmj.JT_analytics_cmj(self.config_obj, self.reports_athlete)
                self.plot_list = self.reports_protocol_athlete_analytics.plot_list

            else:
                self.reports_protocol_athlete_analytics = ake.JT_analytics_knee_ext_iso(self.config_obj, self.reports_athlete)
                self.plot_list = self.reports_protocol_athlete_analytics.plot_list

            # set the defaults for when the app starts up again
            self.config_obj.set_config('reports_protocol', self.reports_protocol)
            self.config_obj.set_config('reports_athlete', self.reports_athlete)

            self.update_reports_plots()

    # method to draw the plots on the 4 quadrants based upon which 4 should be shown.
    def update_reports_plots(self):

        canvas_num = 0
        for canvas_dict in self.canvas_list:
            ax = canvas_dict['ax']
            canvas = canvas_dict['canvas']
            figure = canvas_dict['figure']
            ax.clear()

            try:
                plot = self.plot_list[self.plot_current + canvas_num]
                plot.draw_on_pyqt(ax, figure)
                canvas.draw()
                canvas_num += 1
            except:
                canvas.draw()
                #print(f'plot_list has {len(self.plot_list)} elements, could  get to the {self.plot_current + canvas_num} element')

            num_plots = len(self.plot_list)  # T - Total number of elements
            current_element_index = self.plot_current  # CE - Current element index (0-based)

            # Each page holds 4 elements
            elements_per_page = len(self.canvas_list)

            # Calculate total number of pages
            # We use ceil to round up because even a single element requires a whole page
            total_pages = -(-num_plots // elements_per_page)  # Equivalent to math.ceil(num_plots / elements_per_page)

            # Calculate current page
            # We add 1 because we're counting pages from 1, but elements are 0-indexed
            current_page = (current_element_index // elements_per_page) + 1

            # Create the string
            self.page_info = f"     page {current_page} of {total_pages}     "

            self.page_of_page.setText(self.page_info)

            #log.debug(f'New page of page text: {self.page_info}')

    def reports_page_forward(self):
        num_plots = len(self.plot_list)
        num_canvas = len(self.canvas_list)
        if self.plot_current + num_canvas < num_plots:
            self.plot_current = self.plot_current + num_canvas
        #print(f'page forward - plot_current: {self.plot_current}')

        self.update_reports_plots()

    def reports_page_back(self):
        num_canvas = len(self.canvas_list)
        if self.plot_current - num_canvas >= 0:
            self.plot_current = self.plot_current - num_canvas
        else:
            self.plot_current = 0
        #print(f'page back - plot_current: {self.plot_current}')

        self.update_reports_plots()

    def reports_create_pdf(self):
        #self.reports_protocol_athlete_analytics.create_pdf()
        self.plot_list
        output_file = 'testing/asf.pdf'
        protocol_obj = self.config_obj.protocol_obj

        if self.reports_protocol is None:
            msg = 'Not to be a wise guy but you need to select a report first:-)'
            jtd.JT_Dialog(parent=self, title='User error', msg=msg, type="ok")
            return

        log.debug(f'reports_create_pdf:  self.reports_protocol: {self.reports_protocol}')

        # the following is a total hack to deal with what happens with when the protocol is shortened to
        # eliminate L or R at the end.   Oh well, probably not the last HACK.   Something clearly needs
        # to be done to improve this model on protocols
        protocol_name = protocol_obj.get_short_name_by_short_protocol(self.reports_protocol)
        # pdf filename to be created
        pdf_filename = protocol_name + ' - ' + self.reports_athlete + '.pdf'
        output_file = self.config_obj.path_results + self.reports_athlete + '/' + pdf_filename

        #create the PDF file
        pdf_obj = jtpdf2.JT_PDF_2_across(self.config_obj, self.reports_athlete, protocol_name, self.config_obj.app_name, output_file)
        pdf_filepath = pdf_obj.add_plots_and_create_pdf(self.plot_list, self)

        # have the OS display the pdf
        util.open_file_in_native_viewer(pdf_filepath)

    def open_results_directory_in_OS(self):
        results_dir = self.config_obj.path_results
        util.open_file_explorer(results_dir)

if __name__ == "__main__":
    my_username = gt.getuser()
    my_platform = platform.system()
    log.msg(f"my_username: {my_username}")
    log.msg(f"my_system: {my_platform}")
    print(f'#######level_str: {log.level_str}, level {log.level}')

    app = QApplication(sys.argv)

    # configuration object for keys and values setup
    config_obj = jtc.JT_Config('TPC Analytics', 'TPC', None)

    #validate
    if config_obj.validate_install() == False:
        # get desired directory from user

        print('program has not been set up with all the necessary directions - run TPC_MAIN() to do so')
        sys.exit()

    window = TPC_Analytics_UI(config_obj)
    log.info(f'TPC_Analytics_UI path_app: {config_obj.path_app}')

    window.setWindowTitle(config_obj.app_name)

    def test_specific_trial():
        log.msg(f"path_app: {window.config_obj.path_app}")

        path_zTest = window.config_obj.path_app + 'zTest/'
        fp = path_zTest + 'JTDcmj_huey_2023-08-17_00-38-07.csv'
    #    fp = path_zTest + 'JTSextL_Mickey_2023-08-08_17-36-53.csv'
        fp_video1 = path_zTest + 'test_video1.mp4'
        fp_graph = path_zTest + 'graph1.png'

        trial = jtt.JT_Trial(window.config_obj)
        trial.validate_trial_path(fp)
        trial.process_summary()
        trial.trial_name = "srt test trial"
        trial.video_files["video1"]: fp_video1
        window.set_trial(trial)


#    window.load_tree()

    log.set_logging_level("INFO")
    window.show()
    result = app.exec()
    sys.exit(result)
