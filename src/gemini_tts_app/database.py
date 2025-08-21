# file-path: src/gemini_tts_app/database.py
# version: 4.3
# last-updated: 2025-07-21
# description: Bổ sung hàm get_project_names để hỗ trợ logic đồng bộ thông minh.

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
        self._create_subtitles_table() # THÊM DÒNG NÀY
        self._run_migrations()

    def get_connection(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            print(f"Lỗi kết nối CSDL: {e}")
            return None

    def _run_migrations(self):
        """Kiểm tra và áp dụng các thay đổi cấu trúc cho CSDL đã tồn tại."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(projects)")
                columns = [info['name'] for info in cursor.fetchall()]
                if 'source_group' not in columns:
                    cursor.execute("ALTER TABLE projects ADD COLUMN source_group TEXT")
                if 'status' not in columns:
                    cursor.execute("ALTER TABLE projects ADD COLUMN status TEXT DEFAULT 'Chưa làm'")
                conn.commit()
        except sqlite3.Error as e:
            print(f"Lỗi trong quá trình di chuyển CSDL: {e}")

    def create_tables(self):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS projects (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        source_group TEXT,
                        status TEXT DEFAULT 'Chưa làm'
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS project_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_id INTEGER NOT NULL,
                        type TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
                        UNIQUE(project_id, type)
                    )
                """)
                conn.commit()
        except sqlite3.Error as e:
            print(f"Lỗi tạo bảng: {e}")
            
        # THÊM CÁC LỆNH DƯỚI ĐÂY:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Bảng chứa tất cả các hashtag duy nhất
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS hashtags (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tag_name TEXT UNIQUE NOT NULL
                    )
                """)
                # Bảng liên kết giữa phụ đề và hashtag (quan hệ nhiều-nhiều)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS subtitle_hashtag_link (
                        subtitle_id INTEGER,
                        hashtag_id INTEGER,
                        FOREIGN KEY (subtitle_id) REFERENCES downloaded_subtitles (id) ON DELETE CASCADE,
                        FOREIGN KEY (hashtag_id) REFERENCES hashtags (id) ON DELETE CASCADE,
                        PRIMARY KEY (subtitle_id, hashtag_id)
                    )
                """)
                conn.commit()
        except sqlite3.Error as e:
            print(f"Lỗi khi tạo bảng hashtags hoặc bảng liên kết: {e}")

    # hotfix v4.7.1 - 2025-07-19 - Sửa lỗi không lấy cột 'status'.
    def get_all_projects(self):
        """Lấy tất cả các dự án bao gồm cả trạng thái."""
        sql = "SELECT id, name, timestamp, status FROM projects ORDER BY timestamp DESC"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Lỗi lấy danh sách dự án: {e}")
            return []

    def update_project_status(self, project_id, new_status):
        sql = "UPDATE projects SET status = ? WHERE id = ?"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (new_status, project_id))
                conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Lỗi cập nhật trạng thái dự án: {e}")
            return False
    # hotfix - 2025-07-31 - Thêm hàm để lấy dự án theo nhóm
    def get_projects_by_group(self, group_name):
        """Lấy tất cả các dự án thuộc về một nhóm cụ thể."""
        sql = "SELECT id, name, timestamp, status FROM projects WHERE source_group = ? ORDER BY timestamp DESC"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (group_name,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Lỗi khi lấy dự án theo nhóm '{group_name}': {e}")
            return []
    # --- Các hàm còn lại giữ nguyên không thay đổi ---
    def create_project(self, name, source_group=None):
        sql = "INSERT OR IGNORE INTO projects (name, source_group) VALUES (?, ?)"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (name, source_group))
                cursor.execute(sql, (name, source_group))
                conn.commit()
                cursor.execute("SELECT id FROM projects WHERE name = ?", (name,))
                project = cursor.fetchone()
                return project['id'] if project else None
        except sqlite3.Error as e:
            print(f"Lỗi tạo/lấy dự án: {e}")
            return None
    # hotfix v4.3.1 - 2025-07-21 - Thêm hàm để lấy danh sách tên tất cả các dự án.
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

    def get_project_names(self):
        sql = "SELECT name FROM projects"
        try:
            with self.get_connection() as conn:
                return {row['name'] for row in conn.cursor().execute(sql).fetchall()}
        except sqlite3.Error as e:
            print(f"Lỗi khi lấy tên các dự án: {e}")
            return set()

    def delete_projects_by_group(self, group_name):
        sql = "DELETE FROM projects WHERE source_group = ?"
        try:
            with self.get_connection() as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                conn.cursor().execute(sql, (group_name,))
                conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Lỗi xóa các dự án theo nhóm: {e}")
            return False
    
    # hotfix - 2025-07-31 - Thêm hàm để sửa chữa dữ liệu source_group bị thiếu
    def update_project_source_group(self, project_name, source_group):
        """Cập nhật cột source_group cho một dự án dựa trên tên của nó."""
        sql = "UPDATE projects SET source_group = ? WHERE name = ?"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (source_group, project_name))
                conn.commit()
                return cursor.rowcount > 0 # Trả về True nếu có hàng được cập nhật
        except sqlite3.Error as e:
            print(f"Lỗi khi cập nhật source_group cho '{project_name}': {e}")
            return False
        
    # hotfix - 2025-07-31 - Thêm hàm để cập nhật source_group bằng ID
    def update_project_source_group_by_id(self, project_id, source_group):
        """Cập nhật cột source_group cho một dự án dựa trên ID của nó."""
        sql = "UPDATE projects SET source_group = ? WHERE id = ?"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (source_group, project_id))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Lỗi khi cập nhật source_group cho ID '{project_id}': {e}")
            return False
        
    def _create_subtitles_table(self):
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS downloaded_subtitles (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            video_title TEXT,
                            youtube_url TEXT,
                            language TEXT,
                            is_auto_generated BOOLEAN,
                            content TEXT,
                            download_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    conn.commit()
            except sqlite3.Error as e:
                print(f"Lỗi tạo bảng phụ đề: {e}")

    def add_subtitle(self, data):
        sql = """
            INSERT INTO downloaded_subtitles 
            (video_title, youtube_url, language, is_auto_generated, content) 
            VALUES (?, ?, ?, ?, ?)
        """
        try:
            with self.get_connection() as conn:
                conn.cursor().execute(sql, (
                    data['video_title'],
                    data['youtube_url'],
                    data['language'],
                    data['is_auto_generated'],
                    data['content']
                ))
                conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Lỗi thêm phụ đề vào CSDL: {e}")
            return False
    
    # hotfix - 2025-08-21 - Sửa lỗi IndexError bằng cách SELECT tất cả các cột
    def get_all_subtitles(self):
        """Lấy tất cả các phụ đề đã lưu, sắp xếp theo ngày tải mới nhất."""
        # SỬA LẠI CÂU LỆNH SQL ĐỂ LẤY TẤT CẢ CÁC CỘT
        sql = "SELECT * FROM downloaded_subtitles ORDER BY download_timestamp DESC"
        try:
            with self.get_connection() as conn:
                return conn.cursor().execute(sql).fetchall()
        except sqlite3.Error as e:
            print(f"Lỗi lấy danh sách phụ đề: {e}")
            return []
        
    # Thêm toàn bộ các hàm này vào cuối file database.py
    def get_hashtags_for_subtitle(self, subtitle_id):
        """Lấy danh sách các hashtag của một phụ đề cụ thể."""
        sql = """
            SELECT h.tag_name FROM hashtags h
            JOIN subtitle_hashtag_link shl ON h.id = shl.hashtag_id
            WHERE shl.subtitle_id = ?
        """
        try:
            with self.get_connection() as conn:
                return [row['tag_name'] for row in conn.cursor().execute(sql, (subtitle_id,)).fetchall()]
        except sqlite3.Error as e:
            print(f"Lỗi khi lấy hashtags cho phụ đề {subtitle_id}: {e}")
            return []

    def update_hashtags_for_subtitle(self, subtitle_id, hashtags):
        """Cập nhật toàn bộ danh sách hashtag cho một phụ đề."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Xóa tất cả các liên kết hashtag cũ của phụ đề này
                cursor.execute("DELETE FROM subtitle_hashtag_link WHERE subtitle_id = ?", (subtitle_id,))
                
                for tag_name in hashtags:
                    # Thêm hashtag mới vào bảng hashtags nếu nó chưa tồn tại
                    cursor.execute("INSERT OR IGNORE INTO hashtags (tag_name) VALUES (?)", (tag_name,))
                    # Lấy id của hashtag đó
                    cursor.execute("SELECT id FROM hashtags WHERE tag_name = ?", (tag_name,))
                    hashtag_id = cursor.fetchone()['id']
                    # Tạo liên kết mới
                    cursor.execute("INSERT INTO subtitle_hashtag_link (subtitle_id, hashtag_id) VALUES (?, ?)", (subtitle_id, hashtag_id))
                conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Lỗi khi cập nhật hashtags cho phụ đề {subtitle_id}: {e}")
            return False

    def get_subtitles_by_hashtag(self, tag_name):
        """Lấy danh sách các phụ đề được gán một hashtag cụ thể."""
        sql = """
            SELECT ds.* FROM downloaded_subtitles ds
            JOIN subtitle_hashtag_link shl ON ds.id = shl.subtitle_id
            JOIN hashtags h ON shl.hashtag_id = h.id
            WHERE h.tag_name LIKE ?
            ORDER BY ds.download_timestamp DESC
        """
        try:
            with self.get_connection() as conn:
                # Dùng % để tìm kiếm gần đúng
                return conn.cursor().execute(sql, ('%' + tag_name + '%',)).fetchall()
        except sqlite3.Error as e:
            print(f"Lỗi khi tìm phụ đề theo hashtag '{tag_name}': {e}")
            return []

    def get_subtitle_details(self, subtitle_id):
        """Lấy chi tiết đầy đủ của một phụ đề, bao gồm cả nội dung."""
        sql = "SELECT * FROM downloaded_subtitles WHERE id = ?"
        try:
            with self.get_connection() as conn:
                return conn.cursor().execute(sql, (subtitle_id,)).fetchone()
        except sqlite3.Error as e:
            print(f"Lỗi khi lấy chi tiết phụ đề {subtitle_id}: {e}")
            return None