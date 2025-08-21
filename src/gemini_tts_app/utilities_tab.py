# file-path: src/gemini_tts_app/utilities_tab.py
# version: 2.3
# last-updated: 2025-08-22
# description: Nâng cấp thư viện phụ đề với tính năng tô màu hàng theo hashtag.

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import re
import yt_dlp
import os
import datetime
import html
import logging
from .subtitle_details_window import SubtitleDetailsWindow

class UtilitiesTab(ttk.Frame):
    def __init__(self, parent, db_manager, main_app_instance):
        super().__init__(parent, padding="10")
        self.db_manager = db_manager
        self.main_app = main_app_instance
        self.current_video_info = {}
        self.available_langs_data = {}

        # --- Cấu hình cho việc tô màu theo hashtag ---
        self.hashtag_color_map = {}
        self.color_index = 0
        # Danh sách các màu nền sáng, dễ chịu
        self.colors = ['#E8F8F5', '#FEF9E7', '#F4ECF7', '#EBF5FB', '#FDEDEC', '#F0F3F4']

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

        library_frame = ttk.LabelFrame(self, text="Thư viện Phụ đề", padding="10")
        library_frame.grid(row=2, column=0, sticky="nsew")
        library_frame.columnconfigure(0, weight=1)
        library_frame.rowconfigure(1, weight=1)

        search_frame = ttk.Frame(library_frame)
        search_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        ttk.Label(search_frame, text="Tìm theo Hashtag:").pack(side="left", padx=(0,5))
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<Return>", self._on_search)
        ttk.Button(search_frame, text="Tìm", command=self._on_search).pack(side="left", padx=5)
        ttk.Button(search_frame, text="Hiện tất cả", command=self.load_subtitle_library).pack(side="left")

        columns = ("id", "title", "lang", "type", "hashtags", "date")
        self.sub_library_tree = ttk.Treeview(library_frame, columns=columns, show="headings")
        self.sub_library_tree.grid(row=1, column=0, sticky="nsew")
        self.sub_library_tree.heading("id", text="ID"); self.sub_library_tree.heading("title", text="Tên Video"); self.sub_library_tree.heading("lang", text="Ngôn ngữ"); self.sub_library_tree.heading("type", text="Loại"); self.sub_library_tree.heading("hashtags", text="Hashtags"); self.sub_library_tree.heading("date", text="Ngày tải")
        self.sub_library_tree.column("id", width=0, stretch=tk.NO); self.sub_library_tree.column("title", width=300); self.sub_library_tree.column("lang", width=80); self.sub_library_tree.column("type", width=100); self.sub_library_tree.column("hashtags", width=200); self.sub_library_tree.column("date", width=120)
        self.sub_library_tree.bind("<Double-1>", self._on_open_subtitle_details)
        
        scrollbar = ttk.Scrollbar(library_frame, orient="vertical", command=self.sub_library_tree.yview)
        self.sub_library_tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky="ns")
        
        self.status_label = ttk.Label(self, text="Sẵn sàng.")
        self.status_label.grid(row=3, column=0, sticky="w", pady=(10, 0))
        
    def _populate_treeview(self, subtitles_to_load):
        """Hàm trung tâm để điền dữ liệu vào Treeview và áp dụng màu sắc."""
        for item in self.sub_library_tree.get_children():
            self.sub_library_tree.delete(item)

        if not subtitles_to_load:
            return

        for sub in subtitles_to_load:
            try:
                sub_id = sub['id']
                hashtags = self.db_manager.get_hashtags_for_subtitle(sub_id)
                sub_type = "Tự động" if sub['is_auto_generated'] else "Có sẵn"
                
                # ... (code xử lý thời gian) ...

                row_tag = None
                if hashtags:
                    primary_hashtag = hashtags[0]
                    if primary_hashtag not in self.hashtag_color_map:
                        tag_name = f"style_{primary_hashtag}"
                        color = self.colors[self.color_index % len(self.colors)]
                        self.sub_library_tree.tag_configure(tag_name, background=color)
                        self.hashtag_color_map[primary_hashtag] = tag_name
                        self.color_index += 1
                    row_tag = self.hashtag_color_map[primary_hashtag]

                self.sub_library_tree.insert("", "end", values=(
                    sub_id, sub['video_title'], sub['language'], sub_type, " ".join(hashtags), formatted_time
                ), tags=(row_tag,) if row_tag else ())
            except (IndexError, KeyError) as e:
                self.main_app.log_message(f"[ERROR] Lỗi khi đọc dữ liệu phụ đề từ CSDL: {e}")
                
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

    # hotfix - 2025-08-22 - Sửa lỗi NameError do thiếu logic định dạng thời gian
    def _populate_treeview(self, subtitles_to_load):
        """Hàm trung tâm để điền dữ liệu vào Treeview và áp dụng màu sắc."""
        for item in self.sub_library_tree.get_children():
            self.sub_library_tree.delete(item)

        if not subtitles_to_load:
            return

        for sub in subtitles_to_load:
            try:
                sub_id = sub['id']
                hashtags = self.db_manager.get_hashtags_for_subtitle(sub_id)
                sub_type = "Tự động" if sub['is_auto_generated'] else "Có sẵn"
                
                # --- BỔ SUNG LẠI LOGIC BỊ THIẾU ---
                timestamp_str = sub['download_timestamp']
                try:
                    dt_object = datetime.datetime.strptime(timestamp_str.split('.')[0], '%Y-%m-%d %H:%M:%S')
                    formatted_time = dt_object.strftime('%d-%m-%Y %H:%M')
                except (ValueError, TypeError):
                    formatted_time = timestamp_str
                # --- KẾT THÚC PHẦN BỔ SUNG ---

                row_tag = None
                if hashtags:
                    primary_hashtag = hashtags[0]
                    if primary_hashtag not in self.hashtag_color_map:
                        tag_name = f"style_{primary_hashtag.replace(' ', '_')}" # Đảm bảo tên tag hợp lệ
                        color = self.colors[self.color_index % len(self.colors)]
                        self.sub_library_tree.tag_configure(tag_name, background=color)
                        self.hashtag_color_map[primary_hashtag] = tag_name
                        self.color_index += 1
                    row_tag = self.hashtag_color_map[primary_hashtag]

                self.sub_library_tree.insert("", "end", values=(
                    sub_id, sub['video_title'], sub['language'], sub_type, " ".join(hashtags), formatted_time
                ), tags=(row_tag,) if row_tag else ())
            except (IndexError, KeyError) as e:
                self.main_app.log_message(f"[ERROR] Lỗi khi đọc dữ liệu phụ đề từ CSDL: {e}")

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
        
    def load_subtitle_library(self, event=None):
        if hasattr(self, 'search_entry') and self.search_entry:
            self.search_entry.delete(0, tk.END)
        all_subtitles = self.db_manager.get_all_subtitles()
        self._populate_treeview(all_subtitles)

    def _on_search(self, event=None):
        tag_to_search = self.search_entry.get().strip()
        if not tag_to_search:
            self.load_subtitle_library()
            return
        
        filtered_subs = self.db_manager.get_subtitles_by_hashtag(tag_to_search)
        if not filtered_subs:
            self.status_label.config(text=f"Không tìm thấy phụ đề nào với hashtag: '{tag_to_search}'")
        else:
            self.status_label.config(text=f"Tìm thấy {len(filtered_subs)} kết quả.")
        
        self._populate_treeview(filtered_subs)
    def _on_open_subtitle_details(self, event=None):
        """Mở cửa sổ chi tiết khi người dùng nhấp đúp."""
        selected_item = self.sub_library_tree.focus()
        if not selected_item: return
            
        item_values = self.sub_library_tree.item(selected_item, "values")
        subtitle_id = item_values[0] # Lấy ID từ cột đầu tiên
        
        SubtitleDetailsWindow(self, self.db_manager, subtitle_id, on_close_callback=self.load_subtitle_library)