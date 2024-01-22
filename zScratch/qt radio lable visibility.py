import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QRadioButton, QLabel, QComboBox


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Radio Button Example")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.radio1 = QRadioButton("Radio Button 1")
        self.radio1.toggled.connect(self.on_radio1_toggled)
        layout.addWidget(self.radio1)

        self.radio2 = QRadioButton("Radio Button 2")
        self.radio2.toggled.connect(self.on_radio2_toggled)
        layout.addWidget(self.radio2)

        self.combo_box = QComboBox()
        self.combo_box.currentTextChanged.connect(self.combo_box_changed)
        layout.addWidget(self.combo_box)

        self.label = QLabel("Label Box")
        layout.addWidget(self.label)

        self.radio1.setChecked(True)

    def on_radio1_toggled(self, checked):

        print(f'radio button 1 clicked (checked: {checked}) - radio1 toggled: {self.radio1.isChecked()} radio2 checked: {self.radio2.isChecked()}')
        if checked is False:
            print('    bailing from radio1')
            return
        self.label.setVisible(False)
        self.set_combo_box_values(["Set 1", "a", "b"])

    def on_radio2_toggled(self, checked):
        print(f'radio button 2 clicked (checked: {checked}) - radio1 toggled: {self.radio1.isChecked()} radio2 checked: {self.radio2.isChecked()}')
        if checked is False:
            print('    bailing from radio2')
            return
        self.label.setVisible(True)
        self.set_combo_box_values(["Set 2", "d", "e"])


    def set_combo_box_values(self, values):
        print(f'    new combo box values: {values}')

        # NORMAL CODE TO DO THIS
        # self.combo_box.clear()
        # self.combo_box.addItems(values)

        my_list = values
        #START HACK
        for i in range(self.combo_box.count() - 1, 0, -1):
            self.combo_box.removeItem(i)
        self.combo_box.setItemText(0, my_list[0])
        for i in range(1, len(my_list)):
            print(f'   adding item {i}: {my_list[i]}')
            self.combo_box.addItem(my_list[i])
        # END HACK


    def combo_box_changed(self, value):
        print(f"    combo_box_changed, Selected: {value}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
