import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt6.QtCore import QTimer, QThread

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.button = QPushButton("Start Timer", self)
        self.button.clicked.connect(self.startTimer)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.checkTime)
        self.startTime = 0

        # Set window geometry and show
        self.setGeometry(300, 300, 300, 200)
        self.show()

    def startTimer(self):
        self.startTime = 0
        self.timer.start(1000)  # Timer ticks every second

    def checkTime(self):
        self.startTime += 1
        if self.startTime in [3, 4]:
            QApplication.beep()
        elif self.startTime == 5:
            self.playLongBeep()
            self.timer.stop()  # Stop the timer after 5 seconds

    def playLongBeep(self):
        for _ in range(3):  # Attempt to create a longer beep
            QApplication.beep()
            QThread.msleep(50)  # Short delay between beeps

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec())
