import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QComboBox, QMessageBox
from PyQt6.QtCore import Qt, QTimer

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

        test_dialog = False

        # if test_dialog == True:
        #     self.timer = None
        #     self.showMessageBox()
        # # Use a QTimer to delay the execution of the message box
        # else:
        #     self.timer = QTimer(self)
        #     self.timer.timeout.connect(self.showMessageBox)
        #     self.timer.start(10)  # The timer triggers immediately with a timeout value of 0 milliseconds

    def showMessageBox(self):

        if self.timer:
            self.sender().stop()

        # dialog that doesn't break the whole thing
        dialog = QMessageBox(self)
        dialog.setWindowTitle("my title")
        dialog.setText("my message")
        dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        ret = dialog.exec()
        print(f"message return is: {ret}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CMJ_UI()
    window.show()
    val = window.showMessageBox()
    print(f"message box value: {val}")
    result = app.exec()
    sys.exit(result)


