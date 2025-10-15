from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QSizePolicy, QPushButton
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from views.pong import PongGame

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()

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

        #Left
        stats_layout.addStretch()

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

        #Right
        stats_layout.addStretch()

        #Pong button
        self.pong_btn = QPushButton("Play Pong")
        self.pong_btn.setToolTip("Play Pong")
        self.pong_btn.setFixedHeight(40)
        self.pong_btn.clicked.connect(self.launch_pong_game)
        layout.addWidget(self.pong_btn, alignment=Qt.AlignCenter)

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
