def extract_title_from_content(content: str) -> str:
    """Extracts the first non-empty line as title."""
    lines = content.strip().split("\n")
    return lines[0].strip() if lines else "Untitled"


def safe_content(content: str) -> str:
    """Ensures the content is a valid string."""
    return content if isinstance(content, str) else ""


def update_note_model(note_model, category, note_id, new_title, new_content):
    """Update a note inside the model."""
    note_model.update_note(category, note_id, new_title, new_content)
