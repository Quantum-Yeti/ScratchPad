from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QIcon
from matplotlib import rcParams

from views.components.pong import PongGame
from views.components.sticky_note import StickyNoteWindow
from utils.resource_path_utils import resource_path
from helpers.style_sidebar_button import style_toolbar_button
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


import numpy as np

class AnimatedGraph(FigureCanvas):
    """Responsive, smooth, transparent line graph for the dashboard."""

    def __init__(self, parent=None, update_interval=30):
        self.fig = Figure(figsize=(6, 3), dpi=100)
        self.fig.patch.set_alpha(0.0)  # Transparent
        super().__init__(self.fig)
        self.setParent(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color:transparent;")

        self.axes = self.fig.add_subplot(111)
        self.axes.patch.set_alpha(0.0)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Stats
        self.categories = ["Contacts", "Bookmarks", "CoPilot", "Notes"]
        self.current_values = np.array([0, 0, 0, 0], dtype=float)
        self.target_values = np.array([0, 0, 0, 0], dtype=float)

        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._animate_step)
        self.timer.start(update_interval)  # milliseconds

        self.plot_graph()

    def plot_graph(self):
        self.axes.clear()

        self.fig.patch.set_facecolor('none')
        self.fig.patch.set_alpha(0.0)
        self.axes.patch.set_facecolor('none')

        # Line with markers
        self.axes.plot(self.categories, self.current_values, marker='o',
                       color="#2E86C1", linewidth=2, markersize=6)
        self.axes.fill_between(self.categories, self.current_values, [0] * len(self.categories),
                               color="#2E86C1", alpha=0.1)

        # Remove spines and ticks
        for spine in self.axes.spines.values():
            spine.set_visible(False)
        self.axes.set_xticks(self.categories)
        self.axes.set_yticks([])
        self.axes.grid(False)

        # Labels above points
        max_val = max(max(self.current_values), 10)
        for x, y in zip(self.categories, self.current_values):
            self.axes.text(x, y + max_val * 0.03, f"{y:.0f}", ha='center', va='bottom',
                           fontsize=10, clip_on=False)

        # Set Y limits with padding at bottom
        bottom_padding = max(0.05 * max_val, 1)
        self.axes.set_ylim(-bottom_padding, max_val + max_val * 0.15)

        self.fig.set_constrained_layout(True)
        self.draw()

    def _animate_step(self):
        """Smoothly move current_values towards target_values."""
        diff = self.target_values - self.current_values
        step = diff * 0.1  # smoothing factor
        self.current_values += step
        if np.all(np.abs(diff) < 0.01):
            self.current_values = self.target_values.copy()  # snap to target
        self.plot_graph()

    def update_stats(self, contacts=None, bookmarks=None, copilot=None, notes=None):
        """Set new target values for smooth transition."""
        if contacts is not None:
            self.target_values[0] = contacts
        if bookmarks is not None:
            self.target_values[1] = bookmarks
        if copilot is not None:
            self.target_values[2] = copilot
        if notes is not None:
            self.target_values[3] = notes

class DashboardView(QWidget):
    def __init__(self, model):
        super().__init__()

        self.model = model  # Store model reference

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        title_img = QLabel()
        pixmap = QPixmap(resource_path("icons/dashboard_img.png"))
        pixmap = pixmap.scaledToWidth(200, Qt.SmoothTransformation)
        title_img.setPixmap(pixmap)
        title_img.setAlignment(Qt.AlignCenter)
        title_img.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        title_img.setStyleSheet("margin: 0; padding: 0;")
        layout.addWidget(title_img, alignment=Qt.AlignCenter)

        # Graph stats
        self.graph = AnimatedGraph()
        layout.addWidget(self.graph)

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
        self.copilot_stat = self._create_stat_widget("CoPilot", "0")
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
        self.pong_btn.setIcon(QIcon(resource_path("icons/game.png")))
        self.pong_btn.setFixedHeight(40)
        self.pong_btn.clicked.connect(self.launch_pong_game)
        self.setStyleSheet(style_toolbar_button(self.pong_btn))
        buttons_layout.addWidget(self.pong_btn)

        self.sticky_note_btn = QPushButton("New Sticky Note")
        self.sticky_note_btn.setToolTip("Create a sticky note")
        self.sticky_note_btn.setIcon(QIcon(resource_path("icons/stickynote.png")))
        self.sticky_note_btn.setFixedHeight(40)
        self.sticky_note_btn.clicked.connect(self.launch_new_sticky_note)
        self.setStyleSheet(style_toolbar_button(self.sticky_note_btn))
        buttons_layout.addWidget(self.sticky_note_btn)

        self.load_sticky_notes_btn = QPushButton("Load Sticky Notes")
        self.load_sticky_notes_btn.setToolTip("Load all existing sticky notes")
        self.load_sticky_notes_btn.setFixedHeight(40)
        self.load_sticky_notes_btn.clicked.connect(self.load_sticky_notes)
        self.setStyleSheet(style_toolbar_button(self.load_sticky_notes_btn))
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

    def update_stats(self, *, notes_count=None, contacts_count=None,
                     bookmarks_count=None, copilot_count=None, **kwargs):

        # Update counters
        if notes_count is not None:
            self.notes_stat.value_label.setText(str(notes_count))
        if contacts_count is not None:
            self.contacts_stat.value_label.setText(str(contacts_count))
        if bookmarks_count is not None:
            self.bookmarks_stat.value_label.setText(str(bookmarks_count))
        if copilot_count is not None:
            self.copilot_stat.value_label.setText(str(copilot_count))

        # Update dynamic graph
        self.graph.update_stats(
            contacts=int(self.contacts_stat.value_label.text()),
            bookmarks=int(self.bookmarks_stat.value_label.text()),
            copilot=int(self.copilot_stat.value_label.text()),
            notes=int(self.notes_stat.value_label.text())
        )

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


