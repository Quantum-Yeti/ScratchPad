import os
import uuid
import shutil

from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QFileDialog, QMessageBox
from PySide6.QtGui import QPixmap, QTextCursor
from PySide6.QtCore import Qt

class EditorPanel(QDialog):
    def __init__(self, parent=None, title="", content="", save_callback=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(500, 400)
        self.save_callback = save_callback
        self._image_refs = []

        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit()
        self.text_edit.setAcceptRichText(False)
        layout.addWidget(self.text_edit)

        self._render_content_with_images(content)

        btn_layout = QHBoxLayout()
        layout.addLayout(btn_layout)

        insert_img_btn = QPushButton("Insert Image")
        insert_img_btn.clicked.connect(self._insert_image)
        btn_layout.addWidget(insert_img_btn)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

    def _render_content_with_images(self, content):
        self.text_edit.clear()
        cursor = self.text_edit.textCursor()
        lines = content.splitlines()
        for line in lines:
            if line.startswith("[image:") and line.endswith("]"):
                img_filename = line[len("[image:"):-1]
                img_path = os.path.join("data", img_filename)
                if os.path.exists(img_path):
                    pixmap = QPixmap(img_path).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    cursor.insertImage(pixmap.toImage())
                    cursor.insertBlock()
                    self._image_refs.append(pixmap)
                else:
                    cursor.insertText(f"[Failed to load image: {img_filename}]\n")
            else:
                cursor.insertText(line + "\n")

    def _insert_image(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if filepath:
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

    def _save(self):
        new_content = self.text_edit.toPlainText().strip()
        if new_content:
            if self.save_callback:
                self.save_callback(new_content)
            self.accept()
        else:
            QMessageBox.warning(self, "Empty Note", "Note content cannot be empty.")
