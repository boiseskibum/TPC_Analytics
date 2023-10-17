import sys
from PyQt6.QtWidgets import QApplication, QDialog, QProgressBar, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt, QTimer

class ProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Progress Dialog")
        self.setGeometry(100, 100, 300, 100)

        layout = QVBoxLayout(self)
        self.progressBar = QProgressBar(self)
        layout.addWidget(self.progressBar)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateProgress)
        self.timer.start(50)  # Update every 0.05 seconds (50 milliseconds)

    def updateProgress(self):
        current_value = self.progressBar.value()
        if current_value < 100:
            self.progressBar.setValue(current_value + 1)
        else:
            self.timer.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Show the progress dialog
    progress_dialog = ProgressDialog()
    progress_dialog.exec()

    sys.exit(app.exec())
