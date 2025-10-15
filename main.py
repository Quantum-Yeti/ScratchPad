from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from controllers.controller import NoteController
from models.model import NoteModel
from views.main_view import MainView
from views.dashboard import DashboardView
from helpers.view_switcher import ViewSwitcher

import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scribble Notes")

        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Create model
        self.model = NoteModel()

        # Create main view (contains buttons, note list, editor, and content container)
        self.view = MainView()

        # Create dashboard view
        self.dashboard_view = DashboardView()
        # Add dashboard_view as a child inside main view's content container
        self.dashboard_view.setParent(self.view.content_container)
        self.view.content_layout.addWidget(self.dashboard_view)
        self.dashboard_view.hide()

        # Add only the main view to the main layout
        self.layout.addWidget(self.view)

        # Controller
        self.controller = NoteController(
            model=self.model,
            view=self.view,
            sidebar=self.view.sidebar,
            main_window=self,
            dashboard_view=self.view.dashboard_view
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
