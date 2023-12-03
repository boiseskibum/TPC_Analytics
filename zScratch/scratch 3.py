from PyQt6.QtWidgets import QApplication, QMessageBox
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
app = QApplication([])

msgBox = QMessageBox()
msgBox.setWindowTitle("About")
msgBox.setText(__copyright__)  # Your long about text
#msgBox.setStandardButtons(QMessageBox.Ok)
msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)
msgBox.exec()