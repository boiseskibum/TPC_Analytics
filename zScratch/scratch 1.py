from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QRadioButton, QComboBox, QPushButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Radio Button Example")

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        self.radio_button1 = QRadioButton("Option 1")
        self.radio_button1.setChecked(True)
        self.radio_button1.toggled.connect(self.radio_button_toggled)
        main_layout.addWidget(self.radio_button1)

        self.radio_button2 = QRadioButton("Option 2")
        self.radio_button2.toggled.connect(self.radio_button_toggled)
        main_layout.addWidget(self.radio_button2)

        self.combo_box = QComboBox()
        main_layout.addWidget(self.combo_box)

        self.toggle_button = QPushButton("Toggle Values")
        self.toggle_button.clicked.connect(self.toggle_values)
        main_layout.addWidget(self.toggle_button)

        self.set_combo_box_values(["a", "b"])

    def radio_button_toggled(self):
        if self.radio_button1.isChecked():
            self.set_combo_box_values(["a", "b"])
        elif self.radio_button2.isChecked():
            self.set_combo_box_values(["c", "d"])

    def set_combo_box_values(self, values):
        self.combo_box.clear()
        self.combo_box.addItems(values)


    def toggle_values(self):
        if self.combo_box.count() == 2:
            self.set_combo_box_values(["a", "b"])
        else:
            self.set_combo_box_values(["c", "d"])


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
