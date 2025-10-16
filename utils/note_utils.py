from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTreeWidgetItem


def populate_note_list(note_list, notes):
    """Populate a QTreeWidget with note titles."""
    note_list.blockSignals(True)
    note_list.clear()
    for note in notes:
        item = QTreeWidgetItem([note["title"]])
        item.setData(0, Qt.ItemDataRole.UserRole, note["id"])
        note_list.addTopLevelItem(item)
    note_list.blockSignals(False)


def update_preview(preview_widget, content: str):
    """Safely update the preview pane."""
    preview_widget.setPlainText(content or "")


def update_tree_item_title(note_list, note_id, new_title):
    """Update the title shown in the note tree."""
    for i in range(note_list.topLevelItemCount()):
        item = note_list.topLevelItem(i)
        if item.data(0, Qt.ItemDataRole.UserRole) == note_id:
            item.setText(0, new_title)
            break


def add_note_to_category(note_model, category, title="", content=""):
    """Add a new note to the given category."""
    note_model.add_note(category, title, content)
    return note_model.get_notes(category)


def delete_note_from_category(note_model, category, note_id):
    """Delete a note and return remaining notes."""
    note_model.delete_note(category, note_id)
    return note_model.get_notes(category)
