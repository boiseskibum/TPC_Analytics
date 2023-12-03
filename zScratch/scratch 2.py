from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QTextEdit, QPushButton

__copyright__ = """This software is designed to provide data from sensors (load cells), store the data,
    and provide the data in a usable format for Strength and Conditioning analytics
    Copyright (C) 2023  Jake Taylor and Steve Taylor

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)

        self.setWindowTitle("About")

        self.layout = QVBoxLayout(self)

        # Add a text edit for the long text
        self.textEdit = QTextEdit(self)
        self.textEdit.setReadOnly(True)
        self.textEdit.setText(__copyright__)
        self.layout.addWidget(self.textEdit)

        # Add a close button
        self.closeButton = QPushButton("Close", self)
        self.closeButton.clicked.connect(self.close)
        self.layout.addWidget(self.closeButton)

        self.resize(600, 400)  # You can adjust the size as needed

app = QApplication([])

dialog = AboutDialog()
dialog.exec()
