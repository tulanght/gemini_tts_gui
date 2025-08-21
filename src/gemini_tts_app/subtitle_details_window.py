# file-path: src/gemini_tts_app/subtitle_details_window.py
# version: 1.0
# last-updated: 2025-08-21
# description: Cửa sổ chi tiết để xem nội dung và quản lý hashtag cho phụ đề.

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

class SubtitleDetailsWindow(tk.Toplevel):
    def __init__(self, parent, db_manager, subtitle_id, on_close_callback):
        super().__init__(parent)
        self.db_manager = db_manager
        self.subtitle_id = subtitle_id
        self.on_close_callback = on_close_callback

        self.transient(parent)
        self.grab_set()
        
        self.title("Chi tiết Phụ đề")
        self.geometry("700x600")

        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        self._create_widgets()
        self._load_data()

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(expand=True, fill="both")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1) # Cho phép ô nội dung giãn ra

        # --- Khu vực thông tin & Hashtag ---
        info_frame = ttk.LabelFrame(main_frame, text="Thông tin", padding=10)
        info_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)

        ttk.Label(info_frame, text="Tên video:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.title_label = ttk.Label(info_frame, text="...", wraplength=500, justify="left")
        self.title_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(info_frame, text="Hashtags:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.hashtags_entry = ttk.Entry(info_frame)
        self.hashtags_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(info_frame, text="(Các tag cách nhau bởi dấu phẩy, ví dụ: khoa học, lịch sử)").grid(row=2, column=1, sticky="w", padx=5, pady=2)

        # --- Khu vực Nội dung ---
        content_frame = ttk.LabelFrame(main_frame, text="Nội dung Phụ đề", padding=10)
        content_frame.grid(row=2, column=0, sticky="nsew")
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)

        self.content_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.content_text.pack(expand=True, fill="both")

        # --- Nút bấm ---
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, sticky="e", pady=(10, 0))
        
        ttk.Button(button_frame, text="Lưu thay đổi Hashtag", command=self._save_hashtags, style="Accent.TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Đóng", command=self._on_closing).pack(side="left")

    def _load_data(self):
        details = self.db_manager.get_subtitle_details(self.subtitle_id)
        if not details:
            messagebox.showerror("Lỗi", "Không thể tải chi tiết phụ đề.", parent=self)
            self.destroy()
            return
        
        self.title_label.config(text=details['video_title'])
        
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete("1.0", tk.END)
        self.content_text.insert("1.0", details['content'])
        self.content_text.config(state=tk.DISABLED)

        hashtags = self.db_manager.get_hashtags_for_subtitle(self.subtitle_id)
        self.hashtags_entry.delete(0, tk.END)
        self.hashtags_entry.insert(0, ", ".join(hashtags))

    def _save_hashtags(self):
        # Lấy các tag từ ô nhập, chuyển thành chữ thường, xóa khoảng trắng và loại bỏ các tag rỗng
        tags_str = self.hashtags_entry.get()
        hashtags = [tag.strip().lower() for tag in tags_str.split(',') if tag.strip()]
        
        if self.db_manager.update_hashtags_for_subtitle(self.subtitle_id, hashtags):
            messagebox.showinfo("Thành công", "Đã cập nhật hashtag thành công!", parent=self)
        else:
            messagebox.showerror("Lỗi", "Không thể cập nhật hashtag vào CSDL.", parent=self)

    def _on_closing(self):
        self.on_close_callback()
        self.destroy()