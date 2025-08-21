# file-path: src/gemini_tts_app/utilities_tab.py
# version: 2.2
# last-updated: 2025-08-21
# description: Hoàn thiện logic lọc phụ đề và dọn dẹp code debug.

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import re
import yt_dlp
import os
import datetime
import html
import logging

class UtilitiesTab(ttk.Frame):
    def __init__(self, parent, db_manager, main_app_instance):
        super().__init__(parent, padding="10")
        self.db_manager = db_manager
        self.main_app = main_app_instance
        self.current_video_info = {}
        self.available_langs_data = {}

        self._create_widgets()
        self.load_subtitle_library()

    def _create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        input_frame = ttk.LabelFrame(self, text="Tải phụ đề YouTube", padding="10")
        input_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        ttk.Label(input_frame, text="Dán link YouTube:").grid(row=0, column=0, padx=(0, 5))
        self.url_entry = ttk.Entry(input_frame)
        self.url_entry.grid(row=0, column=1, sticky="ew")
        self.url_entry.bind("<Return>", self._on_url_enter)
        
        self._setup_entry_context_menu(self.url_entry)
        
        self.fetch_button = ttk.Button(input_frame, text="Liệt kê Phụ đề", command=self._on_url_enter, style="Accent.TButton")
        self.fetch_button.grid(row=0, column=2, padx=(5, 0))

        self.results_frame = ttk.Frame(self)
        self.results_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))

        library_frame = ttk.LabelFrame(self, text="Thư viện Phụ đề đã lưu", padding=10)
        library_frame.grid(row=2, column=0, sticky="nsew")
        library_frame.columnconfigure(0, weight=1)
        library_frame.rowconfigure(0, weight=1)

        columns = ("title", "lang", "type", "date")
        self.sub_library_tree = ttk.Treeview(library_frame, columns=columns, show="headings")
        self.sub_library_tree.heading("title", text="Tên Video"); self.sub_library_tree.heading("lang", text="Ngôn ngữ"); self.sub_library_tree.heading("type", text="Loại"); self.sub_library_tree.heading("date", text="Ngày tải")
        self.sub_library_tree.column("title", width=400); self.sub_library_tree.column("lang", width=100); self.sub_library_tree.column("type", width=120); self.sub_library_tree.column("date", width=150)
        
        scrollbar = ttk.Scrollbar(library_frame, orient="vertical", command=self.sub_library_tree.yview)
        self.sub_library_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.sub_library_tree.pack(expand=True, fill="both")
        
        self.status_label = ttk.Label(self, text="Sẵn sàng.")
        self.status_label.grid(row=3, column=0, sticky="w", pady=(10, 0))
        
    # Thêm hàm mới này vào bất kỳ đâu bên trong lớp UtilitiesTab
    def _setup_entry_context_menu(self, entry_widget):
        """Tạo menu chuột phải cho một widget Entry."""
        menu = tk.Menu(entry_widget, tearoff=0)
        menu.add_command(label="Cắt", command=lambda: entry_widget.event_generate("<<Cut>>"))
        menu.add_command(label="Sao chép", command=lambda: entry_widget.event_generate("<<Copy>>"))
        menu.add_command(label="Dán", command=lambda: entry_widget.event_generate("<<Paste>>"))
        menu.add_separator()
        menu.add_command(label="Chọn tất cả", command=lambda: entry_widget.select_range(0, 'end'))

        def show_menu(event):
            menu.tk_popup(event.x_root, event.y_root)

        entry_widget.bind("<Button-3>", show_menu)
        
    def _on_url_enter(self, event=None):
        url = self.url_entry.get().strip()
        if not url: return
        for widget in self.results_frame.winfo_children(): widget.destroy()
        self.status_label.config(text="Đang tìm kiếm phụ đề, vui lòng chờ..."); self.fetch_button.config(state=tk.DISABLED)
        threading.Thread(target=self._fetch_subtitles_thread, args=(url,), daemon=True).start()

    def _fetch_subtitles_thread(self, url):
        try:
            ydl_opts = {'quiet': True, 'listsubtitles': True, 'verbose': False}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                self.current_video_info = {'title': info.get('title', 'Không có tiêu đề'), 'url': url}
                manual_subs = info.get('subtitles', {})
                auto_subs = info.get('automatic_captions', {})
                self.main_app.root.after_idle(self._populate_results, manual_subs, auto_subs)
        except Exception as e:
            self.main_app.root.after_idle(lambda err=e: self.status_label.config(text=f"Lỗi: {str(err)}"))
        finally:
            self.main_app.root.after_idle(lambda: self.fetch_button.config(state=tk.NORMAL))

    # hotfix - 2025-08-21 - Logic cuối cùng, ưu tiên và loại bỏ phụ đề trùng lặp
    def _populate_results(self, manual, auto):
        for widget in self.results_frame.winfo_children(): widget.destroy()
        self.available_langs_data.clear()

        # Bước 1: Tạo một danh sách ưu tiên để xử lý trùng lặp
        # Key là mã ngôn ngữ chính (ví dụ: 'en'), value là (mã đầy đủ, is_auto, data)
        best_subs = {}

        # Ưu tiên 1: Phụ đề có sẵn (manual) luôn là tốt nhất
        for lang_code, data in manual.items():
            main_lang = lang_code.split('-')[0]
            best_subs[main_lang] = (lang_code, False, data)

        # Ưu tiên 2: Phụ đề tự động, chỉ lấy bản gốc và ưu tiên bản "original"
        for lang_code, data in auto.items():
            main_lang = lang_code.split('-')[0]
            is_translation = any('&tlang=' in fmt.get('url', '') for fmt in data)
            
            if not is_translation:
                # Nếu ngôn ngữ này chưa có trong danh sách ưu tiên (tức là chưa có bản manual)
                if main_lang not in best_subs:
                    # Nếu là bản original (-orig), nó có độ ưu tiên cao
                    if lang_code.endswith('-orig'):
                        best_subs[main_lang] = (lang_code, True, data)
                    # Nếu chưa có bản -orig, thì lấy bản thường
                    elif main_lang not in [k for k in best_subs.keys() if k.endswith('-orig')]:
                        best_subs[main_lang] = (lang_code, True, data)

        # Bước 2: Phân loại lại kết quả cuối cùng để hiển thị
        manual_to_display = {info[0]: info[2] for lang, info in best_subs.items() if not info[1]}
        auto_to_display = {info[0]: info[2] for lang, info in best_subs.items() if info[1]}

        # Bước 3: Hiển thị giao diện
        if manual_to_display:
            manual_frame = ttk.LabelFrame(self.results_frame, text="Phụ đề có sẵn (Chất lượng cao nhất)", padding=10)
            manual_frame.pack(fill="x", expand=True, pady=(0, 10))
            # ... (Code hiển thị nút cho manual_to_display)
            row, col = 0, 0
            for lang_code, data in sorted(manual_to_display.items()):
                self.available_langs_data[lang_code] = {'is_auto': False}
                lang_name = data[0].get('name', lang_code)
                btn = ttk.Button(manual_frame, text=lang_name, command=lambda lc=lang_code: self._download_subtitle(lc))
                btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
                col += 1
                if col >= 5: col = 0; row += 1


        if auto_to_display:
            auto_frame = ttk.LabelFrame(self.results_frame, text="Phụ đề Tự động GỐC (Do YouTube tạo)", padding=10)
            auto_frame.pack(fill="x", expand=True)
            # ... (Code hiển thị nút cho auto_to_display)
            row, col = 0, 0
            for lang_code, data in sorted(auto_to_display.items()):
                self.available_langs_data[lang_code] = {'is_auto': True}
                lang_name = data[0].get('name', lang_code)
                btn = ttk.Button(auto_frame, text=f"{lang_name} (Tự động)", command=lambda lc=lang_code: self._download_subtitle(lc))
                btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
                col += 1
                if col >= 5: col = 0; row += 1


        total_found = len(self.available_langs_data)
        if total_found == 0:
            self.status_label.config(text="Không tìm thấy phụ đề nào (bản có sẵn hoặc tự động gốc).")
        else:
            self.status_label.config(text=f"Đã tìm thấy {total_found} phụ đề hợp lệ. Vui lòng chọn để tải.")

    def _download_subtitle(self, lang_code):
        if not lang_code in self.available_langs_data:
            self.status_label.config(text=f"Lỗi logic: Không tìm thấy dữ liệu cho ngôn ngữ '{lang_code}'."); return
        is_auto = self.available_langs_data[lang_code]['is_auto']
        self.status_label.config(text=f"Đang chuẩn bị tải phụ đề '{lang_code}'...")
        self.fetch_button.config(state=tk.DISABLED)
        for widget in self.results_frame.winfo_children():
            if isinstance(widget, ttk.LabelFrame):
                for button in widget.winfo_children():
                    if isinstance(button, ttk.Button): button.config(state=tk.DISABLED)
        threading.Thread(target=self._download_thread, args=(lang_code, is_auto), daemon=True).start()

    def _download_thread(self, lang_code, is_auto):
        try:
            self.main_app.root.after_idle(lambda: self.status_label.config(text=f"Đang tải nội dung '{lang_code}'..."))
            temp_dir = os.path.join(os.path.dirname(self.main_app.db_manager.db_path), "temp_subs")
            os.makedirs(temp_dir, exist_ok=True)
            outtmpl = os.path.join(temp_dir, '%(id)s.%(ext)s')

            ydl_opts = {
                'writesubtitles': not is_auto,
                'writeautomaticsub': is_auto,
                'subtitleslangs': [lang_code],
                'skip_download': True,
                'outtmpl': outtmpl,
                'quiet': True, 'verbose': False, 'encoding': 'utf-8'
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.current_video_info['url'], download=True)
                video_id = info.get('id'); video_title = info.get('title', 'Không có tiêu đề')
                
                expected_filename_base = os.path.join(temp_dir, f"{video_id}.{lang_code}")
                possible_extensions = ['.vtt', '.srt']; temp_filename = None
                for ext in possible_extensions:
                    if os.path.exists(expected_filename_base + ext):
                        temp_filename = expected_filename_base + ext; break
                if not temp_filename: raise Exception(f"Không tìm thấy file phụ đề tạm thời cho '{lang_code}'.")
                with open(temp_filename, 'r', encoding='utf-8') as f: raw_content = f.read()
                os.remove(temp_filename)

            self.main_app.root.after_idle(lambda: self.status_label.config(text="Đã tải xong. Đang dọn dẹp..."))
            cleaned_content = self._clean_subtitle_content(raw_content)

            db_data = {'video_title': video_title, 'youtube_url': self.current_video_info['url'], 'language': lang_code, 'is_auto_generated': is_auto, 'content': cleaned_content}
            self.db_manager.add_subtitle(db_data)

            sanitized_title = re.sub(r'[\\/*?:"<>|]', "", video_title)
            file_prefix = f"[{lang_code.upper()}{' - Auto' if is_auto else ''}]"
            default_filename = f"{file_prefix} - {sanitized_title}.txt"
            
            def ask_save_file():
                filepath = filedialog.asksaveasfilename(initialfile=default_filename, defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
                if filepath:
                    with open(filepath, 'w', encoding='utf-8') as f: f.write(cleaned_content)
                    self.status_label.config(text=f"Đã lưu thành công vào: {os.path.basename(filepath)}")
                else:
                    self.status_label.config(text="Đã hủy lưu file.")
                self.load_subtitle_library()
                for widget in self.results_frame.winfo_children(): widget.destroy()

            self.main_app.root.after_idle(ask_save_file)
            
        except Exception as e:
            self.main_app.root.after_idle(lambda err=e: self.status_label.config(text=f"Lỗi: {str(err)}"))
        finally:
            self.main_app.root.after_idle(lambda: self.fetch_button.config(state=tk.NORMAL))
    
    def _clean_subtitle_content(self, raw_content):
        try:
            decoded_content = html.unescape(raw_content)
            cleaned = re.sub(r'^WEBVTT.*?\n', '', decoded_content, flags=re.MULTILINE | re.IGNORECASE)
            cleaned = re.sub(r'^(Kind|Language):.*?\n', '', cleaned, flags=re.MULTILINE)
            cleaned = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}.*?(?:\n|$)', '', cleaned)
            cleaned = re.sub(r'<[^>]+>', '', cleaned)
            lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
            unique_lines = []
            for line in lines:
                if line not in unique_lines: unique_lines.append(line)
            final_text = ' '.join(unique_lines)
            final_text = re.sub(r'\s{2,}', ' ', final_text).strip()
            return final_text
        except Exception as e:
            self.main_app.log_message(f"[ERROR] Lỗi khi dọn dẹp phụ đề: {e}")
            return raw_content
        
    # hotfix - 2025-08-21 - Sửa lỗi AttributeError do dùng .get() trên sqlite3.Row
    def load_subtitle_library(self):
        for item in self.sub_library_tree.get_children(): self.sub_library_tree.delete(item)
        
        # Giả định get_all_subtitles trả về danh sách các đối tượng sqlite3.Row
        subtitles = self.db_manager.get_all_subtitles() 
        if not subtitles: return

        for sub in subtitles:
            try:
                # SỬA LỖI TẠI ĐÂY: Truy cập bằng key thay vì .get()
                is_auto = sub['is_auto_generated']
                sub_type = "Tự động" if is_auto else "Có sẵn"
                
                timestamp_str = sub['download_timestamp']
                video_title = sub['video_title']
                language = sub['language']

                try:
                    dt_object = datetime.datetime.strptime(timestamp_str.split('.')[0], '%Y-%m-%d %H:%M:%S')
                    formatted_time = dt_object.strftime('%d-%m-%Y %H:%M')
                except (ValueError, TypeError):
                    formatted_time = timestamp_str
                    
                self.sub_library_tree.insert("", "end", values=(video_title, language, sub_type, formatted_time))
            except (IndexError, KeyError) as e:
                self.main_app.log_message(f"[ERROR] Lỗi khi đọc dữ liệu phụ đề từ CSDL: {e}")