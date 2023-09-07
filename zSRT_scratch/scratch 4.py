import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget,  QStandardItem, QStandardItemModel

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

        # Create a model for the tree widget
        self.tree_model = self.tree_widget.model()
        if self.tree_model is None:
            self.tree_model = QStandardItemModel(self.tree_widget)
            self.tree_widget.setModel(self.tree_model)

        # Create top-level items
        parent_item1 = QStandardItem("Parent Item 1")
        parent_item2 = QStandardItem("Parent Item 2")

        # Create child items
        child_item1 = QStandardItem("Child Item 1")
        child_item2 = QStandardItem("Child Item 2")
        child_item3 = QStandardItem("Child Item 3")

        # Add child items to the first parent item
        parent_item1.appendRow([child_item1, child_item2])

        # Add child items to the second parent item
        parent_item2.appendRow(child_item3)

        # Set the top-level items in the model
        self.tree_model.appendRow([parent_item1, parent_item2])

        # Expand all items in the tree
        self.tree_widget.expandAll()

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
