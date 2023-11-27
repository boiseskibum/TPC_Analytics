from PyQt6.QtWidgets import QDialog, QApplication
import jt_add_athlete_dialog

class AddAthleteDialog(QDialog):
    def __init__(self):
        super().__init__()

        # Set up the user interface from Designer
        self.ui = jt_add_athlete_dialog.Ui_Dialog()
        self.ui.setupUi(self)

        # Populate the combo box
        self.ui.comboBox.addItem("Left")
        self.ui.comboBox.addItem("Right")

        # Connect the OK and Cancel buttons
        self.ui.okButton.clicked.connect(self.accept)
        self.ui.cancelButton.clicked.connect(self.reject)

    def get_values(self):
        # Retrieve values from the dialog
        name = self.ui.athletes_name.text()
        hand = self.ui.comboBox.currentText()
        shan_length = self.ui.shan_length.text()  # Convert to float or int as needed

        return name, hand, shan_length

app = QApplication([])
dialog = AddAthleteDialog()

if dialog.exec() == QDialog.DialogCode.Accepted:
    name, hand, shan_length = dialog.get_values()
    print(f"Name: {name}, Hand: {hand}, Shan Length: {shan_length}")

app.exec()
