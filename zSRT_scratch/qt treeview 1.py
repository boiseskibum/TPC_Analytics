import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeView, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtGui import QFileSystemModel
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Tree View Example')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # Create a toggle button to hide/show the tree view
        self.toggle_button = QPushButton('Toggle Tree View')
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(True)
        self.toggle_button.clicked.connect(self.toggle_tree_view)
        layout.addWidget(self.toggle_button)

        # Create the QTreeView
        self.tree_view = QTreeView(self)
        layout.addWidget(self.tree_view)

        # Create a QFileSystemModel to populate the QTreeView with some fake data
        self.file_system_model = QFileSystemModel()
        self.file_system_model.setRootPath('')
        self.tree_view.setModel(self.file_system_model)
        self.tree_view.setRootIndex(self.file_system_model.index(''))

        # Hide the QTreeView initially
        self.tree_view.setVisible(False)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def toggle_tree_view(self):
        # Toggle the visibility of the QTreeView when the button is clicked
        self.tree_view.setVisible(self.toggle_button.isChecked())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
