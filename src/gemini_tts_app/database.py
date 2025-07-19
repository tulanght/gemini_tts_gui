# file-path: src/gemini_tts_app/database.py
# version: 4.4
# last-updated: 2025-07-18
# description: Thêm cột 'source_group' và các hàm hỗ trợ để liên kết dự án với nhóm nguồn.
import sqlite3
import os
from datetime import datetime
from appdirs import user_data_dir
from tkinter import messagebox

from .constants import APP_NAME as APP_NAME_CONST, APP_AUTHOR as APP_AUTHOR_CONST

class DatabaseManager:
    def __init__(self, db_name="gcs_projects_final.db"):
        data_dir = user_data_dir(APP_NAME_CONST, APP_AUTHOR_CONST)
        os.makedirs(data_dir, exist_ok=True)
        self.db_path = os.path.join(data_dir, db_name)
        self.create_tables()

    def get_connection(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            print(f"Lỗi kết nối CSDL: {e}")
            return None
    # hotfix v4.4.1 - 2025-07-18 - Thêm cột source_group vào bảng projects.
    def create_tables(self):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS projects (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        source_group TEXT -- Cột mới để lưu tên nhóm nguồn
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS project_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_id INTEGER NOT NULL,
                        type TEXT NOT NULL, -- 'Story', 'Title', 'Thumbnail'
                        content TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
                        UNIQUE(project_id, type)
                    )
                """)
                conn.commit()
        except sqlite3.Error as e:
            print(f"Lỗi tạo bảng: {e}")
    # hotfix v4.4.2 - 2025-07-18 - Cập nhật hàm create_project để lưu source_group.
    def create_project(self, name, source_group=None):
        """Tạo một dự án mới và trả về ID của nó, có thể kèm theo nhóm nguồn."""
        sql = "INSERT OR IGNORE INTO projects (name, source_group) VALUES (?, ?)"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (name, source_group))
                conn.commit()
                cursor.execute("SELECT id FROM projects WHERE name = ?", (name,))
                project = cursor.fetchone()
                return project['id'] if project else None
        except sqlite3.Error as e:
            print(f"Lỗi tạo/lấy dự án: {e}")
            return None

    def add_or_update_item(self, project_id, item_type, content):
        sql = """
            INSERT INTO project_items (project_id, type, content) VALUES (?, ?, ?)
            ON CONFLICT(project_id, type) DO UPDATE SET 
            content = excluded.content,
            timestamp = CURRENT_TIMESTAMP;
        """
        try:
            with self.get_connection() as conn:
                conn.cursor().execute(sql, (project_id, item_type, content))
                conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Lỗi thêm/cập nhật thành phần: {e}")
            return False

    def get_all_projects(self):
        sql = "SELECT id, name, timestamp FROM projects ORDER BY timestamp DESC"
        try:
            with self.get_connection() as conn:
                return conn.cursor().execute(sql).fetchall()
        except sqlite3.Error as e:
            print(f"Lỗi lấy danh sách dự án: {e}")
            return []
    # hotfix v4.3.1 - 2025-07-18 - Thêm hàm để lấy danh sách tên tất cả các dự án.
    def get_project_names(self):
        """Lấy một tập hợp (set) chứa tên của tất cả các dự án hiện có."""
        sql = "SELECT name FROM projects"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                # Trả về một set để việc kiểm tra 'in' hiệu quả hơn
                return {row['name'] for row in cursor.fetchall()}
        except sqlite3.Error as e:
            print(f"Lỗi khi lấy tên các dự án: {e}")
            return set()
    def get_items_for_project(self, project_id):
        sql = "SELECT id, type, content FROM project_items WHERE project_id = ?"
        try:
            with self.get_connection() as conn:
                return conn.cursor().execute(sql, (project_id,)).fetchall()
        except sqlite3.Error as e:
            print(f"Lỗi lấy các thành phần của dự án: {e}")
            return []

    def update_project_name(self, project_id, new_name):
        sql = "UPDATE projects SET name = ? WHERE id = ?"
        try:
            with self.get_connection() as conn:
                conn.cursor().execute(sql, (new_name, project_id))
                conn.commit()
            return True
        except sqlite3.Error as e:
            if "UNIQUE constraint failed" in str(e):
                raise ValueError("Tên dự án đã tồn tại.")
            else:
                print(f"Lỗi cập nhật tên dự án: {e}")
            return False

    def update_project_item(self, item_id, new_content):
        """Hàm quan trọng còn thiếu: Cập nhật nội dung của một thành phần."""
        sql = "UPDATE project_items SET content = ? WHERE id = ?"
        try:
            with self.get_connection() as conn:
                conn.cursor().execute(sql, (new_content, item_id))
                conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Lỗi cập nhật thành phần: {e}")
            return False
            
    def delete_project(self, project_id):
        sql = "DELETE FROM projects WHERE id = ?"
        try:
            with self.get_connection() as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                conn.cursor().execute(sql, (project_id,))
                conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Lỗi xóa dự án: {e}")
            return False
        
    # hotfix v4.4.3 - 2025-07-18 - Thêm hàm xóa tất cả các dự án thuộc một nhóm.
    def delete_projects_by_group(self, group_name):
        """Xóa tất cả các dự án được tạo từ một nhóm nguồn cụ thể."""
        sql = "DELETE FROM projects WHERE source_group = ?"
        try:
            with self.get_connection() as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                cursor = conn.cursor()
                cursor.execute(sql, (group_name,))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Lỗi xóa các dự án theo nhóm: {e}")
            return False