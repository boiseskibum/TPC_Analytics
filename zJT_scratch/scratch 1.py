from PyQt6.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem, QWidget, QVBoxLayout
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtCore import Qt

class CustomTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Right:
            current_item = self.currentItem()
            if current_item and not current_item.isExpanded():
                self.expandAllChildren(current_item)
                return
        super().keyPressEvent(event)

    def expandAllChildren(self, item: QTreeWidgetItem):
        item.setExpanded(True)
        for i in range(item.childCount()):
            child = item.child(i)
            self.expandAllChildren(child)

app = QApplication([])

# Main window setup
window = QWidget()
layout = QVBoxLayout(window)

# CustomTreeWidget
tree = CustomTreeWidget()
root = QTreeWidgetItem(tree, ["Root"])
child1 = QTreeWidgetItem(root, ["Child 1"])
subchild1 = QTreeWidgetItem(child1, ["Subchild 1"])
subsubchild1 = QTreeWidgetItem(subchild1, ["Subsubchild 1"])
child2 = QTreeWidgetItem(root, ["Child 2"])

layout.addWidget(tree)
window.setLayout(layout)
window.show()

app.exec()

