from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget

class CMJ_UI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Main Window")
        self.setGeometry(100, 100, 400, 300)

        # Create a central widget to hold the main window's layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a vertical layout for the main window
        main_layout = QVBoxLayout(central_widget)

        button = QPushButton("Open Second Window", self)
        button.clicked.connect(self.open_second_window)
        main_layout.addWidget(button)

        # Create a reference to the second window instance
        self.second_window = None

    def open_second_window(self):
        if not self.second_window:
            self.second_window = JT_PreferencesWindow(49, 69)
        self.second_window.show()

class JT_PreferencesWindow(QMainWindow):
    def __init__(self, st_var1, st_var2):
        super().__init__()

        print(f"st stuff   var1: {st_var1}, var2: {st_var2}")

        self.setWindowTitle("Second Window")
        self.setGeometry(200, 200, 300, 200)

        # Create a central widget to hold the second window's layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a vertical layout for the second window
        second_layout = QVBoxLayout(central_widget)

        button = QPushButton("Close", self)
        button.clicked.connect(self.close)
        second_layout.addWidget(button)

if __name__ == "__main__":
    app = QApplication([])
    window = CMJ_UI()
    window.show()
    app.exec()

