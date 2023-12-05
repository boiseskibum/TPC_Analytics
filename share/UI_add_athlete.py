import re
from PyQt6.QtWidgets import QDialog, QApplication, QDialogButtonBox

try:
    from . import UI_add_athlete_designer as aaUI
except:
    import UI_add_athlete_designer as aaUI

class AddAthleteDialog(QDialog, aaUI.Ui_Dialog_add_user):
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

        # remove any double spaces within the string and push it back

        if bool(re.search(r' {2,}', athlete)):
            athlete = re.sub(r'\s{2,}', ' ', athlete)
            self.athlete_edit.setText(athlete)

        # Check if name is not empty and shan_length is a valid number
        try:
            shank_length_valid = float(shank_length) > 0
        except ValueError:
            shank_length_valid = False

        def validate_name(s):
            # Regular expression pattern
            pattern = r'^[a-zA-Z0-9 ~]+$'

            # Using re.match to check if the entire string matches the pattern
            if re.match(pattern, s):
                return True
            else:
                return False

        valid_name = validate_name(athlete)

        # Enable or disable OK button
        self.ok_button.setEnabled(athlete.strip() != "" and shank_length_valid and valid_name)

    def get_values(self):
        # Retrieve values from the dialog
        athlete = self.athlete_edit.text()
        athlete = athlete.strip()
        injured = self.left_right_comboBox.currentText()
        shank_length = self.shank_length_edit.text()  # Convert to float or int as needed

        return athlete, injured, shank_length

if __name__ == "__main__":
    app = QApplication([])
    dialog = AddAthleteDialog()

    if dialog.exec() == QDialog.DialogCode.Accepted:
        athlete, injured, shank_length = dialog.get_values()
        print(f"athletes name: |||{athlete}|||, injured: {injured}, Shank Length: {shank_length}")

    app.exec()
    app.exit()
