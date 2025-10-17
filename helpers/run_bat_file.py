import os
import subprocess

from PySide6.QtWidgets import QFileDialog, QMessageBox


def run_bat_file(self):
    file_path, _ = QFileDialog.getOpenFileName(self, "Select .bat file", os.path.expanduser("~"), "*.bat")
    if file_path:
        try:
            subprocess.Popen(file_path, shell=True)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to run the .bat file:\n{e}")