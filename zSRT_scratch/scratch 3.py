import sys
from PyQt6.QtWidgets import (
    QMainWindow, QApplication,
    QLabel, QToolBar, QStatusBar
)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt

app = QApplication(sys.argv)

window = QMainWindow()
window.show()

menu_bar = window.menuBar()
file_menu = menu_bar.addMenu("File")
file_menu.addAction("Open")
file_menu.addAction("Open2")
file_menu.addAction("Open3")
file_menu.addAction("Open4")

print(menu_bar, file_menu)

app.exec()