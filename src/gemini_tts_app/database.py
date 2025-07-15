# file-path: src/gemini_tts_app/database.py
# version: 4.0
# description: Phiên bản hoàn chỉnh, hỗ trợ mô hình Dự án (một-một), chứa đầy đủ các hàm CRUD cho projects và project_items.

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
        self.conn = None
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.create_tables()
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")

    def create_tables(self):
        """
        Tạo các bảng cần thiết nếu chúng chưa tồn tại.
        """
        if not self.conn:
            return
        
        cursor = self.conn.cursor()
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
        self.conn.commit()
        cursor.close()

    def add_final_title(self, title_text, char_count, word_count):
        """
        Thêm một tiêu đề đã chốt vào cơ sở dữ liệu.
        """
        if not self.conn:
            return False
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = '''INSERT INTO final_titles(title_text, char_count, word_count, timestamp)
                 VALUES(?,?,?,?)'''
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, (title_text, char_count, word_count, timestamp))
            self.conn.commit()
            cursor.close()
            return True
        except sqlite3.Error as e:
            if "UNIQUE constraint failed" in str(e):
                raise ValueError("Tên dự án đã tồn tại.")
            else:
                print(f"Lỗi cập nhật tên dự án: {e}")
            return False

    def add_final_thumbnail(self, thumbnail_text, char_count, word_count, line_count):
        """
        Thêm một text thumbnail đã chốt vào cơ sở dữ liệu.
        """
        if not self.conn:
            return False

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = '''INSERT INTO final_thumbnails(thumbnail_text, char_count, word_count, line_count, timestamp)
                 VALUES(?,?,?,?,?)'''
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, (thumbnail_text, char_count, word_count, line_count, timestamp))
            self.conn.commit()
            cursor.close()
            return True
        except sqlite3.Error as e:
            print(f"Lỗi xóa dự án: {e}")
            return False

    def close(self):
        """
        Đóng kết nối CSDL khi ứng dụng thoát.
        """
        if self.conn:
            self.conn.close()