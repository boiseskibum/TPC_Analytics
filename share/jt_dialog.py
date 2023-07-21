# jt_dialog.py
# Purpose: to provide non-blocking dialogs to the application so that threads can continue to run on the side and
# the main screen can be updated

import sys
from PyQt6.QtWidgets import (QApplication, QLabel, QWidget, QPushButton, QMessageBox,
                             QVBoxLayout, QDialog, QDialogButtonBox, QInputDialog)

#used just for the testing routine at the bottom of file
import tkinter as tk

def JT_Dialog(parent, title="Default Title", msg="Default message", type="okcancel"):

    dialog = QMessageBox(parent)
    dialog.setWindowTitle(title)
    dialog.setText(msg)

    if type == "yesno":
        dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    elif type == "retrycancel":
        dialog.setStandardButtons(QMessageBox.StandardButton.Retry | QMessageBox.StandardButton.Cancel)
    elif type == "okcancel":
        dialog.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
    else:
        dialog.setStandardButtons(QMessageBox.StandardButton.Ok)

    ret = dialog.exec()

    # return either True for yes/ok/retry or False for no/cancel
    value =0
    if type == "yesno":
        if ret == QMessageBox.StandardButton.Yes:
            value = 1
        elif ret == QMessageBox.StandardButton.No:
            value = 0
    elif type == "retrycancel":
        if ret == QMessageBox.StandardButton.Retry:
            value = 1
        elif ret == QMessageBox.StandardButton.Cancel:
            value = 0
    elif type == "okcancel":
        if ret == QMessageBox.StandardButton.Ok:
            value = 1
        elif ret == QMessageBox.StandardButton.Cancel:
            value = 0
    else:
        value = 1

    return(value)

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
            self.button1.clicked.connect(self.show_dialog)
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


            self.setLayout(layout)
            self.show()

        def show_dialog(self):
            result = JT_Dialog(self, title="SRT title for okcancel", msg="srt message really long text to see if this works in a bad example", type="okcancel")
            print(result)

        def show_dialog2(self):
            result = JT_Dialog(self, title="SRT Title for y/n that", msg="srt message text", type="yesno")
            print(result)

        def show_dialog3(self):
            result = JT_Dialog(self, title="SRT Title for OK only", msg="srt message text", type="ok")
            print(result)

        def show_dialog4(self):
            result = JT_Dialog(self, title="SRT Title for multi-line OK only",
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
