from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from views.dashboard import DashboardView


class DashboardContainer(QWidget):
    """
    Wraps the DashboardView in a layout that keeps it top-centered
    and handles showing/hiding cleanly for MainView.
    """

    def __init__(self, model):
        super().__init__()

        # Dashboard instance
        self.dashboard_view = DashboardView(model)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        layout.addWidget(self.dashboard_view, alignment=Qt.AlignHCenter)
        layout.addStretch()  # pushes dashboard to top

        # Start hidden
        self.hide()

    def show_dashboard(self):
        """Show the dashboard view."""
        self.show()
        self.dashboard_view.show()

    def hide_dashboard(self):
        """Hide the dashboard view."""
        self.dashboard_view.hide()
        self.hide()

    def update_stats(self, **kwargs):
        """Forward stat updates to the actual dashboard view."""
        self.dashboard_view.update_stats(**kwargs)
