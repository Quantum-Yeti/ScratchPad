from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem,
    QLabel, QAbstractItemView, QSizePolicy, QTextBrowser
)
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QIcon, QDesktopServices

from utils.resource_path_utils import resource_path
from views.dashboard import DashboardView
from views.components.sidebar import Sidebar
from models.model import NoteModel
from helpers.editor_helper import open_note_editor
from views.components.dashboard_container import DashboardContainer
import re


class MainView(QWidget):
    """
    Main application view for Scribble Notes.
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
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(4)
        main_layout.addWidget(right_container, stretch=1)

        # Category label
        self.category_title = QLabel("")
        self.category_title.setAlignment(Qt.AlignLeft)
        self.category_title.setStyleSheet("font-weight: bold; font-size: 16px;")
        right_layout.addWidget(self.category_title)

        # --- Toolbar Buttons ---
        self.add_btn = QPushButton("Add")
        self.add_btn.setIcon(QIcon(resource_path("icons/add.png")))
        self.add_btn.setMaximumWidth(90)

        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setIcon(QIcon(resource_path("icons/edit.png")))
        self.edit_btn.setMaximumWidth(90)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setIcon(QIcon(resource_path("icons/delete.png")))
        self.delete_btn.setMaximumWidth(90)

        self.btn_layout = QHBoxLayout()
        self.btn_layout.setSpacing(5)
        self.btn_layout.setContentsMargins(0, 0, 0, 0)
        self.btn_layout.addWidget(self.add_btn)
        self.btn_layout.addWidget(self.edit_btn)
        self.btn_layout.addWidget(self.delete_btn)
        self.btn_layout.addStretch()
        right_layout.addLayout(self.btn_layout)

        # --- Notes & Preview ---
        bottom_container = QWidget()
        bottom_layout = QHBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(5)

        # Dashboard Container
        self.dashboard_container = DashboardContainer(model=self.note_model)
        right_layout.addWidget(self.dashboard_container, alignment=Qt.AlignTop)
        right_layout.addWidget(bottom_container, stretch=1)

        # Note list
        self.note_list = QTreeWidget()
        self.note_list.setColumnCount(1)
        self.note_list.setHeaderLabels([""])
        self.note_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.note_list.setMinimumWidth(200)
        bottom_layout.addWidget(self.note_list, stretch=1)

        # Preview pane
        self.preview = QTextBrowser()
        self.preview.setReadOnly(True)
        self.preview.setOpenExternalLinks(False)  # Handle clicks manually
        self.preview.anchorClicked.connect(self.open_link_externally)
        self.preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        bottom_layout.addWidget(self.preview, stretch=2)

        # === Connections ===
        self.sidebar.category_selected.connect(self.load_notes_for_category)
        self.note_list.itemSelectionChanged.connect(self.on_note_selected)
        self.note_list.itemDoubleClicked.connect(self.handle_double_click)
        self.add_btn.clicked.connect(self.add_new_note)
        self.edit_btn.clicked.connect(self.handle_edit_click)
        self.delete_btn.clicked.connect(self.delete_selected_note)

    # ---------------- Internal Helpers ----------------
    def populate_note_list(self, notes):
        self.note_list.blockSignals(True)
        self.note_list.clear()
        for note in notes:
            item = QTreeWidgetItem([note["title"]])
            item.setData(0, Qt.ItemDataRole.UserRole, note["id"])
            self.note_list.addTopLevelItem(item)
        self.note_list.blockSignals(False)

    def on_note_selected(self):
        """Updates the preview when a note is selected and makes URLs clickable."""
        selected_items = self.note_list.selectedItems()
        if not selected_items or not self.current_category:
            self.preview.clear()
            return

        item = selected_items[0]
        note_id = item.data(0, Qt.ItemDataRole.UserRole)
        note = self.note_model.get_note_by_id(self.current_category, note_id)
        if not note:
            self.preview.clear()
            return

        self.current_note_id = note_id
        self.current_note_content = note["content"]

        # Convert URLs to clickable links
        def linkify(text):
            url_pattern = r"(https?://[^\s]+)"
            return re.sub(
                url_pattern,
                r'<a href="\1" style="color:#2E86C1;text-decoration:none;">\1</a>',
                text
            )

        html_content = linkify(self.current_note_content).replace("\n", "<br>")
        self.preview.setHtml(html_content)

    def open_link_externally(self, url: QUrl):
        """Open clicked URL in default system browser."""
        QDesktopServices.openUrl(url)

    # ---------------- Event Handlers ----------------
    def handle_double_click(self, item, column):
        if not item or not self.current_category:
            return
        QTimer.singleShot(0, lambda: open_note_editor(self, item, self.current_category))

    def handle_edit_click(self):
        selected_items = self.note_list.selectedItems()
        if not selected_items or not self.current_category:
            return
        item = selected_items[0]

        def _open():
            if getattr(self, "_editor_open", False):
                return
            self._editor_open = True
            try:
                open_note_editor(self, item, self.current_category)
            finally:
                QTimer.singleShot(0, lambda: setattr(self, "_editor_open", False))

        QTimer.singleShot(0, _open)

    # ---------------- Public Methods ----------------
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
        """Switches to dashboard view."""
        self.category_title.hide()
        self.add_btn.hide()
        self.edit_btn.hide()
        self.delete_btn.hide()
        self.note_list.hide()
        self.preview.hide()
        self.dashboard_container.show_dashboard()

    def show_notes(self):
        """Switches back to notes view."""
        self.sidebar.show()
        self.category_title.show()
        self.add_btn.show()
        self.edit_btn.show()
        self.delete_btn.show()
        self.note_list.show()
        self.preview.show()
        self.dashboard_container.hide_dashboard()

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
