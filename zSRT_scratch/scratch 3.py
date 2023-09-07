import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QVBoxLayout, QWidget, QTreeWidgetItem, QAbstractItemView

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle("Tree Widget Example")

        # Create a tree widget
        self.tree_widget = QTreeWidget(self)
        self.tree_widget.itemClicked.connect(self.on_item_clicked)
        self.tree_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)  # Allow selecting a single item

        # Create top-level items
        parent_item1 = QTreeWidgetItem(self.tree_widget, ["Parent Item 1"])
        parent_item2 = QTreeWidgetItem(self.tree_widget, ["Parent Item 2"])

        # Create child items
        child_item1 = QTreeWidgetItem(parent_item1, ["Child Item 1"])
        child_item2 = QTreeWidgetItem(parent_item1, ["Child Item 2"])
        child_item3 = QTreeWidgetItem(parent_item2, ["Child Item 3"])

        # Create a layout for the main window
        layout = QVBoxLayout()
        layout.addWidget(self.tree_widget)

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
