import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtWidgets import QLineEdit, QPushButton, QMenu, QMessageBox, QDialog, QComboBox, QToolBar
from PyQt6.QtGui import QAction


# Main window class
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Serial Port Manager")
        self.setGeometry(100, 100, 400, 200)

        # Create the central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a grid layout for buttons and input fields
        grid_layout = QGridLayout(central_widget)
        grid_layout.setHorizontalSpacing(10)
        grid_layout.setVerticalSpacing(10)

        # Create three input fields
        self.input_fields = []
        for i in range(3):
            label = QLabel(f"Input {i+1}:", self)
            line_edit = QLineEdit(self)
            grid_layout.addWidget(label, i, 0, alignment=Qt.AlignmentFlag.AlignRight)
            grid_layout.addWidget(line_edit, i, 1)
            self.input_fields.append(line_edit)

        # Create three buttons
        buttons_layout = QHBoxLayout()
        self.buttons = []
        for i in range(3):
            button = QPushButton(f"Button {i+1}", self)
            buttons_layout.addWidget(button)
            self.buttons.append(button)
        grid_layout.addLayout(buttons_layout, 3, 0, 1, 2)

    def create_menu(self):
        # Create the menu bar
        menu_bar = self.menuBar()
        #        bit_menu = menu_bar.addMenu("who knows")

        file_menu = QMenu("File_st", self)
        settings_action = QAction("Open", self)
        settings_action = QAction("Settings", self)
        quit_action = QAction("quit", self)
        open_action = QAction("quit", self)
        file_menu.addAction(settings_action)
        file_menu.addAction(quit_action)
        file_menu.addAction(open_action)

        # Create edit menu and add actions
        edit_menu = QMenu("edit", self)
        copy_action = QAction("Copy", self)
        more_settings_action = QAction("Settings", self)
        paste_action = QAction("Paste", self)
        edit_menu.addAction(copy_action)
        edit_menu.addAction(more_settings_action)
        edit_menu.addAction(paste_action)

        # Create edit menu and add actions
        cmj_menu = QMenu("Cmj", self)
        more_settings_action = QAction("Settings", self)
        edit_menu.addAction(more_settings_action)
        other_action = QAction("Other", self)
        edit_menu.addAction(other_action)

#        copy_action.triggered.connect(self.show_settings_dialog)
        more_settings_action.triggered.connect(self.show_settings_dialog)
        other_action.triggered.connect(self.show_settings_dialog)

        menu_bar.addMenu(edit_menu)
        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(cmj_menu)

    def show_settings_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog.setFixedSize(300, 100)

        layout = QVBoxLayout(dialog)

        reload_button = QPushButton("Reload Serial Ports", dialog)
        reload_button.clicked.connect(self.reload_serial_ports)
        layout.addWidget(reload_button)

        serial_ports = ["COM1", "COM2", "COM3", "COM4"]  # Replace with actual serial ports
        port_label = QLabel("Select Serial Port:", dialog)
        port_combo_box = QComboBox(dialog)
        port_combo_box.addItems(serial_ports)
        layout.addWidget(port_label)
        layout.addWidget(port_combo_box)

        dialog.exec()

    def reload_serial_ports(self):
        # Replace with actual code to reload serial ports
        QMessageBox.information(self, "Reload Serial Ports", "Serial ports reloaded.")

# Create the application
app = QApplication(sys.argv)
window = MainWindow()
window.show()
window.create_menu()

# Run the event loop
sys.exit(app.exec())
