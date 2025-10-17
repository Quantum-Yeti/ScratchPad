from PySide6.QtCore import Qt, QSignalBlocker
from views.editor_panel import EditorPanel


def open_note_editor(main_view, item, category):
    """Opens the full EditorPanel popup for editing a note."""
    if item is None or category is None:
        return

    # 🟢 Prevent reopening if already open
    if getattr(main_view, "_editor_open", False):
        return

    note_id = item.data(0, Qt.ItemDataRole.UserRole)
    note = main_view.note_model.get_note_by_id(category, note_id)
    if not note:
        return

    def _title_from_content(content):
        first = content.strip().split("\n")[0] if content.strip() else ""
        return first[:30] if first else "Untitled"

    def _update_tree_item_title(note_id, new_title):
        for i in range(main_view.note_list.topLevelItemCount()):
            it = main_view.note_list.topLevelItem(i)
            if it.data(0, Qt.ItemDataRole.UserRole) == note_id:
                it.setText(0, new_title)
                return

    def save_callback(new_content):
        """Save button handler — no reopen bug."""
        new_title = _title_from_content(new_content)
        main_view.note_model.edit_note(category, note_id, new_title, new_content)
        main_view.current_note_id = note_id
        main_view.current_note_content = new_content
        main_view.preview.setPlainText(new_content)
        _update_tree_item_title(note_id, new_title)

    # Block signals temporarily to prevent re-entry
    with QSignalBlocker(main_view.note_list):
        # 🟩 Mark editor open
        main_view._editor_open = True

        # Create the original EditorPanel dialog
        editor = EditorPanel(
            parent=main_view,
            title=f"Edit Note: {note['title']}",
            content=note["content"],
            save_callback=save_callback
        )

        # When it closes, clear the guard
        editor.finished.connect(lambda _: setattr(main_view, "_editor_open", False))

        # Open editor modally
        editor.exec()
