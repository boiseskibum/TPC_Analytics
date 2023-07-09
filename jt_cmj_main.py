import serial
import serial.tools.list_ports
import tkinter as tk
import tkinter.simpledialog as sd
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk   # used for icon

import threading
import pandas as pd
import json

# Import necessary modules
import os
import platform
import glob
import sys
import time
import datetime
from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns   #pip install seaborn

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

# this appends to the path so that files can be picked up in the different sub directories
sys.path.append('./share')
sys.path.append('./JT_analytics')
sys.path.append('./JT_capture')

import jt_util as util

# set base and application path
path_base = util.jt_path_base()  # this figures out right base path for Colab, MacOS, and Windows
print(f"")

# setup path variables for base and misc
path_app = path_base + 'Force Plate Testing/'
path_data = path_app + 'data/'
path_results = path_app + 'results/'
path_log = path_app + 'log/'
path_config = path_app + 'config/'

# validate that all paths exist
if not os.path.isdir(path_base):
    print(f'ERROR path: {path_base} does not exist')
if not os.path.isdir(path_app):
    print(f'ERROR path: {path_app} does not exist')
if not os.path.isdir(path_data):
    print(f'ERROR path: {path_data} does not exist')


# logging configuration - the default level if not set is DEBUG
log = util.jt_logging()

log.msg(f'INFO - Valid logging levels are: {util.logging_levels}')
log.set_logging_level("WARNING")  # this will show errors but not files actually processed
# log.set_logging_level("INFO")   # this will show each file processed

# Save log file to the directory specified
# log.set_log_file(path_log, 'cmj_')

import jt_dialog as jtd
import jt_serial as jts
import jt_protocol as jtp
import jt_athletes as jta

# if set to >= 0 it utilizes test data instead of data from serial line
test_data_file = None
#test_data_file = 'test_output_ex1.txt'

#configuration file name, holds last port #, and anothr other state information
app_config_file = path_config + "jt_cmj_main_config.json"

#protocol configs holds all the infor about single, double, name and actual protocol used
protocol_config_file = path_config + "jt_protocol_config.csv"

jt_icon_path = "jt.png"    #icon for message boxes
log.msg(f"path_base: {path_base}")
log.msg(f"my_username: {my_username}")
log.msg(f"my_system: {my_platform}")
log.msg(f"app_config_file: {app_config_file}")
log.msg(f"protocol_config_file: {protocol_config_file}")


# sets up the TTK Tkinter theme being used (see code below in the main to complete this)
def set_theme(my_root):
    os_name = platform.system()

    if os_name == "Darwin":
        # macOS
        theme = "aqua"
    elif os_name == "Windows":
        # Windows
        theme = "vista"
    else:
        # Default theme
        theme = "default"

    # Set the theme
    my_root.style.theme_use(theme)

##################################################################################################


#return the key value, if nothing found then None reurned
def get_config_key(my_key):
    try:
        with open(app_config_file, "r") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {}

    #if the key is not found then "None" is returned
    last_key_value = config.get(my_key, None)

    return last_key_value

#set a key/value in the config file
def set_config_key(my_key, new_key_value):
    try:
        with open(app_config_file, "r") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {}

    config[my_key] = new_key_value
    with open(app_config_file, "w") as f:
        json.dump(config, f)

    return

#### logging of calibration data for long term study
def log_calibration_data(my_dict)

    my_dict['timestamp'] = time.time()
    my_dict['platform'] = my_platform
    my_dict['username'] = my_username

    my_csv_filename = path_log + "strain_gauge_multiplier-zero_history.csv"
    df.to_csv(my_csv_filename, mode='a', header=not os.path.isfile(my_csv_filename))


#### read in test file and return data as a list of JSON files
# returns Dataframe with timestamp, s1, and s2
def read_test_file(filename):
    my_data = []
    raw_data = []
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
class CMJ_UI(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()

        self.application_name = "Jake Taylor Analytics for Athletes"

        self.master.title(self.application_name)

        ##### serial port setup #####

        # get my my customized serial object
        self.jt_reader = jts.SerialDataReader()

        self.serial_ports_list = self.jt_reader.get_available_ports()

        self.baud_rate = 115200
        self.calibration_measurement_count = 20 # for calibration readings
        self.updated_weight_count = 5      # for updating the weight on the screen
        self.serial_port = None

        # if only one port available then attempt to connect to it
        if len(self.serial_ports_list) == 1:
            self.serial_port_name = self.serial_ports_list[0]
            log.debug(f"Only one port available, setting port to: {self.serial_port_name}, baud {self.baud_rate}")

            # attempt to connect to port
            if self.check_serial_port() != True:
                self.serial_port_name = None

        #if multiple serial ports attempt to connect to last port selected
        else:
            self.serial_port_name = get_config_key("last_port")
            if self.check_serial_port() != True:
                self.serial_port_name = None

        self.is_recording = False

        ##### Protocol #####

        # Get list of protocols, throw error message if unsuccessful at getting list
        try:
            self.protocol_obj = jtp.JT_protocol(protocol_config_file)
            str = self.protocol_obj.validate_data()
            if len(str) > 0:
                dialog = jtd.JT_Dialog(parent=self.master, title="ERROR: Protocol Config Validation",
                                       msg=f"{str}",
                                       type="ok")  # this is custom dialog class created above
        except:
            dialog = jtd.JT_Dialog(parent=self.master, title="Protocol Config File ERROR",
                                   msg=f"{protocol_config_file} could not be opened or found",
                                   type="ok")  # this is custom dialog class created above

        # protocol type
        self.protocol_type_selected = get_config_key("protocol_type")

        if self.protocol_type_selected == None or len(self.protocol_type_selected) < 1:
            self.protocol_type_selected = "single"
        self.protocol_name_list = self.protocol_obj.get_names_by_type(self.protocol_type_selected)

        log.debug(f"protocol type_selected: {self.protocol_type_selected} name_list: {self.protocol_name_list}")

        # protocol name
        self.protocol_name_selected = get_config_key("protocol_name")

        # validate protocol_name
        if ( self.protocol_name_selected == None or len(self.protocol_name_selected) < 1 or
                self.protocol_obj.validate_type_name_combination(self.protocol_type_selected, self.protocol_name_selected) == False ):
            self.protocol_name_selected = self.protocol_name_list[0]

        log.debug(f"protocol type_selected: {self.protocol_type_selected}, name_selected: {self.protocol_name_selected} name_list: {self.protocol_name_list}")

        self.saved = True  #flag so that the user can be asked if they want to save the previous set of data before recording new data

        ##### Athletes #####
        # get list of valid athletes, last athlete, output_file_dir
        self.athletes_list_filename = get_config_key( my_platform + "-athletes_list_filename_key")

        try:
            # create the athletes Object
            self.athletes_obj = jta.JT_athletes(self.athletes_list_filename) # get list of valid athletes from CSV file
            self.athletes = self.athletes_obj.get_athletes()
        except:
            dialog = jtd.JT_Dialog(parent=self.master, title="Athletes List Error", msg="Go to Settings tab and set the location for the athletes list", type="ok") # this is custom dialog class created above
            self.athletes = []

        self.last_run_athlete = get_config_key("last_athlete")

        self.output_file_dir = get_config_key( my_platform + "-output_file_dir")

        ###### general setup
        self.results_df = pd.DataFrame()  # Empty DataFrame
        self.collecting_data = False

        # Calibration - attempt to read prior calibration information
        self.l_zero = get_config_key("l_zero")
        if self.l_zero == None:
            self.l_zero = -1

        self.r_zero = get_config_key("r_zero")
        if self.r_zero == None:
            self.r_zero = -1

        self.l_mult = get_config_key("l_mult")
        if self.l_mult == None:
            self.l_mult = -1

        self.r_mult = get_config_key("r_mult")
        if self.r_mult == None:
            self.r_mult = -1

        # regardless if prior calibration info found mark them as not calibrated so that dialog box pops up
        self.l_calibration = False
        self.r_calibration = False

        #variables for utilizing test data
        self.file_list = glob.glob("output*.txt")

        # Create notebook with tabs
        self.notebook = ttk.Notebook(self.master)

        # this gets windows to expand for size of overall window
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.notebook.grid_rowconfigure(0, weight=1)
        self.notebook.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.tab_config = ttk.Frame(self.notebook)
        self.tab_help = ttk.Frame(self.notebook)

        self.notebook.add(self.tab1, text=" Collection ")
        self.notebook.add(self.tab_config, text=" Settings ")
        self.notebook.add(self.tab2, text=" Last Results ")
        self.notebook.add(self.tab_help, text=" Help ")

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

####  TAB 1 - Main ######################################################
        #  CMJ

        trow = 0

        # Add Icon - Load the PNG image using PIL
        #remove the image stuff for now
        if False:
            image = Image.open("jt.png")
            image = image.resize((100, 100))
            image_tk = ImageTk.PhotoImage(image)  # Convert the image to Tkinter-compatible format

            self.image_label = ttk.Label(self.tab1, image=image_tk)

            self.image_label.grid(row=trow, column=0, columnspan=1)  # Adjust the grid position as needed

        #clock
#        self.clock_label = ttk.Label(self.tab1, font=('Arial', 16), anchor="center")
        self.clock_label = ttk.Label(self.tab1, font=('Arial', 16))
        self.clock_label.grid(row=trow, column=3, columnspan=1, sticky="nsew")  # Adjust the grid position as needed

        #radio buttons
        self.protocol_selected_type_var = tk.StringVar(value=self.protocol_type_selected)  # Control variable to track the selected option

        self.single_radiobutton = ttk.Radiobutton(self.tab1, text="Single", variable=self.protocol_selected_type_var, value="single", command=self.toggle_protocol_type)
        self.single_radiobutton.grid(row=trow, column=1, sticky="nsew")

        trow += 1
        self.cmj_radiobutton = ttk.Radiobutton(self.tab1, text="Double", variable=self.protocol_selected_type_var, value="double", command=self.toggle_protocol_type)
        self.cmj_radiobutton.grid(row=trow, column=1, sticky="nsew")

        # protocol_name selection - COMBO BOX
        trow += 2
        self.protocol_name_combobox_var = tk.StringVar(value=self.protocol_name_selected)
        self.protocol_name_combobox = ttk.Combobox(self.tab1, values=self.protocol_name_list, textvariable=self.protocol_name_combobox_var)
        self.protocol_name_combobox.grid(row=trow, column=1, sticky="nsew")
        self.protocol_name_combobox.bind("<<ComboboxSelected>>", self.protocol_name_combobox_changed)

        trow += 1
        # column header of weight column
        self.l_display1 = ttk.Label(self.tab1, text="Weight (lbs)", width=10, anchor="center")
        self.l_display1.grid(row=trow, column=2)

        # Calibration for Left sensor
        trow += 1
        self.l_calibrate_button = ttk.Button(self.tab1, text=self.calibrate_button_text(), command=lambda:self.l_calibrate('s1'))
        self.l_calibrate_button.grid(row=trow, column=1, sticky="nsew")
        self.l_calibration_display = ttk.Label(self.tab1, text="0", width=10, anchor="center")  #, relief="solid"
        self.l_calibration_display.grid(row=trow, column=2, sticky="nsew")

        # Calibration for Right sensor
        trow += 1
        self.r_calibrate_button = ttk.Button(self.tab1, text="Calibrate Right", command=lambda: self.r_calibrate('s2'))
        self.r_calibrate_button.grid(row=trow, column=1, sticky="nsew")
        self.r_calibration_display = ttk.Label(self.tab1, text="0", width=10, anchor="center")
        self.r_calibration_display.grid(row=trow, column=2, sticky="nsew")

        # athlete selection - COMBO BOX
        trow += 1
        self.athlete_combobox_var = tk.StringVar(value=self.last_run_athlete)
        self.athlete_combobox = ttk.Combobox(self.tab1, values=self.athletes, textvariable=self.athlete_combobox_var)
        self.athlete_combobox.grid(row=trow, column=1, sticky="nsew")
        self.tab1.grid_rowconfigure(trow, weight=1)

        # Start/Stop buttons and dropdown menu for user
        trow += 1                                           # highlightbackground='lightgreen'
        self.start_button = ttk.Button(self.tab1, text="Start", width=15, command=self.start_recording, padding=10)
        self.start_button.grid(row=trow, column=0, sticky="nsew")

        self.stop_button = ttk.Button(self.tab1, text="Stop", width=10, command=self.stop_cmj_recording)
        self.stop_button.grid(row=trow, column=1, sticky="nsew")
        self.stop_button.configure(state=tk.DISABLED)
        self.tab1.grid_rowconfigure(trow, weight=1)

        # Save Data button and dropdown menu for user
        self.save_button = ttk.Button(self.tab1, text="Save Data", width=10, command=self.save_data_to_csv)
        self.save_button.grid(row=trow, column=3, sticky="nsew")
        self.save_button.configure(state=tk.DISABLED)
        self.tab1.grid_rowconfigure(trow, weight=1)

        #create area for graph
        trow += 1
        self.fig_tab1 = plt.figure(figsize=(3, 2)) # Set the size of the first graph  (5,3
#        self.fig_tab1, self.ax_tab1 = plt.subplots()
        self.canvas_tab1 = FigureCanvasTkAgg(self.fig_tab1, master=self.tab1)
        self.canvas_tab1.draw()
        self.canvas_tab1.get_tk_widget().grid(row=trow, column=0, padx=5, pady=5, columnspan=4, sticky="new")
        self.tab1.grid_rowconfigure(trow, weight=1)

        # quit button
        trow += 1
        self.quit_button = ttk.Button(self.tab1, text="Quit", width=12, command=self.quit_app)
        self.quit_button.grid(row=trow, column=3, sticky="s")
        self.tab1.grid_rowconfigure(trow, weight=1)

        #status field
        trow += 1
        #  self.status_str = tk.StringVar("my srt status")
        self.status_display =  tk.Label(self.tab1, text="", height =2)
        self.status_display.grid(row=trow, column=0, columnspan=4)
        self.tab1.grid_rowconfigure(trow, weight=1)

#        self.tab1.grid_columnconfigure(0, weight=1)

        #######  Last thing on first tab to make sure is right
        #set up initial buttons to either be shown or not based upon current state (single or double)
        #technically this doesn't actually toggle them, it leaves it in the current state
        self.toggle_protocol_type()


        ####  TAB 2 - Last Results screen

        self.dataframe_frame = ttk.Frame(self.tab2)

        self.text_widget_results = tk.Text(self.tab2, height=20 , width=60)
        self.scrollbar_y = tk.Scrollbar(self.tab2, command=self.text_widget_results.yview)
        self.scrollbar_x = tk.Scrollbar(self.tab2, command=self.text_widget_results.xview, orient='horizontal')

        self.text_widget_results.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_widget_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ### TAB 3 - Config

        #list of athletes configure
        trow = 0
        self.athletes_button = ttk.Button(self.tab_config, text="Set Athletes List Filename", command=self.get_athletes_list_filename)
        if self.athletes_list_filename == None:
            file_name = "Needs to be selected"
        else:
            file_name = os.path.basename(self.athletes_list_filename)

        self.athletes_list_filename_display = ttk.Label(self.tab_config, text=file_name, width=40)
        self.athletes_button.grid(row=trow, column=0, sticky="nsew")
        self.athletes_list_filename_display.grid(row=trow, column=1, sticky="w")

        #file output directory
        trow += 1
        if self.output_file_dir == None:
            output_file_dir = "Needs to be selected"
        else:
            output_file_dir = os.path.basename(self.output_file_dir)
        self.output_file_dir_button = ttk.Button(self.tab_config, text="Set Output File Directory", command=self.set_output_file_dir)
        self.output_file_dir_display = ttk.Label(self.tab_config, text=output_file_dir, width=40)
        self.output_file_dir_button.grid(row=trow, column=0, sticky="nsew")
        self.output_file_dir_display.grid(row=trow, column=1, sticky="w")

        #serial port list
        trow += 1
        self.reload_serial_button = ttk.Button(self.tab_config, text="Reload Serial Ports", command=self.reload_serial_ports)

        self.serial_combobox_var = tk.StringVar(value=self.serial_port_name)
        self.serial_combobox = ttk.Combobox(self.tab_config, textvariable=self.serial_combobox_var, values=self.serial_ports_list)
        self.serial_combobox.bind("<<ComboboxSelected>>", self.on_serial_combobox_select)

        self.reload_serial_button.grid(row=trow, column=0, sticky="nsew")
        self.serial_combobox.grid(row=trow, column=1)

        #validate serial port
        trow += 1
        self.validate_button = ttk.Button(self.tab_config, text="Validate Serial Port", command=self.read_serial_data)
        self.validate_button.grid(row=trow, column=0, sticky="nsew")


        trow += 1
        self.text_area = tk.Text(self.tab_config, height=10)
        self.text_area.grid(row=trow, column=0, sticky="w", columnspan=3)

        self.dataframe_frame = ttk.Frame(self.tab_help)

        self.text_widget_help = tk.Text(self.tab_help, height=35 , width=60)
        self.scrollbar_y = tk.Scrollbar(self.tab_help, command=self.text_widget_help.yview)
        self.scrollbar_x = tk.Scrollbar(self.tab_help, command=self.text_widget_help.xview, orient='horizontal')

        self.text_widget_help.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_widget_help.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        #add in new text strf
        self.text_widget_help.insert(tk.END, f"{self.application_name} Help Information: \n\n{self.help_str}")

    def check_serial_port(self):

        my_return = self.jt_reader.configure_serial_port(self.serial_port_name, self.baud_rate)
        if my_return:

            #validate some data is coming down the pipe
            if self.jt_reader.serial_port_validate_data('s2'):
                #store the current serial port into the configuration file
                set_config_key("last_port", self.serial_port_name)
                return True
            else:
                dialog = jtd.JT_Dialog(parent=self.master, title="Serial Port Error",
                                       msg="Go to Settings tab and set the serial port, data doesn't look right",
                                       type="ok")  # this is custom dialog class created above
                return False
        else:
            dialog = jtd.JT_Dialog(parent=self.master, title="Serial Port Error", msg="Go to Settings tab and set the serial port", type="ok") # this is custom dialog class created above
            return False

    def toggle_protocol_type(self):
        log.f()
        self.protocol_type_selected = self.protocol_selected_type_var.get()
        set_config_key("protocol_type", self.protocol_type_selected )

        self.protocol_name_list = self.protocol_obj.get_names_by_type(self.protocol_type_selected)
        self.protocol_name_selected = self.protocol_name_list[0]
        self.protocol_name_combobox_var.set(self.protocol_name_selected)
        self.protocol_name_combobox['values'] = self.protocol_name_list

        #change the button text on the left calibrate button
        self.l_calibrate_button.configure(text = self.calibrate_button_text())
        log.debug(f"protocol type_selected: {self.protocol_type_selected}, name_selected: {self.protocol_name_selected} name_list: {self.protocol_name_list}")

        if self.protocol_type_selected == "double":
            self.r_calibrate_button.grid()
            self.r_calibration_display.grid()

        elif self.protocol_type_selected == "single":
            self.r_calibrate_button.grid_remove()
            self.r_calibration_display.grid_remove()

    def calibrate_button_text(self):
        if self.protocol_type_selected == 'single':
            return 'Calibrate'
        else:
            return 'Calibrate Left'

    def protocol_name_combobox_changed(self, event):
        log.f()
        self.protocol_name_selected = self.protocol_name_combobox.get()
        set_config_key("protocol_name", self.protocol_name_selected )
        log.debug(f"protocol name: {self.protocol_type_selected}, name_selected: {self.protocol_name_selected}, name_list: {self.protocol_name_list}")


    def display_graph_results2(self, fig, canvas, df_column, title):
        self.fig_tab1.clear()
        self.subplot = self.fig_tab1.add_subplot(111)

        jt_color1 = colors_seismic[2]
        jt_color2 = colors_icefire[4]

        if self.protocol_type_selected == 'single':
            self.subplot.plot(self.results_df['force_N'], linewidth=1, color=jt_color1)

        else:
            self.subplot.plot(self.results_df['l_force_N'], linewidth=1, color=jt_color1)
            self.subplot.plot(self.results_df['r_force_N'], linewidth=1, color=jt_color2)

        self.subplot.set_title("Abc", fontdict={'fontweight': 'bold', 'fontsize': 12})
        canvas.draw()
        log.debug(f"displayed graph: {title}, {df_column}")

    def l_calibrate(self, json_key):
        log.debug(f"left calibrate:" )

        if self.check_serial_port() != True:
            return

        dialog = jtd.JT_Dialog(parent=self.master, title="Left Calibration Zero", msg="Have nothing on the scale:", type="okcancel") # this is custom dialog class created above
        if dialog.result:

            zero_reading = self.get_average_reading('s1_clean', 0, self.calibration_measurement_count)

            entered_weight = tk.simpledialog.askinteger("Left Weighted Calibration", "Enter weight in lbs:", initialvalue=30)
            if entered_weight is not None:
                #log.debug(f"Ok'ed weighted calibration: {entered_weight} lbs")
                weighted_reading = self.get_average_reading('s1_clean', entered_weight, self.calibration_measurement_count)
                self.l_zero = zero_reading
                self.l_mult = (weighted_reading - zero_reading)/entered_weight
                set_config_key("l_zero", self.l_zero)
                set_config_key("l_mult", self.l_mult)
                self.l_calibration = True

                log.debug(f"Left Calibration - entered_weight: {entered_weight}, zero: {zero_reading}, weighted: {weighted_reading}, multiplier: {self.l_mult}")
                self.message_line(f"Left sensor calibrated")

    def r_calibrate(self, json_key):
        log.debug(f"right calibrate:" )

        if self.check_serial_port() != True:
            return

        dialog = jtd.JT_Dialog(parent=self.master, title="Right Calibration Zero", msg="Have nothing on the scale:", type="okcancel") # this is custom dialog class created above
        if dialog.result:

            zero_reading = self.get_average_reading('s2_clean', 0, self.calibration_measurement_count)

            entered_weight = tk.simpledialog.askinteger("Right Weighted Calibration", "Enter weight in lbs:", initialvalue=8)
            if entered_weight is not None:
                #log.debug(f"Ok'ed weighted calibration: {entered_weight} lbs")
                weighted_reading = self.get_average_reading('s2_clean', entered_weight, self.calibration_measurement_count)
                self.r_zero = zero_reading
                self.r_mult = (weighted_reading - zero_reading)/entered_weight
                set_config_key("r_zero", self.r_zero)
                set_config_key("r_mult", self.r_mult)
                self.r_calibration = True

                log.debug(f"Right Calibration - entered_weight: {entered_weight}, zero: {zero_reading}, weighted: {weighted_reading}, multiplier: {self.r_mult}")
                self.message_line(f"Right sensor calibrated")

    def start_recording(self):

        # Need to have the athlete specified to run
        self.last_run_athlete = self.athlete_combobox.get()

        if len(self.last_run_athlete) < 1:
            jtd.JT_Dialog(parent=self.master, title="Start Run",
                                   msg="You Must specify an athlete to run",
                                   type="ok")
            return

        set_config_key("last_athlete", self.last_run_athlete)

        # check with user if they want to proceed without calibration?
        if self.protocol_type_selected == 'single' and self.l_calibration == False:
            dialog = jtd.JT_Dialog(parent=self.master, title="Uncalibrated", msg="Continue uncalibrated?",
                                   type="yesno")  # this is custom dialog class created above
            if dialog.result == False:
                return
        elif self.protocol_type_selected == 'double' and (self.l_calibration == False or self.r_calibration == False):
            dialog = jtd.JT_Dialog(parent=self.master, title="Uncalibrated", msg="Continue uncalibrated?",
                                   type="yesno")  # this is custom dialog class created above
            if dialog.result == False:
                return

        #if prior run has not been saved then request for them to save it
        if self.saved == False:

            dialog = jtd.JT_Dialog(parent=self.master, title="Save Last Run", msg="Save last run? NO will lose data",
                                       type="yesno")
            # save the data if requested
            if dialog.result == True:
                self.save_data_to_csv(True)
            else:
                pass

            # remove the graph from the canvas
            if self.subplot:
                self.subplot.clear()
                self.canvas_tab1.draw()

            jtd.JT_Dialog(parent=self.master, title="Start Run", msg="Press ok to start run",
                                       type="ok")

        log.f()

        #button enabled/disabled
        self.buttons_running()
        self.saved = False
        self.start_time = time.time()

        #start recording thread
        self.is_recording = True

        # if in testing mode them skip actually getting data and allow the stop button to read it from a file
        if test_data_file == None:
            self.jt_reader.start_reading()

        log.debug(f"Start recording, protocol: {self.protocol_name_selected}, athlete: {self.last_run_athlete}")

    def stop_cmj_recording(self):
        log.f()

        self.is_recording = False

        if test_data_file == None:
            self.num_measurements = self.jt_reader.stop_reading()
        else:
            log.debug(f"UTILIZING TEST FILE: {test_data_file}")
            my_df = read_test_file(test_data_file)
            self.jt_reader.set_test_data_list(my_df)
            self.num_measurements = len(my_df)

        log.debug(f"Stop_cmj_recording, num meas: {self.num_measurements}, protocol: {self.protocol_name_selected}")
        # get the df
        # def get_data_df(self, l_zero=0, l_mult=1, r_zero=0, r_mult=1, athlete='na', protocol='na'):
        leg = self.protocol_obj.get_leg_by_name(self.protocol_name_selected)
        self.results_df = self.jt_reader.get_data_df(self.l_zero, self.l_mult, self.r_zero, self.r_mult,
                    self.last_run_athlete, self.protocol_name_selected, self.protocol_type_selected, leg)

        #button enabled/disabled
        self.buttons_stopped()

        log.debug(f"results_df columns: {self.results_df.columns}")
        log.debug(f"results_df: {self.results_df.head(3)}")

        #display graphed results on first tab
        self.display_graph_results2( self.fig_tab1, self.canvas_tab1, "l_force_kg", "CMJ plot")

        #display the dataframe on the "results" tab
        self.display_results_df()

        end_time = time.time()
        elapsed = end_time - self.start_time

        elapsed_str = "{:.2f}".format(elapsed)

        self.message_line(f"Elapsed Time: {elapsed_str}, recorded {len(self.results_df)}")

    def buttons_running(self):
        #flip flop which buttons are enabled
        self.start_button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.NORMAL)
        self.l_calibrate_button.configure(state=tk.DISABLED)
        self.r_calibrate_button.configure(state=tk.DISABLED)
        self.save_button.configure(state=tk.DISABLED)

    def buttons_stopped(self):
        #flip flop which buttons are enabled
        self.start_button.configure(state=tk.NORMAL)
        self.stop_button.configure(state=tk.DISABLED)
        self.l_calibrate_button.configure(state=tk.NORMAL)
        self.r_calibrate_button.configure(state=tk.NORMAL)
        self.save_button.configure(state=tk.NORMAL)

    def message_line(self, msg):
        self.status_display.config(text=msg)

    #### Clock updating
    def update_button_fields(self):


        current_time = time.strftime('%H:%M:%S')
        self.clock_label.config(text=current_time)

        #only update weights if nobody else is reading in data, and the serial port is configured in jt_reader
        doit = True
        if self.is_recording == False and self.jt_reader.serial_port != None and doit == True:

  #          log.debug(f"updating clock and weights")
            left_weight = self.get_average_reading('s1_clean', 0, self.updated_weight_count)
            l_force = self.get_force_lbs(left_weight, self.l_zero, self.l_mult)
            self.l_calibration_display.config(text="{:.0f}".format(l_force))  #format force to just an integer

            #only do the measurements if both legs are being measured
            if self.protocol_type_selected != 'single':
                right_weight = self.get_average_reading('s2_clean', 0, self.updated_weight_count)
                r_force = self.get_force_lbs(right_weight, self.r_zero, self.r_mult)
                self.r_calibration_display.config(text="{:.0f}".format(r_force))

        self.clock_label.after(200, self.update_button_fields)

    def save_data_to_csv(self, lose_last_run=False):

        protocol_filename = self.protocol_obj.get_protocol_by_name((self.protocol_name_selected))
        self.last_run_athlete = self.athlete_combobox.get()
        set_config_key("last_athlete", self.last_run_athlete)

        if lose_last_run == True:
            dialog = jtd.JT_Dialog(parent=self.master, title="Save Last Run", msg="If you say NO it will be lost", type="yesno")
        else:
            dialog = jtd.JT_Dialog(parent=self.master, title="Save Last Run", msg="Do you want to save the last run?", type="yesno")

        if dialog.result:

            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{protocol_filename}_{self.last_run_athlete}_{now}.csv"

            if self.output_file_dir == None:

                #if not output directory defined make them go define one
                dialog = jtd.JT_Dialog(parent=self.master, title="Error", msg="No output directory defined, go to Settings tab and define one",
                                       type="ok")  # this is custom dialog class created above
                return(False)

            else:
                path_athlete = self.output_file_dir + "/" + self.last_run_athlete + "/"

                log.debug(f'path_athlete: {path_athlete}')

                # Check if the directory already exists
                if not os.path.exists(path_athlete):
                    # Create the directory if it doesn't exist
                    os.makedirs(path_athlete)
                    log.debug(f'Directory created: {path_athlete}')

                path_filename = path_athlete + filename
                self.results_df.to_csv(path_filename, index=True)

                log.debug(f"saved file: {path_filename}")

                self.saved = True
                self.save_button.configure(state=tk.DISABLED)
                self.message_line(f"saved file: {filename}")

        return (dialog.result)

    # button for exit app
    def quit_app(self):
        self.master.destroy()

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
            my_df = self.jt_reader.read_lines(num_measurements)
            self.is_recording = False

        else:
            if calibration_weight == 0:
                my_df = read_test_file('test_output_0_lbs.txt')
            else:
                my_df = read_test_file('test_output_30_lbs.txt')

            self.jt_reader.set_test_data_list( my_df)

        my_df = self.jt_reader.get_data_df()
        if len(my_df) > 0:
            avg_reading = my_df[json_field_name].mean()
        #log.f(f"average: {avg_reading}")
        else:
            avg_reading =-101

        return avg_reading


    def display_results_df(self):

        my_str = str(self.results_df)

        print(f" my crap {self.results_df}")

        # Panda - set the max rows to display
        pd.set_option("display.max_rows", 100)  # Set the desired number of rows

        # Insert the dataframe into the text widget
        self.text_widget_results.insert("end", my_str)

        # Clear the text widget
        self.text_widget_results.delete('1.0', tk.END)

        #add in new text strf
        self.text_widget_results.insert(tk.END, f"{my_str}\n")

        # Reset the view to the top
        self.text_widget_results.yview_moveto(0.0)

        # Panda - resets the # of rows to display for all pandas to the default
        pd.reset_option("display.max_rows")



    ####  TAB 3 ######################################################

    def get_athletes_list_filename(self):

        #default box for selecting a file
        file_path = filedialog.askopenfilename(initialdir=self.athletes_list_filename)

        if file_path:
            if file_path.endswith('.csv'):

                # pass in new filepath for athletes and see if it works.
                self.athletes = self.athletes_obj.get_athletes(file_path)

                if len(self.athletes) < 1:
                    dialog = jtd.JT_Dialog(parent=self.master, title="Error", msg="No athletes in the file",
                                           type="ok")  # this is custom dialog class created above
                else:
                    self.athlete_combobox['values'] = self.athletes
                    set_config_key( my_platform + "-athletes_list_filename_key", file_path)
                    self.athletes_list_filename = file_path

                    #update display with just the actual filename
                    file_name = os.path.basename(self.athletes_list_filename)
                    self.athletes_list_filename_display.config(text=file_name)
                    my_str = f"Athletes list filename: \n  {self.athletes_list_filename}"
                    log.info(my_str)
                    self.text_area.delete(1.0, tk.END)  # Clear the text area
                    self.text_area.insert(tk.END, my_str)
            else:
                dialog = jtd.JT_Dialog(parent=self.master, title="Error", msg="File must be a CSV file",
                                       type="ok")  # this is custom dialog class created above

    def set_output_file_dir(self):

        selected_dir = filedialog.askdirectory(initialdir=self.output_file_dir)
        if selected_dir:
            # Use the selected_directory path for saving files or any other purpose
            self.output_file_dir = selected_dir

            #store key in config file
            set_config_key( my_platform + "-output_file_dir", selected_dir)
            self.output_file_dir_display.config(text = selected_dir)
            my_str = f"Output file directory: \n  {selected_dir}"

            log.info(my_str)
            self.text_area.delete(1.0, tk.END)  # Clear the text area
            self.text_area.insert(tk.END, my_str)

        else:
            pass


    def reload_serial_ports(self):
        self.serial_ports_list = self.jt_reader.get_available_ports()
        self.serial_combobox['values'] = self.serial_ports_list
        my_str = f"Valid Serial Ports are: \n  {self.serial_ports_list}"
        self.text_area.delete(1.0, tk.END)  # Clear the text area
        self.text_area.insert(tk.END, my_str)

    def on_serial_combobox_select(self, event):

        self.serial_port_name = self.serial_combobox.get()
        log.debug(f'Combobox selection for serial port of: {self.serial_port_name}')

        #this should validate the serial port all the way to getting data from it
        self.check_serial_port()

    #function just to validate if data is coming in
    def read_serial_data(self):

        if self.is_recording == False:

            avg = self.get_average_reading('s1', 0, 20)

            line1 = f"Serial Port: {self.serial_port_name}, 's1' has average of {avg}\n"

            #if not able to read any lines
            my_str = ""
            if avg == None:

                my_str = f"Failed to read JSON Data"
            else:
                my_str = f"Successfully read JSON data: avg: {avg}, Raw Data is: {my_str}"
            log.debug(my_str)

            self.text_area.delete(1.0, tk.END)  # Clear the text area
            self.text_area.insert(tk.END, my_str)  # Insert the data into the text area
            self.serial_busy = False


    ####  TAB 4 ######################################################

    # self.fig_tab4 = plt.Figure(figsize=(5, 4), dpi=100)
    # self.canvas = FigureCanvasTkAgg(self.fig_tab4, master=self.tab_config)   #sets up which tab it is on
    # self.canvas.draw()
    # self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    # Replace these values with the correct serial port and baud rate for your sensor

    log.set_logging_level("DEBUG")

    # create a tkinter root window
    root = tk.Tk()
#    root.geometry("700x650")

    # Create a style object
    root.style = ttk.Style()

    # Set the theme
    set_theme(root)

    recorder = CMJ_UI(root)

    # update clock initially which also starts timer for it
    recorder.update_button_fields()

    recorder.mainloop()


