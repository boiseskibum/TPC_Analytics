import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QComboBox, QPushButton


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Combo Box Example")

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        self.combo_box = QComboBox()
        self.combo_box.currentTextChanged.connect(self.combo_box_changed)
        main_layout.addWidget(self.combo_box)

        self.toggle_button = QPushButton("Toggle Values")
        self.toggle_button.clicked.connect(self.toggle_values)
        main_layout.addWidget(self.toggle_button)

        self.set_combo_box_values(["Set 1", "set 2"])

    def combo_box_changed(self, value):
        print(f"Selected: {value}")

    def set_combo_box_values(self, values):
        self.combo_box.clear()
        self.combo_box.addItems(values)

    def toggle_values(self):
        if self.combo_box.count() == 2:
            self.set_combo_box_values(["Set 1", "a", "b"])
        else:
            self.set_combo_box_values(["Set 2", "d", "e"])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
