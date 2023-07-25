import sys
from PyQt6.QtWidgets import (QApplication, QWidget,
                             QPushButton, QVBoxLayout, QDialog)


class SecondWindow(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)



        self.setMinimumSize(500, 300)
        self.setMaximumSize(1000, 800)

        #sets policy based resizing.  I am not sure exactly what to expect from this.
#        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)

        quit_button = QPushButton("Quit")
        quit_button.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(quit_button)
        self.setLayout(layout)


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        # Set initial size
        self.resize(600, 400)
#        self.setFixedSize( 600, 400)

        button1 = QPushButton("Non-modal Window")
        button1.clicked.connect(self.open_second_nonModal)

        button2 = QPushButton("Modal Window")
        button2.clicked.connect(self.open_second_modal)

        layout = QVBoxLayout()
        layout.addWidget(button1)
        layout.addWidget(button2)
        self.setLayout(layout)


    def open_second_nonModal(self):
        self.w1 = SecondWindow()
        self.w1.setWindowTitle("Second Window - NonModal")
        self.w1.show()           # non modal window

    def open_second_modal(self):
        self.w2 = SecondWindow(self)
        self.w2.setWindowTitle("Second Window - Modal")
        self.w2.exec()           # modal window

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

