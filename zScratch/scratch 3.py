import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt6.QtCore import QTimer, QUrl
from PyQt6.QtMultimedia import QSoundEffect

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.button = QPushButton("Start Timer", self)
        self.button.clicked.connect(self.startTimer)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.checkTime)
        self.curTime = 0
        self.beginTime = 1

        self.shortBeep = QSoundEffect()
        self.shortBeep.setSource(QUrl.fromLocalFile("first1.wav"))
        self.longBeep = QSoundEffect()
        self.longBeep.setSource(QUrl.fromLocalFile("last.wav"))

        # Set window geometry and show
        self.setGeometry(300, 300, 300, 200)
        self.show()

    def startTimer(self):
        self.curTime = 0
        self.timer.start(1000)  # Timer ticks every second

    def checkTime(self):
        self.curTime += 1
        if self.curTime == self.beginTime or self.curTime == self.beginTime+1:
            self.shortBeep.play()
        elif self.curTime == self.beginTime+2:
            self.longBeep.play()
            self.timer.stop()  # Stop the timer after 5 seconds

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec())
