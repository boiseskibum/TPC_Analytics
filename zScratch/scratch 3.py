import sys
import time
from PyQt6.QtWidgets import QApplication, QProgressDialog, QLabel, QVBoxLayout, QPushButton, QWidget
from PyQt6 import QtCore, QtWidgets

class FileProcessor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Processor")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout(self)

        # Button to start processing files
        start_button = QPushButton("Process Files", self)
        start_button.clicked.connect(self.process_files)
        layout.addWidget(start_button)

        # Label to display progress
        self.progress_label = QLabel(self)
        layout.addWidget(self.progress_label)

    def process_files(self):
        total_files = 129
        delay = 0.05  # Delay in seconds for each file processing

        # Create QProgressDialog
        progress = QProgressDialog("Processing Files...", "Cancel", 0, total_files, self)
        progress.setWindowModality(QtCore.Qt.WindowModality.WindowModal)

        for file_number in range(1, total_files + 1):
            time.sleep(delay)  # Simulate file processing time
            progress.setValue(file_number)
            progress.setLabelText(f"Processing File {file_number}/{total_files}")
            QtWidgets.QApplication.processEvents()  # Process events to update the UI
            if progress.wasCanceled():
                break

        progress.setValue(total_files)  # Ensure the progress bar reaches 100%
        self.progress_label.setText("Processing completed.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileProcessor()
    window.show()
    sys.exit(app.exec())
