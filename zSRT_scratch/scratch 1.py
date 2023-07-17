import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QMenu
from PyQt6.QtGui import QAction

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        # Create menu bar
        self.menuBar().clear()
        QApplication.processEvents()
        menu_bar = self.menuBar()

        # Create file menu and add actions
        file_menu = QMenu("File", self)
        open_action = QAction("Open", self)
        close_action = QAction("Close", self)
        settings_action = QAction("Settings", self)
        file_menu.addAction(open_action)
        file_menu.addAction(close_action)
        file_menu.addAction(settings_action)

        # Create edit menu and add actions
        edit_menu = QMenu("Edit", self)
        copy_action = QAction("Copy", self)
        paste_action = QAction("Paste", self)
        edit_menu.addAction(copy_action)
        edit_menu.addAction(paste_action)

        # Add menus to menu bar
        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(edit_menu)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())