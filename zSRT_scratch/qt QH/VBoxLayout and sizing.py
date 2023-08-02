import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy
from PyQt6.QtCore import Qt

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("Nested Layout Example")

    main_layout = QVBoxLayout()  # Create the main QVBoxLayout

    # First row (Vertical layout with 2 buttons)
    vertical_layout = QVBoxLayout()

    button1 = QPushButton("Button 1")
    button2 = QPushButton("Button 2")

    vertical_layout.addWidget(button1)
    vertical_layout.addWidget(button2)

    main_layout.addLayout(vertical_layout)  # Add the vertical layout to the main layout

    # Second row (Horizontal layout with 2 buttons)
    horizontal_layout = QHBoxLayout()

    button3 = QPushButton("Button 3")
    button4 = QPushButton("Button 4")

    button3.setSizePolicy(
        QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
    )

    button4.setSizePolicy(
        QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
    )

    horizontal_layout.addWidget(button3)
    horizontal_layout.addWidget(button4)

    main_layout.addLayout(horizontal_layout)  # Add the horizontal layout to the main layout


    # Last row (Stretch both horizontally and vertically)
    # stretch_button = QPushButton("Stretch Button")
    # stretch_button.setSizePolicy(
    #     QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
    # )

    #main_layout.addWidget(stretch_button)  # Add the stretch button to the main layout

    window.setLayout(main_layout)  # Set the main QVBoxLayout as the main layout of the window

    window.show()
    sys.exit(app.exec())
