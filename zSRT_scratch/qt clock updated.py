import sys
import time
from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel,
    QPushButton, QVBoxLayout, QDialog
)


class ClockThread(QThread):
    update_signal = pyqtSignal(str)

    def run(self):
        while True:
            time.sleep(1)
            curr_time = time.strftime("%H:%M:%S")
            self.update_signal.emit(curr_time)


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.label = QLabel("Clock")
        self.button = QPushButton("Popup Dialog")
        self.button.clicked.connect(self.show_dialog)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)

        self.setLayout(layout)

        self.clock_thread = ClockThread()
        self.clock_thread.update_signal.connect(self.update_label)
        self.clock_thread.start()

    @pyqtSlot(str)
    def update_label(self, text):
        self.label.setText(text)

    def show_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Dialog")
        dialog.exec()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()