# jt_dialog.py
# Purpose: to provide non-blocking dialogs to the application so that threads can continue to run on the side and
# the main screen can be updated

import sys
import time

from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QMessageBox, QComboBox
from PyQt6.QtWidgets import QVBoxLayout, QDialog, QDialogButtonBox, QInputDialog
from PyQt6.QtCore import QTimer

#used just for the testing routine at the bottom of file
import tkinter as tk


class JT_Dialog2(QMessageBox):
    def __init__(self, parent, title="Default Title", msg="Default message", type="okcancel"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setText(msg)
        self.dialog_type = type

        if type == "ok":
            self.setStandardButtons(QMessageBox.StandardButton.Ok)
        elif type == "okcancel":
            self.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        elif type == "yesno":
            self.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        elif type == "yesnocancel":
            self.dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
        elif type == "retrycancel":
            self.dialog.setStandardButtons(QMessageBox.StandardButton.Retry | QMessageBox.StandardButton.Cancel)

        # Use a QTimer to delay the execution of the dialog
        timer = QTimer(self)
        timer.timeout.connect(self.showDialog)
        timer.start(100)  # The timer triggers after 100 milliseconds

    def showDialog(self):
        # Stop the timer to prevent repeated execution
        self.sender().stop()
        print('about to call self.exec')
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
            print("made it to ok cancel")
            if ret == QMessageBox.StandardButton.Ok:
                value = 1
            elif ret == QMessageBox.StandardButton.Cancel:
                value = 0
        else:
            value = 1   # this is for ok dialog where regardless of value it returns 1

        self.ret = ret
        self.value = value
        print(f"Dialog return value is: {self.value}, message_str: {self.message_str()}")

        return value

    def message_str(self):

        if self.ret == QMessageBox.StandardButton.Yes:
            temp = f"return Yes, value:{self.value}"
            print(f"         Inside message_str:  {temp}")
        if self.ret == QMessageBox.StandardButton.No:
            temp = f"return No, value:{self.value}"
            print(f"         Inside message_str:  {temp}")
        if self.ret == QMessageBox.StandardButton.Cancel:
            temp = f"return Cancel, value:{self.value}"
            print(f"         Inside message_str:  {temp}")
        if self.ret == QMessageBox.StandardButton.Retry:
            temp = f"return Retry, value:{self.value}"
            print(f"         Inside message_str:  {temp}")
        if self.ret == QMessageBox.StandardButton.Ok:
            temp = f"return Ok, value:{self.value}"
            print(f"         Inside message_str:  {temp}")

        return (temp)

def JT_Dialog_Integer(parent, title="Default Title", msg="Default message", value = 0):
    number, ok = QInputDialog.getInt(parent, title, msg, value=value)
    if ok == False:
        number = None
    return number

if __name__ == "__main__":
    class MainWindow(QWidget):
        def __init__(self):
            super().__init__()

            self.setWindowTitle("Main Window")

            layout = QVBoxLayout()

            self.button1 = QPushButton("Show Dialog okcancel")
            self.button1.clicked.connect(self.show_dialog1)
            layout.addWidget(self.button1)

            self.button2 = QPushButton("Show Dialog yes/no")
            self.button2.clicked.connect(self.show_dialog2)
            layout.addWidget(self.button2)

            self.button3 = QPushButton("Show Dialog ok")
            self.button3.clicked.connect(self.show_dialog3)
            layout.addWidget(self.button3)

            self.button4 = QPushButton("Show Dialog: long text")
            self.button4.clicked.connect(self.show_dialog4)
            layout.addWidget(self.button4)

            self.button4 = QPushButton("Show Dialog Integer")
            self.button4.clicked.connect(self.show_dialog5)
            layout.addWidget(self.button4)

            self.athletes = ['huey', 'duey', 'louie']
            self.athlete_combobox = QComboBox()
            print(f'list of athletes: {self.athletes}')
            self.athlete_combobox.addItems(self.athletes)
#            self.grid_layout.addWidget(self.athlete_combobox, 0, 1)

            self.setLayout(layout)
            self.show()

        def show_dialog1(self):
            result = JT_Dialog2(self, title="SRT title for okcancel", msg="srt message really long text to see if this works in a bad example", type="okcancel")
            print(f"type: {type(result)}")
            time.sleep(.25)
            print(f"after .25 sleep    {result.message_str()}")

        def show_dialog2(self):
            result = JT_Dialog2(self, title="SRT Title for y/n that", msg="srt message text", type="yesno")
            print(result)

        def show_dialog3(self):
            result = JT_Dialog2(self, title="SRT Title for OK only", msg="srt message text", type="ok")
            print(result)

        def show_dialog4(self):
            result = JT_Dialog2(self, title="SRT Title for multi-line OK only",
                   msg="srt message text\n 2nd line \n 3rd line this is a freaking reall long and crazy wide line that is ", type="ok")
            print(result)

        def show_dialog5(self):
            result = JT_Dialog_Integer(self, title="Title of Integer", msg="Please enter an integer", value=39)
            print(result)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
