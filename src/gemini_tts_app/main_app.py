# file-path: src/gemini_tts_app/main_app.py
# version: 7.0
# last-updated: 2025-07-23
# description: Hoàn tất tái cấu trúc. main_app.py giờ chỉ đóng vai trò điều phối.

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import os
import sys

from .settings_manager import load_settings, NUM_API_KEYS
from .constants import APP_NAME
from .utils import get_resource_path
from .database import DatabaseManager

# --- IMPORT TẤT CẢ CÁC MODULE TAB ---
from .tts_tab import TTSTab
from .library_tab import LibraryTab
from .editorial_assistant_tab import EditorialAssistantTab
from .long_form_composer_tab import LongFormComposerTab
from .settings_tab import SettingsTab

class TkinterLogHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_widget.configure(state='normal')
            self.text_widget.insert(tk.END, msg + '\n')
            self.text_widget.configure(state='disabled')
            self.text_widget.yview(tk.END)
        self.text_widget.after_idle(append)

class TTSApp:
    # hotfix - 2025-07-24 - Sắp xếp lại thứ tự pack để log và status bar luôn hiển thị
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} v1.9.0")
        self.root.geometry("950x850")

        style = ttk.Style(self.root)
        self.STATUS_COLOR_INCOMPLETE = "#FFF9C4"
        self.STATUS_COLOR_COMPLETE = "#C8E6C9"
        style.configure("Incomplete.TFrame", background=self.STATUS_COLOR_INCOMPLETE)
        style.configure("Complete.TFrame", background=self.STATUS_COLOR_COMPLETE)

        self.db_manager = DatabaseManager()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.settings = load_settings()
        
        # Biến dùng chung được quản lý bởi main_app
        self.api_key_vars = [tk.StringVar(value=self.settings.get(f"api_key_{i+1}", "")) for i in range(NUM_API_KEYS)]
        self.api_label_vars = [tk.StringVar(value=self.settings.get(f"label_{i+1}", f"API Key {i+1}")) for i in range(NUM_API_KEYS)]
        
        self.active_project_id = None
        self.active_project_name = None
        self.active_project_status = tk.StringVar(value="Trạng thái: Chưa có dự án nào đang hoạt động.")
        
        self._set_window_icon()
        
        # --- SẮP XẾP LẠI BỐ CỤC CHÍNH ---
        # 1. Đặt các thành phần ở dưới cùng TRƯỚC
        self.status_bar_frame = ttk.Frame(root, padding=5)
        self.status_bar_frame.pack(side="bottom", fill="x")
        status_label = ttk.Label(self.status_bar_frame, textvariable=self.active_project_status, anchor="w")
        status_label.pack(fill="x", expand=True)
        
        self.setup_ui_logging(root) # Hàm này sẽ tự pack log frame vào bottom

        # 2. Đặt Notebook (khu vực tab) vào không gian còn lại
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=5)

        # --- KHỞI TẠO VÀ THÊM TẤT CẢ CÁC TAB (DẠNG MODULE) ---
        self.tts_tab = TTSTab(self.notebook, self)
        self.library_tab = LibraryTab(self.notebook, self.db_manager, self)
        self.editorial_assistant_tab = EditorialAssistantTab(self.notebook, self.db_manager, self)
        self.composer_tab = LongFormComposerTab(self.notebook, self.db_manager, self)
        self.settings_tab = SettingsTab(self.notebook, self)
        
        self.notebook.add(self.tts_tab, text="🎙️ Text-to-Speech")
        self.notebook.add(self.library_tab, text="📖 Thư viện")
        self.notebook.add(self.editorial_assistant_tab, text="✍️ Trợ lý Biên tập")
        self.notebook.add(self.composer_tab, text="📝 Soạn Truyện Dài")
        self.notebook.add(self.settings_tab, text="⚙️ Cài đặt")

    def get_active_api_keys(self):
        active_keys = []
        for i in range(NUM_API_KEYS):
            key = self.api_key_vars[i].get().strip()
            if key:
                active_keys.append({
                    "key": key,
                    "label": self.api_label_vars[i].get().strip() or f"API Key {i+1}"
                })
        return active_keys

    def setup_ui_logging(self, parent):
        log_frame = ttk.LabelFrame(parent, text="Nhật ký Hoạt động", padding=5)
        log_frame.pack(side="bottom", fill="x", padx=10, pady=(0, 10))
        log_text = tk.Text(log_frame, height=5, wrap=tk.WORD, state="disabled", font=("Segoe UI", 9))
        log_text.pack(expand=True, fill="x")
        handler = TkinterLogHandler(log_text)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(handler)

    def _check_and_update_project_status_color(self):
        if not self.active_project_id:
            self.status_bar_frame.configure(style="TFrame")
            return
        items = self.db_manager.get_items_for_project(self.active_project_id)
        types_found = {item['type'] for item in items}
        required_items = {'Story', 'Title', 'Thumbnail', 'Hook'}
        if required_items.issubset(types_found):
            self.status_bar_frame.configure(style="Complete.TFrame")
        else:
            self.status_bar_frame.configure(style="Incomplete.TFrame")

    def set_active_project(self, project_id, project_name):
        self.active_project_id = project_id
        self.active_project_name = project_name
        self.active_project_status.set(f"Trạng thái: Đang làm việc trên dự án '{self.active_project_name}' (ID: {self.active_project_id})")
        
        items = self.db_manager.get_items_for_project(project_id)
        story_content = ""
        for item in items:
            if item['type'] == 'Story':
                story_content = item['content']
                break
        self.composer_tab.load_story_from_project(story_content, project_name)
        
        self._check_and_update_project_status_color()
        self.notebook.select(self.composer_tab)
        self.log_message(f"Đã kích hoạt dự án: '{project_name}'")

    def send_story_to_tts(self, project_id):
        items = self.db_manager.get_items_for_project(project_id)
        story_content = ""
        for item in items:
            if item['type'] == 'Story':
                story_content = item['content']
                break
        if story_content:
            self.tts_tab.set_script_content(story_content)
            self.notebook.select(self.tts_tab)
            self.log_message(f"Đã tải nội dung truyện từ dự án ID {project_id} sang tab TTS.")
        else:
            messagebox.showwarning("Không có Nội dung", "Dự án này chưa có nội dung truyện.", parent=self.root)

    def on_closing(self):
        if hasattr(self.composer_tab, 'is_monitoring_clipboard') and self.composer_tab.is_monitoring_clipboard:
            self.composer_tab.is_monitoring_clipboard = False
        self.root.destroy()

    def log_message(self, message: str):
        logging.info(message)
    
    def _set_window_icon(self):
        try:
            if sys.platform.startswith('win'):
                icon_path = get_resource_path("icons/app_icon.ico")
                if os.path.exists(icon_path): self.root.iconbitmap(icon_path)
        except Exception as e:
            self.log_message(f"Error setting window icon: {e}")