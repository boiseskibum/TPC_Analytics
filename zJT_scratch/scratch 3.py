import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QMenuBar
from PyQt6.QtGui import QAction

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        menubar = self.menuBar()

        # Creating a File menu
        fileMenu = menubar.addMenu('File')

        # Creating actions for the File menu
        dirMaintAction = QAction('Directories and Maintenance', self)
        preferenceAction = QAction('Settings', self)   # this shows up as preferences in the MACOS
        aboutAction = QAction('About', self)

        # Adding actions to the File menu
        fileMenu.addAction(dirMaintAction)
        fileMenu.addAction(preferenceAction)
        fileMenu.addAction(aboutAction)

        # Connect the actions to their respective functions
        dirMaintAction.triggered.connect(self.showDirMaint)
        preferenceAction.triggered.connect(self.showPreferences)
        aboutAction.triggered.connect(self.showAbout)

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Menu Example')
        self.show()

    def showPreferences(self):
        print("Preferences clicked")

    def showDirMaint(self):
        print("DirMaint clicked")

    def showAbout(self):
        print("About clicked")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec())
