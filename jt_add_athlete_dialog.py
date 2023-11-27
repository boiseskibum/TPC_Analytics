from PyQt6.QtWidgets import QDialog, QApplication, QDialogButtonBox
from jt_add_athlete_dialog_designer import Ui_Dialog_add_user

class AddAthleteDialog(QDialog, Ui_Dialog_add_user):
    def __init__(self):
        super().__init__()

        # Set up the user interface from Designer
#        self = jt_add_athlete_dialog_Dialog()
        self.setupUi(self)

        # Populate the combo box
        self.left_right_comboBox.addItems(["left", "right"])

        self.athlete_edit.textChanged.connect(self.validate_inputs)
        self.shank_length_edit.textChanged.connect(self.validate_inputs)
        self.left_right_comboBox.currentIndexChanged.connect(self.validate_inputs)

        # Retrieve the OK button and disable it
        self.ok_button = self.buttonBox.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setEnabled(False)


    def validate_inputs(self):
        athlete = self.athlete_edit.text()
        shank_length = self.shank_length_edit.text()

        # Check if name is not empty and shan_length is a valid number
        try:
            shank_length_valid = float(shank_length) > 0
        except ValueError:
            shank_length_valid = False

        # Enable or disable OK button
        self.ok_button.setEnabled(athlete.strip() != "" and shank_length_valid)

    def get_values(self):
        # Retrieve values from the dialog
        athlete = self.athlete_edit.text()
        injured = self.left_right_comboBox.currentText()
        shank_length = self.shank_length_edit.text()  # Convert to float or int as needed

        return athlete, injured, shank_length

if __name__ == "__main__":
    app = QApplication([])
    dialog = AddAthleteDialog()

    if dialog.exec() == QDialog.DialogCode.Accepted:
        athlete, injured, shank_length = dialog.get_values()
        print(f"athletes name: {athlete}, injured: {injured}, Shank Length: {shank_length}")

    app.exec()
