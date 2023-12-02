from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QLabel, QLineEdit, QPushButton, QWidget


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grid Layout Example")

        # Create the main widget and set it as the central widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Create a grid layout for the main widget
        grid_layout = QGridLayout()
        main_widget.setLayout(grid_layout)

        # Create labels
        label1 = QLabel("Label 1")
        label2 = QLabel("Label 2")

        # Create input fields
        input1 = QLineEdit()
        input2 = QLineEdit()

        # Create buttons
        button1 = QPushButton("Button 1")
        button2 = QPushButton("Button 2")

        # Add widgets to the grid layout
        grid_layout.addWidget(label1, 0, 0)
        grid_layout.addWidget(input1, 0, 1)
        grid_layout.addWidget(button1, 0, 2)

        grid_layout.addWidget(label2, 1, 0)
        grid_layout.addWidget(input2, 1, 1)
        grid_layout.addWidget(button2, 1, 2)


if __name__ == "__main__":
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec()
