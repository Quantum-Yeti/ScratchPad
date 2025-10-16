from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem,
    QLabel, QAbstractItemView, QTextEdit, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon

from utils.resource_path_utils import resource_path
from views.dashboard import DashboardView
from views.sidebar import Sidebar
from models.model import NoteModel
from helpers.editor_helper import open_note_editor


class MainView(QWidget):
    """
    The main application view for Scribble Notes.
    Provides sidebar, note list, preview, and top toolbar buttons.
    """

    def __init__(self):
        super().__init__()

        # === Core model/state ===
        self.note_model = NoteModel()
        self.current_category = None
        self.current_note_id = None
        self.current_note_content = ""
        self._editor_open = False  # guard flag

        # === Layout ===
        main_layout = QHBoxLayout(self)

        # Sidebar
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)

        # Right content area
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        main_layout.addWidget(right_container, stretch=1)

        # Category label
        self.category_title = QLabel("")
        self.category_title.setAlignment(Qt.AlignLeft)
        self.category_title.setStyleSheet("font-weight: bold; font-size: 16px;")
        right_layout.addWidget(self.category_title)

        # Toolbar
        self.add_btn = QPushButton("Add")
        self.add_btn.setIcon(QIcon(resource_path("icons/add.png")))

        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setIcon(QIcon(resource_path("icons/edit.png")))

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setIcon(QIcon(resource_path("icons/delete.png")))

        self.btn_layout = QHBoxLayout()
        self.btn_layout.addWidget(self.add_btn)
        self.btn_layout.addWidget(self.edit_btn)
        self.btn_layout.addWidget(self.delete_btn)
        right_layout.addLayout(self.btn_layout)

        # Bottom: notes + preview
        bottom_container = QWidget()
        bottom_layout = QHBoxLayout(bottom_container)
        right_layout.addWidget(bottom_container, stretch=1)

        # Note list
        self.note_list = QTreeWidget()
        self.note_list.setColumnCount(1)
        self.note_list.setHeaderLabels(["Title"])
        self.note_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.note_list.setMinimumWidth(200)
        bottom_layout.addWidget(self.note_list, stretch=1)

        # Preview pane
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        bottom_layout.addWidget(self.preview, stretch=2)

        # Dashboard view
        self.dashboard_view = DashboardView(model=self.note_model)
        self.dashboard_view.hide()
        right_layout.addWidget(self.dashboard_view)

        # === Connections ===
        self.sidebar.category_selected.connect(self.load_notes_for_category)
        self.note_list.itemSelectionChanged.connect(self.on_note_selected)
        self.note_list.itemDoubleClicked.connect(self.handle_double_click)
        self.add_btn.clicked.connect(self.add_new_note)
        self.edit_btn.clicked.connect(self.handle_edit_click)
        self.delete_btn.clicked.connect(self.delete_selected_note)

    # Internal helpers

    def populate_note_list(self, notes):
        """Fills the note list widget."""
        self.note_list.blockSignals(True)
        self.note_list.clear()
        for note in notes:
            item = QTreeWidgetItem([note["title"]])
            item.setData(0, Qt.ItemDataRole.UserRole, note["id"])
            self.note_list.addTopLevelItem(item)
        self.note_list.blockSignals(False)

    def on_note_selected(self):
        """Updates the preview when a note is selected."""
        selected_items = self.note_list.selectedItems()
        if selected_items:
            item = selected_items[0]
            note_id = item.data(0, Qt.ItemDataRole.UserRole)
            note = self.note_model.get_note_by_id(self.current_category, note_id)
            if note:
                self.current_note_id = note_id
                self.current_note_content = note["content"]
                self.preview.setPlainText(self.current_note_content)
                return
        self.preview.clear()

    # Event Handlers (Double-click + Edit)
    def handle_double_click(self, item, column):
        print("DOUBLE CLICK handler invoked:", item, column, "cat:", self.current_category, "_editor_open:", getattr(self, "_editor_open", False))

        if not item or not self.current_category:
            return
        QTimer.singleShot(0, lambda: open_note_editor(self, item, self.current_category))

    def handle_edit_click(self):
        selected_items = self.note_list.selectedItems()
        if not selected_items or not self.current_category:
            return
        item = selected_items[0]

        # same deferred logic as double-click
        def _open():
            if getattr(self, "_editor_open", False):
                return
            self._editor_open = True
            try:
                open_note_editor(self, item, self.current_category)
            finally:
                QTimer.singleShot(0, lambda: setattr(self, "_editor_open", False))

        QTimer.singleShot(0, _open)


    # Public methods
    def set_category_title(self, title: str):
        self.category_title.setText(title)

    def load_notes_for_category(self, category):
        self.current_category = category
        self.set_category_title(category)
        notes = self.note_model.get_notes(category)
        self.populate_note_list(notes)
        self.current_note_id = None
        self.current_note_content = ""
        self.preview.clear()
        self.show_notes()

    def show_dashboard(self):
        self.note_list.hide()
        self.preview.hide()
        self.dashboard_view.show()

    def show_notes(self):
        self.dashboard_view.hide()
        self.note_list.show()
        self.preview.show()

    def add_new_note(self):
        if not self.current_category:
            return
        self.note_model.add_note(self.current_category, "", "")
        self.load_notes_for_category(self.current_category)

    def delete_selected_note(self):
        selected_items = self.note_list.selectedItems()
        if not selected_items or not self.current_category:
            return
        item = selected_items[0]
        note_id = item.data(0, Qt.ItemDataRole.UserRole)
        self.note_model.delete_note(self.current_category, note_id)
        self.load_notes_for_category(self.current_category)
