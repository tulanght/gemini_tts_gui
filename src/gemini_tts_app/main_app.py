# main_app.py - show_thumbnail_preview
# v2.0 - 2025-06-24: Refactored to use ThumbnailPreviewWindow class
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import os
import sys
import platform
import subprocess
import datetime
import traceback
import re
import time
import logging

import json
try:
    import docx
except ImportError:
    docx = None
try:
    import pyperclip
except ImportError:
    pyperclip = None
from .thumbnail_preview import ThumbnailPreviewWindow
from .tts_logic import generate_tts_audio_multithreaded
from .settings_manager import save_settings, load_settings, NUM_API_KEYS
from .constants import (
    DEFAULT_VOICE, MIN_TEMPERATURE, MAX_TEMPERATURE,
    APP_NAME, APP_VERSION, PREDEFINED_READING_STYLES,
    GEMINI_TTS_VOICES_DETAILED, DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P, MIN_TOP_P, MAX_TOP_P,
    TITLE_CHAR_LIMIT_GOOD_MIN, TITLE_CHAR_LIMIT_GOOD_MAX, TITLE_CHAR_LIMIT_MAX,
    COLOR_OK, COLOR_WARN, COLOR_ERROR, COLOR_NORMAL
)
from .utils import get_resource_path
from .database import DatabaseManager

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
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("950x850")

        style = ttk.Style(self.root)
        style.layout("thin.Horizontal.TProgressbar",
                    [('thin.Horizontal.TProgressbar.trough',
                        {'children': [('thin.Horizontal.TProgressbar.pbar',
                                        {'side': 'left', 'sticky': 'ns'})],
                        'sticky': 'nswe'})])
        style.configure("thin.Horizontal.TProgressbar", thickness=4, background=COLOR_OK, troughcolor='#E0E0E0')

        self.db_manager = DatabaseManager()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.settings = load_settings()
        
        self.voice_display_list = [f"{v['name']} ({v['gender']}) - {v['description']}" for v in GEMINI_TTS_VOICES_DETAILED]
        self.voice_name_list = [v['name'] for v in GEMINI_TTS_VOICES_DETAILED]
        
        self.api_key_vars = [tk.StringVar(value=self.settings.get(f"api_key_{i+1}", "")) for i in range(NUM_API_KEYS)]
        self.api_label_vars = [tk.StringVar(value=self.settings.get(f"label_{i+1}", f"API Key {i+1}")) for i in range(NUM_API_KEYS)]
        self.selected_voice_name = tk.StringVar(value=self.settings.get("default_voice", DEFAULT_VOICE))
        self.selected_voice_display = tk.StringVar() 
        self.temperature_var = tk.DoubleVar(value=self.settings.get("temperature", DEFAULT_TEMPERATURE))
        self.top_p_var = tk.DoubleVar(value=self.settings.get("top_p", DEFAULT_TOP_P))
        self.words_per_chunk_var = tk.IntVar(value=self.settings.get("max_words_per_part", 1000))
        self.output_dir_var = tk.StringVar(value=self.settings.get("save_dir", os.path.expanduser("~")))
        self.story_name_var = tk.StringVar(value="MyStory")
        self.reading_style_prompt_var = tk.StringVar(value=PREDEFINED_READING_STYLES[0])
        self.last_saved_output_dir = None
        self.thread_status_labels = []
        self._full_options_text = []
        self.continuation_prompt_var = tk.StringVar()
        self.floating_panel = None
        self.clipboard_monitoring_thread = None
        self.is_monitoring_clipboard = False
        self.last_clipboard_content = ""
      
        self._set_window_icon()
        self.notebook = ttk.Notebook(root)
        
        self.main_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.main_tab, text="Text-to-Speech")
        self.create_main_tab_widgets()
        
        self.assistant_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.assistant_tab, text="Trợ Lý Biên Tập")
        self.create_assistant_tab_widgets()

        self.composer_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.composer_tab, text="Soạn Truyện Dài")
        self.create_composer_tab_widgets()

        self.settings_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.settings_tab, text="Settings")
        self.create_settings_tab_widgets()

        self.setup_ui_logging()
        self.update_voice_display(self.selected_voice_name.get())
        self.notebook.pack(expand=True, fill="both", padx=5, pady=5)
        self.update_word_count()

    
    def setup_ui_logging(self):
        """Tạo và thêm handler để hiển thị log trên giao diện."""
        tkinter_handler = TkinterLogHandler(self.log_area)
        # Định dạng cho log trên UI, đơn giản hơn
        formatter = logging.Formatter('%(message)s')
        tkinter_handler.setFormatter(formatter)
        tkinter_handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(tkinter_handler)
            
    # --- Phiên bản chính xác cho hàm create_composer_tab_widgets ---
    def create_composer_tab_widgets(self):
        """Thiết kế lại tab Soạn Truyện Dài để chứa nút mở panel."""
        frame = self.composer_tab
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        # Khung chính chứa ô văn bản và bộ đếm
        main_pane = ttk.LabelFrame(frame, text="Bản thảo truyện", padding=10)
        main_pane.grid(row=0, column=0, sticky="nsew")
        main_pane.rowconfigure(0, weight=1)
        main_pane.columnconfigure(0, weight=1)

        self.composer_text = scrolledtext.ScrolledText(main_pane, wrap=tk.WORD, height=15)
        self.composer_text.grid(row=0, column=0, sticky="nsew")
        self.composer_text.bind("<KeyRelease>", self.update_composer_counter)

        # 1. Giữ lại BỘ ĐẾM TỔNG: Nó hiển thị số từ/ký tự của toàn bộ bản thảo
        self.composer_counter_label = ttk.Label(main_pane, text="Tổng cộng: 0 ký tự | 0 từ")
        self.composer_counter_label.grid(row=1, column=0, sticky="w", pady=(5,0))

        # 2. Giữ lại NÚT MỞ PANEL: Đây là nút duy nhất để bạn kích hoạt bảng điều khiển
        self.toggle_panel_button = ttk.Button(frame, text="Mở Bảng điều khiển Viết truyện", command=self.toggle_composer_panel, style="Accent.TButton")
        self.toggle_panel_button.grid(row=1, column=0, pady=(10,0))
        
    def toggle_clipboard_monitoring(self):
        """Bật hoặc tắt chế độ theo dõi clipboard."""
        if self.is_monitoring_clipboard:
            # --- Dừng theo dõi ---
            self.is_monitoring_clipboard = False
            self.toggle_monitoring_button.config(text="Bắt đầu Theo dõi")
            self.log_message("Đã dừng theo dõi Clipboard.")
        else:
            # --- Bắt đầu theo dõi ---
            if pyperclip is None:
                messagebox.showerror("Thiếu thư viện", "Vui lòng cài đặt 'pyperclip' để sử dụng tính năng này.\nChạy lệnh: pip install pyperclip")
                return
            
            self.is_monitoring_clipboard = True
            # --- SỬA LỖI: Reset last_clipboard_content để luôn bắt được lần copy đầu tiên ---
            self.last_clipboard_content = ""
            self.toggle_monitoring_button.config(text="Dừng Theo dõi")
            self.log_message("Bắt đầu theo dõi Clipboard...")

            self.clipboard_monitoring_thread = threading.Thread(target=self._clipboard_monitor_loop, daemon=True)
            self.clipboard_monitoring_thread.start()
                
    def _clipboard_monitor_loop(self):
        """Vòng lặp chạy ngầm để kiểm tra clipboard và áp dụng bộ lọc."""
        while self.is_monitoring_clipboard:
            try:
                current_content = pyperclip.paste()
                if current_content and current_content != self.last_clipboard_content:
                    # Ghi nhận nội dung mới để không xử lý lại
                    self.last_clipboard_content = current_content
                    
                    # --- ÁP DỤNG BỘ LỌC THÔNG MINH ---
                    if self._is_valid_story_chunk(current_content):
                        # Lên lịch thực hiện việc nối văn bản trên luồng chính
                        self.root.after_idle(self.paste_and_append_story, current_content)

            except Exception as e:
                logging.warning(f"Lỗi trong vòng lặp theo dõi clipboard: {e}")

            time.sleep(1)
            
    def toggle_composer_panel(self):
        """Mở hoặc đóng panel điều khiển."""
        if self.floating_panel and self.floating_panel.winfo_exists():
            self.floating_panel.destroy()
            self.floating_panel = None
            self.root.deiconify() # Khôi phục cửa sổ chính
            self.toggle_panel_button.config(text="Mở Bảng điều khiển Viết truyện")
        else:
            self.create_floating_panel()
            self.root.iconify() # Thu nhỏ cửa sổ chính
            self.toggle_panel_button.config(text="Đóng Bảng điều khiển")

    # --- HOTFIX [2025-06-18]: Cập nhật đúng nút bấm trên Panel điều khiển. Thay thế toàn bộ hàm này. ---
    def create_floating_panel(self):
        """Tạo ra panel nổi để điều khiển việc soạn truyện."""
        if self.floating_panel and self.floating_panel.winfo_exists():
            self.floating_panel.lift()
            return
            
        self.floating_panel = tk.Toplevel(self.root)
        self.floating_panel.title("Bảng điều khiển")
        self.floating_panel.geometry("450x180")
        
        # Giữ panel luôn nổi trên cùng
        self.floating_panel.attributes("-topmost", True)
        
        # Khi panel này đóng, hãy gọi hàm toggle để khôi phục cửa sổ chính
        self.floating_panel.protocol("WM_DELETE_WINDOW", self.toggle_composer_panel)

        panel_frame = ttk.Frame(self.floating_panel, padding=10)
        panel_frame.pack(expand=True, fill="both")
        panel_frame.columnconfigure(0, weight=1)

        # --- THAY ĐỔI TẠI ĐÂY ---
        # Các nút điều khiển
        button_frame = ttk.Frame(panel_frame)
        button_frame.grid(row=0, column=0, columnspan=2, pady=(0,10), sticky="ew")
        
        # Thay thế nút "Dán & Nối" bằng nút "Bắt đầu/Dừng Theo dõi"
        self.toggle_monitoring_button = ttk.Button(button_frame, text="Bắt đầu Theo dõi Clipboard", command=self.toggle_clipboard_monitoring)
        self.toggle_monitoring_button.pack(side="left", padx=(0,5))
        
        self.save_story_button = ttk.Button(button_frame, text="Lưu .txt...", command=self.save_story_to_file)
        self.save_story_button.pack(side="left")
        # --- KẾT THÚC THAY ĐỔI ---

        # Khu vực Prompt Gợi ý
        prompt_suggestion_frame = ttk.LabelFrame(panel_frame, text="Gợi ý Prompt tiếp theo", padding=10)
        prompt_suggestion_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10,0))
        prompt_suggestion_frame.columnconfigure(0, weight=1)

        self.continuation_prompt_entry = ttk.Entry(prompt_suggestion_frame, textvariable=self.continuation_prompt_var, state="readonly")
        self.continuation_prompt_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        self.copy_prompt_button = ttk.Button(prompt_suggestion_frame, text="Copy Prompt", command=self.copy_continuation_prompt)
        self.copy_prompt_button.grid(row=0, column=1, sticky="e")
        
    def update_composer_counter(self, event=None):
        """Đếm và cập nhật số liệu cho bản thảo."""
        content = self.composer_text.get("1.0", tk.END).strip()
        char_count = len(content)
        word_count = len(content.split()) if content else 0
        self.composer_counter_label.config(text=f"Tổng cộng: {char_count:,} ký tự | {word_count:,} từ")

    def paste_and_append_story(self, content_to_paste):
        """Hàm này giờ chỉ làm nhiệm vụ nối văn bản đã được xác thực."""
        try:
            # Không cần kiểm tra pyperclip ở đây nữa vì content đã được truyền vào
            if not content_to_paste: return
            
            # Kiểm tra trùng lặp lần cuối
            current_manuscript = self.composer_text.get("1.0", tk.END)
            if content_to_paste in current_manuscript:
                self.log_message("Phát hiện nội dung trùng lặp, đã bỏ qua.")
                return

            separator = "\n\n" if current_manuscript.strip() else ""
            self.composer_text.insert(tk.END, separator + content_to_paste)
            self.composer_text.yview(tk.END)
            self.update_composer_counter()
            self.log_message("Đã tự động nối nội dung hợp lệ từ clipboard.")

            new_chunk_word_count = len(content_to_paste.split())
            
            end_phrase = "Xin chân thành cảm ơn và hẹn gặp lại quý vị!"
            if end_phrase in content_to_paste:
                continuation_prompt = f"Bạn đã viết được {new_chunk_word_count} từ cho đoạn trên. Tổng kết."
                self.continuation_prompt_var.set(continuation_prompt)
                self.log_message("Đã phát hiện đoạn kết truyện! Tự động dừng theo dõi.")
                if self.is_monitoring_clipboard:
                    self.toggle_clipboard_monitoring()
            else:
                continuation_prompt = f"Bạn đã viết được {new_chunk_word_count} từ cho đoạn trên. Continue."
                self.continuation_prompt_var.set(continuation_prompt)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xử lý nội dung: {e}")
            self.log_message(f"Lỗi khi dán và nối: {e}")
            
    def copy_continuation_prompt(self):
        """Sao chép prompt gợi ý vào clipboard."""
        if pyperclip is None:
            messagebox.showerror("Thiếu thư viện", "Vui lòng cài đặt 'pyperclip'.")
            return
        
        prompt_text = self.continuation_prompt_var.get()
        if prompt_text:
            pyperclip.copy(prompt_text)
            self.log_message(f"Đã copy prompt: '{prompt_text}'")
            
            # Tạm thời đổi text của nút để xác nhận
            original_text = self.copy_prompt_button.cget("text")
            self.copy_prompt_button.config(text="Đã copy!")
            self.root.after(2000, lambda: self.copy_prompt_button.config(text=original_text))
        else:
            self.log_message("Không có prompt gợi ý để copy.")
            
    def save_story_to_file(self):
        """Lưu toàn bộ nội dung bản thảo ra file .txt."""
        content = self.composer_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Nội dung trống", "Không có nội dung để lưu.", parent=self.composer_tab)
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Lưu bản thảo truyện",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo("Thành công", f"Đã lưu bản thảo thành công tại:\n{file_path}", parent=self.composer_tab)
            self.log_message(f"Đã lưu bản thảo ra file: {file_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu file: {e}", parent=self.composer_tab)
            self.log_message(f"Lỗi khi lưu bản thảo: {e}")
                                  
    def on_closing(self):
        self.is_monitoring_clipboard = False
        if self.clipboard_monitoring_thread and self.clipboard_monitoring_thread.is_alive():
            self.clipboard_monitoring_thread.join(timeout=1.1)
        #if self.db_manager:
            #self.db_manager.close()
        if self.floating_panel and self.floating_panel.winfo_exists():
            self.floating_panel.destroy()
        self.root.destroy()
    # --- Hàm mới để kiểm tra nội dung clipboard ---
    def _is_valid_story_chunk(self, text: str) -> bool:
        """
        Bộ lọc thông minh để kiểm tra xem text có phải là một đoạn truyện hợp lệ không.
        """
        if not text:
            return False

        # Quy tắc 1: Kiểm tra số lượng từ
        word_count = len(text.split())
        if not (500 <= word_count <= 2500):
            self.log_message(f"Nội dung bị bỏ qua: số từ ({word_count}) không nằm trong khoảng 500-2500.")
            return False

        # Quy tắc 2: Kiểm tra từ khóa code
        code_keywords = ["import ", "def ", "class ", "from .", "const ", "let ", "var "]
        stripped_text = text.strip()
        if any(stripped_text.startswith(kw) for kw in code_keywords):
            self.log_message("Nội dung bị bỏ qua: phát hiện từ khóa code.")
            return False
            
        # Nếu vượt qua tất cả các bộ lọc
        return True
    
    def create_assistant_tab_widgets(self):
        frame = self.assistant_tab
        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        top_frame = ttk.Frame(frame)
        top_frame.grid(row=0, column=0, sticky="nsew")
        top_frame.rowconfigure(0, weight=1)
        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=1)

        input_pane = ttk.LabelFrame(top_frame, text="1. Dán toàn bộ phản hồi của Gemini tại đây", padding=10)
        input_pane.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        input_pane.rowconfigure(0, weight=1)
        input_pane.columnconfigure(0, weight=1)
        self.assistant_input_text = scrolledtext.ScrolledText(input_pane, wrap=tk.WORD, height=10)
        self.assistant_input_text.grid(row=0, column=0, sticky="nsew")
        self.parse_button = ttk.Button(input_pane, text="Bóc Tách & Phân Tích", command=self.parse_input_text)
        self.parse_button.grid(row=1, column=0, sticky="ew", pady=(10, 0))

        list_pane = ttk.LabelFrame(top_frame, text="2. Các lựa chọn đã được xử lý (Nhấp để chọn)", padding=10)
        list_pane.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        list_pane.rowconfigure(0, weight=1)
        list_pane.columnconfigure(0, weight=1)
        self.options_display_text = scrolledtext.ScrolledText(list_pane, wrap=tk.WORD, height=10)
        self.options_display_text.grid(row=0, column=0, sticky="nsew")
        self.options_display_text.tag_configure("highlight", background="lightblue")
        self.options_display_text.config(state=tk.DISABLED)
        
        bottom_frame = ttk.LabelFrame(frame, text="3. Soạn thảo & Chốt phương án", padding=10)
        bottom_frame.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        bottom_frame.rowconfigure(1, weight=1)
        bottom_frame.columnconfigure(0, weight=1)
        
        mode_frame = ttk.Frame(bottom_frame)
        mode_frame.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        self.assistant_mode = tk.StringVar(value="title")
        ttk.Label(mode_frame, text="Chế độ:").pack(side="left")
        ttk.Radiobutton(mode_frame, text="Tiêu đề", variable=self.assistant_mode, value="title", command=self.on_mode_change).pack(side="left", padx=5)
        ttk.Radiobutton(mode_frame, text="Thumbnail", variable=self.assistant_mode, value="thumbnail", command=self.on_mode_change).pack(side="left", padx=5)

        self.editor_text = scrolledtext.ScrolledText(bottom_frame, wrap=tk.WORD, height=5)
        self.editor_text.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.editor_text.bind("<KeyRelease>", self.update_editor_metrics)

        action_frame = ttk.Frame(bottom_frame)
        action_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        action_frame.columnconfigure(0, weight=1)

        self.counter_label = ttk.Label(action_frame, text="Ký tự: 0 | Từ: 0", font=("Segoe UI", 10))
        self.counter_label.grid(row=0, column=0, sticky="w", padx=5)
        # --- THÊM NÚT MỚI VÀO ĐÂY ---
        self.preview_button = ttk.Button(action_frame, text="Xem trước Thumbnail", command=self.show_thumbnail_preview)
        self.preview_button.grid(row=0, column=1, sticky="e", padx=5)
        # ---

        self.save_button = ttk.Button(action_frame, text="Chốt & Lưu", state=tk.DISABLED, command=self.save_final_version, style="Accent.TButton")
        self.save_button.grid(row=0, column=2, sticky="e", padx=5)

    def _parse_titles(self, text):
        """
        Sử dụng phương pháp tách chuỗi nhiều lớp để trích xuất các lựa chọn tiêu đề
        một cách ổn định và chính xác từ phản hồi của Gemini.
        """
        # --- LOGIC BÓC TÁCH MỚI ---
        cleaned_options = []
        try:
            # Bước 1: Phân tách các khối lựa chọn lớn bằng "---"
            blocks = text.split('---')
            
            for block in blocks:
                # Bỏ qua các khối không chứa thông tin cần thiết (ví dụ: phần mở đầu)
                if "**Tiêu đề:**" not in block:
                    continue

                # Bước 2: Tìm dòng "chìa khóa" và trích xuất nội dung
                lines = block.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith("**Tiêu đề:**"):
                        # Lấy toàn bộ nội dung sau "Tiêu đề:"
                        raw_title = line.split(":", 1)[1]
                        
                        # Bước 3: Làm sạch dữ liệu
                        # Xóa các ký tự markdown và khoảng trắng thừa
                        clean_title = raw_title.replace('**', '').strip()
                        
                        if clean_title:
                            cleaned_options.append(clean_title)
                        # Sau khi tìm thấy tiêu đề trong một khối, có thể bỏ qua các dòng còn lại của khối đó
                        break 
                        
            return cleaned_options
        except Exception as e:
            self.log_message(f"Lỗi trong quá trình bóc tách tiêu đề: {e}")
            # Trả về một danh sách rỗng nếu có lỗi
            return []

    def _parse_thumbnails(self, text: str) -> list[str]:
        """
        Bóc tách kịch bản thumbnail bằng cách nhận diện các dòng được in đậm (**)
        và loại trừ một cách tường minh các dòng metadata như "phong cách".
        """
        self.log_message("Bắt đầu bóc tách kịch bản thumbnail (logic v7.0 - Loại trừ)...")
        try:
            # Tách văn bản thành các khối lựa chọn
            blocks = text.split("---")
            
            cleaned_options = []
            # Bỏ qua khối đầu tiên (thường là phần giới thiệu)
            for block in blocks[1:]:
                if not block.strip():
                    continue

                script_lines = []
                for line in block.strip().split('\n'):
                    stripped_line = line.strip()

                    # ĐIỀU KIỆN THEN CHỐT:
                    # Phải là dòng in đậm VÀ không phải là dòng mô tả phong cách.
                    is_bolded = stripped_line.startswith('**') and stripped_line.endswith('**')
                    is_style_line = '(phong cách' in stripped_line.lower()

                    if is_bolded and not is_style_line:
                        # Làm sạch và lưu lại dòng kịch bản
                        clean_line = stripped_line.replace('**', '').strip()
                        if clean_line:
                            script_lines.append(clean_line)
                
                if script_lines:
                    full_script = "\n".join(script_lines)
                    cleaned_options.append(full_script)
            
            self.log_message(f"Hoàn tất. Tìm thấy {len(cleaned_options)} kịch bản hợp lệ.")
            return cleaned_options

        except Exception as e:
            import traceback
            self.log_message(f"[ERROR] Lỗi nghiêm trọng trong quá trình bóc tách thumbnail: {e}")
            self.log_message(f"[ERROR] Traceback: {traceback.format_exc()}")
            return []

    def parse_input_text(self):
        self.options_display_text.config(state=tk.NORMAL)
        self.options_display_text.delete("1.0", tk.END)
        
        self.editor_text.delete("1.0", tk.END)
        self.update_editor_metrics(None)
        
        full_text = self.assistant_input_text.get("1.0", tk.END)
        if not full_text.strip():
            messagebox.showwarning("Thông báo", "Vùng nhập liệu đang trống.", parent=self.assistant_tab)
            return

        is_thumbnail_mode = "KỊCH BẢN THUMBNAIL" in full_text.upper() or "PHONG CÁCH:" in full_text.upper()
        current_mode = "thumbnail" if is_thumbnail_mode else "title"
        self.assistant_mode.set(current_mode)
        
        cleaned_options = self._parse_thumbnails(full_text) if current_mode == "thumbnail" else self._parse_titles(full_text)

        if not cleaned_options:
            messagebox.showinfo("Không tìm thấy", "Không thể bóc tách được lựa chọn nào.", parent=self.assistant_tab)
            self.options_display_text.config(state=tk.DISABLED)
            return

        self._full_options_text = cleaned_options
        self.display_parsed_options(cleaned_options, current_mode)
            
        messagebox.showinfo("Hoàn tất", f"Đã bóc tách {len(cleaned_options)} lựa chọn theo chế độ '{current_mode}'.", parent=self.assistant_tab)
        self.on_mode_change()
        
    def display_parsed_options(self, options, mode):
        self.options_display_text.config(state=tk.NORMAL)
        self.options_display_text.delete("1.0", tk.END)

        for tag in self.options_display_text.tag_names():
            if tag.startswith("option_"):
                self.options_display_text.tag_delete(tag)

        separator = "\n" + ("-" * 60) + "\n\n"

        for i, option_text in enumerate(options):
            tag_name = f"option_{i}"
            start_index = self.options_display_text.index(tk.END)
            
            prefix = "(Thumbnail)" if mode == "thumbnail" else "(Tiêu đề)"
            display_header = f"--- LỰA CHỌN {i+1} {prefix} ---\n"
            self.options_display_text.insert(tk.END, display_header, ("h2", "center"))
            self.options_display_text.insert(tk.END, option_text)
            
            end_index = self.options_display_text.index(tk.END)
            
            self.options_display_text.tag_add(tag_name, start_index, f"{end_index}-1c")
            self.options_display_text.tag_bind(tag_name, "<Button-1>", lambda e, index=i: self.on_text_option_clicked(e, index))
            
            if i < len(options) - 1:
                self.options_display_text.insert(tk.END, separator, ("separator", "center"))

        self.options_display_text.config(state=tk.DISABLED)

    def on_text_option_clicked(self, event, index):
        for tag in self.options_display_text.tag_names():
            if tag.startswith("option_"):
                self.options_display_text.tag_configure(tag, background="white")
        
        tag_name = f"option_{index}"
        self.options_display_text.tag_configure(tag_name, background="lightblue")

        if hasattr(self, '_full_options_text') and 0 <= index < len(self._full_options_text):
            full_text = self._full_options_text[index]
            self.editor_text.delete("1.0", tk.END)
            self.editor_text.insert("1.0", full_text)
            self.update_editor_metrics(None)
            
    def on_option_selected(self, event):
        # Hàm này không còn được sử dụng với ScrolledText, nhưng giữ lại để không gây lỗi nếu có binding sót
        pass
    def on_mode_change(self):
        self.update_editor_metrics(None)
        
    def update_editor_metrics(self, event):
        content = self.editor_text.get("1.0", tk.END).strip()
        char_count = len(content)
        word_count = len(content.split()) if content else 0
        line_count = len([line for line in content.splitlines() if line.strip()])

        mode = self.assistant_mode.get()
        label_text, label_color, button_state = "", COLOR_NORMAL, tk.DISABLED

        if mode == "title":
            label_text = f"Ký tự: {char_count} | Từ: {word_count}"
            if char_count == 0: pass
            elif TITLE_CHAR_LIMIT_GOOD_MIN <= char_count <= TITLE_CHAR_LIMIT_GOOD_MAX:
                label_color, button_state = COLOR_OK, tk.NORMAL
            elif char_count > TITLE_CHAR_LIMIT_MAX:
                label_color = COLOR_ERROR
            else:
                label_color = COLOR_WARN
        elif mode == "thumbnail":
            label_text = f"Ký tự: {char_count} | Từ: {word_count} | Dòng: {line_count}"
            if char_count > 0:
                label_color, button_state = COLOR_OK, tk.NORMAL

        self.counter_label.config(text=label_text, foreground=label_color)
        self.save_button.config(state=button_state)
    
    # --- HOTFIX [2025-06-18 09:40]: Thêm logic lưu trữ vào CSDL cho nút "Chốt & Lưu". Thay thế toàn bộ hàm này. ---
    def save_final_version(self):
        final_text = self.editor_text.get("1.0", tk.END).strip()
        if not final_text:
            messagebox.showwarning("Nội dung trống", "Không có nội dung để lưu.", parent=self.assistant_tab)
            return

        mode = self.assistant_mode.get()
        char_count = len(final_text)
        word_count = len(final_text.split())
        line_count = len(final_text.splitlines())
        
        success = False
        if mode == "title":
            success = self.db_manager.add_final_title(final_text, char_count, word_count)
        elif mode == "thumbnail":
            success = self.db_manager.add_final_thumbnail(final_text, char_count, word_count, line_count)

        if success:
            messagebox.showinfo("Thành công", f"Đã lưu phương án '{mode}' thành công!", parent=self.assistant_tab)
            self.editor_text.delete("1.0", tk.END)
            self.update_editor_metrics(None)
        else:
            messagebox.showerror("Thất bại", "Lỗi khi lưu vào cơ sở dữ liệu.", parent=self.assistant_tab)
    
    # --- HOTFIX [2025-06-23]: Nâng cấp tính năng Xem trước Thumbnail (Giai đoạn 1). Thay thế/thêm các hàm này. ---
    def update_editor_metrics(self, event):
        """Sửa lỗi đếm dòng và cập nhật các chỉ số."""
        content = self.editor_text.get("1.0", tk.END)
        # Đếm ký tự bao gồm cả ký tự xuống dòng nhưng trừ ký tự cuối cùng do ScrolledText tự thêm vào
        char_count = len(content) - 1 if len(content) > 0 else 0
        # Đếm từ
        word_count = len(content.strip().split()) if content.strip() else 0
        # Đếm số dòng có nội dung
        line_count = len([line for line in content.strip().splitlines() if line.strip()])

        mode = self.assistant_mode.get()
        label_text, label_color, button_state = "", COLOR_NORMAL, tk.DISABLED

        if mode == "title":
            # Logic cho title không đổi
            label_text = f"Ký tự: {char_count} | Từ: {word_count}"
            if char_count == 0: pass
            elif TITLE_CHAR_LIMIT_GOOD_MIN <= char_count <= TITLE_CHAR_LIMIT_GOOD_MAX:
                label_color, button_state = COLOR_OK, tk.NORMAL
            elif char_count > TITLE_CHAR_LIMIT_MAX:
                label_color = COLOR_ERROR
            else:
                label_color = COLOR_WARN
        elif mode == "thumbnail":
            # Cập nhật để hiển thị đúng số dòng
            label_text = f"Ký tự: {char_count} | Từ: {word_count} | Dòng: {line_count}"
            if char_count > 0:
                label_color, button_state = COLOR_OK, tk.NORMAL

        self.counter_label.config(text=label_text, foreground=label_color)
        self.save_button.config(state=button_state)

    def show_thumbnail_preview(self):
        """Mở cửa sổ xem trước thumbnail trong một module riêng."""
        text_content = self.editor_text.get("1.0", tk.END).strip()
        if not text_content:
            messagebox.showwarning("Nội dung trống", "Không có nội dung để xem trước.", parent=self.assistant_tab)
            return

        # Khởi tạo cửa sổ từ class riêng, truyền các đối tượng cần thiết.
        # Cửa sổ này sẽ tự quản lý vòng đời của nó.
        ThumbnailPreviewWindow(
            parent=self.root, 
            text_content=text_content, 
            log_callback=self.log_message
        )
        
    # --- Các hàm của các tab khác (giữ nguyên, không tóm tắt) ---
    def _set_window_icon(self):
        try:
            if sys.platform.startswith('win'):
                icon_path = get_resource_path("icons/app_icon.ico")
                if os.path.exists(icon_path): self.root.iconbitmap(icon_path)
            else:
                icon_path_png = get_resource_path("icons/app_icon.png")
                if os.path.exists(icon_path_png):
                    photo = tk.PhotoImage(file=icon_path_png)
                    self.root.iconphoto(False, photo)
        except Exception as e:
            self.log_message(f"Error setting window icon: {e}")

    # --- KHÔI PHỤC CÁC HÀM ---
    def create_main_tab_widgets(self):
        frame = self.main_tab
        frame.rowconfigure(0, weight=3); frame.rowconfigure(1, weight=0); frame.rowconfigure(2, weight=0); 
        frame.rowconfigure(3, weight=0); frame.rowconfigure(4, weight=0); frame.rowconfigure(5, weight=3)
        frame.columnconfigure(0, weight=1)

        input_text_frame = ttk.LabelFrame(frame, text="Input Text", padding="10")
        input_text_frame.grid(row=0, column=0, sticky="ewns", padx=5, pady=5)
        input_text_frame.rowconfigure(0, weight=1); input_text_frame.columnconfigure(0, weight=1)
        self.main_text_input = scrolledtext.ScrolledText(input_text_frame, wrap=tk.WORD, height=10)
        self.main_text_input.grid(row=0, column=0, sticky="nsew")
        self.main_text_input.bind("<KeyRelease>", self.update_word_count)
        
        count_frame = ttk.Frame(input_text_frame)
        count_frame.grid(row=1, column=0, sticky="ew", pady=(5,0), padx=5)
        self.main_word_count_label = ttk.Label(count_frame, text="Ký tự: 0 | Từ: 0 | Dự kiến chunks: 0")
        self.main_word_count_label.pack(side="left")
        self.import_button = ttk.Button(count_frame, text="Import từ File...", command=self.import_text_from_file)
        self.import_button.pack(side="right")

        reading_style_frame = ttk.LabelFrame(frame, text="Reading Style Prompt (Select or Type Custom)", padding="10")
        reading_style_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.reading_style_combobox = ttk.Combobox(reading_style_frame, textvariable=self.reading_style_prompt_var, values=PREDEFINED_READING_STYLES, height=10)
        self.reading_style_combobox.pack(fill="x", expand=True, padx=5, pady=5)

        settings_container_frame = ttk.Frame(frame)
        settings_container_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        settings_container_frame.columnconfigure(0, weight=1); settings_container_frame.columnconfigure(1, weight=1)

        gen_settings_frame = ttk.LabelFrame(settings_container_frame, text="Generation Settings", padding="10")
        gen_settings_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        gen_settings_frame.columnconfigure(1, weight=1)
        
        ttk.Label(gen_settings_frame, text="Select Voice:").grid(row=0, column=0, sticky="w", pady=2)
        self.voice_dropdown = ttk.Combobox(gen_settings_frame, textvariable=self.selected_voice_display, values=self.voice_display_list, state="readonly")
        self.voice_dropdown.grid(row=0, column=1, columnspan=2, sticky="ew", pady=2)
        self.voice_dropdown.bind('<<ComboboxSelected>>', self.on_voice_selected)

        ttk.Label(gen_settings_frame, text="Temperature:").grid(row=1, column=0, sticky="w", pady=2)
        self.temp_scale = ttk.Scale(gen_settings_frame, from_=MIN_TEMPERATURE, to=MAX_TEMPERATURE, variable=self.temperature_var, orient=tk.HORIZONTAL, command=lambda v: self.temp_scale_val_label.config(text=f"{float(v):.2f}"))
        self.temp_scale.grid(row=1, column=1, sticky="ew", pady=2)
        self.temp_scale_val_label = ttk.Label(gen_settings_frame, text=f"{self.temperature_var.get():.2f}", width=4)
        self.temp_scale_val_label.grid(row=1, column=2, sticky="w", padx=(5,0))
        
        ttk.Label(gen_settings_frame, text="Top P:").grid(row=2, column=0, sticky="w", pady=2)
        self.top_p_scale = ttk.Scale(gen_settings_frame, from_=MIN_TOP_P, to=MAX_TOP_P, variable=self.top_p_var, orient=tk.HORIZONTAL, command=lambda v: self.top_p_scale_val_label.config(text=f"{float(v):.2f}"))
        self.top_p_scale.grid(row=2, column=1, sticky="ew", pady=2)
        self.top_p_scale_val_label = ttk.Label(gen_settings_frame, text=f"{self.top_p_var.get():.2f}", width=4)
        self.top_p_scale_val_label.grid(row=2, column=2, sticky="w", padx=(5,0))
        
        ttk.Label(gen_settings_frame, text="Ghi chú: Giữ Temp ở mức 1.0 để có kết quả ổn định nhất.", style="secondary.TLabel").grid(row=3, column=1, columnspan=2, padx=5, pady=(5, 0), sticky="w")
        
        output_settings_frame = ttk.LabelFrame(settings_container_frame, text="Output File Settings", padding="10")
        output_settings_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        output_settings_frame.columnconfigure(1, weight=1)
        
        ttk.Label(output_settings_frame, text="Output Directory:").grid(row=0, column=0, sticky="w", pady=2)
        self.output_dir_entry = ttk.Entry(output_settings_frame, textvariable=self.output_dir_var)
        self.output_dir_entry.grid(row=0, column=1, sticky="ew", pady=2)
        ttk.Button(output_settings_frame, text="Browse...", command=self.browse_main_output_directory).grid(row=0, column=2, padx=(5,0))

        ttk.Label(output_settings_frame, text="Story/Base Name:").grid(row=1, column=0, sticky="w", pady=2)
        self.story_name_entry = ttk.Entry(output_settings_frame, textvariable=self.story_name_var)
        self.story_name_entry.grid(row=1, column=1, columnspan=2, sticky="ew", pady=2)
        
        action_buttons_frame = ttk.Frame(frame, padding="5")
        action_buttons_frame.grid(row=3, column=0, pady=(10,0), sticky="ew", padx=5)
        self.generate_button = ttk.Button(action_buttons_frame, text="Generate Voice", command=self.start_tts_thread, style="Accent.TButton")
        self.generate_button.pack(side="left", padx=5)
        self.open_folder_button = ttk.Button(action_buttons_frame, text="Open Output Folder", command=self.open_last_output_folder, state="disabled")
        self.open_folder_button.pack(side="left", padx=5)

        progress_frame = ttk.LabelFrame(frame, text="Progress", padding="10")
        progress_frame.grid(row=4, column=0, sticky="ewns", padx=5, pady=5)
        progress_frame.columnconfigure(1, weight=1) 
        overall_progress_subframe = ttk.Frame(progress_frame)
        overall_progress_subframe.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        overall_progress_subframe.columnconfigure(1, weight=1)
        ttk.Label(overall_progress_subframe, text="Overall:", width=10).grid(row=0, column=0, sticky="w")
        self.progress_bar_total = ttk.Progressbar(overall_progress_subframe, orient="horizontal", mode="determinate", style="thin.Horizontal.TProgressbar")
        self.progress_bar_total.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.total_time_label = ttk.Label(overall_progress_subframe, text="Tổng thời gian: 00:00", style="secondary.TLabel")
        self.total_time_label.grid(row=0, column=2, sticky="e")

        self.thread_status_labels = []
        for i in range(NUM_API_KEYS):
            ttk.Label(progress_frame, text=f"API Key {i+1}:", width=10).grid(row=i+1, column=0, sticky="w", pady=1)
            status_label = ttk.Label(progress_frame, text="Idle", foreground=COLOR_NORMAL, anchor="w")
            status_label.grid(row=i+1, column=1, sticky="ew", pady=1, padx=5)
            self.thread_status_labels.append(status_label)
        
        log_frame = ttk.LabelFrame(frame, text="Log", padding="10")
        log_frame.grid(row=5, column=0, sticky="ewns", padx=5, pady=5)
        log_frame.rowconfigure(0, weight=1); log_frame.columnconfigure(0, weight=1)
        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=8, state='disabled')
        self.log_area.grid(row=0, column=0, sticky="nsew", padx=(5,0), pady=5)
        self.clear_log_button = ttk.Button(log_frame, text="Clear Log", command=self.clear_log_area, width=10)
        self.clear_log_button.grid(row=0, column=1, sticky="ne", padx=(2,5), pady=5)

    def on_voice_selected(self, event):
        selected_index = event.widget.current()
        if 0 <= selected_index < len(self.voice_name_list):
            voice_name = self.voice_name_list[selected_index]
            self.selected_voice_name.set(voice_name)

    def update_voice_display(self, voice_name_to_set):
        try:
            if voice_name_to_set in self.voice_name_list:
                idx = self.voice_name_list.index(voice_name_to_set)
                display_text = self.voice_display_list[idx]
                self.selected_voice_display.set(display_text)
            else: 
                if self.voice_display_list:
                    self.selected_voice_display.set(self.voice_display_list[0])
                    self.selected_voice_name.set(self.voice_name_list[0])
        except (ValueError, IndexError):
            if self.voice_display_list:
                self.selected_voice_display.set(self.voice_display_list[0])
                if self.voice_name_list:
                    self.selected_voice_name.set(self.voice_name_list[0])
    def import_text_from_file(self):
        """Mở dialog để chọn file .txt hoặc .docx và nạp nội dung."""
        file_path = filedialog.askopenfilename(
            title="Chọn file văn bản",
            filetypes=[("Word Document", "*.docx"), ("Text File", "*.txt"), ("All files", "*.*")]
        )
        if not file_path:
            return

        content = ""
        try:
            if file_path.lower().endswith(".txt"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif file_path.lower().endswith(".docx"):
                if docx is None:
                    messagebox.showerror("Thiếu thư viện", "Vui lòng cài đặt thư viện 'python-docx' để đọc file .docx.\nChạy lệnh: pip install python-docx")
                    return
                doc = docx.Document(file_path)
                content = "\n".join([para.text for para in doc.paragraphs])
            else:
                messagebox.showwarning("Định dạng không hỗ trợ", "Chỉ hỗ trợ file .txt và .docx.")
                return

            self.main_text_input.delete("1.0", tk.END)
            self.main_text_input.insert("1.0", content)
            self.update_word_count(None) # Cập nhật lại bộ đếm
            self.log_message(f"Đã import thành công nội dung từ: {os.path.basename(file_path)}")

        except Exception as e:
            messagebox.showerror("Lỗi đọc file", f"Đã có lỗi xảy ra khi đọc file:\n{e}")
            self.log_message(f"Lỗi import file: {e}")
            
    def create_settings_tab_widgets(self):
        frame = self.settings_tab
        api_keys_frame = ttk.LabelFrame(frame, text="API Key Management", padding="10")
        api_keys_frame.grid(row=0, column=0, padx=5, pady=10, sticky="ew")
        self.api_key_entries = [] 
        self.api_label_entries = []
        for i in range(NUM_API_KEYS):
            ttk.Label(api_keys_frame, text=f"Label API Key {i+1}:").grid(row=i*2, column=0, padx=5, pady=(10,2), sticky="w")
            label_entry = ttk.Entry(api_keys_frame, textvariable=self.api_label_vars[i], width=40)
            label_entry.grid(row=i*2, column=1, columnspan=2, padx=5, pady=(10,2), sticky="ew")
            self.api_label_entries.append(label_entry)
            ttk.Label(api_keys_frame, text=f"API Key {i+1}:").grid(row=i*2+1, column=0, padx=5, pady=2, sticky="w")
            key_entry = ttk.Entry(api_keys_frame, textvariable=self.api_key_vars[i], width=50, show="*")
            key_entry.grid(row=i*2+1, column=1, columnspan=2, padx=5, pady=2, sticky="ew")
            self.api_key_entries.append(key_entry)
        api_keys_frame.columnconfigure(1, weight=1)

        general_settings_frame = ttk.LabelFrame(frame, text="General Settings", padding="10")
        general_settings_frame.grid(row=1, column=0, padx=5, pady=10, sticky="ew")
        general_settings_frame.columnconfigure(1, weight=1)
        
        ttk.Label(general_settings_frame, text="Default Voice:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.settings_voice_dropdown = ttk.Combobox(general_settings_frame, textvariable=self.selected_voice_display, values=self.voice_display_list, state='readonly', width=40)
        self.settings_voice_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.settings_voice_dropdown.bind('<<ComboboxSelected>>', self.on_voice_selected)
        
        # --- MỚI: Thêm ô tùy chỉnh Chunk Size ---
        ttk.Label(general_settings_frame, text="Số từ tối đa mỗi chunk:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.chunk_size_entry = ttk.Entry(general_settings_frame, textvariable=self.words_per_chunk_var, width=10)
        self.chunk_size_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(general_settings_frame, text="Default Save Directory:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.settings_save_dir_entry = ttk.Entry(general_settings_frame, textvariable=self.output_dir_var, width=40)
        self.settings_save_dir_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(general_settings_frame, text="Browse...", command=self.browse_main_output_directory).grid(row=2, column=2, padx=5, pady=5)
        
        self.save_settings_button = ttk.Button(frame, text="Save All Settings", command=self.save_app_settings, style="Accent.TButton")
        self.save_settings_button.grid(row=2, column=0, padx=5, pady=15)
        ttk.Label(frame, text="Note: Settings are saved automatically on exit.").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        frame.columnconfigure(0, weight=1)
            
    def browse_main_output_directory(self):
        directory = filedialog.askdirectory(initialdir=self.output_dir_var.get(), title="Select Output Directory", parent=self.root)
        if directory: self.output_dir_var.set(directory); self.log_message(f"Output directory set to: {directory}")

    def clear_log_area(self):
        if hasattr(self, 'log_area') and self.log_area.winfo_exists():
            self.log_area.config(state="normal"); self.log_area.delete("1.0", tk.END); self.log_area.config(state="disabled")

    def open_last_output_folder(self):
        if self.last_saved_output_dir and os.path.isdir(self.last_saved_output_dir):
            try:
                if platform.system() == "Windows": os.startfile(self.last_saved_output_dir)
                elif platform.system() == "Darwin": subprocess.call(["open", self.last_saved_output_dir])
                else: subprocess.call(["xdg-open", self.last_saved_output_dir])
            except Exception as e: self.log_message(f"Error opening folder: {e}"); messagebox.showerror("Error", f"Could not open folder: {self.last_saved_output_dir}\n{e}", parent=self.root)
        else: self.log_message("No output folder recorded or folder does not exist.");

    def update_word_count(self, event=None):
        content = self.main_text_input.get("1.0", tk.END).strip()
        char_count = len(content)
        word_count = len(content.split()) if content else 0
        # Ước tính số chunks, giả định 1000 từ mỗi chunk
        est_chunks = (word_count + 999) // 1000 if word_count > 0 else 0
        
        self.main_word_count_label.config(text=f"Ký tự: {char_count} | Từ: {word_count} | Dự kiến chunks: {est_chunks}")

     # --- Sửa hàm log_message ---
    def log_message(self, message: str):
        # Giờ đây, hàm này chỉ cần gọi logging, hệ thống sẽ tự lo phần còn lại
        logging.info(message)

    def update_overall_progress(self, value: int):
        if hasattr(self, 'progress_bar_total') and self.progress_bar_total.winfo_exists():
            def _update():
                if self.progress_bar_total.winfo_exists(): self.progress_bar_total["value"] = value
            self.root.after_idle(_update)

    # --- THAY ĐỔI: Hàm update_thread_progress để nhận màu sắc ---
    def update_thread_progress(self, thread_index: int, status_message: str, status_color: str):
        if thread_index < len(self.thread_status_labels) and self.thread_status_labels[thread_index].winfo_exists():
            def _update_lbl():
                if self.thread_status_labels[thread_index].winfo_exists():
                    self.thread_status_labels[thread_index].config(text=status_message, foreground=status_color)
            self.root.after_idle(_update_lbl)
            
    def save_app_settings(self):
        current_settings = {
            "default_voice": self.selected_voice_name.get(),
            "temperature": self.temperature_var.get(),
            "top_p": self.top_p_var.get(),
            "save_dir": self.output_dir_var.get(),
            "max_words_per_part": self.words_per_chunk_var.get() # MỚI
        }
        for i in range(NUM_API_KEYS):
            current_settings[f"api_key_{i+1}"] = self.api_key_vars[i].get()
            current_settings[f"label_{i+1}"] = self.api_label_vars[i].get()
        if save_settings(current_settings):
            self.settings = current_settings; self.log_message("Settings saved successfully.")
            messagebox.showinfo("Settings", "Settings saved successfully!", parent=self.root)
        else:
            self.log_message("Failed to save settings."); messagebox.showerror("Error", "Failed to save settings.", parent=self.root)

    # --- HOTFIX [2025-06-18]: Sửa lỗi AttributeError do gọi sai tên biến text input. Thay thế toàn bộ hàm này. ---
    def start_tts_thread(self):
        # Sửa lại self.text_input thành self.main_text_input
        text_to_convert = self.main_text_input.get("1.0", tk.END).strip()
        if not text_to_convert:
            messagebox.showerror("Input Error", "Please enter text.", parent=self.root)
            return
        
        active_keys_info_list = []
        for i in range(NUM_API_KEYS):
            key_val = self.api_key_vars[i].get().strip()
            if key_val:
                active_keys_info_list.append({
                    "key": key_val, 
                    "label": self.api_label_vars[i].get().strip() or f"API Key {i+1}"
                })
        if not active_keys_info_list:
            messagebox.showerror("API Key Error", f"Please set at least one API Key in Settings.", parent=self.root)
            self.notebook.select(self.settings_tab)
            return
        self.log_message(f"Found {len(active_keys_info_list)} active API Key(s).")

        voice_to_use = self.selected_voice_name.get()
        if not voice_to_use:
            messagebox.showerror("Voice Error", "Please select a voice.", parent=self.root)
            return

        output_dir = self.output_dir_var.get().strip()
        story_base_name = self.story_name_var.get().strip()
        if not output_dir or not os.path.isdir(output_dir):
            messagebox.showerror("Output Error", "Invalid output directory.", parent=self.root)
            return
        if not story_base_name:
            messagebox.showerror("Output Error", "Please enter a Story/Base Name.", parent=self.root)
            return
        
        reading_style_prompt_text = self.reading_style_prompt_var.get().strip()

        selected_voice_for_filename = voice_to_use.replace("-", "")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_story_name = "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in story_base_name).rstrip()
        safe_voice_name = "".join(c if c.isalnum() else '' for c in selected_voice_for_filename)
        output_filename_only = f"{safe_voice_name}_{safe_story_name}_{timestamp}"
        output_file_path_base = os.path.normpath(os.path.join(output_dir, output_filename_only))
        
        self.log_message(f"Output base name: {output_filename_only}")

        self.generate_button.config(state="disabled", text="Generating...")
        if hasattr(self, 'open_folder_button'): self.open_folder_button.config(state="disabled")
        self.root.config(cursor="watch")
        
        thread = threading.Thread(
            target=self._tts_task_wrapper,
            args=(
                text_to_convert, voice_to_use, output_file_path_base,
                self.temperature_var.get(), self.top_p_var.get(),
                reading_style_prompt_text
            ),
            daemon=True
        )
        thread.start()

    # --- HOTFIX [2025-06-18]: Cung cấp phiên bản đầy đủ và chính xác của hàm _tts_task_wrapper. Thay thế toàn bộ hàm này. ---
    def _tts_task_wrapper(self, text_to_convert, voice, output_file_path_base, temp, top_p, reading_style_prompt):
        task_start_time = time.time()

        # Reset các hiển thị trên UI trước khi bắt đầu
        def _setup_ui_for_run():
            if hasattr(self, 'total_time_label') and self.total_time_label.winfo_exists():
                self.total_time_label.config(text="Tổng thời gian: 00:00")
            
            active_keys_count = sum(1 for var in self.api_key_vars if var.get().strip())
            for i in range(NUM_API_KEYS):
                if i < active_keys_count:
                    self.update_thread_progress(i, "Sẵn sàng...", COLOR_NORMAL)
                else:
                    self.update_thread_progress(i, "Không sử dụng", "gray")

        self.root.after_idle(_setup_ui_for_run)
        
        sanitized_temp = round(temp, 2)
        sanitized_top_p = round(top_p, 2)
        
        self.last_saved_output_dir = None
        try:
            active_keys_info_for_logic = [] 
            for i in range(NUM_API_KEYS):
                key_val = self.api_key_vars[i].get().strip()
                if key_val:
                    active_keys_info_for_logic.append({
                        "key": key_val, 
                        "label": self.api_label_vars[i].get().strip() or f"API Key {i+1}"
                    })
            if not active_keys_info_for_logic:
                self.log_message("Lỗi: Không có API Key nào được cấu hình.")
                # Phải gọi finalize để bật lại nút bấm
                # Dùng return sẽ không chạy vào finally, nên ta sẽ để nó chạy qua
                raise ValueError("No active API keys configured.")

            thread_specific_callbacks = []
            for i in range(len(active_keys_info_for_logic)):
                def create_callback(thread_idx_captured):
                    def _update_ui_for_thread(status_msg, status_color):
                        self.update_thread_progress(thread_idx_captured, status_msg, status_color)
                    return _update_ui_for_thread
                thread_specific_callbacks.append(create_callback(i))
            
            max_words = self.words_per_chunk_var.get()
            token_fallback = int(self.settings.get("max_tokens_fallback", 4800)) 
            retries = int(self.settings.get("max_retries_per_part", 1)) 
            timeout = int(self.settings.get("part_timeout", 600))
            
            success, final_file_path = generate_tts_audio_multithreaded( 
                active_api_keys_info=active_keys_info_for_logic, 
                text_to_speak=text_to_convert, 
                voice_name=voice, 
                output_file_path_base=output_file_path_base, 
                log_callback_ui=self.log_message, 
                progress_callback_ui_total=self.update_overall_progress,
                progress_callbacks_ui_thread=thread_specific_callbacks,
                reading_style_prompt=reading_style_prompt, 
                temp_setting=sanitized_temp,
                top_p_setting=sanitized_top_p,
                max_words_per_part=max_words,
                max_tokens_fallback=token_fallback,
                max_retries_per_part=retries,
                part_timeout=timeout
            )
            
            if success and final_file_path:
                self.log_message(f"TTS task completed successfully. Final file: {final_file_path}")
                self.last_saved_output_dir = os.path.dirname(final_file_path)
            else:
                self.log_message("TTS task failed or did not complete.")

        except Exception as e:
            logging.error(f"Error in TTS task wrapper: {e}", exc_info=True)
            self.log_message(f"Đã xảy ra lỗi: {e}")
        finally: 
            def _finalize_ui(): 
                duration = time.time() - task_start_time
                minutes, seconds = divmod(duration, 60)
                time_str = f"Tổng thời gian: {int(minutes):02d}:{int(seconds):02d}"

                if hasattr(self, 'root') and self.root.winfo_exists():
                    if hasattr(self, 'generate_button'):
                        self.generate_button.config(state="normal", text="Generate Voice")
                    self.root.config(cursor="")
                    if self.last_saved_output_dir and hasattr(self, 'open_folder_button'):
                        self.open_folder_button.config(state="normal")
                    if hasattr(self, 'total_time_label'):
                        self.total_time_label.config(text=time_str)
                    
                    for i in range(NUM_API_KEYS): 
                        if i < len(self.thread_status_labels) and self.thread_status_labels[i].winfo_exists():
                                self.update_thread_progress(i, "Idle", COLOR_NORMAL)
            
            if hasattr(self, 'root') and self.root.winfo_exists():
                self.root.after_idle(_finalize_ui)