import sys
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox, QInputDialog


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dialog Box Examples")

        # Yes/No Dialog
        self.show_yes_no_dialog()

        # OK Dialog
        self.show_ok_dialog()

        # Input Integer Dialog
        self.show_input_integer_dialog()

        # OK/Cancel Dialog
        self.show_ok_cancel_dialog()

    def show_yes_no_dialog(self):
        reply = QMessageBox.question(self, "Yes/No Dialog", "Do you like Python?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            print(f"You clicked Yes!   {reply}" )
        else:
            print(f"You clicked No!   {reply}")

    def show_ok_dialog(self):
        QMessageBox.information(self, "OK Dialog", "This is an OK dialog.")

    def show_input_integer_dialog(self):
        number, ok = QInputDialog.getInt(self, "Input Integer", "Enter a number:")
        if ok:
            print(f"You entered: {number}, {ok}")
        else:
            print(f"No number entered:  {number}, {ok}")

    def show_ok_cancel_dialog(self):
        reply = QMessageBox.question(self, "OK/Cancel Dialog", "Do you want to proceed?",
                                     QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        if reply == QMessageBox.StandardButton.Ok:
            print(f"You clicked OK!  {reply}")
        else:
            print(f"You clicked Cancel!: {reply}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
