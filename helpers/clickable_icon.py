from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
import webbrowser

class ClickableIcon(QLabel):
    def __init__(self, url=None, parent=None):
        super().__init__(parent)
        self.url = url
        self.setCursor(Qt.PointingHandCursor)  # Make it look clickable

    def mousePressEvent(self, event):
        if self.url:
            webbrowser.open(self.url)
