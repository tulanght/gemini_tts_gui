# file-path: src/gemini_tts_app/utilities_tab.py
# version: 3.2
# last-updated: 2025-08-22
# description: Phiên bản hoàn chỉnh, đầy đủ tất cả các hàm cần thiết.

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import re
import yt_dlp
import os
import datetime
import html
import logging
import pyperclip
from .subtitle_details_window import SubtitleDetailsWindow

class UtilitiesTab(ttk.Frame):
    def __init__(self, parent, db_manager, main_app_instance):
        super().__init__(parent, padding="10")
        self.db_manager = db_manager
        self.main_app = main_app_instance
        self.current_video_info = {}
        self.available_langs_data = {}
        self.hashtag_color_map = {}
        self.color_index = 0
        self.colors = ['#E8F8F5', '#FEF9E7', '#F4ECF7', '#EBF5FB', '#FDEDEC', '#F0F3F4']

        self._create_widgets()
        self.load_subtitle_library()

    def _create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        input_frame = ttk.LabelFrame(self, text="1. Tải phụ đề YouTube", padding="10")
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

        processing_frame = ttk.LabelFrame(self, text="2. Xử lý Nội dung & Tạo Prompt", padding="10")
        processing_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        processing_frame.columnconfigure(0, weight=1)
        self.selected_sub_content = scrolledtext.ScrolledText(processing_frame, height=7, wrap=tk.WORD, state=tk.DISABLED)
        self.selected_sub_content.grid(row=0, column=0, columnspan=5, sticky="ew", pady=(0, 10))
        prompt_buttons_frame = ttk.Frame(processing_frame)
        prompt_buttons_frame.grid(row=1, column=0, columnspan=5, sticky="w")
        ttk.Button(prompt_buttons_frame, text="Tóm tắt", command=lambda: self._generate_prompt("summary")).pack(side="left", padx=(0,5))
        ttk.Button(prompt_buttons_frame, text="Dịch sang Tiếng Việt", command=lambda: self._generate_prompt("translate")).pack(side="left", padx=5)
        ttk.Button(prompt_buttons_frame, text="Viết lại thành lời dẫn", command=lambda: self._generate_prompt("rewrite")).pack(side="left", padx=5)
        ttk.Button(prompt_buttons_frame, text="Tìm ý chính", command=lambda: self._generate_prompt("main_ideas")).pack(side="left", padx=5)
        self.generated_prompt_text = scrolledtext.ScrolledText(processing_frame, height=5, wrap=tk.WORD)
        self.generated_prompt_text.grid(row=2, column=0, columnspan=5, sticky="ew", pady=(10, 5))
        ttk.Button(processing_frame, text="Sao chép Prompt", command=self._copy_prompt, style="Accent.TButton").grid(row=3, column=0, columnspan=5, pady=(5,0))

        library_frame = ttk.LabelFrame(self, text="3. Thư viện Phụ đề", padding="10")
        library_frame.grid(row=3, column=0, sticky="nsew")
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
        self.sub_library_tree.bind("<Button-3>", self._show_library_context_menu)
        self.sub_library_tree.bind("<ButtonRelease-1>", self._on_subtitle_select)
        scrollbar = ttk.Scrollbar(library_frame, orient="vertical", command=self.sub_library_tree.yview)
        self.sub_library_tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky="ns")
        
        self.status_label = ttk.Label(self, text="Sẵn sàng.")
        self.status_label.grid(row=4, column=0, sticky="w", pady=(10, 0))
        self.library_context_menu = tk.Menu(self, tearoff=0)
        self.library_context_menu.add_command(label="Xóa Phụ đề đã chọn", command=self._on_delete_subtitle)

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

    def _populate_results(self, manual, auto):
        for widget in self.results_frame.winfo_children(): widget.destroy()
        self.available_langs_data.clear()
        best_subs = {}
        for lang_code, data in manual.items():
            if not data: continue
            main_lang = lang_code.split('-')[0]
            best_subs[main_lang] = (lang_code, False, data)
        for lang_code, data in auto.items():
            if not data: continue
            main_lang = lang_code.split('-')[0]
            is_translation = any('&tlang=' in fmt.get('url', '') for fmt in data)
            if not is_translation:
                if main_lang not in best_subs:
                    if lang_code.endswith('-orig'):
                        best_subs[main_lang] = (lang_code, True, data)
                    elif main_lang not in [k for k in best_subs.keys() if k.endswith('-orig')]:
                         best_subs[main_lang] = (lang_code, True, data)
        manual_to_display = {info[0]: info[2] for lang, info in best_subs.items() if not info[1]}
        auto_to_display = {info[0]: info[2] for lang, info in best_subs.items() if info[1]}
        if manual_to_display:
            manual_frame = ttk.LabelFrame(self.results_frame, text="Phụ đề có sẵn (Chất lượng cao nhất)", padding=10)
            manual_frame.pack(fill="x", expand=True, pady=(0, 10))
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
            self.status_label.config(text=f"Lỗi logic: Không tìm thấy dữ liệu cho '{lang_code}'."); return
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
            ydl_opts = {'writesubtitles': not is_auto, 'writeautomaticsub': is_auto, 'subtitleslangs': [lang_code], 'skip_download': True, 'outtmpl': outtmpl, 'quiet': True, 'verbose': False, 'encoding': 'utf-8'}
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

    def _populate_treeview(self, subtitles_to_load):
        for item in self.sub_library_tree.get_children():
            self.sub_library_tree.delete(item)
        if not subtitles_to_load: return
        for sub in subtitles_to_load:
            try:
                sub_id = sub['id']
                hashtags = self.db_manager.get_hashtags_for_subtitle(sub_id)
                sub_type = "Tự động" if sub['is_auto_generated'] else "Có sẵn"
                timestamp_str = sub['download_timestamp']
                try:
                    dt_object = datetime.datetime.strptime(timestamp_str.split('.')[0], '%Y-%m-%d %H:%M:%S')
                    formatted_time = dt_object.strftime('%d-%m-%Y %H:%M')
                except (ValueError, TypeError): formatted_time = timestamp_str
                row_tag = None
                if hashtags:
                    primary_hashtag = hashtags[0]
                    if primary_hashtag not in self.hashtag_color_map:
                        tag_name = f"style_{primary_hashtag.replace(' ', '_')}"
                        color = self.colors[self.color_index % len(self.colors)]
                        self.sub_library_tree.tag_configure(tag_name, background=color)
                        self.hashtag_color_map[primary_hashtag] = tag_name
                        self.color_index += 1
                    row_tag = self.hashtag_color_map[primary_hashtag]
                self.sub_library_tree.insert("", "end", values=(sub_id, sub['video_title'], sub['language'], sub_type, " ".join(hashtags), formatted_time), tags=(row_tag,) if row_tag else ())
            except (IndexError, KeyError) as e:
                self.main_app.log_message(f"[ERROR] Lỗi khi đọc dữ liệu phụ đề từ CSDL: {e}")

    def load_subtitle_library(self, event=None):
        if hasattr(self, 'search_entry') and self.search_entry: self.search_entry.delete(0, tk.END)
        all_subtitles = self.db_manager.get_all_subtitles()
        self._populate_treeview(all_subtitles)

    def _on_search(self, event=None):
        tag_to_search = self.search_entry.get().strip()
        if not tag_to_search:
            self.load_subtitle_library(); return
        filtered_subs = self.db_manager.get_subtitles_by_hashtag(tag_to_search)
        if not filtered_subs:
            self.status_label.config(text=f"Không tìm thấy phụ đề nào với hashtag: '{tag_to_search}'")
        else:
            self.status_label.config(text=f"Tìm thấy {len(filtered_subs)} kết quả.")
        self._populate_treeview(filtered_subs)

    def _on_open_subtitle_details(self, event=None):
        selected_item = self.sub_library_tree.focus()
        if not selected_item: return
        item_values = self.sub_library_tree.item(selected_item, "values")
        subtitle_id = item_values[0]
        SubtitleDetailsWindow(self, self.db_manager, subtitle_id, on_close_callback=self.load_subtitle_library)

    def _show_library_context_menu(self, event):
        item_id = self.sub_library_tree.identify_row(event.y)
        if item_id:
            self.sub_library_tree.selection_set(item_id)
            self.library_context_menu.tk_popup(event.x_root, event.y_root)

    def _on_delete_subtitle(self):
        selected_item = self.sub_library_tree.focus()
        if not selected_item: return
        item_values = self.sub_library_tree.item(selected_item, "values")
        subtitle_id = item_values[0]; video_title = item_values[1]
        if messagebox.askyesno("Xác nhận Xóa", f"Bạn có chắc chắn muốn xóa vĩnh viễn phụ đề cho video:\n\n'{video_title}'\n\nThao tác này không thể hoàn tác.", parent=self):
            if self.db_manager.delete_subtitle(subtitle_id):
                self.status_label.config(text="Đã xóa phụ đề thành công.")
                self.load_subtitle_library()
            else:
                messagebox.showerror("Lỗi", "Không thể xóa phụ đề khỏi CSDL.", parent=self)

    def _setup_entry_context_menu(self, entry_widget):
        menu = tk.Menu(entry_widget, tearoff=0)
        menu.add_command(label="Cắt", command=lambda: entry_widget.event_generate("<<Cut>>"))
        menu.add_command(label="Sao chép", command=lambda: entry_widget.event_generate("<<Copy>>"))
        menu.add_command(label="Dán", command=lambda: entry_widget.event_generate("<<Paste>>"))
        menu.add_separator()
        menu.add_command(label="Chọn tất cả", command=lambda: entry_widget.select_range(0, 'end'))
        def show_menu(event):
            menu.tk_popup(event.x_root, event.y_root)
        entry_widget.bind("<Button-3>", show_menu)

    def _on_subtitle_select(self, event=None):
        selected_item = self.sub_library_tree.focus()
        if not selected_item: return
        item_values = self.sub_library_tree.item(selected_item, "values")
        subtitle_id = item_values[0]
        details = self.db_manager.get_subtitle_details(subtitle_id)
        if details:
            self.selected_sub_content.config(state=tk.NORMAL)
            self.selected_sub_content.delete("1.0", tk.END)
            self.selected_sub_content.insert("1.0", details['content'])
            self.selected_sub_content.config(state=tk.DISABLED)
            self.generated_prompt_text.delete("1.0", tk.END)

    def _generate_prompt(self, mode):
        content = self.selected_sub_content.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Nội dung trống", "Vui lòng chọn một phụ đề từ thư viện trước.", parent=self)
            return
        prompt = ""
        if mode == "summary":
            prompt = f"Hãy tóm tắt nội dung sau đây thành một đoạn văn ngắn gọn, súc tích:\n\n---\n{content}\n---"
        elif mode == "translate":
            prompt = f"Hãy dịch toàn bộ nội dung sau đây sang Tiếng Việt một cách tự nhiên và chính xác:\n\n---\n{content}\n---"
        elif mode == "rewrite":
            prompt = f"Dựa vào nội dung gốc dưới đây, hãy viết lại thành một kịch bản lời dẫn (voice-over) cho video YouTube. Giọng văn cần tự nhiên, hấp dẫn và dễ nghe:\n\n---\n{content}\n---"
        elif mode == "main_ideas":
            prompt = f"Hãy phân tích và liệt kê các ý chính hoặc các luận điểm quan trọng nhất từ nội dung sau đây dưới dạng gạch đầu dòng:\n\n---\n{content}\n---"
        self.generated_prompt_text.delete("1.0", tk.END)
        self.generated_prompt_text.insert("1.0", prompt)
        self.status_label.config(text=f"Đã tạo prompt cho tác vụ '{mode}'.")

    def _copy_prompt(self):
        prompt_text = self.generated_prompt_text.get("1.0", tk.END).strip()
        if prompt_text:
            try:
                pyperclip.copy(prompt_text)
                self.status_label.config(text="Đã sao chép prompt vào clipboard!")
            except Exception as e:
                self.status_label.config(text=f"Lỗi sao chép: {e}")
                messagebox.showerror("Lỗi", "Không thể truy cập clipboard. Vui lòng đảm bảo thư viện 'pyperclip' đã được cài đặt.", parent=self)
        else:
            self.status_label.config(text="Không có prompt nào để sao chép.")