# src/gemini_tts_app/database.py
# Module quản lý cơ sở dữ liệu SQLite cho Trợ lý Biên Tập

import sqlite3
import os
from datetime import datetime
from appdirs import user_data_dir

# Sử dụng appdirs để có đường dẫn lưu trữ nhất quán và phù hợp với HĐH
from .constants import APP_NAME as APP_NAME_CONST, APP_AUTHOR as APP_AUTHOR_CONST

class DatabaseManager:
    def __init__(self, db_name="assistant_data.db"):
        """
        Khởi tạo và kết nối tới cơ sở dữ liệu.
        CSDL sẽ được lưu trong thư mục dữ liệu của ứng dụng.
        """
        data_dir = user_data_dir(APP_NAME_CONST, APP_AUTHOR_CONST)
        os.makedirs(data_dir, exist_ok=True)
        self.db_path = os.path.join(data_dir, db_name)
        # Sử dụng context manager thay vì giữ kết nối mở
    
    def get_connection(self):
        """Tạo và trả về một kết nối cơ sở dữ liệu mới."""
        try:
            conn = sqlite3.connect(self.db_path)
            # Giúp trả về các dòng dưới dạng dict thay vì tuple (dễ làm việc hơn)
            conn.row_factory = sqlite3.Row 
            return conn
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return None

    def create_tables(self):
        """
        Tạo các bảng cần thiết nếu chúng chưa tồn tại.
        Hàm này sẽ được gọi một lần khi ứng dụng khởi động.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Bảng cho các tiêu đề đã chốt
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS final_titles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title_text TEXT NOT NULL,
                    char_count INTEGER NOT NULL,
                    word_count INTEGER NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            
            # Bảng cho các text thumbnail đã chốt
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS final_thumbnails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    thumbnail_text TEXT NOT NULL,
                    char_count INTEGER NOT NULL,
                    word_count INTEGER NOT NULL,
                    line_count INTEGER NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            conn.commit()

    def add_final_title(self, title_text, char_count, word_count):
        """Thêm một tiêu đề đã chốt vào cơ sở dữ liệu."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = '''INSERT INTO final_titles(title_text, char_count, word_count, timestamp)
                 VALUES(?,?,?,?)'''
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (title_text, char_count, word_count, timestamp))
                conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Failed to add title: {e}")
            return False

    def add_final_thumbnail(self, thumbnail_text, char_count, word_count, line_count):
        """Thêm một text thumbnail đã chốt vào cơ sở dữ liệu."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = '''INSERT INTO final_thumbnails(thumbnail_text, char_count, word_count, line_count, timestamp)
                 VALUES(?,?,?,?,?)'''
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (thumbnail_text, char_count, word_count, line_count, timestamp))
                conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Failed to add thumbnail text: {e}")
            return False

    # --- CÁC HÀM MỚI ĐỂ QUẢN LÝ DỮ LIỆU ---

    def get_all_data(self):
        """Lấy tất cả dữ liệu từ cả hai bảng, gộp lại và sắp xếp."""
        sql = """
            SELECT id, 'Tiêu đề' as type, title_text as content, timestamp FROM final_titles
            UNION ALL
            SELECT id, 'Thumbnail' as type, thumbnail_text as content, timestamp FROM final_thumbnails
            ORDER BY timestamp DESC;
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Failed to get all data: {e}")
            return []

    def update_data(self, item_id, item_type, new_content):
        """Cập nhật một mục dựa vào ID và loại (Tiêu đề/Thumbnail)."""
        table = "final_titles" if item_type == "Tiêu đề" else "final_thumbnails"
        column = "title_text" if item_type == "Tiêu đề" else "thumbnail_text"
        
        sql = f"UPDATE {table} SET {column} = ? WHERE id = ?"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (new_content, item_id))
                conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Failed to update {item_type}: {e}")
            return False

    def delete_data(self, item_id, item_type):
        """Xóa một mục dựa vào ID và loại (Tiêu đề/Thumbnail)."""
        table = "final_titles" if item_type == "Tiêu đề" else "final_thumbnails"
        sql = f"DELETE FROM {table} WHERE id = ?"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (item_id,))
                conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Failed to delete {item_type}: {e}")
            return False