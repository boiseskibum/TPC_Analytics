import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QComboBox, QMessageBox
from PyQt6.QtCore import Qt, QTimer

class CustomDialog(QMessageBox):
    def __init__(self, parent, title, text, dialog_type):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setText(text)
        self.dialog_type = dialog_type

        if dialog_type == "ok":
            self.setStandardButtons(QMessageBox.StandardButton.Ok)
        elif dialog_type == "okcancel":
            self.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        elif dialog_type == "yesno":
            self.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        elif dialog_type == "yesnocancel":
            self.dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
        elif dialog_type == "retrycancel":
            self.dialog.setStandardButtons(QMessageBox.StandardButton.Retry | QMessageBox.StandardButton.Cancel)

        # Use a QTimer to delay the execution of the dialog
        timer = QTimer(self)
        timer.timeout.connect(self.showDialog)
        timer.start(100)  # The timer triggers after 100 milliseconds

    def showDialog(self):
        # Stop the timer to prevent repeated execution
        self.sender().stop()

        # Show the dialog modally
        ret = self.exec()

        # return either True for yes/ok/retry or False for no/cancel
        value = 0
        if self.dialog_type == "yesno" or self.dialog_type == "yesnocancel":
            if ret == QMessageBox.StandardButton.Yes:
                value = 1
            elif ret == QMessageBox.StandardButton.No:
                value = 0
            elif ret == QMessageBox.StandardButton.Cancel:
                value = None
        elif self.dialog_type == "retrycancel":
            if ret == QMessageBox.StandardButton.Retry:
                value = 1
            elif ret == QMessageBox.StandardButton.Cancel:
                value = 0
        elif self.dialog_type == "okcancel":
            if ret == QMessageBox.StandardButton.Ok:
                value = 1
            elif ret == QMessageBox.StandardButton.Cancel:
                value = 0
        else:
            value = 1   # this is for ok dialog where regardless of value it returns 1

        print(f"Dialog return value is: {value}")

        return value

class CMJ_UI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.application_name = "my combo test app"
        self.setWindowTitle(self.application_name)
        self.athletes = ['huey', 'duey', 'louie']

        #### Main Screen ######################################################
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.grid_layout = QGridLayout(central_widget)

        self.athlete_combobox = QComboBox()
        print(f'list of athletes: {self.athletes}')
        self.athlete_combobox.addItems(self.athletes)
        self.grid_layout.addWidget(self.athlete_combobox, 0, 1)

    def test_dialog(self):
        dialog_title = "Custom Dialog"
        dialog_text = "This is a custom dialog."
        dialog_type = "okcancel"  # Change this to "ok" or "yesno" as needed
        custom_dialog = CustomDialog(self, dialog_title, dialog_text, dialog_type)
        return custom_dialog.showDialog()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CMJ_UI()
    window.show()
    val = window.test_dialog()
    print()

    result = app.exec()
    sys.exit(result)
