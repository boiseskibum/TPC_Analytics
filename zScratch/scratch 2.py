from PyQt6.QtWidgets import QMainWindow, QApplication, QComboBox, QVBoxLayout, QPushButton, QWidget


class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Combo Box fix Example")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.combo_box = QComboBox()
        self.combo_box.currentTextChanged.connect(self.combo_box_changed)
        layout.addWidget(self.combo_box)

        self.button1 = QPushButton("Button1 - remove")
        self.button1.clicked.connect(self.on_pushButton1_clicked)
        layout.addWidget(self.button1)

        self.button2 = QPushButton("Button2 - add")
        self.button2.clicked.connect(self.on_pushButton2_clicked)
        layout.addWidget(self.button2)

        self.button3 = QPushButton("Button3 - do nothing")
        self.button3.clicked.connect(self.on_pushButton3_clicked)
        layout.addWidget(self.button3)

        self.button4 = QPushButton("Button4 - fixit")
        self.button4.clicked.connect(self.on_pushButton4_clicked)
        layout.addWidget(self.button4)

    def on_pushButton1_clicked(self):
        try:
            for i in range(self.combo_box.count() - 1, 0, -1):
                self.combo_box.removeItem(i)
                print(f'removed item i = {i}')
            print("combo_box->count():", self.combo_box.count())
        except Exception as e:
            print("exception:", e)

    def on_pushButton2_clicked(self):
        try:
            self.combo_box.addItem("some text " + str(self.combo_box.count()))
            print("combo_box->count():", self.combo_box.count())
        except Exception as e:
            print("exception:", e)

    def on_pushButton3_clicked(self):
        print('clicked combo box 3')
        self.combo_box.setCurrentText("")

    def on_pushButton4_clicked(self):
        print('clicked combo box 4')
        self.combo_box.setCurrentText("")

        my_list = "hi baby", "val 1", "val 2", "val 3", "val 4"
        for i in range(self.combo_box.count() - 1, 0, -1):
            self.combo_box.removeItem(i)
        self.combo_box.setItemText(0, my_list[0])
        for i in range(1, len(my_list)):
            print(f'   adding item {i}: {my_list[i]}')
            self.combo_box.addItem(my_list[i])

    def combo_box_changed(self, value):
        print(f"    combo_box_changed, Selected: {value}")



if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
