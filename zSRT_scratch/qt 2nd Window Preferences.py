import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QLabel
from PyQt6.QtWidgets import    QPushButton, QComboBox, QTextEdit, QGroupBox, QSizePolicy
from PyQt6.QtCore import Qt  # Import the Qt module

sys.path.append('../share')
import jt_serial as jts
import jt_config as jtc
import jt_util as util

log = util.jt_logging()

class PreferencesWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.jt_reader_obj = None
        self.jt_config_obj = None

        self.setWindowTitle("Preferences")
        self.setGeometry(100, 100, 500, 600)

        layout = QGridLayout()
        self.setLayout(layout)

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

        # Row 4: Refresh Camera List button and ComboBox to select the camera
        trow += 2

        list_of_cameras = ["do not use", "0", "1", "2"]

        #Set up camera #1
        self.camera1_combobox = QComboBox()
        self.camera1_combobox.currentTextChanged.connect(self.camera1_combox_changed)
        self.camera1_combobox.addItems(list_of_cameras)
        camera1 = self.jt_config_obj.get_config("camera1")
        index = 0  # this is the default index
        try:
            list_of_cameras.index(camera1)
        except ValueError:
            pass
        self.camera1_combobox.setCurrentIndex(index)
        layout.addWidget(self.camera1_combobox, trow, 0)

        #Set up camera #1
        self.camera2_combobox = QComboBox()
        self.camera2_combobox.currentTextChanged.connect(self.camera2_combox_changed)
        self.camera2_combobox.addItems(list_of_cameras)
        camera1 = self.jt_config_obj.get_config("camera1")
        index = 0  # this is the default index
        try:
            list_of_cameras.index(camera1)
        except ValueError:
            pass
        self.camera2_combobox.setCurrentIndex(index)
        layout.addWidget(self.camera2_combobox, trow, 1)

        # Row 5: Preview widget with video control (QGroupBox with QLabel)
        trow += 1
        preview_group_box = QGroupBox("Preview")
        preview_layout = QVBoxLayout()

        preview_label = QLabel("Preview Video Here")
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(preview_label)

        preview_group_box.setLayout(preview_layout)
        layout.addWidget(preview_group_box, trow, 0, 1, 2)
        # Set the vertical size policy of the preview_group_box to Expanding (it will expand vertically)
        preview_group_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_jt_objects(self, jt_reader_obj, jt_config):
        self.jt_reader_obj = jt_reader_obj
        self.jt_config_obj = jt_config

    def reload_serial_ports(self):

        # get list of ports
        self.serial_ports_list = self.jt_reader_obj.get_available_ports()
        self.serial_port_combobox.clear()
        self.serial_port_combobox.addItems(self.serial_ports_list)

        # if only one port default to that
        if len(self.serial_ports_list) == 1:
            result = self.jt_reader_obj.configure_serial_port(self.serial_ports_list[0])

            if self.connection_validation():
                self.jt_config_obj.set_config("last_port", self.serial_port_name)
        else:
            my_str = f"Valid Serial Ports are: {self.serial_ports_list}\n, need to select your port "
            self.text_widget.setPlainText(my_str)

    def serial_port_combobox_changed(self, value):
        self.serial_port_name = value

        if self.jt_reader_obj == None:
            return

        self.jt_reader_obj.configure_serial_port(self.serial_port_name)

        # test out serial port
        if self.connection_validation():
            self.jt_config_obj.set_config("last_port", self.serial_port_name)

    def baud_rate_combobox_changed(self, value):
        self.baud_rate = value
        if self.jt_reader_obj == None:
            return

        self.jt_reader_obj.config.configure_serial_port(self.serial_port_name, self.baud_rate)

        if self.connection_validation():
            self.jt_config_obj.set_config("last_port", self.serial_port_name)

    def connection_validation(self):
        # test out serial port
        result, line = self.jt_reader_obj.serial_port_validate_data('s1')
        if result == True:
            my_str = f"Successful connection to port: {self.serial_port_name} baud_rate: {self.baud_rate}\n, result: {result}, line: was{line} "
        else:
            my_str = f"FAILED connection to port: {self.serial_port_name} baud_rate: {self.baud_rate} \n, result: {result}, line: was{line} "

        log.debug(my_str)
        self.text_widget.setPlainText(my_str)
        return result

    def camera1_combox_changed(self, value):
        self.camera1 = value

    def camera2_combox_changed(self, value):
        pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.jt_reader_obj = jts.SerialDataReader()
        self.jt_config_obj = jtc.JT_config("testing_config.json")


        self.setWindowTitle("Main Window")

        layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        preferences_button = QPushButton("Open Preferences")
        preferences_button.clicked.connect(self.open_preferences)
        layout.addWidget(preferences_button)

    def open_preferences(self):
        self.preferences_window = PreferencesWindow()
        self.preferences_window.set_jt_objects(self.jt_reader_obj, self.jt_config_obj)
        self.preferences_window.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
    sys.exit()


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = PreferencesWindow()
#     window.show()
#     sys.exit(app.exec())
