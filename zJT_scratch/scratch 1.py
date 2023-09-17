import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt6.QtGui import QIcon, QPixmap

app = QApplication(sys.argv)
window = QMainWindow()
central_widget = QWidget()
window.setCentralWidget(central_widget)

layout = QVBoxLayout()

# Create a QPushButton
button = QPushButton("Click me")
label = QLabel("label here")

# Load an image as a QPixmap
pixmap = QPixmap("jt.png")

# Create an QIcon from the QPixmap
icon = QIcon(pixmap)

# Set the icon on the QPushButton
button.setIcon(icon)
button.setFlat(True)
# Add the button to the layout
layout.addWidget(button)

label.setPixmap(pixmap)
layout.addWidget(label)

central_widget.setLayout(layout)

window.show()
sys.exit(app.exec())

