# Main program

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox
from PyQt6.QtWidgets import QLineEdit, QPushButton, QMenu, QComboBox, QToolBar, QRadioButton
from PyQt6.QtWidgets import QMessageBox, QDialog, QFileDialog
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtGui import QAction

from PIL import Image, ImageTk   # used for icon

# Import necessary modules
import os, platform, glob, sys, time, json, datetime
import getpass as gt   #username info
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import seaborn as sns   # pip install seaborn

# Importing Colors
colors_blue = sns.color_palette('Blues', 10)
colors_grey = sns.color_palette('Greys', 10)
colors = sns.color_palette('rocket', 10)
colors_icefire = sns.color_palette('icefire', 10)
colors3 = sns.color_palette('rainbow', 5)
colors_seismic = sns.color_palette('seismic', 10)

######################################################################
# debuggging and logging
from share import jt_util as util

# logging configuration - the default level if not set is DEBUG
log = util.jt_logging()

log.msg(f'INFO - Valid logging levels are: {util.logging_levels}')
log.set_logging_level("WARNING")  # this will show errors but not files actually processed

# import Jakes files
from share import jt_dialog as jtd
from share import jt_serial as jts
from share import jt_config as jtc
from share import jt_trial as jtt
from share import jt_trial_manager as jttm
from share import jt_video as jtv
from share import jt_plot as jtpl
from share import jt_maintenance_UI as jtmaint
from share import jt_preferences_UI as jtpref
import jt_main_analytics1 as jtanalytics

# Testing data
# if set to >= 0 it utilizes test data instead of data from serial line
test_data_file = None
#test_data_file = 'test_output_ex1.txt'

my_username = gt.getuser()
my_platform = platform.system()
log.msg(f"my_username: {my_username}")
log.msg(f"my_system: {my_platform}")

##################################################################################################

#### logging of calibration data for long term study
# my dict should include Serial Port, sensor (s1 or s2), zero, multiplier
def log_calibration_data(my_dict, path_log):

    my_dict['timestamp'] = time.time()
    my_dict['datetime'] = time.strftime("%Y%m%d_%H%M%S")
    my_dict['platform'] = my_platform
    my_dict['username'] = my_username

    my_list = []
    my_list.append(my_dict)

    df = pd.DataFrame(my_list)

    csv_log_filename = path_log + "strain_gauge_history.csv"

    if not os.path.isfile(csv_log_filename):
        df.to_csv(csv_log_filename, index=False)
    else:
        df.to_csv(csv_log_filename, mode='a', header=False, index=False)

#### read in test file and return data as a list of JSON files
# returns Dataframe with timestamp, s1, and s2
def read_test_file(filename):
    my_data = []
    #log.f(f"reading file {filename}, getting json field {json_field_name}")
    try:
        with open(filename, "r") as my_file:

            timestamp = time.time()

            for line in my_file:
                line = line.strip()  # Remove leading/trailing whitespace, including newlines

                # Process the line here
                line = line.replace("'", "\"")
                data = json.loads(line)

                s1 = data['s1']
                s2 = data['s2']
                row = [timestamp, s1, s2]

                my_data.append(row)

                timestamp += .01

        my_columns = ["Timestamp", "s1", "s2"]
        my_df = pd.DataFrame(my_data, columns=my_columns)

            #log.debug(f"filename: {filename} had len: {len(readings)} ")  # Or do something else with the line
    except FileNotFoundError:
        log.error(f"File '{filename}' not found.")
    except IOError:
        log.error("Error reading the file.")

    my_file.close()

    return my_df

##################################################################################################
##################################################################################################
##################################################################################################
class CMJ_UI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.application_name = "Taylor Performance Consulting Analytics"

        str = ""
        str = f"The following things will need to be set up in order to run this applicaton:\n"
        str = str + f"- assign USB communications port, see Settings tab\n"
        str = str + f"- assign list of users file (.csv), see Settings tab\n"
        str = str + f"- assign directory location of where to create output or saved files, see Settings tab\n"
        str = str + f"- calibration will need to be done for the left and right plates\n"
        str = str + f"  if only a single device is used then just the one calibration is necessary\n"
        str = str + f"  it is recommended that calibration be done for each testing session\n"
        str = str + f"  \n"
        self.help_str = str

        self.jt_reader = None
        self.video1 = None
        self.video2 = None
        self.trial = None
        self.analytics_ui = None
        self.video_on = False
        self.is_recording = False
        # initial state is saved as there is no data at this time to be saved
        self.saved = True  #flag so that the user can be asked if they want to save the previous set of data before recording new data

        self.last_original_filename = ""


#######################################################################
#### Main Screen ######################################################

        self.setWindowTitle(self.application_name)
        #        self.setGeometry(500, 100, 500, 700)

        menubar = self.menuBar()

        # Creating a File menu
        fileMenu = menubar.addMenu('File')

        # Creating actions for the File menu
        dirMaintAction = QAction('Directories and Maintenance', self)
        preferenceAction = QAction('Settings', self)   # this shows up as preferences in the MACOS
        aboutAction = QAction('About', self)

        # Adding actions to the File menu
        fileMenu.addAction(preferenceAction)
        fileMenu.addAction(dirMaintAction)
        fileMenu.addAction(aboutAction)

        # Connect the actions to their respective functions
        preferenceAction.triggered.connect(self.preferences_screen)
        dirMaintAction.triggered.connect(self.showDirMaint)
        aboutAction.triggered.connect(self.showAbout)


        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.grid_layout = QGridLayout(central_widget)

        trow = 0

        # Add Icon - Load the PNG image using PIL
        w = 75
        h = 75

        image = jtc.validate_path_and_return_QImage("jt.ico")
        scaled_image = image.scaled(w,h)
        ico_image = QPixmap.fromImage(scaled_image)

        # Create the ico label
        ico_label = QLabel(self)
        ico_label.setPixmap(ico_image)
        ico_label.setStyleSheet("background-color: rgba(255, 255, 255, 0);")   #make background transparent
        self.grid_layout.addWidget(ico_label, trow,0, 3, 1)

        # Preferences/Configurate/Settings button
        settings_image = QPixmap( jtc.validate_path_and_return_Pixmap("icon_settings.png") ).scaled(30, 30)
        settings_icon = QIcon(settings_image)

        # Create the ico image button
        self.gear_button = QPushButton(clicked=self.preferences_screen)
        self.gear_button.setIcon(settings_icon)
        self.gear_button.setIconSize(settings_image.size())
        self.gear_button.setStyleSheet("background-color: rgba(255, 255, 255, 0);")   #make background transparent
        self.grid_layout.addWidget(self.gear_button, trow, 3)

        trow += 1
        #clock
        self.clock_label = QLabel("12:33:44")
        self.clock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.addWidget(self.clock_label, trow, 3)

        #radio buttons
        self.single_radiobutton = QRadioButton("Single")
        self.single_radiobutton.toggled.connect( self.protocol_type_single)
        self.grid_layout.addWidget(self.single_radiobutton, trow, 1)
        trow += 1
        self.double_radiobutton = QRadioButton("Double")
        self.double_radiobutton.toggled.connect( self.protocol_type_double)
        self.grid_layout.addWidget(self.double_radiobutton, trow, 1)

        # protocol_name selection - COMBO BOX
        trow += 2
        self.protocol_name_combobox = QComboBox()
        self.protocol_name_combobox.setMinimumWidth(250)
        self.protocol_name_combobox.currentTextChanged.connect(self.protocol_name_combobox_changed)
        self.grid_layout.addWidget(self.protocol_name_combobox, trow, 1)

        trow += 1
        # column header of weight column
        self.l_display1 = QLabel("Weight (lbs)")
        self.l_display1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.l_display1.setFixedHeight(16)
        self.grid_layout.addWidget(self.l_display1, trow, 2)

        # Calibration for Left sensor
        trow += 1
        self.l_calibrate_button = QPushButton("Calibrate Left", clicked=self.l_calibrate)
        self.grid_layout.addWidget(self.l_calibrate_button, trow, 1)
        self.l_calibration_display = QLabel("0")  #, relief="solid"
        self.l_calibration_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.addWidget(self.l_calibration_display, trow, 2)

        # Calibration for Right sensor
        trow += 1
        self.r_calibrate_button = QPushButton("Calibrate Right", clicked=self.r_calibrate)
        self.grid_layout.addWidget(self.r_calibrate_button, trow, 1)
        self.r_calibration_display = QLabel(text="0")
        self.r_calibration_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.addWidget(self.r_calibration_display, trow, 2)

        # athlete selection - COMBO BOX
        trow += 1

        self.athlete_combobox = QComboBox()
        self.athlete_combobox.currentTextChanged.connect(self.athlete_combobox_change)
        self.grid_layout.addWidget(self.athlete_combobox, trow, 1)

        trow +=1
        self.video_checkbox = QCheckBox('Video On')
        self.video_checkbox.setChecked(False)
        self.video_checkbox.stateChanged.connect(self.on_video_checkbox_checkbox_changed)
        self.grid_layout.addWidget(self.video_checkbox, trow, 1)

        # Start/Stop buttons and dropdown menu for user
        trow += 1                                           # highlightbackground='lightgreen'
        self.start_button = QPushButton("Start", clicked=self.start_recording)
        self.grid_layout.addWidget(self.start_button, trow, 0)

        self.stop_button = QPushButton("Stop", clicked=self.stop_recording)
        self.stop_button.setEnabled(False)
        self.grid_layout.addWidget(self.stop_button, trow, 1)

        self.data_button = QPushButton("Analytics", clicked=self.jt_analytics)
        self.data_button.setEnabled(True)
        self.grid_layout.addWidget(self.data_button, trow, 2)

        # Save Data button and dropdown menu for user
        self.save_button = QPushButton("Save Data", clicked=self.save_data_to_csv)
        self.save_button.setEnabled(False)
        self.grid_layout.addWidget(self.save_button, trow, 3)

        #create area for graph
        trow += 1

        self.canvas = FigureCanvasQTAgg(plt.figure())
        self.grid_layout.addWidget(self.canvas, trow, 0, 1, 4)   #row 1, column 0, spanning 1 row and 4 columns
        self.grid_layout.setRowStretch(9, 1)
        self.grid_layout.setColumnStretch(0, 1)      # the next 3 lines say for the columns stretch evenlly
        self.grid_layout.setColumnStretch(1, 1)
        self.grid_layout.setColumnStretch(2, 1)
        self.grid_layout.setColumnStretch(3, 1)
 #       self.setLayout(self.grid_layout)

        # quit button
        trow += 1
        self.quit_button = QPushButton("Quit", clicked=self.close)
        self.grid_layout.addWidget(self.quit_button, trow, 3)


        #status field
        trow += 1
        #  self.status_str = tk.StringVar("my srt status")
        self.status_display = QLabel("")
        self.grid_layout.addWidget(self.status_display, trow, 0, 1, 4)

        #fire off timer that updates time as well as the weight fields
        time_interval = 500      # in milliseconds
        self.timer = QTimer()
        self.timer.setInterval(time_interval)  # Update every 0.5 seconds
        self.timer.timeout.connect(self.update_fields)
        self.timer.start()

        QTimer.singleShot(250, self.initial_setup_and_config)  # this does the initial setup of config/serial/athlete/etc

    #################################
    ##### Initial data setup - config_obj, Serial port, protocol, etc
    #################################
    def initial_setup_and_config(self):

        # config_obj for keys and values setup, first validate it and if it returns False then
        #
        self.config_obj = jtc.JT_Config(self.application_name, 'TPC')
        if self.config_obj.validate_install() == False:
            # get desired directory from user

            instructions = 'The next step will be to select the directory that the data will stored. '
            instructions = instructions + 'While technically changable, it is NOT easy to do so.  Select wisely grasshopper!'
            value = jtd.JT_Dialog(parent=self, title="Installation Directory",
                                  msg=instructions,
                                  type="ok")  # this is custom dialog class created above

            # get the new directory to store stuff in
            value = False
            while value == False:
                default_directory = self.config_obj.documents_folder
                directory = QFileDialog.getExistingDirectory(self, 'Select Directory', default_directory)
                value = jtd.JT_Dialog(parent=self, title="Install Directory", msg=f"Are you sure you want to save to: {directory}",
                                  type="yesnocancel")
                if value == True:
                    self.config_obj.setup_app_location(directory)
                if value == None:
                    sys.exit()

        log.msg(f"path_app: {window.config_obj.path_app}")

        ##### serial port setup #####
        self.reader_obj = jts.SerialDataReader()

        self.baud_rate = 115200
        self.calibration_measurement_count = 20 # for calibration readings
        self.updated_weight_count = 5      # for updating the weight on the screen
        self.serial_port = None

        self.serial_ports_list = self.reader_obj.get_available_ports()

        # if only one port available then attempt to connect to it
        if len(self.serial_ports_list) == 1:
            self.serial_port_name = self.serial_ports_list[0]
            log.debug(f"Only one port available, setting port to: {self.serial_port_name}, baud {self.baud_rate}")

            # attempt to connect to port
            if self.check_serial_port() != True:
                self.serial_port_name = None

        #if multiple serial ports attempt to connect to last port selected
        else:
            self.serial_port_name = self.config_obj.get_config("last_port")
            if self.check_serial_port() != True:
                self.serial_port_name = None

        ##### Protocol #####
        self.protocol_obj = self.config_obj.protocol_obj

        # protocol type
        self.protocol_type_selected = self.config_obj.get_config("protocol_type")

        if self.protocol_type_selected == None or len(self.protocol_type_selected) < 1:
            self.protocol_type_selected = "single"
        self.protocol_name_list = self.protocol_obj.get_names_by_type(self.protocol_type_selected)
        log.debug(f"protocol type_selected: {self.protocol_type_selected} name_list: {self.protocol_name_list}")

        # protocol name and validate it
        self.protocol_name_selected = self.config_obj.get_config("protocol_name")

        if ( self.protocol_name_selected == None or len(self.protocol_name_selected) < 1 or
                self.protocol_obj.validate_type_name_combination(self.protocol_type_selected, self.protocol_name_selected) == False ):
            self.protocol_name_selected = self.protocol_name_list[0]
        log.debug(f"protocol type_selected: {self.protocol_type_selected}, name_selected: {self.protocol_name_selected} name_list: {self.protocol_name_list}")

        if self.protocol_type_selected == "single":
            self.protocol_type_single()
            self.single_radiobutton.setChecked(True)
        else:
            self.protocol_type_double()
            self.double_radiobutton.setChecked(True)

        ##### Athletes #####
        try:
            # create the athletes Object
            self.athletes_obj = self.config_obj.athletes_obj
            self.athletes = self.athletes_obj.get_athletes()
        except:
            error = f'Could not find file: {self.config_obj.athletes_file_path}'
            value = jtd.JT_Dialog(parent=self, title="Athletes List Error", msg=error, type="ok")
            self.athletes = []

        self.last_run_athlete = self.config_obj.get_config("last_athlete")
        log.debug(f'last_athlete from config is {self.last_run_athlete}')
        if self.last_run_athlete == None:
            self.last_run_athlete = ""

        # add athletes to the list
        self.enable_config_save = False   #this is a hack just for startup mode so it doesn't save to the config file one time only
        self.athlete_combobox.addItems(self.athletes)
        self.enable_config_save = True

        try:
            index = self.athletes.index(self.last_run_athlete)
        except ValueError:
            index = 0
        self.athlete_combobox.setCurrentIndex(index)

        #Trial Manager
        self.trial_mgr_obj = jttm.JT_JsonTrialManager(self.config_obj)

        self.last_original_filename = self.config_obj.get_config("last_original_filename")

        ###### general setup ######
        self.results_df = pd.DataFrame()  # Empty DataFrame
        self.collecting_data = False

        if self.serial_port_name is None:
            temp_serial_port_name = "not_defined"
        else:
            temp_serial_port_name = self.serial_port_name

        # Calibration - attempt to read prior calibration information
        self.l_zero = self.config_obj.get_config("l_zero__" + temp_serial_port_name)
        if self.l_zero == None:
            self.l_zero = -1

        self.r_zero = self.config_obj.get_config("r_zero__" + temp_serial_port_name)
        if self.r_zero == None:
            self.r_zero = -1

        self.l_mult = self.config_obj.get_config("l_mult__" + temp_serial_port_name)
        if self.l_mult == None:
            self.l_mult = -1

        self.r_mult = self.config_obj.get_config("r_mult__" + temp_serial_port_name)
        if self.r_mult == None:
            self.r_mult = -1

        # regardless if prior calibration info found mark them as not calibrated so that dialog box pops up
        self.l_calibration = False
        self.r_calibration = False

        #variables for utilizing test data
        self.file_list = glob.glob("output*.txt")



    def check_serial_port(self):

        my_return = self.reader_obj.configure_serial_port(self.serial_port_name, self.baud_rate)
        if my_return:

            #validate some data is coming down the pipe
            if self.reader_obj.serial_port_validate_data('s2'):
                #store the current serial port into the configuration file
                self.config_obj.set_config("last_port", self.serial_port_name)
                return True
            else:
                value = jtd.JT_Dialog(parent=self, title="Serial Port Error",
                                       msg="Go to Settings tab and set the serial port, data doesn't look right",
                                       type="ok")  # this is custom dialog class created above
                return False
        else:
            value = jtd.JT_Dialog(parent=None, title="Serial Port Error",
                                  msg="Go to Settings tab and set the serial port",
                                  type="ok") # this is custom dialog class created above
            return False

    def showDirMaint(self):
        self.maintenance_window = jtmaint.JT_MaintenanceWindow(self.config_obj, self.reader_obj)
        self.maintenance_window.setModal(True)
        self.maintenance_window.show()

    def showAbout(self):
        log.debug("About clicked")

    def preferences_screen(self):
        self.preferences_window = jtpref.JT_PreferencesWindow(self.config_obj, self.reader_obj)
        try:
            self.preferences_window.show()
        except Exception as e:
            log.error(f"self.preferences_window.show() an error occurred: {e}")

    def protocol_type_single(self):
        log.f()
        self.protocol_type_selected = "single"
        self.config_obj.set_config("protocol_type", self.protocol_type_selected)

        #change the button text on the left calibrate button and setup combo box
        self.l_calibrate_button.setText( self.double_single_configuratrion_setup() )
        log.debug(f"protocol type_selected: {self.protocol_type_selected}, name_selected: {self.protocol_name_selected} name_list: {self.protocol_name_list}")

        self.r_calibrate_button.setVisible(False)
        self.r_calibration_display.setVisible(False)

    def protocol_type_double(self):
        log.f()
        self.protocol_type_selected = "double"
        self.config_obj.set_config("protocol_type", self.protocol_type_selected)

        #change the button text on the left calibrate button and setup combo box
        self.l_calibrate_button.setText( self.double_single_configuratrion_setup() )
        log.debug(f"protocol type_selected: {self.protocol_type_selected}, name_selected: {self.protocol_name_selected} name_list: {self.protocol_name_list}")

        self.r_calibrate_button.setVisible(True)
        self.r_calibration_display.setVisible(True)

    #set up button text for double and Single measurements
    def double_single_configuratrion_setup(self):

        #bonus finish out combo box
        self.protocol_name_list = self.protocol_obj.get_names_by_type(self.protocol_type_selected)
        self.protocol_name_selected = self.protocol_name_list[0]
        self.protocol_name_combobox.clear()
        self.protocol_name_combobox.addItems(self.protocol_name_list)

        if self.protocol_type_selected == 'single':
            return 'Calibrate'
        else:
            return 'Calibrate Left'

    def protocol_name_combobox_changed(self, value):
        log.f()
        self.protocol_name_selected = value
        self.config_obj.set_config("protocol_name", self.protocol_name_selected )
        log.debug(f"protocol name: {self.protocol_type_selected}, name_selected: {self.protocol_name_selected}, name_list: {self.protocol_name_list}")

    def l_calibrate(self):
        log.debug(f"left calibrate:" )

        if self.check_serial_port() != True:
            return

        value = jtd.JT_Dialog(self, "Left Calibration Zero", "Have nothing on the scale:", "okcancel") # this is custom dialog class created above
        if value:

            zero_reading = self.get_average_reading('s1_clean', 0, self.calibration_measurement_count)

            entered_weight = jtd.JT_Dialog_Integer(self, "Left Weighted Calibration", "Enter weight in lbs:", 30)
            if entered_weight is not None:
                #log.debug(f"Ok'ed weighted calibration: {entered_weight} lbs")
                weighted_reading = self.get_average_reading('s1_clean', entered_weight, self.calibration_measurement_count)
                self.l_zero = zero_reading
                self.l_mult = (weighted_reading - zero_reading)/entered_weight
                self.config_obj.set_config("l_zero__" + self.serial_port_name, self.l_zero)
                self.config_obj.set_config("l_mult__" + self.serial_port_name, self.l_mult)
                self.l_calibration = True

                log.debug(f"Left Calibration - entered_weight: {entered_weight}, zero: {zero_reading}, weighted: {weighted_reading}, multiplier: {self.l_mult}")
                self.message_line(f"Left sensor calibrated")

                my_dict = {}
                my_dict['serial port'] =self.serial_port_name
                my_dict['sensor'] = 's1'
                my_dict['zero'] = self.l_zero
                my_dict['multiplier'] = self.l_mult
                log_calibration_data(my_dict, self.config_obj.path_log)


    def r_calibrate(self):
        log.debug(f"right calibrate:" )

        if self.check_serial_port() != True:
            return

        value = jtd.JT_Dialog(self, "Right Calibration Zero", "Have nothing on the scale:", "okcancel") # this is custom dialog class created above
        if value:

            zero_reading = self.get_average_reading('s2_clean', 0, self.calibration_measurement_count)

            entered_weight = jtd.JT_Dialog_Integer(self, "Right Weighted Calibration", "Enter weight in lbs:", 30)
            if entered_weight is not None:
                #log.debug(f"Ok'ed weighted calibration: {entered_weight} lbs")
                weighted_reading = self.get_average_reading('s2_clean', entered_weight, self.calibration_measurement_count)
                self.r_zero = zero_reading
                self.r_mult = (weighted_reading - zero_reading)/entered_weight
                self.config_obj.set_config("r_zero__" + self.serial_port_name, self.r_zero)
                self.config_obj.set_config("r_mult__" + self.serial_port_name, self.r_mult)
                self.r_calibration = True

                log.debug(f"Right Calibration - entered_weight: {entered_weight}, zero: {zero_reading}, weighted: {weighted_reading}, multiplier: {self.r_mult}")
                self.message_line(f"Right sensor calibrated")
                my_dict = {}
                my_dict['serial port'] =self.serial_port_name
                my_dict['sensor'] = 's2'
                my_dict['zero'] = self.r_zero
                my_dict['multiplier'] = self.r_mult
                log_calibration_data(my_dict, self.config_obj.path_log)

    def athlete_combobox_change(self, value):
        if self.enable_config_save:
            self.last_run_athlete = value
            self.config_obj.set_config("last_athlete", self.last_run_athlete)

        log.debug(f'athlete_combobox_change: {value}')

    def on_video_checkbox_checkbox_changed(self, value):

        if value != 0:
            self.video_on = True
            camera_index = self.config_obj.get_config('camera1')
            if camera_index != None and camera_index > -1:
                self.video1 = jtv.JT_Video(self.config_obj)
                self.video1.display_video = False       # turns off writing the video to the screen
                self.video1.save_frames = True          # turns on recording of a video
                self.video1.camera_index = camera_index
                log.debug(f"video1 configured for index: {camera_index}")

        else:
            self.video1.quit()
            self.video_on = False

    def start_recording(self):
        log.f()

        #check if athlete selected
        if len(self.last_run_athlete) < 1:
            jtd.JT_Dialog(parent=self, title="Start Run",
                                   msg="You Must specify an athlete to run",
                                   type="ok")
            return

        #prior run saved?  if it has not been saved then request for them to save it
        if self.saved == False:

            value = jtd.JT_Dialog(parent=self, title="Save Last Run", msg="Save last run? NO will lose data",
                                       type="yesno")
            # save the data if requested
            if value == True:
                self.save_data_to_csv(True)
            else:
                pass

            jtd.JT_Dialog(parent=self, title="Start Run", msg="Press ok to start run", type="ok")

        # Calibration - check with user if they want to proceed without calibration?
        if self.protocol_type_selected == 'single' and self.l_calibration == False:
            value = jtd.JT_Dialog(parent=self, title="Uncalibrated", msg="Continue uncalibrated?",
                                   type="yesno")  # this is custom dialog class created above
            if value == False:
                return
        elif self.protocol_type_selected == 'double' and (self.l_calibration == False or self.r_calibration == False):
            value = jtd.JT_Dialog(parent=self, title="Uncalibrated", msg="Continue uncalibrated?",
                                   type="yesno")  # this is custom dialog class created above
            if value == False:
                return

        # remove the graph from the canvas
        if self.canvas:
            self.canvas.figure.clear()
            self.canvas.draw()

        #button enabled/disabled
        self.buttons_running()
        self.saved = False
        self.start_time = time.time()

        #start recording thread
        self.is_recording = True

        # if in testing mode them skip actually getting data and allow the stop button to read it from a file
        if test_data_file == None:
            self.reader_obj.start_reading()
            #start video
            if self.video_on == True:
                self.video1.start()

        log.debug(f"Start recording, protocol: {self.protocol_name_selected}, athlete: {self.last_run_athlete}")

    def stop_recording(self):
        log.f()

        self.is_recording = False
        if self.video_on == True:
            self.video1.stop()

        #button enabled/disabled
        self.buttons_stopped()

        if test_data_file == None:
            self.num_measurements = self.reader_obj.stop_reading()
            if self.num_measurements == 0:
                jtd.JT_Dialog(parent=self, title="Run Error", msg="No data collected, press ok to continue", type="ok")
                return
        else:
            log.debug(f"UTILIZING TEST FILE: {test_data_file}")
            my_df = read_test_file(test_data_file)
            self.reader_obj.set_test_data_list(my_df)
            self.num_measurements = len(my_df)

        log.debug(f"stop_recording, num meas: {self.num_measurements}, protocol: {self.protocol_name_selected}")
        # get the df
        # def get_data_df(self, l_zero=0, l_mult=1, r_zero=0, r_mult=1, athlete='na', protocol='na'):
        leg = self.protocol_obj.get_leg_by_name(self.protocol_name_selected)
        self.results_df = self.reader_obj.get_data_df(self.l_zero, self.l_mult, self.r_zero, self.r_mult,
                    self.last_run_athlete, self.protocol_name_selected, self.protocol_type_selected, leg)

        log.debug(f"results_df columns: {self.results_df.columns}")
        log.debug(f"results_df: {self.results_df.head(3)}")

        #display graphed results on screen
        self.canvas.figure.clear()
        axes = self.canvas.figure.add_subplot(111)

        # jt_color1 = colors_seismic[2]
        # jt_color2 = colors_icefire[4]
        #
        # if self.protocol_type_selected == 'single':
        #     axes.plot(self.results_df['force_N'], linewidth=1, color=jt_color1, label='Force')
        # else:
        #     axes.plot(self.results_df['l_force_N'], linewidth=1, color=jt_color1, label="Left")
        #     axes.plot(self.results_df['r_force_N'], linewidth=1, color=jt_color2, label="Right")
        #
        # axes.legend()
        # axes.set_title("Current run", fontdict={'fontweight': 'bold', 'fontsize': 12})
        # axes.set_ylabel("force (N)")
        # axes.set_xlabel("measurement number")

        if self.protocol_type_selected == 'single':
            line_data = [
                {'y': self.results_df['force_N'], 'label': 'Force (N)', 'color': 0}]

        else:
            line_data = [
                {'y': self.results_df['l_force_N'], 'label': 'Left', 'color': 0},
                {'y': self.results_df['r_force_N'], 'label': 'Right', 'color': 1}]

        my_plot = jtpl.JT_plot('Current run', 'measurement number', 'force (N)', line_data)
        my_plot.set_marker_none()
        my_plot.draw_on_pyqt(axes, self.canvas.figure)

        self.canvas.draw()

        end_time = time.time()
        elapsed = end_time - self.start_time

        elapsed_str = "{:.2f}".format(elapsed)

        self.message_line(f"Elapsed Time: {elapsed_str}, recorded {len(self.results_df)}")

    def buttons_running(self):
        #flip flop which buttons are enabled
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
#        self.data_button.setEnabled(False)
        self.l_calibrate_button.setEnabled(False)
        self.r_calibrate_button.setEnabled(False)
        self.save_button.setEnabled(False)

    def buttons_stopped(self):
        #flip flop which buttons are enabled
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
#        self.data_button.setEnabled(True)
        self.l_calibrate_button.setEnabled(True)
        self.r_calibrate_button.setEnabled(True)
        self.save_button.setEnabled(True)

    def message_line(self, msg):
        self.status_display.setText(msg)

    #### Clock updating
    def update_fields(self):

        current_time = time.strftime('%H:%M:%S')
        #log.debug(f"update time: {current_time}")
        self.clock_label.setText(current_time)

        #only update weights if nobody else is reading in data, and the serial port is configured in reader_obj
        doit = True
        if self.reader_obj is not None:
            if self.is_recording == False and self.reader_obj.serial_port != None and doit == True:

      #          log.debug(f"updating clock and weights")
                left_weight = self.get_average_reading('s1_clean', 0, self.updated_weight_count)
                l_force = self.get_force_lbs(left_weight, self.l_zero, self.l_mult)
                self.l_calibration_display.setText("{:.0f}".format(l_force))  #format force to just an integer

                #only do the measurements if both legs are being measured
                if self.protocol_type_selected != 'single':
                    right_weight = self.get_average_reading('s2_clean', 0, self.updated_weight_count)
                    r_force = self.get_force_lbs(right_weight, self.r_zero, self.r_mult)
                    self.r_calibration_display.setText("{:.0f}".format(r_force))

    def jt_analytics(self):

        if self.analytics_ui == None:
            self.analytics_ui = jtanalytics.JT_Analytics_UI(parent=self)

# not sure that this was needed in order to go to jt_analytics
#            if self.last_original_filename:
#                self.trial_mgr_obj.load_all_trials()

            if self.trial != None:
                self.analytics_ui.set_trial( self.trial)

#            self.analytics_ui.set_video1('resources/testing/test_video.mp4')

            self.analytics_ui.show()

            # connect to closed event of analytics window
            self.analytics_ui.closed.connect(self.analytics_ui_closed)

    # catch closed event
    def analytics_ui_closed(self):
        log.debug("analytics window closed.")
        self.analytics_ui = None

    ########  SAVE DATA ########
    def save_data_to_csv(self, lose_last_run=False):

        if lose_last_run == True:
            value = jtd.JT_Dialog(parent=self, title="Save Last Run", msg="If you say NO it will be lost", type="yesno")
        else:
            value = jtd.JT_Dialog(parent=self, title="Save Last Run", msg="Do you want to save the last run?", type="yesno")

        if value:

            protocol_filename = self.protocol_obj.get_protocol_by_name(self.protocol_name_selected)

            # Create Trial which will allow dataframe, videos and images to be saved
            self.trial = jtt.JT_Trial(self.config_obj)
            self.trial.setup_for_save(self.last_run_athlete, protocol_filename )
            self.trial.attach_results_df(self.results_df)

            # add videos
            if self.video1 != None:
                self.trial.attach_video('VIDEO_1', self.video1)

            if self.video2 != None:
                self.trial.attach_video('VIDEO_2', self.video2)

            # save Trial to disk (run/videos/images)
            trial_dict = self.trial.save_raw_trial()
            self.last_original_filename = trial_dict['original_filename']
            filepath = self.config_obj.path_data + '/' + self.last_run_athlete + '/' + self.last_original_filename

            # process the Trial (this creates summary data from it
            # this creates the summary data and there is also some graphs that are produced
            # the graph location(s) are returned in the return_dict
            if self.trial.process_summary() == False:
                # do something - throw message up on screen about couldn't write summarize trial
                pass

            # save the summary data
            images_dict = self.trial.save_summary()

            #save the last_original filename - not sure why but what the heck
            self.config_obj.set_config("last_original_filename", self.last_original_filename)

            if(images_dict != False):
                trial_dict.update(images_dict)
            else:
                log.error(f'No Dictionary returned trial.save_summary while processing: {filepath}')

            #save trial structural information to disk
            self.trial_mgr_obj.save_trial_indexing(trial_dict)

            self.saved = True
            self.save_button.setEnabled(False)
            self.message_line(f"saved file: {self.last_original_filename}")


    #get weight (lbs or kg) using zero, multiplier, and wether or not kb or lbs
    def get_force_lbs(self, reading, zero, multiplier):

        force = -101
        if multiplier != 0:
            force = (reading - zero)/multiplier

        return force

    ##   averages "n" readings for calibration
    def get_average_reading(self, json_field_name, calibration_weight, num_measurements):

        if(test_data_file == None):

            self.is_recording = True
            my_df = self.reader_obj.read_lines(num_measurements)
            self.is_recording = False

        else:
            if calibration_weight == 0:
                my_df = read_test_file('test_output_0_lbs.txt')
            else:
                my_df = read_test_file('test_output_30_lbs.txt')

            self.reader_obj.set_test_data_list( my_df)

        my_df = self.reader_obj.get_data_df()
        if len(my_df) > 0:
            avg_reading = my_df[json_field_name].mean()
        #log.f(f"average: {avg_reading}")
        else:
            avg_reading =-101

        return avg_reading

####################################################
if __name__ == "__main__":
    # Replace these values with the correct serial port and baud rate for your sensor

    log.set_logging_level("DEBUG")

    app = QApplication(sys.argv)
    window = CMJ_UI()

    window.adjustSize()
    window.show()

#    window.initial_setup_and_config()

    # update clock initially which also starts timer for it
#    window.update_fields()
    result = app.exec()
    sys.exit(result)



