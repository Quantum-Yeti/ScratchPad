from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from controllers.controller import NoteController
from models.model import NoteModel
from views.main_view import MainView
from helpers.view_switcher import ViewSwitcher

import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scribble Notes")

        # Window background palette
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(60, 60, 60))
        self.setPalette(palette)

        # Central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Create model
        self.model = NoteModel()

        # Create main view, which already contains dashboard_view inside its layout
        self.view = MainView()

        # Add main view to layout
        self.layout.addWidget(self.view)

        # Controller uses dashboard_view from the main view directly
        self.controller = NoteController(
            model=self.model,
            view=self.view,
            sidebar=self.view.sidebar,
            main_window=self,
            dashboard_view=self.view.dashboard_view  # Use dashboard_view from MainView
        )

        # View Switcher
        self.view_switcher = ViewSwitcher(self, self.controller)

        # Start on Dashboard
        self.view_switcher.on_sidebar_select("Dashboard")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
