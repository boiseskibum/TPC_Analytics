# jt_dialog.py
# Purpose: to provide non-blocking dialogs to the application so that threads can continue to run on the side and
# the main screen can be updated

import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QMessageBox,
                             QVBoxLayout,  QInputDialog, QDialog, QTextEdit)

#used just for the testing routine at the bottom of file
import tkinter as tk

def JT_Dialog(parent, title="Default Title", msg="Default message", type="okcancel"):

    if parent == None:
        dialog = QMessageBox()
    else:
        dialog = QMessageBox(parent)

    dialog.setWindowTitle(title)
    dialog.setText(msg)

    if type == "yesno":
        dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    elif type == "yesnocancel":
        dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
    elif type == "retrycancel":
        dialog.setStandardButtons(QMessageBox.StandardButton.Retry | QMessageBox.StandardButton.Cancel)
    elif type == "okcancel":
        dialog.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
    else:
        dialog.setStandardButtons(QMessageBox.StandardButton.Ok)

    ret = dialog.exec()

    # return either True for yes/ok/retry or False for no/cancel
    value = 0
    if type == "yesno" or type == "yesnocancel":
        if ret == QMessageBox.StandardButton.Yes:
            value = 1
        elif ret == QMessageBox.StandardButton.No:
            value = 0
        elif ret == QMessageBox.StandardButton.Cancel:
            value = None
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

    return value

def JT_Dialog_Integer(parent, title="Default Title", msg="Default message", value = 0):
    number, ok = QInputDialog.getInt(parent, title, msg, value=value)
    if ok == False:
        number = None
    return number

__copyright__ = """This software is designed to provide data from sensors (load cells), store the data,
    and provide the data in a usable format for Strength and Conditioning analytics
    Copyright (C) 2023  Jake Taylor and Steve Taylor

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
class JT_DialogLongText(QDialog):
    def __init__(self, parent=None, title='default Title', msg='def message'):
        super(JT_DialogLongText, self).__init__(parent)

        self.setWindowTitle(title)

        self.layout = QVBoxLayout(self)

        # Add a text edit for the long text
        self.textEdit = QTextEdit(self)
        self.textEdit.setReadOnly(True)
        self.textEdit.setText(msg)
        self.layout.addWidget(self.textEdit)

        # Add a close button
        self.closeButton = QPushButton("Close", self)
        self.closeButton.clicked.connect(self.close)
        self.layout.addWidget(self.closeButton)

        self.resize(600, 400)  # You can adjust the size as needed

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

            self.button5 = QPushButton("Show Dialog Integer")
            self.button5.clicked.connect(self.show_dialog5)
            layout.addWidget(self.button5)

            self.button6 = QPushButton("Show big text")
            self.button6.clicked.connect(self.show_dialog6)
            layout.addWidget(self.button6)


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

        def show_dialog6(self):

            bigB = JT_DialogLongText(self, title="Title of BIG text", msg=__copyright__)
            bigB.exec()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
