import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QSplitter

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Resizable Widgets with QSplitter")
        self.setGeometry(100, 100, 800, 600)

        # Create widgets
        left_widget = QWidget(self)
        right_widget = QWidget(self)

        # Create layouts for widgets
        left_layout = QVBoxLayout(left_widget)
        right_layout = QVBoxLayout(right_widget)

        # Populate left and right widgets with content
        left_layout.addWidget(QPushButton("Left Widget Content"))
        right_layout.addWidget(QPushButton("Right Widget Content"))

        # Create splitter and add widgets
        splitter = QSplitter(self)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        # Set stylesheet for splitter handle
        splitter.setStyleSheet("QSplitter::handle { background-color: grey; }")

        # Set the main layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(splitter)

        central_widget = QWidget(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
