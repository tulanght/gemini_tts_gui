# file-path: src/gemini_tts_app/editorial_assistant_tab.py
# version: 1.0
# last-updated: 2025-07-22
# description: Module chuyên trách cho tab Trợ lý Biên tập, được tái cấu trúc từ main_app.py.

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from .thumbnail_preview import ThumbnailPreviewWindow

class EditorialAssistantTab(ttk.Frame):
    def __init__(self, parent, db_manager, main_app_instance):
        super().__init__(parent, padding="10")
        self.db_manager = db_manager
        self.main_app = main_app_instance

        self._full_options_text = []
        self.assistant_mode = tk.StringVar(value="title")

        self._create_widgets()

    # hotfix - 2025-07-24 - Thêm tùy chọn 'uniform' để ép tỉ lệ cột 1:3 hiển thị chính xác
    def _create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # --- KHUNG NHẬP LIỆU CHUNG ---
        input_pane = ttk.LabelFrame(self, text="1. Dán toàn bộ phản hồi của Gemini tại đây", padding=10)
        input_pane.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        input_pane.rowconfigure(0, weight=1)
        input_pane.columnconfigure(0, weight=1)
        self.assistant_input_text = scrolledtext.ScrolledText(input_pane, wrap=tk.WORD, height=10)
        self.assistant_input_text.grid(row=0, column=0, sticky="nsew")
        self.parse_button = ttk.Button(input_pane, text="Bóc Tách & Phân Tích", command=self.parse_input_text, style="Accent.TButton")
        self.parse_button.grid(row=1, column=0, sticky="ew", pady=(10, 0))

        # --- KHU VỰC LÀM VIỆC VỚI CÁC TAB CON ---
        main_work_area = ttk.Frame(self)
        main_work_area.grid(row=1, column=0, sticky="nsew")
        
        # THAY ĐỔI TẠI ĐÂY: Thêm 'uniform' để buộc áp dụng tỉ lệ
        main_work_area.columnconfigure(0, weight=1, uniform="group1") 
        main_work_area.columnconfigure(1, weight=3, uniform="group1")
        main_work_area.rowconfigure(0, weight=1)

        # --- KHUNG BÊN TRÁI: DANH SÁCH LỰA CHỌN ---
        list_pane = ttk.LabelFrame(main_work_area, text="2. Các lựa chọn đã được xử lý", padding=10)
        list_pane.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        list_pane.rowconfigure(0, weight=1)
        list_pane.columnconfigure(0, weight=1)
        self.options_display_text = scrolledtext.ScrolledText(list_pane, wrap=tk.WORD, height=10)
        self.options_display_text.grid(row=0, column=0, sticky="nsew")
        self.options_display_text.tag_configure("highlight", background="lightblue")
        self.options_display_text.config(state=tk.DISABLED)

        # --- KHUNG BÊN PHẢI: SOẠN THẢO VÀ CHỐT PHƯƠNG ÁN ---
        editor_pane = ttk.LabelFrame(main_work_area, text="3. Soạn thảo & Chốt phương án", padding=10)
        editor_pane.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        editor_pane.rowconfigure(0, weight=1)
        editor_pane.columnconfigure(0, weight=1)

        self.sub_notebook = ttk.Notebook(editor_pane)
        self.sub_notebook.grid(row=0, column=0, columnspan=2, sticky="nsew")

        # Tạo các tab con
        self.title_tab = self._create_editor_sub_tab("Tiêu đề", "title")
        self.thumbnail_tab = self._create_editor_sub_tab("Thumbnail", "thumbnail")
        self.hook_tab = self._create_editor_sub_tab("Hook", "hook")

        self.sub_notebook.add(self.title_tab, text="Tiêu đề")
        self.sub_notebook.add(self.thumbnail_tab, text="Thumbnail")
        self.sub_notebook.add(self.hook_tab, text="Hook")

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

        save_button = ttk.Button(action_frame, text=f"Chốt & Lưu {name}", state=tk.DISABLED, command=lambda: self.save_final_version(editor_text, mode_value), style="Accent.TButton")
        save_button.grid(row=0, column=2, sticky="e", padx=5)

        # Lưu các widget vào instance để có thể truy cập sau này
        frame.editor_text = editor_text
        frame.counter_label = counter_label
        frame.save_button = save_button

        editor_text.bind("<KeyRelease>", lambda event, f=frame, m=mode_value: self.update_editor_metrics(event, f, m))

        return frame
        
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
            return None # Không có tab nào được chọn
        return None

    def _parse_titles(self, text):
        # (Nội dung hàm này giữ nguyên như trong main_app.py)
        cleaned_options = []
        try:
            blocks = text.split('---')
            for block in blocks:
                if "**Tiêu đề:**" not in block:
                    continue
                lines = block.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith("**Tiêu đề:**"):
                        raw_title = line.split(":", 1)[1]
                        clean_title = raw_title.replace('**', '').strip()
                        if clean_title:
                            cleaned_options.append(clean_title)
                        break 
            return cleaned_options
        except Exception as e:
            self.main_app.log_message(f"Lỗi trong quá trình bóc tách tiêu đề: {e}")
            return []

    def _parse_thumbnails(self, text: str) -> list[str]:
        # (Nội dung hàm này giữ nguyên như trong main_app.py)
        self.main_app.log_message("Bắt đầu bóc tách kịch bản thumbnail...")
        try:
            blocks = text.split("---")
            cleaned_options = []
            for block in blocks[1:]:
                if not block.strip():
                    continue
                script_lines = []
                for line in block.strip().split('\n'):
                    stripped_line = line.strip()
                    is_bolded = stripped_line.startswith('**') and stripped_line.endswith('**')
                    is_style_line = '(phong cách' in stripped_line.lower()
                    if is_bolded and not is_style_line:
                        clean_line = stripped_line.replace('**', '').strip()
                        if clean_line:
                            script_lines.append(clean_line)
                if script_lines:
                    full_script = "\n".join(script_lines)
                    cleaned_options.append(full_script)
            self.main_app.log_message(f"Hoàn tất. Tìm thấy {len(cleaned_options)} kịch bản hợp lệ.")
            return cleaned_options
        except Exception as e:
            self.main_app.log_message(f"[ERROR] Lỗi bóc tách thumbnail: {e}")
            return []
    
    def _parse_hooks(self, text: str) -> list[str]:
        """Bóc tách các đoạn hook, thường được đánh dấu bằng số."""
        self.main_app.log_message("Bắt đầu bóc tách Hook mở đầu...")
        # Đây là một logic giả định, có thể cần tinh chỉnh
        import re
        # Tìm các dòng bắt đầu bằng số theo sau là dấu chấm hoặc ngoặc
        hooks = re.findall(r'^\d[\.\)]\s*(.*)', text, re.MULTILINE)
        cleaned_hooks = [hook.strip() for hook in hooks if hook.strip()]
        self.main_app.log_message(f"Hoàn tất. Tìm thấy {len(cleaned_hooks)} hook hợp lệ.")
        return cleaned_hooks

    def parse_input_text(self):
        full_text = self.assistant_input_text.get("1.0", tk.END)
        if not full_text.strip():
            messagebox.showwarning("Thông báo", "Vùng nhập liệu đang trống.", parent=self)
            return

        # Tự động nhận diện chế độ
        if "KỊCH BẢN THUMBNAIL" in full_text.upper() or "PHONG CÁCH:" in full_text.upper():
            mode = "thumbnail"
            self.sub_notebook.select(self.thumbnail_tab)
        elif "HOOK" in full_text.upper():
             mode = "hook"
             self.sub_notebook.select(self.hook_tab)
        else:
            mode = "title"
            self.sub_notebook.select(self.title_tab)

        if mode == "title":
            cleaned_options = self._parse_titles(full_text)
        elif mode == "thumbnail":
            cleaned_options = self._parse_thumbnails(full_text)
        else: # mode == "hook"
            cleaned_options = self._parse_hooks(full_text)
        
        if not cleaned_options:
            messagebox.showinfo("Không tìm thấy", "Không thể bóc tách được lựa chọn nào.", parent=self)
            return

        self._full_options_text = cleaned_options
        self.display_parsed_options(cleaned_options)
        messagebox.showinfo("Hoàn tất", f"Đã bóc tách {len(cleaned_options)} lựa chọn theo chế độ '{mode}'.", parent=self)

    def display_parsed_options(self, options):
        self.options_display_text.config(state=tk.NORMAL)
        self.options_display_text.delete("1.0", tk.END)

        for tag in self.options_display_text.tag_names():
            if tag.startswith("option_"):
                self.options_display_text.tag_delete(tag)

        separator = "\n" + ("-" * 40) + "\n\n"

        for i, option_text in enumerate(options):
            tag_name = f"option_{i}"
            start_index = self.options_display_text.index(tk.END)
            
            display_header = f"--- LỰA CHỌN {i+1} ---\n"
            self.options_display_text.insert(tk.END, display_header, ("h2", "center"))
            self.options_display_text.insert(tk.END, option_text)
            
            end_index = self.options_display_text.index(tk.END)
            
            self.options_display_text.tag_add(tag_name, start_index, f"{end_index}-1c")
            self.options_display_text.tag_bind(tag_name, "<Button-1>", lambda e, index=i: self.on_text_option_clicked(e, index))
            
            if i < len(options) - 1:
                self.options_display_text.insert(tk.END, separator, ("separator", "center"))

        self.options_display_text.config(state=tk.DISABLED)

    def on_text_option_clicked(self, event, index):
        current_frame = self.get_current_editor_frame()
        if not current_frame: return

        # Bỏ highlight tất cả các lựa chọn
        for tag in self.options_display_text.tag_names():
            if tag.startswith("option_"):
                self.options_display_text.tag_configure(tag, background="white")
        
        # Highlight lựa chọn được nhấp
        tag_name = f"option_{index}"
        self.options_display_text.tag_configure(tag_name, background="lightblue")

        if hasattr(self, '_full_options_text') and 0 <= index < len(self._full_options_text):
            full_text = self._full_options_text[index]
            current_frame.editor_text.delete("1.0", tk.END)
            current_frame.editor_text.insert("1.0", full_text)
            self.update_editor_metrics(None, current_frame, self.sub_notebook.tab(self.sub_notebook.select(), "text").lower())
    
    def update_editor_metrics(self, event, frame, mode):
        # (Nội dung hàm này cần được điều chỉnh lại từ main_app.py để hoạt động với frame và mode)
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
            elif TITLE_CHAR_LIMIT_GOOD_MIN <= char_count <= TITLE_CHAR_LIMIT_GOOD_MAX:
                label_color, button_state = COLOR_OK, tk.NORMAL
            elif char_count > TITLE_CHAR_LIMIT_MAX:
                label_color = COLOR_ERROR
            else:
                label_color = COLOR_WARN
        else: # "thumbnail" hoặc "hook"
            label_text = f"Ký tự: {char_count} | Từ: {word_count} | Dòng: {line_count}"
            if char_count > 0:
                label_color, button_state = COLOR_OK, tk.NORMAL

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

        item_type_map = {"tiêu đề": "Title", "thumbnail": "Thumbnail", "hook": "Hook"}
        item_type = item_type_map.get(mode.lower())
        
        if not item_type: return

        success = self.db_manager.add_or_update_item(self.main_app.active_project_id, item_type, final_text)

        if success:
            messagebox.showinfo("Thành công", f"Đã lưu '{item_type}' vào dự án '{self.main_app.active_project_name}' thành công!", parent=self)
            self.main_app._check_and_update_project_status_color()
            editor_widget.delete("1.0", tk.END)
        else:
            messagebox.showerror("Thất bại", "Lỗi khi lưu vào cơ sở dữ liệu.", parent=self)