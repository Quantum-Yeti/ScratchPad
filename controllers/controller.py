import os
import re

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QCheckBox, QMessageBox
)

from helpers.tooltip import ToolTip
from views.editor_panel import EditorPanel


class NoteController:
    def __init__(self, model, view, sidebar, main_window, dashboard_view=None):
        self.model = model
        self.view = view
        self.sidebar = sidebar
        self.main_window = main_window
        self.dashboard_view = dashboard_view

        self.current_category = None

        # Keep pixmaps alive for embedded images if needed somewhere else
        self.view._image_refs = []

        self._connect_signals()
        self._setup_always_on_top_checkbox()

    def _connect_signals(self):
        self.view.controller = self
        self.sidebar.category_selected.connect(self.select_category)

        if hasattr(self.sidebar, 'dashboard_btn'):
            self.sidebar.dashboard_btn.clicked.connect(self.show_dashboard)

        self.view.add_btn.clicked.connect(self.add_note)
        self.view.edit_btn.clicked.connect(self.edit_note)
        self.view.delete_btn.clicked.connect(self.delete_note)
        self.view.note_list.itemSelectionChanged.connect(self.on_note_select)  # fixed signal for QTreeWidget

    def _setup_always_on_top_checkbox(self):
        self.always_on_top_cb = QCheckBox("Always on Top")
        self.always_on_top_cb.setChecked(False)
        self.always_on_top_cb.stateChanged.connect(self.toggle_always_on_top)
        ToolTip(self.always_on_top_cb, "Toggle Always on Top for window")
        self.view.btn_layout.addWidget(self.always_on_top_cb)

    # ---- Event Handlers ----

    def toggle_always_on_top(self, state):
        self.main_window.setWindowFlag(Qt.WindowStaysOnTopHint, bool(state))
        self.main_window.show()

    def select_category(self, category):
        if category == "Dashboard" and self.dashboard_view:
            self.show_dashboard()
            return

        self.current_category = category
        notes = self.model.get_notes(category)
        self.view.populate_note_list(notes)
        self.view.set_category_title(category)
        self.view.show_notes()
        if self.dashboard_view:
            self.dashboard_view.hide()

        # Clear current note selection and content cache
        self.view.current_note_id = None
        self.view.current_note_content = ""

    def show_dashboard(self):
        if not self.dashboard_view:
            return

        self.current_category = None
        self.view.set_category_title("Dashboard")
        self.view.show_dashboard()
        if self.dashboard_view:
            self.dashboard_view.show()
            self.update_dashboard_stats()

        # Clear current note selection and content cache
        self.view.current_note_id = None
        self.view.current_note_content = ""

    def update_dashboard_stats(self):
        if not self.dashboard_view:
            return

        notes = self.model.get_notes("Notes") or []
        contacts = self.model.get_notes("Contacts") or []
        bookmarks = self.model.get_notes("Bookmarks") or []
        copilot = self.model.get_notes("Copilot") or []

        completed_tasks = self.model.count_completed_tasks() if hasattr(self.model, 'count_completed_tasks') else 0
        storage_percent = self.model.get_storage_usage_percent() if hasattr(self.model, 'get_storage_usage_percent') else 0

        self.dashboard_view.update_stats(
            notes_count=len(notes),
            contacts_count=len(contacts),
            bookmarks_count=len(bookmarks),
            copilot_count=len(copilot),
            tasks_completed=completed_tasks,
            storage_percent=storage_percent
        )

    def get_selected_note_id(self):
        selected_items = self.view.note_list.selectedItems()
        if not selected_items:
            return None
        item = selected_items[0]
        return item.data(0, Qt.ItemDataRole.UserRole)

    def on_note_select(self):
        note_id = self.get_selected_note_id()
        if note_id is not None and self.current_category:
            note = self.model.get_note_by_id(self.current_category, note_id)
            if note:
                # Update cached note info in view, but do not try to display it here
                self.view.current_note_id = note_id
                self.view.current_note_content = note["content"]
            else:
                self.view.current_note_id = None
                self.view.current_note_content = ""
        else:
            self.view.current_note_id = None
            self.view.current_note_content = ""

    def add_note(self):
        if not self.current_category:
            QMessageBox.warning(self.main_window, "Warning", "Please select a category first.")
            return
        self._open_edit_dialog("Add Note", "", self._add_note_callback)

    def edit_note(self):
        note_id = self.get_selected_note_id()
        if note_id is None or not self.current_category:
            QMessageBox.warning(self.main_window, "Warning", "Please select a note to edit.")
            return

        note = self.model.get_note_by_id(self.current_category, note_id)
        if note:
            self._open_edit_dialog("Edit Note", note["content"], lambda content: self._edit_note_callback(note_id, content))

    def delete_note(self):
        note_id = self.get_selected_note_id()
        if note_id is None or not self.current_category:
            QMessageBox.warning(self.main_window, "Warning", "Please select a note to delete.")
            return

        confirm = QMessageBox.question(self.main_window, "Delete", "Are you sure you want to delete this note?")
        if confirm == QMessageBox.StandardButton.Yes:
            self.model.delete_note(self.current_category, note_id)
            self.select_category(self.current_category)
            if self.dashboard_view and self.current_category is None:
                self.update_dashboard_stats()

    # ---- Private Methods ----

    def _open_edit_dialog(self, title, content, save_callback):
        dialog = EditorPanel(self.main_window, title, content, save_callback)
        dialog.exec()

    def _add_note_callback(self, content):
        title = content.split('\n')[0][:30] or "Untitled"
        self.model.add_note(self.current_category, title, content)
        self.select_category(self.current_category)
        if self.dashboard_view and self.current_category is None:
            self.update_dashboard_stats()

    def _edit_note_callback(self, note_id, content):
        title = content.split('\n')[0][:30] or "Untitled"
        self.model.edit_note(self.current_category, note_id, title, content)
        self.select_category(self.current_category)
        if self.dashboard_view and self.current_category is None:
            self.update_dashboard_stats()
