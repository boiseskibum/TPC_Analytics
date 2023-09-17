import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QPixmap

app = QApplication(sys.argv)
window = QMainWindow()
central_widget = QWidget()
window.setCentralWidget(central_widget)

layout = QVBoxLayout()

# Create a QLabel
label = QLabel()

# Specify the path to the image file
image_path = "jt.png"

# Create a QPixmap and validate if the image exists
pixmap = QPixmap(image_path)

if pixmap.isNull():
    print(f"Image '{image_path}' does not exist or is invalid.")
else:
    # Set the pixmap as the QLabel's image
    label.setPixmap(pixmap)

# Add the QLabel to the layout
layout.addWidget(label)

central_widget.setLayout(layout)

window.show()
sys.exit(app.exec())



