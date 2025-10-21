from PySide6.QtWidgets import QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QTimer

class StickyNoteWindow(QMainWindow):
    def __init__(self, model, note_id):
        super().__init__()
        self.setWindowTitle("Sticky Note")
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.resize(350, 350)

        self.model = model
        self.note_id = note_id

        # Central widget with vertical layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Text editor
        self.text_edit = QTextEdit()
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #ffff88;
                font-size: 14px;
                color: #000000;
                padding: 10px;
                border: none;
            }
        """)
        layout.addWidget(self.text_edit)

        # Delete button
        self.delete_btn = QPushButton("Delete Note")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #90D5FF;
                color: white;
                font-weight: bold;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #90D4FF;
            }
        """)
        self.delete_btn.clicked.connect(self.delete_note)
        layout.addWidget(self.delete_btn)

        # Load content
        self.load_content()

        # Save timer
        self.save_timer = QTimer()
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self.save_content)
        self.text_edit.textChanged.connect(self.on_text_changed)

    def load_content(self):
        content = self.model.get_note_content(self.note_id)
        if content is not None:
            self.text_edit.setPlainText(content)

    def save_content(self):
        content = self.text_edit.toPlainText()
        self.model.save_note_content(self.note_id, content)

    def on_text_changed(self):
        self.save_timer.start(1000)

    def delete_note(self):
        self.model.delete_sticky_note(self.note_id)
        self.close()

    def closeEvent(self, event):
        self.save_content()
        super().closeEvent(event)
