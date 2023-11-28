from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QTimer
import time

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timeout)
        self.timer.start(1000 // 33)  # Approximately 33 times per second

        self.last_call = time.perf_counter()

    def on_timeout(self):
        current_call = time.perf_counter()
        elapsed = current_call - self.last_call
        self.last_call = current_call

        print(f"Elapsed time since last call: {elapsed:.4f} seconds")

app = QApplication([])
window = MainWindow()
window.show()
app.exec()
