# file-path: src/gemini_tts_app/editorial_assistant_tab.py
# version: 1.1
# last-updated: 2025-07-30
# description: Sửa lỗi logic nhận dạng, xóa hàm parse_input_text bị trùng lặp.

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from .thumbnail_preview import ThumbnailPreviewWindow
import re

class EditorialAssistantTab(ttk.Frame):
    def __init__(self, parent, db_manager, main_app_instance):
        super().__init__(parent, padding="10")
        self.db_manager = db_manager
        self.main_app = main_app_instance
        self._full_options_text = []
        self.assistant_mode = tk.StringVar(value="title")
        self._create_widgets()
        self.set_active(False)

    def _create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        input_pane = ttk.LabelFrame(self, text="1. Dán toàn bộ phản hồi của Gemini tại đây", padding=10)
        input_pane.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        input_pane.rowconfigure(0, weight=1)
        input_pane.columnconfigure(0, weight=1)
        self.assistant_input_text = scrolledtext.ScrolledText(input_pane, wrap=tk.WORD, height=10)
        self.assistant_input_text.grid(row=0, column=0, sticky="nsew")
        self.parse_button = ttk.Button(input_pane, text="Bóc Tách & Phân Tích", command=self.parse_input_text, style="Accent.TButton")
        self.parse_button.grid(row=1, column=0, sticky="ew", pady=(10, 0))

        main_work_area = ttk.Frame(self)
        main_work_area.grid(row=1, column=0, sticky="nsew")
        main_work_area.columnconfigure(0, weight=1, uniform="group1") 
        main_work_area.columnconfigure(1, weight=3, uniform="group1")
        main_work_area.rowconfigure(0, weight=1)

        list_pane = ttk.LabelFrame(main_work_area, text="2. Các lựa chọn đã được xử lý", padding=10)
        list_pane.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        list_pane.rowconfigure(0, weight=1)
        list_pane.columnconfigure(0, weight=1)
        self.options_display_text = scrolledtext.ScrolledText(list_pane, wrap=tk.WORD, height=10)
        self.options_display_text.grid(row=0, column=0, sticky="nsew")
        self.options_display_text.tag_configure("highlight", background="lightblue")
        self.options_display_text.config(state=tk.DISABLED)

        editor_pane = ttk.LabelFrame(main_work_area, text="3. Soạn thảo & Chốt phương án", padding=10)
        editor_pane.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        editor_pane.rowconfigure(0, weight=1)
        editor_pane.columnconfigure(0, weight=1)

        self.sub_notebook = ttk.Notebook(editor_pane)
        self.sub_notebook.grid(row=0, column=0, columnspan=2, sticky="nsew")

        self.title_tab = self._create_editor_sub_tab("Tiêu đề", "title")
        self.thumbnail_tab = self._create_editor_sub_tab("Thumbnail", "thumbnail")
        self.hook_tab = self._create_editor_sub_tab("Hook", "hook")

        self.sub_notebook.add(self.title_tab, text="Tiêu đề")
        self.sub_notebook.add(self.thumbnail_tab, text="Thumbnail")
        self.sub_notebook.add(self.hook_tab, text="Hook")
        
    def set_active(self, is_active):
        state = tk.NORMAL if is_active else tk.DISABLED
        # Vô hiệu hóa tất cả các widget con một cách an toàn
        for widget in self.winfo_children():
            self._recursive_widget_state(widget, state)
    def _recursive_widget_state(self, parent_widget, state):
        try:
            parent_widget.config(state=state)
        except tk.TclError:
            pass
        for child in parent_widget.winfo_children():
            self._recursive_widget_state(child, state)
    
    def _create_editor_sub_tab(self, name, mode_value):
        frame = ttk.Frame(self.sub_notebook, padding="10")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        editor_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=8)
        editor_text.grid(row=0, column=0, sticky="nsew")
        
        action_frame = ttk.Frame(frame)
        action_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        action_frame.columnconfigure(0, weight=1)

        counter_label = ttk.Label(action_frame, text="Ký tự: 0 | Từ: 0", font=("Segoe UI", 10))
        counter_label.grid(row=0, column=0, sticky="w", padx=5)

        if mode_value == "thumbnail":
            preview_button = ttk.Button(action_frame, text="Xem trước Thumbnail", command=lambda: self.show_thumbnail_preview(editor_text))
            preview_button.grid(row=0, column=1, sticky="e", padx=5)

        if mode_value == "hook":
            insert_button = ttk.Button(action_frame, text="🚀 Chèn vào đầu truyện", command=lambda: self._insert_hook_into_story(editor_text), style="Accent.TButton")
            insert_button.grid(row=0, column=2, sticky="e", padx=5)

        save_button = ttk.Button(action_frame, text=f"Chốt & Lưu {name}", state=tk.DISABLED, command=lambda: self.save_final_version(editor_text, mode_value))
        save_button.grid(row=0, column=3, sticky="e", padx=5)

        frame.editor_text = editor_text
        frame.counter_label = counter_label
        frame.save_button = save_button

        editor_text.bind("<KeyRelease>", lambda event, f=frame, m=mode_value: self.update_editor_metrics(event, f, m))
        return frame

    def _insert_hook_into_story(self, editor_widget):
        hook_content = editor_widget.get("1.0", tk.END).strip()
        if not hook_content:
            messagebox.showwarning("Nội dung trống", "Không có nội dung hook để chèn.", parent=self)
            return
        if not self.main_app.active_project_id:
            messagebox.showwarning("Chưa có Dự án hoạt động", "Vui lòng vào tab 'Thư viện' và chọn một dự án để làm việc trước.", parent=self)
            return
        self.main_app.insert_hook_with_warning(hook_content)
        
    def get_current_editor_frame(self):
        """Lấy frame của tab con đang được chọn."""
        try:
            selected_tab_index = self.sub_notebook.index(self.sub_notebook.select())
            if selected_tab_index == 0:
                return self.title_tab
            elif selected_tab_index == 1:
                return self.thumbnail_tab
            elif selected_tab_index == 2:
                return self.hook_tab
        except tk.TclError:
            return None
        return None

    def _parse_titles(self, text: str) -> list[str]:
        """Bóc tách các lựa chọn tiêu đề từ định dạng mới (danh sách có số và trích dẫn)."""
        self.main_app.log_message("Bắt đầu bóc tách tiêu đề (logic mới)...")
        try:
            titles = re.findall(r'^\s*"(.+?)"\s*$', text, re.MULTILINE)
            cleaned_titles = [title.strip() for title in titles if title.strip()]
            self.main_app.log_message(f"Hoàn tất. Tìm thấy {len(cleaned_titles)} tiêu đề hợp lệ.")
            return cleaned_titles
        except Exception as e:
            self.main_app.log_message(f"Lỗi trong quá trình bóc tách tiêu đề: {e}")
            return []

    # hotfix - 2025-08-05 - Cập nhật logic để bóc tách định dạng thumbnail mới của Gemini
    def _parse_thumbnails(self, text: str) -> list[str]:
        """
        Bóc tách kịch bản thumbnail bằng cách tìm khối văn bản sau dòng
        '**KỊCH BẢN THUMBNAIL:**'.
        """
        self.main_app.log_message("Bắt đầu bóc tách kịch bản thumbnail (logic mới)...")
        try:
            # Regex để tìm tất cả các khối văn bản nằm ngay sau dòng KỊCH BẢN THUMBNAIL
            # và kết thúc trước Lựa chọn tiếp theo hoặc cuối chuỗi.
            # [\s\S]*? : khớp với mọi ký tự (bao gồm cả xuống dòng) một cách không tham lam.
            # (?=...) : Positive lookahead, đảm bảo nó dừng lại trước Lựa chọn tiếp theo mà không ăn mất nó.
            pattern = re.compile(r'\*\*KỊCH BẢN THUMBNAIL:\*\*\s*([\s\S]*?)(?=\*\*Lựa chọn|\Z)', re.IGNORECASE)
            
            matches = pattern.findall(text)
            
            # Làm sạch các kết quả tìm được
            cleaned_options = [match.strip() for match in matches if match.strip()]
            
            self.main_app.log_message(f"Hoàn tất. Tìm thấy {len(cleaned_options)} kịch bản thumbnail hợp lệ.")
            return cleaned_options
        except Exception as e:
            self.main_app.log_message(f"[ERROR] Lỗi trong quá trình bóc tách thumbnail: {e}")
            return []
    
    def _parse_hooks(self, text: str) -> list[str]:
        self.main_app.log_message("Bắt đầu bóc tách Hook mở đầu...")
        try:
            parts = re.split(r'(?i)\s*Lựa chọn \d+:', text)
            hooks = []
            for part in parts[1:]:
                if not part.strip(): continue
                cleaned_part = re.sub(r'^\(.*\)\s*', '', part.strip(), flags=re.DOTALL)
                hooks.append(cleaned_part.strip())
            self.main_app.log_message(f"Hoàn tất. Tìm thấy {len(hooks)} hook hợp lệ.")
            return hooks
        except Exception as e:
            self.main_app.log_message(f"[ERROR] Lỗi khi bóc tách hook: {e}")
            return []

    def parse_input_text(self):
        full_text = self.assistant_input_text.get("1.0", tk.END)
        lower_full_text = full_text.lower()
        if not full_text.strip():
            messagebox.showwarning("Thông báo", "Vùng nhập liệu đang trống.", parent=self)
            return

        # Logic nhận dạng chính xác và có thứ tự ưu tiên
        if "kịch bản thumbnail" in lower_full_text or "phong cách:" in lower_full_text:
            mode = "thumbnail"
            self.sub_notebook.select(self.thumbnail_tab)
        elif ("hook mở đầu" in lower_full_text or "lựa chọn hook" in lower_full_text) and "lựa chọn 1" in lower_full_text:
             mode = "hook"
             self.sub_notebook.select(self.hook_tab)
        else:
            mode = "title"
            self.sub_notebook.select(self.title_tab)

        self.main_app.log_message(f"Đã nhận dạng chế độ là: '{mode}'")

        if mode == "title":
            cleaned_options = self._parse_titles(full_text)
        elif mode == "thumbnail":
            cleaned_options = self._parse_thumbnails(full_text)
        else: # mode == "hook"
            cleaned_options = self._parse_hooks(full_text)
        
        if not cleaned_options:
            messagebox.showinfo("Không tìm thấy", f"Không thể bóc tách được lựa chọn nào ở chế độ '{mode}'.", parent=self)
            return

        self._full_options_text = cleaned_options
        self.display_parsed_options(cleaned_options)
        messagebox.showinfo("Hoàn tất", f"Đã bóc tách {len(cleaned_options)} lựa chọn theo chế độ '{mode}'.", parent=self)

    def display_parsed_options(self, options):
        self.options_display_text.config(state=tk.NORMAL)
        self.options_display_text.delete("1.0", tk.END)
        for tag in self.options_display_text.tag_names():
            if tag.startswith("option_"): self.options_display_text.tag_delete(tag)

        separator = "\n" + ("-" * 40) + "\n\n"
        for i, option_text in enumerate(options):
            tag_name = f"option_{i}"
            start_index = self.options_display_text.index(tk.END)
            display_header = f"--- LỰA CHỌN {i+1} ---\n"
            self.options_display_text.insert(tk.END, display_header)
            self.options_display_text.insert(tk.END, option_text)
            end_index = self.options_display_text.index(tk.END)
            self.options_display_text.tag_add(tag_name, start_index, f"{end_index}-1c")
            self.options_display_text.tag_bind(tag_name, "<Button-1>", lambda e, index=i: self.on_text_option_clicked(e, index))
            if i < len(options) - 1: self.options_display_text.insert(tk.END, separator)
        self.options_display_text.config(state=tk.DISABLED)

    def on_text_option_clicked(self, event, index):
        current_frame = self.get_current_editor_frame()
        if not current_frame: return
        for tag in self.options_display_text.tag_names():
            if tag.startswith("option_"): self.options_display_text.tag_configure(tag, background="white")
        tag_name = f"option_{index}"
        self.options_display_text.tag_configure(tag_name, background="lightblue")
        if hasattr(self, '_full_options_text') and 0 <= index < len(self._full_options_text):
            full_text = self._full_options_text[index]
            current_frame.editor_text.delete("1.0", tk.END)
            current_frame.editor_text.insert("1.0", full_text)
            self.update_editor_metrics(None, current_frame, self.sub_notebook.tab(self.sub_notebook.select(), "text").lower())
    
    def update_editor_metrics(self, event, frame, mode):
        from .constants import (
            TITLE_CHAR_LIMIT_GOOD_MIN, TITLE_CHAR_LIMIT_GOOD_MAX, TITLE_CHAR_LIMIT_MAX,
            COLOR_OK, COLOR_WARN, COLOR_ERROR, COLOR_NORMAL
        )
        content = frame.editor_text.get("1.0", tk.END).strip()
        char_count = len(content)
        word_count = len(content.split()) if content else 0
        line_count = len([line for line in content.splitlines() if line.strip()])
        label_text, label_color, button_state = "", COLOR_NORMAL, tk.DISABLED
        if mode == "tiêu đề":
            label_text = f"Ký tự: {char_count} | Từ: {word_count}"
            if char_count == 0: pass
            elif TITLE_CHAR_LIMIT_GOOD_MIN <= char_count <= TITLE_CHAR_LIMIT_GOOD_MAX: label_color, button_state = COLOR_OK, tk.NORMAL
            elif char_count > TITLE_CHAR_LIMIT_MAX: label_color = COLOR_ERROR
            else: label_color = COLOR_WARN
        else:
            label_text = f"Ký tự: {char_count} | Từ: {word_count} | Dòng: {line_count}"
            if char_count > 0: label_color, button_state = COLOR_OK, tk.NORMAL
        frame.counter_label.config(text=label_text, foreground=label_color)
        frame.save_button.config(state=button_state)

    def show_thumbnail_preview(self, editor_widget):
        text_content = editor_widget.get("1.0", tk.END).strip()
        if not text_content:
            messagebox.showwarning("Nội dung trống", "Không có nội dung để xem trước.", parent=self)
            return
        ThumbnailPreviewWindow(parent=self.winfo_toplevel(), text_content=text_content, log_callback=self.main_app.log_message)

    def save_final_version(self, editor_widget, mode):
        if not self.main_app.active_project_id:
            messagebox.showwarning("Chưa có Dự án hoạt động", "Vui lòng vào tab 'Thư viện' và chọn một dự án để làm việc trước.", parent=self)
            return
        final_text = editor_widget.get("1.0", tk.END).strip()
        if not final_text:
            messagebox.showwarning("Nội dung trống", "Không có nội dung để lưu.", parent=self)
            return
        item_type_map = {"title": "Title", "thumbnail": "Thumbnail", "hook": "Hook"}
        item_type = item_type_map.get(mode)
        if not item_type: 
            self.main_app.log_message(f"[ERROR] Không thể xác định loại mục để lưu. Chế độ nhận được: {mode}")
            return
        if item_type == "Title" and len(final_text) > 100:
            messagebox.showwarning("Tiêu đề quá dài", f"Tiêu đề không được vượt quá 100 ký tự.\n(Độ dài hiện tại: {len(final_text)} ký tự)", parent=self)
            return
        success = self.db_manager.add_or_update_item(self.main_app.active_project_id, item_type, final_text)
        if success:
            messagebox.showinfo("Thành công", f"Đã lưu '{item_type}' vào dự án '{self.main_app.active_project_name}' thành công!", parent=self)
            self.main_app._check_and_update_project_status_color()
            editor_widget.delete("1.0", tk.END)
        else:
            messagebox.showerror("Thất bại", "Lỗi khi lưu vào cơ sở dữ liệu.", parent=self)