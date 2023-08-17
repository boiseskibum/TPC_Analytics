import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QMenu

class CustomTreeWidget(QTreeWidget):
    def __init__(self):
        super().__init__()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        expand_all_action = menu.addAction("Expand All")
        expand_all_action.triggered.connect(self.expand_all_items)

        collapse_all_action = menu.addAction("Collapse All")
        collapse_all_action.triggered.connect(self.collapse_all_items)

        menu.exec(event.globalPos())

    def expand_all_items(self):
        for i in range(self.topLevelItemCount()):
            self.topLevelItem(i).setExpanded(True)

    def collapse_all_items(self):
        for i in range(self.topLevelItemCount()):
            self.topLevelItem(i).setExpanded(False)

class TreeWidgetExample(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tree Widget Example")
        self.setGeometry(100, 100, 400, 300)

        self.tree_widget = CustomTreeWidget()
        self.tree_widget.setHeaderLabels(["Athlete", "Date", "Trial"])
        self.setCentralWidget(self.tree_widget)

        self.populate_tree()

    def populate_tree(self):
        athletes = ["Athlete 1", "Athlete 2", "Athlete 3"]

        for athlete in athletes:
            athlete_item = QTreeWidgetItem([athlete])
            self.tree_widget.addTopLevelItem(athlete_item)

            dates = ["2023-08-01", "2023-08-02", "2023-08-03"]

            for date in dates:
                date_item = QTreeWidgetItem([date])
                athlete_item.addChild(date_item)

                trials = ["Trial 1", "Trial 2", "Trial 3"]

                for trial in trials:
                    trial_item = QTreeWidgetItem([trial])
                    date_item.addChild(trial_item)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TreeWidgetExample()
    window.show()
    sys.exit(app.exec())
