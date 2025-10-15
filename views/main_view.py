from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem,
    QTextEdit, QLabel, QAbstractItemView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from utils.resource_path_utils import resource_path

from views.dashboard import DashboardView
from views.sidebar import Sidebar


class MainView(QWidget):
    def __init__(self):
        super().__init__()

        self._image_refs = []

        main_layout = QHBoxLayout(self)

        # Sidebar on the left
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)

        # Right side container
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        main_layout.addWidget(right_container, stretch=1)

        # Category title label
        self.category_title = QLabel("")
        self.category_title.setAlignment(Qt.AlignLeft)
        self.category_title.setStyleSheet("font-weight: bold; font-size: 16px;")
        right_layout.addWidget(self.category_title)

        # Buttons layout
        self.add_btn = QPushButton("Add")
        self.add_btn.setIcon(QIcon(resource_path("icons/add.png")))
        self.edit_btn = QPushButton("Edit")
        self.delete_btn = QPushButton("Delete")
        self.btn_layout = QHBoxLayout()
        self.btn_layout.addWidget(self.add_btn)
        self.btn_layout.addWidget(self.edit_btn)
        self.btn_layout.addWidget(self.delete_btn)
        right_layout.addLayout(self.btn_layout)

        # Content container for notes or dashboard
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        right_layout.addWidget(self.content_container, stretch=1)

        # Note list
        self.note_list = QTreeWidget()
        self.note_list.setColumnCount(1)
        self.note_list.setHeaderLabels(["Title"])
        self.note_list.setSelectionMode(QAbstractItemView.SingleSelection)

        # Editor
        self.editor = QTextEdit()
        self.editor.setReadOnly(True)

        # Add note list and editor
        self.content_layout.addWidget(self.note_list)
        self.content_layout.addWidget(self.editor)

        # Create dashboard view, hidden by default
        self.dashboard_view = DashboardView()
        self.dashboard_view.hide()
        self.content_layout.addWidget(self.dashboard_view)

        # Model for note_list to get item from index
        self.note_model = self.note_list.model()

    def populate_note_list(self, notes):
        self.note_list.clear()
        for note in notes:
            item = QTreeWidgetItem([note['title']])
            # Store note id in column 0 with UserRole
            item.setData(0, Qt.ItemDataRole.UserRole, note['id'])
            self.note_list.addTopLevelItem(item)

    def display_note_content(self, content):
        self.editor.setPlainText(content)

    def set_category_title(self, title):
        self.category_title.setText(title)

    def show_dashboard(self):
        self.note_list.hide()
        self.editor.hide()
        self.dashboard_view.show()

    def show_notes(self):
        self.dashboard_view.hide()
        self.note_list.show()
        self.editor.show()
