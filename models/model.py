import sqlite3
import uuid
import os

class NoteModel:
    def __init__(self, db_path="data/notes.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    completed INTEGER NOT NULL DEFAULT 0
                )
            """)

    def get_notes(self, category):
        with self.conn:
            cursor = self.conn.execute("SELECT id, title, content FROM notes WHERE category = ?", (category,))
            rows = cursor.fetchall()
            return [{'id': row[0], 'title': row[1], 'content': row[2]} for row in rows]

    def get_note_by_id(self, category, note_id):
        with self.conn:
            cursor = self.conn.execute(
                "SELECT id, title, content FROM notes WHERE category = ? AND id = ?",
                (category, note_id)
            )
            row = cursor.fetchone()
            if row:
                return {'id': row[0], 'title': row[1], 'content': row[2]}
            return None

    def add_note(self, category, title, content):
        note_id = str(uuid.uuid4())
        with self.conn:
            self.conn.execute(
                "INSERT INTO notes (id, category, title, content) VALUES (?, ?, ?, ?)",
                (note_id, category, title, content)
            )
        return note_id

    def edit_note(self, category, note_id, title, content):
        with self.conn:
            self.conn.execute(
                "UPDATE notes SET title = ?, content = ? WHERE id = ? AND category = ?",
                (title, content, note_id, category)
            )

    def delete_note(self, category, note_id):
        with self.conn:
            self.conn.execute(
                "DELETE FROM notes WHERE id = ? AND category = ?",
                (note_id, category)
            )

    # Dashboard stats methods:

    def count_notes(self):
        with self.conn:
            cursor = self.conn.execute("SELECT COUNT(*) FROM notes")
            return cursor.fetchone()[0]

    def count_completed_tasks(self):
        with self.conn:
            cursor = self.conn.execute("SELECT COUNT(*) FROM tasks WHERE completed = 1")
            return cursor.fetchone()[0]

    def get_used_storage(self):
        # Proxy: sum of content lengths in all notes
        with self.conn:
            cursor = self.conn.execute("SELECT SUM(LENGTH(content)) FROM notes")
            result = cursor.fetchone()[0]
            return result if result is not None else 0

    #def get_max_storage(self):
        #return 1_000_000

    #def get_storage_usage_percent(self):
        used = self.get_used_storage()
        max_storage = self.get_max_storage()
        percent = int((used / max_storage) * 100) if max_storage else 0
        return min(percent, 100)  # cap at 100%

    # Sticky notes methods

    def add_sticky_note(self):
        sticky_category = "sticky"
        new_id = str(uuid.uuid4())
        with self.conn:
            self.conn.execute(
                "INSERT INTO notes (id, category, title, content) VALUES (?, ?, ?, ?)",
                (new_id, sticky_category, "Sticky Note", "")
            )
        return new_id

    def get_note_content(self, note_id):
        with self.conn:
            cursor = self.conn.execute(
                "SELECT content FROM notes WHERE id = ?",
                (note_id,)
            )
            row = cursor.fetchone()
            return row[0] if row else ""

    def save_note_content(self, note_id, content):
        with self.conn:
            self.conn.execute(
                "UPDATE notes SET content = ? WHERE id = ?",
                (content, note_id)
            )
