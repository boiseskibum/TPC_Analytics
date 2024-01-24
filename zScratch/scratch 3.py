import sys, os
from PyQt6.QtWidgets import QDialog, QMessageBox, QPushButton, QApplication, QWidget, QVBoxLayout
from PyQt6.QtGui import QIcon

class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()

        button = QPushButton("dialog box", self)
        button.clicked.connect(self.showDialog)
        layout.addWidget(button)

        button1 = QPushButton("dialog1 box", self)
        button1.clicked.connect(self.showDialog1)
        layout.addWidget(button1)

        self.setLayout(layout)
    def showDialog(self):
        print('dialog clicked')
        dialog = QMessageBox(self)
        dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        dialog.setIcon(QMessageBox.Icon.Question)
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.setText("srt dialog that has crappy icoon")
        dialog.exec()

    def showDialog1(self):
        print('dialog clicked')
        dialog = QDialog()
#        dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
#        dialog.setIcon(QMessageBox.Icon.Question)
        dialog.exec()

##########################################
if __name__ == '__main__':

    #Set a custom icon.   From the main program it will fall into the first example.
    fp = 'resources/img/jt.ico'
    icon = None
    if os.path.exists(fp):
        icon = QIcon(fp)  # Replace with your icon file path
    else:
        # Get the current working directory
        current_path = os.getcwd()

        # Go back one directory
        parent_path = os.path.dirname(current_path)

        # Construct the new path
        new_path = os.path.join(parent_path, fp)
        print(f'new_path:  {new_path}')

        # Check if the file exists
        if os.path.exists(new_path):
            icon = QIcon(fp)  # Replace with your icon file path
            print ('found icon path!')

    app = QApplication(sys.argv)

    app.setWindowIcon(icon)  # Replace with the path to your icon

    window = MainWindow(app)
    window.show()

    my_ret = app.exec()
    sys.exit(my_ret)
