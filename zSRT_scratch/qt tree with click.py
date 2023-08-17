from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt
import sys

class TreeWidgetExample(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tree Widget Example")
        self.setGeometry(100, 100, 400, 300)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Athlete", "Date", "Trial"])
        self.setCentralWidget(self.tree_widget)

        self.populate_tree()
        self.tree_widget.itemClicked.connect(self.item_clicked)

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
                    trial_item.setData(0, Qt.ItemDataRole.UserRole, athlete+'/'+date+'/'+trial)
    def item_clicked(self, item, column):
        #print(f"item {item}, column: {col
        # umn}")
        if item.childCount() == 0:
            parent_path = ""
            current_item = item
            while current_item.parent():
                parent_path = f"/{current_item.text(0)}{parent_path}"
                current_item = current_item.parent()
            additional_data = item.data(0, Qt.ItemDataRole.UserRole)
            print(f"Clicked: {item.text(0)}, Parent Path: {parent_path}, additional data: {additional_data}")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TreeWidgetExample()
    window.show()
    sys.exit(app.exec())
