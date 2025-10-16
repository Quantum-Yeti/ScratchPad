from PySide6.QtCore import Qt

def _reselect_note_in_list(view, note_id):
    """
    Reselect a note in the given view’s QTreeWidget based on its note_id.
    Keeps selection stable after edits or reloads.
    """
    if not hasattr(view, "note_list"):
        return

    note_list = view.note_list
    for i in range(note_list.topLevelItemCount()):
        item = note_list.topLevelItem(i)
        if item.data(0, Qt.ItemDataRole.UserRole) == note_id:
            note_list.setCurrentItem(item)
            note_list.scrollToItem(item)
            return

