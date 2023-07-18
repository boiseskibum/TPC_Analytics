import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QRadioButton, QLabel


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Radio Button Example")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.radio_button1 = QRadioButton("Radio Button 1")
        self.radio_button1.setChecked(True)
        self.radio_button1.toggled.connect(self.on_radio_button_toggled)
        layout.addWidget(self.radio_button1)

        self.radio_button2 = QRadioButton("Radio Button 2")
        self.radio_button2.toggled.connect(self.on_radio_button_toggled)
        layout.addWidget(self.radio_button2)

        self.label = QLabel("Label Box")
        layout.addWidget(self.label)

    def on_radio_button_toggled(self):
        if self.radio_button2.isChecked():
            self.label.setVisible(False)
        else:
            self.label.setVisible(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
