from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QMessageBox

from helpers.tooltip import ToolTip
from views.components.editor_panel import EditorPanel
from helpers.reselect_note import _reselect_note_in_list


class NoteController:
    """Controls note-related interactions between the model, view, and sidebar."""

    def __init__(self, model, view, sidebar, main_window, dashboard_view=None):
        self.model = model
        self.view = view
        self.sidebar = sidebar
        self.main_window = main_window
        self.dashboard_view = dashboard_view

        self.current_category = None
        self.view._image_refs = []  # keep pixmaps alive for embedded images

        self._connect_signals()
        self._setup_always_on_top_checkbox()

    # -------------------------------------------------------------------------
    # Initialization
    # -------------------------------------------------------------------------

    def _connect_signals(self):
        """Connect UI signals to their corresponding controller handlers."""
        self.view.controller = self
        self.sidebar.category_selected.connect(self.select_category)

        if hasattr(self.sidebar, "dashboard_btn"):
            self.sidebar.dashboard_btn.clicked.connect(self.show_dashboard)

        # Ensure single connections
        try:
            self.view.add_btn.clicked.disconnect()
        except TypeError:
            pass  # no previous connections
        self.view.add_btn.clicked.connect(self.add_note)

        self.view.edit_btn.clicked.connect(self.edit_note)
        self.view.delete_btn.clicked.connect(self.delete_note)
        self.view.note_list.itemSelectionChanged.connect(self.on_note_select)

    def _setup_always_on_top_checkbox(self):
        """Add an 'Always on Top' toggle checkbox to the view."""
        checkbox = QCheckBox("Always on Top")
        checkbox.setChecked(False)
        checkbox.stateChanged.connect(self.toggle_always_on_top)
        ToolTip(checkbox, "Keep window always on top")
        self.view.btn_layout.addWidget(checkbox)
        self.always_on_top_cb = checkbox

    # -------------------------------------------------------------------------
    # Category / Dashboard
    # -------------------------------------------------------------------------

    def select_category(self, category):
        """Handle when a category is selected from the sidebar."""
        if category == "Dashboard" and self.dashboard_view:
            self.show_dashboard()
            return

        self.current_category = category
        notes = self.model.get_notes(category) or []

        self.view.populate_note_list(notes)
        self.view.set_category_title(category)
        self.view.show_notes()
        if self.dashboard_view:
            self.dashboard_view.hide()

        self._clear_note_selection()

    def show_dashboard(self):
        """Show dashboard stats and hide the note editor."""
        if not self.dashboard_view:
            return

        self.current_category = None
        self.view.set_category_title("Dashboard")
        self.view.show_dashboard()
        self.dashboard_view.show()
        self.update_dashboard_stats()
        self._clear_note_selection()

    def update_dashboard_stats(self):
        """Refresh dashboard data (counts, storage, etc.)."""
        if not self.dashboard_view:
            return

        get_notes = lambda c: self.model.get_notes(c) or []

        stats = {
            "notes_count": len(get_notes("Notes")),
            "contacts_count": len(get_notes("Contacts")),
            "bookmarks_count": len(get_notes("Bookmarks")),
            "copilot_count": len(get_notes("CoPilot")),
            "tasks_completed": getattr(self.model, "count_completed_tasks", lambda: 0)(),
            "storage_percent": getattr(self.model, "get_storage_usage_percent", lambda: 0)(),
        }

        self.dashboard_view.update_stats(**stats)

    # -------------------------------------------------------------------------
    # Note Selection
    # -------------------------------------------------------------------------

    def get_selected_note_id(self):
        """Return the selected note’s ID from the note list."""
        items = self.view.note_list.selectedItems()
        if not items:
            return None
        return items[0].data(0, Qt.ItemDataRole.UserRole)

    def on_note_select(self):
        """Load selected note’s content into view cache."""
        note_id = self.get_selected_note_id()
        if note_id and self.current_category:
            note = self.model.get_note_by_id(self.current_category, note_id)
            if note:
                self.view.current_note_id = note_id
                self.view.current_note_content = note["content"]
                return
        self._clear_note_selection()

    def _clear_note_selection(self):
        """Reset current note state in the view."""
        self.view.current_note_id = None
        self.view.current_note_content = ""

    # -------------------------------------------------------------------------
    # Note Operations (Add / Edit / Delete)
    # -------------------------------------------------------------------------

    def add_note(self):
        if not self.current_category:
            QMessageBox.warning(self.main_window, "Warning", "Please select a category first.")
            return
        self._open_edit_dialog("Add Note", "", self._add_note_callback)

    def edit_note(self):
        note_id = self.get_selected_note_id()
        if not (note_id and self.current_category):
            QMessageBox.warning(self.main_window, "Warning", "Please select a note to edit.")
            return

        note = self.model.get_note_by_id(self.current_category, note_id)
        if not note:
            QMessageBox.warning(self.main_window, "Warning", "Could not find this note.")
            return

        # Store the ID so it persists after editing
        self.view.current_note_id = note_id

        # Open editor dialog
        self._open_edit_dialog(
            "Edit Note",
            note["content"],
            lambda content: self._edit_note_callback(note_id, content)
        )

    def delete_note(self):
        note_id = self.get_selected_note_id()
        if not (note_id and self.current_category):
            QMessageBox.warning(self.main_window, "Warning", "Please select a note to delete.")
            return

        if QMessageBox.question(self.main_window, "Delete", "Are you sure you want to delete this note?") \
           == QMessageBox.StandardButton.Yes:
            self.model.delete_note(self.current_category, note_id)
            self.select_category(self.current_category)
            if self.dashboard_view and self.current_category is None:
                self.update_dashboard_stats()

    # -------------------------------------------------------------------------
    # Private Helpers
    # -------------------------------------------------------------------------

    def _open_edit_dialog(self, title, content, save_callback):
        """Open the editor dialog for adding or editing notes."""
        EditorPanel(self.main_window, title, content, save_callback).exec()

    def _generate_title(self, content, category):
        """Generate a title from note content."""
        raw_title = (content.strip().split("\n")[0][:30]) or "Untitled Note"
        if category == "CoPilot":
            return raw_title or "CoPilot Note"
        return raw_title

    def _add_note_callback(self, content):
        if not content.strip():
            QMessageBox.warning(self.main_window, "Warning", "Note content cannot be empty.")
            return

        title = self._generate_title(content, self.current_category)
        self.model.add_note(self.current_category, title, content)
        self._refresh_notes_view()

    def _edit_note_callback(self, note_id, content):
        # Derive new title from first line of content
        new_title = (content.strip().split('\n')[0][:30]) or "Untitled"

        # Update the model
        self.model.edit_note(self.current_category, note_id, new_title, content)

        # Update the item title directly in the tree (instant UI update)
        for i in range(self.view.note_list.topLevelItemCount()):
            item = self.view.note_list.topLevelItem(i)
            if item.data(0, Qt.ItemDataRole.UserRole) == note_id:
                item.setText(0, new_title)
                break

        # Update the content preview
        self.view.current_note_content = content
        self.view.preview.setPlainText(content)

        # reselect the edited item so selection remains
        _reselect_note_in_list(self.view, note_id)

        # Optionally refresh dashboard
        if self.dashboard_view and self.current_category is None:
            self.update_dashboard_stats()

    def _refresh_notes_view(self):
        """Refresh notes list for current category and optionally dashboard."""
        if not self.current_category:
            return

        notes = self.model.get_notes(self.current_category)
        self.view.populate_note_list(notes)

        if self.dashboard_view and self.current_category is None:
            self.update_dashboard_stats()

    # -------------------------------------------------------------------------
    # Misc
    # -------------------------------------------------------------------------

    def toggle_always_on_top(self, state):
        """Toggle 'Always on Top' window flag."""
        self.main_window.setWindowFlag(Qt.WindowStaysOnTopHint, bool(state))
        self.main_window.show()

    def _reselect_note_in_list(self, note_id):
        """Re-select a note in the list after it has been updated."""
        for i in range(self.view.note_list.topLevelItemCount()):
            item = self.view.note_list.topLevelItem(i)
            if item.data(0, Qt.ItemDataRole.UserRole) == note_id:
                self.view.note_list.setCurrentItem(item)
                break

