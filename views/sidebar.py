from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSizePolicy, QSpacerItem, QFileDialog, QMessageBox
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QPixmap, QIcon
import subprocess
import os

from helpers.clickable_icon import ClickableIcon
from utils.resource_path_utils import resource_path


class Sidebar(QWidget):
    category_selected = Signal(str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(2, 2, 2, 2)

        # Mapping category names to their respective icon filenames
        icon_paths = {
            "Contacts": resource_path("icons/contacts.png"),
            "Bookmarks": resource_path("icons/bookmarks.png"),
            "Copilot": resource_path("icons/copilot.png"),
            "Notes": resource_path("icons/notes.png")
        }

        categories = ["Contacts", "Bookmarks", "Copilot", "Notes"]
        self.category_buttons = []

        for category in categories:
            btn = QPushButton(category)
            btn.setToolTip(f"{category}")
            btn.setCheckable(True)
            btn.setFixedHeight(50)

            icon_path = icon_paths.get(category)
            if icon_path and os.path.exists(icon_path):
                btn.setIcon(QIcon(icon_path))
                btn.setIconSize(QSize(24, 24))

            btn.clicked.connect(lambda checked, c=category: self.category_selected.emit(c))
            layout.addWidget(btn)
            self.category_buttons.append(btn)

        # Ensure only one button can be checked at a time
        for btn in self.category_buttons:
            btn.clicked.connect(self._update_category_button_states)

        if self.category_buttons:
            self.category_buttons[0].setChecked(True)
            self.category_selected.emit(self.category_buttons[0].text())

        # Spacer to push bottom buttons to the bottom
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)

        # Bottom container for additional controls
        bottom_container = QWidget()
        bottom_layout = QVBoxLayout(bottom_container)
        bottom_layout.setSpacing(10)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        # Dashboard button
        self.dashboard_btn = QPushButton("Dashboard")
        self.dashboard_btn.setToolTip("Dashboard")
        self.dashboard_btn.setFixedHeight(40)
        self.dashboard_btn.setIcon(QIcon(resource_path("icons/dashboard.png")))
        self.dashboard_btn.setIconSize(QSize(20, 20))
        bottom_layout.addWidget(self.dashboard_btn)

        # Run .bat file button
        self.run_bat_btn = QPushButton("Run .bat file")
        self.run_bat_btn.setToolTip("Run a local .bat file")
        self.run_bat_btn.setFixedHeight(40)
        self.run_bat_btn.setIcon(QIcon(resource_path("icons/run.png")))
        self.run_bat_btn.setIconSize(QSize(20, 20))
        self.run_bat_btn.clicked.connect(self.run_bat_file)
        bottom_layout.addWidget(self.run_bat_btn)

        # Developer logo linking to GitHub
        self.dev_logo = ClickableIcon("https://github.com/Quantum-Yeti/ScratchPad")
        self.dev_logo.setToolTip("GitHub Repository")
        logo_path = resource_path("icons/dev_logo.png")
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            self.dev_logo.setPixmap(pixmap.scaledToWidth(100, Qt.SmoothTransformation))
        self.dev_logo.setAlignment(Qt.AlignCenter)
        bottom_layout.addWidget(self.dev_logo)

        layout.addWidget(bottom_container)

    def run_bat_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select .bat file", os.path.expanduser("~"), "*.bat")
        if file_path:
            try:
                subprocess.Popen(file_path, shell=True)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to run the .bat file:\n{e}")

    def _update_category_button_states(self):
        sender = self.sender()
        for btn in self.category_buttons:
            if btn is not sender:
                btn.setChecked(False)
