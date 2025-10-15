from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSizePolicy, QSpacerItem
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QFileDialog, QMessageBox
import subprocess
import os

from helpers.clickable_icon import ClickableIcon


class Sidebar(QWidget):
    category_selected = Signal(str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(2, 2, 2, 2)

        icon_paths = {
            "Contacts": "icons/contacts.png",
            "Bookmarks": "icons/bookmarks.png",
            "Copilot": "icons/copilot.png",
            "Notes": "icons/notes.png"
        }

        categories = ["Contacts", "Bookmarks", "Copilot", "Notes"]
        self.category_buttons = []

        for category in categories:
            btn = QPushButton(category)
            btn.setToolTip(f"{category}")
            btn.setCheckable(True)
            btn.setFixedHeight(50)

            # Set icon if available
            icon_path = icon_paths.get(category)
            if icon_path:
                btn.setIcon(QIcon(icon_path))
                btn.setIconSize(QSize(24, 24))

            btn.clicked.connect(lambda checked, c=category: self.category_selected.emit(c))
            layout.addWidget(btn)
            self.category_buttons.append(btn)

        # Ensure only one category button is checked at a time
        for btn in self.category_buttons:
            btn.clicked.connect(self._update_category_button_states)

        if self.category_buttons:
            self.category_buttons[0].setChecked(True)
            self.category_selected.emit(self.category_buttons[0].text())

        # Add a spacer to push the bottom buttons to the bottom
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)

        # Container widget for bottom buttons + logo
        bottom_container = QWidget()
        bottom_layout = QVBoxLayout(bottom_container)
        bottom_layout.setSpacing(10)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        # Dashboard button
        self.dashboard_btn = QPushButton("Dashboard")
        self.dashboard_btn.setToolTip("Dashboard")
        self.dashboard_btn.setFixedHeight(40)
        self.dashboard_btn.setIcon(QIcon("icons/dashboard.png"))
        self.dashboard_btn.setIconSize(QSize(20, 20))
        bottom_layout.addWidget(self.dashboard_btn)

        # Run .bat file button
        self.run_bat_btn = QPushButton("Run .bat file")
        self.run_bat_btn.setToolTip("Run a local .bat file")
        self.run_bat_btn.setFixedHeight(40)
        self.run_bat_btn.setIcon(QIcon("icons/run.png"))
        self.run_bat_btn.setIconSize(QSize(20, 20))
        self.run_bat_btn.clicked.connect(self.run_bat_file)
        bottom_layout.addWidget(self.run_bat_btn)

        # Developer logo (replace 'path_to_logo.png' with your image path)
        self.dev_logo = ClickableIcon("https://github.com/Quantum-Yeti/ScratchPad")
        self.dev_logo.setToolTip("GitHub Repository")
        pixmap = QPixmap("icons/dev_logo.png")
        if not pixmap.isNull():
            self.dev_logo.setPixmap(pixmap.scaledToWidth(100, Qt.SmoothTransformation))
        self.dev_logo.setAlignment(Qt.AlignCenter)
        bottom_layout.addWidget(self.dev_logo)

        layout.addWidget(bottom_container)

    def run_bat_file(self):
        file_path = QFileDialog.getOpenFileName(self, "Select .bat file", os.path.expanduser("~"),"*.bat")
        if file_path:
            try:
                subprocess.Popen(file_path, shell=True)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to run the .bat file: \n{e}")


    def _update_category_button_states(self):
        sender = self.sender()
        for btn in self.category_buttons:
            if btn is not sender:
                btn.setChecked(False)

