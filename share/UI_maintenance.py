import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QDialog
from PyQt6.QtWidgets import QPushButton


try:
    from . import jt_serial as jts
    from . import jt_config as jtc
    from . import jt_util as util
    from . import jt_dialog as jtd
    from . import jt_trial_manager as jttm

except:
    import jt_serial as jts
    import jt_config as jtc
    import jt_util as util
    import jt_dialog as jtd
    import jt_trial_manager as jttm

log = util.jt_logging()

#class JT_MaintenanceWindow(QMainWindow):

class JT_MaintenanceWindow(QDialog):
    def __init__(self, jt_config_obj, jt_serial_reader):
        super().__init__()

        layout = QVBoxLayout(self)

        self.config_obj = jt_config_obj
        self.reader_obj = jt_serial_reader

        self.serial_port_name = self.config_obj.get_config("last_port")

        self.text_widget = None # this is done here so that with serial combo box the thing doesn't error out when updating status bar

        self.setWindowTitle("Preferences")
        self.setGeometry(600, 200, 400, 400)
        self.setFixedSize(400, 400)

        # button to rebuild indexes
        self.rebuild_indexes_button = QPushButton("rebuild Indexes", clicked=self.rebuild_indexes)
        layout.addWidget(self.rebuild_indexes_button)

    def rebuild_indexes(self):

        value = jtd.JT_Dialog(parent=self, title="Index Maintenance",
                              msg=f"Are you sure you rebuild the Indexes?",
                              type="yesno")
        if value == True:

            trial_mgr_obj = jttm.JT_JsonTrialManager(self.config_obj)

            trial_mgr_obj.reprocess_all_files(self)
    def resizeEvent(self, event):
        # Ignore resize event
        pass
    def closeEvent(self, event):
        pass

if __name__ == '__main__':

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.reader_obj = jts.SerialDataReader()
#            self.config_obj = jtc.JT_Config('taylor performance', None, "testing_config.json")
            self.config_obj = jtc.JT_Config('taylor performance', None)
            val = self.config_obj.validate_install()
            print(f'config_obj.validate return value: {val}')

            self.setWindowTitle("Main Window")

            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
#            central_widget.setLayout(layout)


            maintenace_button = QPushButton("Open Maintenance UI")
            maintenace_button.clicked.connect(self.open_preferences)
            layout.addWidget(maintenace_button)

        def open_preferences(self):
            self.maintenance_window = JT_MaintenanceWindow(self.config_obj, self.reader_obj)
            self.maintenance_window.setModal(True)
            self.maintenance_window.show()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    result = app.exec()
    sys.exit(result)

