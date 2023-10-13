import sys
from PyQt6.QtWidgets import QApplication, QFileDialog, QMainWindow, QPushButton, QVBoxLayout, QWidget

class DirectorySelectionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        selectDirButton = QPushButton('Select Directory', self)
        selectDirButton.clicked.connect(self.showDialog)

        layout.addWidget(selectDirButton)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.setWindowTitle('Directory Selection App')
        self.setGeometry(100, 100, 400, 200)

    def showDialog(self):
        # Set the default directory
        default_directory = "/path/to/your/default/directory"

        directory = QFileDialog.getExistingDirectory(self, 'Select Directory', default_directory)

        if directory:
            print('Selected Directory:', directory)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DirectorySelectionApp()
    window.show()
    sys.exit(app.exec())
