import sys
from PyQt6.QtCore import QDateTime, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Grid Layout Example")

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        grid_layout = QGridLayout()
        main_layout.addLayout(grid_layout)

        label1 = QLabel("Label 1:")
        grid_layout.addWidget(label1, 0, 0)

        input1 = QLineEdit()
        grid_layout.addWidget(input1, 0, 1)

        label2 = QLabel("Label 2:")
        grid_layout.addWidget(label2, 1, 0)

        input2 = QLineEdit()
        grid_layout.addWidget(input2, 1, 1)

        button1 = QPushButton("Open Second Window")
        button1.clicked.connect(self.open_second_window)
        grid_layout.addWidget(button1, 2, 0, 1, 2)

        button2 = QPushButton("Update Time")
        button2.clicked.connect(self.update_time)
        grid_layout.addWidget(button2, 3, 0, 1, 2)

        self.time_label = QLabel()
        main_layout.addWidget(self.time_label, alignment=Qt.AlignmentFlag.AlignBottom)

    def open_second_window(self):
        second_window = SecondWindow(self)
        second_window.show()

    def update_time(self):
        current_time = QDateTime.currentDateTime().toString(Qt.DateFormat.DefaultLocaleLongDate)
        self.time_label.setText(f"Current Time: {current_time}")


class SecondWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Second Window")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()
        self.setLayout(layout)

        quit_button = QPushButton("Quit")
        quit_button.clicked.connect(self.close)
        layout.addWidget(quit_button)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

