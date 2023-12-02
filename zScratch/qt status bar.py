import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QProgressBar, QPushButton, QWidget, QStatusBar
from PyQt6.QtCore import QTimer

class ProgressBarWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Progress Bar Example")
        self.setGeometry(100, 100, 400, 200)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create a progress bar
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        # Create a button to start the progress
        start_button = QPushButton("Start Progress", self)
        start_button.clicked.connect(self.start_progress)
        layout.addWidget(start_button)

        # Create a status bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        # Initialize variables
        self.progress_value = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)

    def start_progress(self):
        # Reset progress bar and start the timer
        self.progress_value = 0
        self.progress_bar.setValue(0)
        self.timer.start(50)  # Update every 50 milliseconds (0.05 seconds)

    def update_progress(self):
        # Update progress and check if it's completed
        self.progress_value += 1
        self.progress_bar.setValue(self.progress_value)

        # Update status bar with percentage
        percentage = (self.progress_value / 100) * 100
        self.status_bar.showMessage(f"Progress: {percentage:.2f}%")

        if self.progress_value >= 100:
            # Progress completed, stop the timer
            self.timer.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProgressBarWindow()
    window.show()
    sys.exit(app.exec())
