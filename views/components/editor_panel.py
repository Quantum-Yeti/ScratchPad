import os
import uuid
import shutil

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout,
    QFileDialog, QMessageBox
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QSignalBlocker


class EditorPanel(QDialog):
    """
    Editor dialog for editing note content (with optional embedded images).
    """

    def __init__(self, parent=None, title="", content="", save_callback=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(500, 400)

        self.save_callback = save_callback
        self._image_refs = []
        self._is_saving = False  # 🟢 Guard to prevent re-entrant opens

        # === Layout ===
        layout = QVBoxLayout(self)

        # --- Text Editor ---
        self.text_edit = QTextEdit()
        self.text_edit.setAcceptRichText(False)
        layout.addWidget(self.text_edit)

        # Load initial content (handles image tags)
        self._render_content_with_images(content)

        # --- Buttons ---
        btn_layout = QHBoxLayout()
        layout.addLayout(btn_layout)

        insert_img_btn = QPushButton("Insert Image")
        insert_img_btn.clicked.connect(self._insert_image)
        btn_layout.addWidget(insert_img_btn)

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_note)
        btn_layout.addWidget(self.save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)


    #IMAGE HANDLING
    def _render_content_with_images(self, content: str):
        """Renders text and [image:...] placeholders."""
        self.text_edit.clear()
        cursor = self.text_edit.textCursor()

        for line in content.splitlines():
            if line.startswith("[image:") and line.endswith("]"):
                img_filename = line[len("[image:"):-1]
                img_path = os.path.join("data", img_filename)

                if os.path.exists(img_path):
                    pixmap = QPixmap(img_path).scaled(
                        50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                    cursor.insertImage(pixmap.toImage())
                    cursor.insertBlock()
                    self._image_refs.append(pixmap)
                else:
                    cursor.insertText(f"[Failed to load image: {img_filename}]\n")
            else:
                cursor.insertText(line + "\n")

    def _insert_image(self):
        """Insert a selected image into the editor."""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg)"
        )
        if not filepath:
            return

        img_folder = "data"
        os.makedirs(img_folder, exist_ok=True)

        ext = os.path.splitext(filepath)[1]
        new_name = f"{uuid.uuid4()}{ext}"
        new_path = os.path.join(img_folder, new_name)

        shutil.copy(filepath, new_path)

        pixmap = QPixmap(new_path).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        cursor = self.text_edit.textCursor()
        cursor.insertImage(pixmap.toImage())
        cursor.insertText(f"\n[image:{new_name}]\n")

        self._image_refs.append(pixmap)


    # SAVE HANDLING
    def save_note(self):
        """Handles Save button logic safely (prevents reopen)."""
        if self._is_saving:
            return  # 🚫 prevent recursion

        self._is_saving = True

        new_content = self.text_edit.toPlainText().strip()
        if not new_content:
            QMessageBox.warning(self, "Empty Note", "Note content cannot be empty.")
            self._is_saving = False
            return

        if callable(self.save_callback):
            try:
                # 🛡️ Block signals from parent note_list to avoid retriggering open_note_editor
                if hasattr(self.parent(), "note_list"):
                    with QSignalBlocker(self.parent().note_list):
                        self.save_callback(new_content)
                else:
                    self.save_callback(new_content)
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save note:\n{e}")
                self._is_saving = False
                return

        # Close normally
        self._is_saving = False
        self.accept()
