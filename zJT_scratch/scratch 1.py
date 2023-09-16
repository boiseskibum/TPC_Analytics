import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QCheckBox, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

def checkbox_changed(state):
    if state == 2:
        print(f"Checkbox is checked {state}")
    else:
        print(f"Checkbox is unchecked: {state}, Qt...Checked: {Qt.CheckState.Checked}")

app = QApplication(sys.argv)
window = QMainWindow()
central_widget = QWidget()
window.setCentralWidget(central_widget)

layout = QVBoxLayout()
checkbox = QCheckBox("Check me")

layout.addWidget(checkbox)
central_widget.setLayout(layout)

# Connect the checkbox's stateChanged signal to the custom slot checkbox_changed
checkbox.stateChanged.connect(checkbox_changed)

window.show()
sys.exit(app.exec())
