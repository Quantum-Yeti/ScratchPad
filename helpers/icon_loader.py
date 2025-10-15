from PySide6.QtGui import QIcon
import os

ICON_FOLDER = os.path.join(os.path.dirname(__file__), "..", "icons")

def load_icon(name):
    path = os.path.join(ICON_FOLDER, f"{name}.png")
    if os.path.exists(path):
        return QIcon(path)
    return QIcon()
