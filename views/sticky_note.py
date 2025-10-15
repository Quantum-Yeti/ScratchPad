from PySide6.QtWidgets import QMainWindow, QTextEdit
from PySide6.QtCore import Qt, QTimer

class StickyNoteWindow(QMainWindow):
    def __init__(self, model, note_id):
        super().__init__()
        self.setWindowTitle("Sticky Note")
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.resize(350, 350)

        self.model = model
        self.note_id = note_id

        # Text editor for note content
        self.text_edit = QTextEdit()
        self.setCentralWidget(self.text_edit)

        # Apply styling for sticky note appearance
        self.setStyleSheet("""
            QTextEdit {
                background-color: #ffff88;
                font-size: 14px;
                color: #000000;
                padding: 10px;
                border: none;
            }
        """)

        # Load existing content from the model (if any)
        self.load_content()

        # Timer to delay saving after typing stops (debounce)
        self.save_timer = QTimer()
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self.save_content)

        # Connect text changes to restart save timer
        self.text_edit.textChanged.connect(self.on_text_changed)

    def load_content(self):
        """Load the note content from the model into the text editor."""
        content = self.model.get_note_content(self.note_id)
        if content is not None:
            self.text_edit.setPlainText(content)

    def save_content(self):
        """Save the current content from the text editor into the model."""
        content = self.text_edit.toPlainText()
        self.model.save_note_content(self.note_id, content)

    def on_text_changed(self):
        """Restart the save timer when the user changes the text."""
        self.save_timer.start(1000)  # 1 second delay after last keystroke

    def closeEvent(self, event):
        """Ensure content is saved immediately when the window closes."""
        self.save_content()
        super().closeEvent(event)
