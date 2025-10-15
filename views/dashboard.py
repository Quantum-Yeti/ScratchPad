from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from views.pong import PongGame
from views.sticky_note import StickyNoteWindow

class DashboardView(QWidget):
    def __init__(self, model):
        super().__init__()

        self.model = model  # Store model reference

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(20)

        title_img = QLabel()
        pixmap = QPixmap("icons/dashboard_img.png")
        pixmap = pixmap.scaledToWidth(200, Qt.SmoothTransformation)
        title_img.setPixmap(pixmap)
        title_img.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_img)

        # Stat panels layout
        stats_layout = QHBoxLayout()
        layout.addLayout(stats_layout)

        stats_layout.addStretch()  # Left spacer

        # Contacts
        self.contacts_stat = self._create_stat_widget("Contacts", "0")
        stats_layout.addWidget(self.contacts_stat)

        # Bookmarks
        self.bookmarks_stat = self._create_stat_widget("Bookmarks", "0")
        stats_layout.addWidget(self.bookmarks_stat)

        # Copilot
        self.copilot_stat = self._create_stat_widget("Copilot", "0")
        stats_layout.addWidget(self.copilot_stat)

        # Notes
        self.notes_stat = self._create_stat_widget("Notes", "0")
        stats_layout.addWidget(self.notes_stat)

        stats_layout.addStretch()  # Right spacer

        # Bottom Buttons layout (Pong + Sticky Note side by side)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        buttons_layout.setAlignment(Qt.AlignCenter)

        self.pong_btn = QPushButton("Play Pong")
        self.pong_btn.setToolTip("Play Pong")
        self.pong_btn.setFixedHeight(40)
        self.pong_btn.clicked.connect(self.launch_pong_game)
        buttons_layout.addWidget(self.pong_btn)

        self.sticky_note_btn = QPushButton("New Sticky Note")
        self.sticky_note_btn.setToolTip("Create a sticky note")
        self.sticky_note_btn.setFixedHeight(40)
        self.sticky_note_btn.clicked.connect(self.launch_new_sticky_note)
        buttons_layout.addWidget(self.sticky_note_btn)

        self.load_sticky_notes_btn = QPushButton("Load Sticky Notes")
        self.load_sticky_notes_btn.setToolTip("Load all existing sticky notes")
        self.load_sticky_notes_btn.setFixedHeight(40)
        self.load_sticky_notes_btn.clicked.connect(self.load_sticky_notes)
        buttons_layout.addWidget(self.load_sticky_notes_btn)

        layout.addLayout(buttons_layout)

        # Keep track of sticky notes windows
        self._sticky_notes = []

    def _create_stat_widget(self, label_text, value_text):
        widget = QWidget()
        v_layout = QVBoxLayout(widget)
        v_layout.setAlignment(Qt.AlignCenter)

        label = QLabel(label_text)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-weight: bold; font-size: 14px;")

        value = QLabel(value_text)
        value.setAlignment(Qt.AlignCenter)
        value.setStyleSheet("font-size: 24px; color: #2E86C1;")

        v_layout.addWidget(label)
        v_layout.addWidget(value)

        widget.value_label = value  # Store reference for dynamic updates
        return widget

    def update_stats(self, *, notes_count=None, contacts_count=None, bookmarks_count=None,
                     copilot_count=None, tasks_completed=None, storage_percent=None):
        if notes_count is not None:
            self.notes_stat.value_label.setText(str(notes_count))
        if contacts_count is not None:
            self.contacts_stat.value_label.setText(str(contacts_count))
        if bookmarks_count is not None:
            self.bookmarks_stat.value_label.setText(str(bookmarks_count))
        if copilot_count is not None:
            self.copilot_stat.value_label.setText(str(copilot_count))

    def launch_pong_game(self):
        self.pong_window = PongGame()
        self.pong_window.show()

    def launch_new_sticky_note(self):
        note_id = self.model.add_sticky_note()
        sticky = StickyNoteWindow(self.model, note_id)
        sticky.show()
        self._sticky_notes.append(sticky)

    def load_sticky_notes(self):
        from PySide6.QtWidgets import QMessageBox
        notes = self.model.get_notes("sticky")
        if not notes:
            QMessageBox.information(self, "Sticky Notes", "No sticky notes found.")
            return

        for note in notes:
            sticky = StickyNoteWindow(self.model, note["id"])
            sticky.show()
            self._sticky_notes.append(sticky)
