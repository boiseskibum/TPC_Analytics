import sys, time
from PyQt6.QtWidgets import QDialog, QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtWidgets import QPushButton, QComboBox, QTextEdit, QGroupBox, QSizePolicy, QLineEdit, QCheckBox
from PyQt6.QtCore import Qt  # Import the Qt module

try:
    from . import jt_serial as jts
    from . import jt_config as jtc
    from . import jt_util as util
    from . import jt_video as jtv
except:
    import jt_serial as jts
    import jt_config as jtc
    import jt_util as util
    import jt_video as jtv

log = util.jt_logging()

camera_sleep_time = .2   #time for cameras to shut down so that they can be restarted.

def convert_to_int(value):
    try:
        integer_value = int(value)
        return integer_value
    except ValueError:
        return -1
class JT_PreferencesWindow(QDialog):
    def __init__(self, jt_config_obj, jt_serial_reader):
        super().__init__()

        layout = QGridLayout(self)

        self.config_obj = jt_config_obj
        self.reader_obj = jt_serial_reader

        self.serial_port_name = self.config_obj.get_config("last_port")

        self.text_widget = None # this is done here so that with serial combo box the thing doesn't error out when updating status bar

        self.setWindowTitle("Preferences")
        self.setGeometry(600, 200, 500, 700)
        self.setFixedSize(500, 700)

        self.num_cameras = 1
        self.video1 = None
        self.camera1 = -1
        self.ignore_combox_change = False

        # Row 1: Refresh Serial Ports button and ComboBox to select the serial port
        trow = 0
        self.refresh_serial_button = QPushButton("Refresh Serial Ports", clicked=self.reload_serial_ports)
        layout.addWidget(self.refresh_serial_button, trow, 0)

        self.serial_port_combobox = QComboBox()
        self.serial_port_combobox.currentTextChanged.connect(self.serial_port_combobox_changed)
        layout.addWidget(self.serial_port_combobox, trow, 1)

        # Row 2: ComboBox to select the baud rate
        trow += 1
        self.baud_rate_combobox = QComboBox()
        self.baud_rate_combobox.currentTextChanged.connect(self.baud_rate_combobox_changed)
        self.baud_rate_combobox.addItems(["115200"])
        self.baud_rate_combobox.setCurrentIndex(0)
        layout.addWidget(self.baud_rate_combobox, trow, 1)

        # Row 3: Widget with room for 3 rows of text (QTextEdit)
        trow += 1
        self.text_widget = QTextEdit()
        layout.addWidget(self.text_widget, trow, 0, 2, 2)

        trow += 2
        label1 = QLabel("Camera Configuration")
        label1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label1, trow, 0)

        # Row 4: Refresh Camera List button and ComboBox to select the camera
        trow += 1

        camera_count, cameras = jtv.external_camera_count()
        camera_index = self.config_obj.get_config('camera1')
        log.info(f'External Camera count: {camera_count}, Models: {cameras}, Camera_index = {camera_index}')

        list_of_cameras = ["not in use"]
        if camera_count > 0:
            list_of_cameras.append('0')

        #Set up camera #1
        self.camera1_combobox = QComboBox()
        self.camera1_combobox.currentTextChanged.connect(self.camera1_combox_changed)
        self.camera1_combobox.addItems(list_of_cameras)
        layout.addWidget(self.camera1_combobox, trow, 0)

        ###### VIDEO ######
        # Row 5: Preview widget with video control (QGroupBox with QLabel)

        trow += 1
        preview_group_box = QGroupBox()
        preview_layout = QHBoxLayout()
        video_label1 = QLabel("Preview Video 1")
        video_label1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        video_label1 = QLabel("Preview Video 1")
        video_label1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(video_label1)

        preview_group_box.setLayout(preview_layout)
        layout.addWidget(preview_group_box, trow, 0, 1, 2)
        # Set the vertical size policy of the preview_group_box to Expanding (it will expand vertically)
        preview_group_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.video1 = jtv.JT_Video(self.config_obj, video_label1)

        cam1_index = self.config_obj.get_config("camera1")

        if cam1_index is not None and cam1_index > -1:
            self.camera1_combobox.setCurrentIndex(cam1_index + 1)
#            print(f'Setting combobox index to: {cam1_index+1}')
        else:
            self.video1.camera_offline()

        ##### Branding #####
        trow += 1

        self.brand_label = QLabel("Custom Branding:")
        self.brand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.brand_label, trow, 0)

        self.brand_text_input = QLineEdit()
        self.brand_text_input.setMaxLength(20)
        layout.addWidget(self.brand_text_input, trow, 1)
        self.brand_text_input.editingFinished.connect(self.on_branding_edit_finished)

        txt = self.config_obj.get_config("branding")
        if txt is not None:
            self.brand_text_input.setText(txt)

        ##### Countdown *****
        trow += 1
        #get current countdown timer.   The funky code sets the default to True if it has not been saved previously
        self.countdown = True
        cd = self.config_obj.get_config("countdown")
        if cd is False:
            self.countdown = False

        self.countdown_checkbox = QCheckBox('Countdown timer on')
        self.countdown_checkbox.setChecked(self.countdown)
        self.countdown_checkbox.stateChanged.connect(self.on_countdown_checkbox_changed)
        layout.addWidget(self.countdown_checkbox, trow, 1)

        ###### Close  ######
        trow += 1
        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button, trow, 1)


    def reload_serial_ports(self):

        # get list of ports
        self.serial_ports_list = self.reader_obj.get_available_ports()
        self.serial_port_combobox.clear()
        self.serial_port_combobox.addItems(self.serial_ports_list)

        # if only one port default to that
        if len(self.serial_ports_list) == 1:
            result = self.reader_obj.configure_serial_port(self.serial_ports_list[0])

            if self.connection_validation():
                self.config_obj.set_config("last_port", self.serial_port_name)
        else:
            my_str = f"Valid Serial Ports are: {self.serial_ports_list}\n, need to select your port "
            self.text_widget.setPlainText(my_str)

    def serial_port_combobox_changed(self, value):
        self.serial_port_name = value

        if self.reader_obj == None:
            return

        self.reader_obj.configure_serial_port(self.serial_port_name)

        # test out serial port
        if self.connection_validation():
            self.config_obj.set_config("last_port", self.serial_port_name)

    def baud_rate_combobox_changed(self, value):
        self.baud_rate = value
        if self.reader_obj == None:
            return

        self.reader_obj.configure_serial_port(self.serial_port_name, self.baud_rate)

        if self.connection_validation():
            self.config_obj.set_config("last_port", self.serial_port_name)

    def connection_validation(self):
        # test out serial port
        result, line = self.reader_obj.serial_port_validate_data('s1')
        if result == True:
            my_str = f"Successful connection to port: {self.serial_port_name} baud_rate: {self.baud_rate}, result: {result}, line: was{line} "
        else:
            my_str = f"FAILED connection to port: {self.serial_port_name} baud_rate: {self.baud_rate}, result: {result}, line: was{line} "

        log.debug(my_str)
        if self.text_widget != None:
            self.text_widget.setPlainText(my_str)

        return result


    def camera1_combox_changed(self, value):

        if self.video1 == None or self.ignore_combox_change == True:
            return
        self.video1.stop()
        time.sleep(camera_sleep_time)

        log.debug(f"combox_changed for video1 to: {value}")
        value = convert_to_int(value)
        if value > -1:      #this skips if -1 coming back from convert_to_int.   IE if the user selects
                # 'not in use' it won't convert and will come back as a -1

            self.video1.camera_index = value

            self.start_video1()

        else:   #handle case of not in use
            self.camera1_combobox.setCurrentIndex(0)
            self.video1.camera_offline()

        self.save_video_config()

    def start_video1(self):
        log.debug(f"checking to start video1: {self.video1.camera_index}")
        video_start_time = time.time()

        selected_item = self.camera1_combobox.currentText()
        value = convert_to_int(selected_item)
        if self.video1 and value > -1:
            self.video1.start()
            log.debug(f"starting video1.   value: {value}")

            video_end_time = time.time()
            delta_time = video_end_time - video_start_time
            log.debug(f'Time for camera to start up: {delta_time:.3f}')

    def save_video_config(self):

        cam1_index = convert_to_int(self.camera1_combobox.currentText())

        self.config_obj.set_config("camera1", cam1_index)

    def on_branding_edit_finished(self):
        txt = self.brand_text_input.text()
        log.info(f'new branding: {txt}')
        self.config_obj.set_config("branding", txt)

    def on_countdown_checkbox_changed(self, value):
#        print(f'###### countdown changed was called: {value}, before change countdown was: {self.countdown} ')
        if value != 0:
            self.countdown = True
            self.config_obj.set_config('countdown', True)
        else:
            self.countdown = False
            self.config_obj.set_config('countdown', False)

    def resizeEvent(self, event):
        # Ignore resize event
        pass
    def closeEvent(self, event):
        self.video1.stop()
        time.sleep(camera_sleep_time)


if __name__ == '__main__':

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.reader_obj = jts.SerialDataReader()
            self.config_obj = jtc.JT_Config('taylor performance', None, "testing_config.json")
            val = self.config_obj.validate_install()
            print('convig_obj.validate return value: {val}')

            self.setWindowTitle("Main Window")

            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
#            central_widget.setLayout(layout)


            preferences_button = QPushButton("Open Preferences")
            preferences_button.clicked.connect(self.open_preferences)
            layout.addWidget(preferences_button)

        def open_preferences(self):
            self.preferences_window = JT_PreferencesWindow(self.config_obj, self.reader_obj)
            self.preferences_window.show()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    result = app.exec()
    sys.exit(result)

