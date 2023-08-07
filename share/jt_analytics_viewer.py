from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtWidgets import    QPushButton, QComboBox, QTextEdit, QGroupBox, QSizePolicy
from PyQt6.QtCore import Qt  # Import the Qt module
class JT_PreferencesWindow(QWidget):
    def __init__(self, jt_config, jt_trial=None):
        super().__init__()

        self.setWindowTitle("Preferences")
        self.setGeometry(600, 200, 500, 700)
