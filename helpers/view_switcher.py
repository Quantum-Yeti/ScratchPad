from PySide6.QtWidgets import QWidget

class ViewSwitcher:
    def __init__(self, main_window, controller):
        self.main_window = main_window
        self.controller = controller

    def on_sidebar_select(self, category):
        self.controller.view = self.main_window.view

        if category == "Dashboard":
            self.controller.show_dashboard()
        else:
            self.controller.select_category(category)
