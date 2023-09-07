import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle("Tree Widget Example")

        # Create a tree widget
        tree_widget = QTreeWidget(self)
        tree_widget.setColumnCount(1)

        tree_widget.itemClicked.connect(self.on_item_clicked)

        # Add items to the tree widget
        root_item = QTreeWidgetItem(tree_widget, ["Root Item"])
        child_item1 = QTreeWidgetItem(root_item, ["Child Item 1"])
        child_item2 = QTreeWidgetItem(root_item, ["Child Item 2"])

        # Create a layout for the main window
        layout = QVBoxLayout()
        layout.addWidget(tree_widget)

        # Create a central widget and set the layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def on_item_clicked(self, item, column):
        # This slot is called when an item in the tree widget is clicked
        print(f"Item clicked: {item.text(column)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
