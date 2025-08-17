# file-path: src/gemini_tts_app/long_form_composer_tab.py
# version: 2.0
# last-updated: 2025-08-12
# description: Tái cấu trúc khu vực "Lưu vào Thư viện" và logic nút lưu.

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import time
import logging

try:
    import pyperclip
except ImportError:
    pyperclip = None
class LongFormComposerTab(ttk.Frame):
    def __init__(self, parent, db_manager, main_app_instance):
        super().__init__(parent, padding="10")
        self.db_manager = db_manager
        self.main_app = main_app_instance
        self.continuation_prompt_var = tk.StringVar()
        self.floating_panel = None
        self.clipboard_monitoring_thread = None
        self.is_monitoring_clipboard = False
        self.last_clipboard_content = ""
        
        # Biến mới để theo dõi trạng thái nút lưu
        self.save_button_state = tk.BooleanVar(value=False)

        self._create_widgets()
        self.set_active(False) 
        
    # hotfix - 2025-08-12 - Cập nhật định nghĩa hàm để nhận project_name
    def set_active(self, is_active, project_name=None):
        """Kích hoạt hoặc vô hiệu hóa các thành phần chính của tab."""
        state = tk.NORMAL if is_active else tk.DISABLED
        self._recursive_widget_state(self, state)
        
        # Cập nhật label và trạng thái nút lưu
        if is_active and project_name:
            self.save_status_label.config(text=f"Lưu vào dự án đang hoạt động: '{project_name}'")
            self.save_to_db_button.config(state=tk.NORMAL)
        else:
            self.save_status_label.config(text="Lưu vào dự án đang hoạt động: (Chưa chọn)")
            self.save_to_db_button.config(state=tk.DISABLED)

    def _recursive_widget_state(self, parent_widget, state):
        try:
            parent_widget.config(state=state)
        except tk.TclError:
            pass
        for child in parent_widget.winfo_children():
            self._recursive_widget_state(child, state)
                    
    def _create_widgets(self):
        self.columnconfigure(0, weight=1)

        main_pane = ttk.LabelFrame(self, text="Bản thảo truyện", padding=10)
        main_pane.grid(row=0, column=0, sticky="nsew")
        main_pane.rowconfigure(0, weight=1)
        main_pane.columnconfigure(0, weight=1)

        self.composer_text = scrolledtext.ScrolledText(main_pane, wrap=tk.WORD, height=10)
        self.composer_text.grid(row=0, column=0, sticky="nsew")
        self.composer_text.bind("<KeyRelease>", self.update_composer_counter)

        self.composer_counter_label = ttk.Label(main_pane, text="Tổng cộng: 0 ký tự | 0 từ")
        self.composer_counter_label.grid(row=1, column=0, sticky="w", pady=(5,0))

        self.toggle_panel_button = ttk.Button(self, text="Mở Bảng điều khiển Viết truyện", command=self.toggle_composer_panel, style="Accent.TButton")
        self.toggle_panel_button.grid(row=1, column=0, pady=(10,0))
        
        # --- KHU VỰC "LƯU VÀO THƯ VIỆN" ĐÃ ĐƯỢC TÁI CẤU TRÚC ---
        project_frame = ttk.LabelFrame(self, text="Lưu vào Thư viện", padding=10)
        project_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=(10,0))
        project_frame.columnconfigure(0, weight=1)

        # Label hiển thị trạng thái thay cho Combobox
        self.save_status_label = ttk.Label(project_frame, text="Lưu vào dự án đang hoạt động: (Chưa chọn)")
        self.save_status_label.grid(row=0, column=0, padx=5, sticky="ew")
        
        # Nút lưu, trạng thái được quản lý bởi biến
        self.save_to_db_button = ttk.Button(project_frame, text="Lưu truyện vào Dự án", style="Accent.TButton", command=self._save_composer_story_to_project)
        self.save_to_db_button.grid(row=0, column=1, padx=5)

    # hotfix - 2025-08-13 - Xóa bỏ tham chiếu đến combobox không còn tồn tại
    def load_story_from_project(self, story_content, project_name):
        """Hàm công khai để main_app có thể tải truyện vào khi kích hoạt dự án."""
        self.composer_text.delete("1.0", tk.END)
        self.composer_text.insert("1.0", story_content)
        self.update_composer_counter()
        # Dòng code gây lỗi đã được xóa bỏ, không cần thiết nữa

    def toggle_composer_panel(self):
        if self.floating_panel and self.floating_panel.winfo_exists():
            self.floating_panel.destroy()
            self.floating_panel = None
            self.main_app.root.deiconify()
            self.toggle_panel_button.config(text="Mở Bảng điều khiển Viết truyện")
        else:
            self.create_floating_panel()
            self.main_app.root.iconify()
            self.toggle_panel_button.config(text="Đóng Bảng điều khiển")

    def create_floating_panel(self):
        if self.floating_panel and self.floating_panel.winfo_exists():
            self.floating_panel.lift()
            return
            
        self.floating_panel = tk.Toplevel(self.main_app.root)
        self.floating_panel.title("Bảng điều khiển")
        self.floating_panel.geometry("450x180")
        self.floating_panel.attributes("-topmost", True)
        self.floating_panel.protocol("WM_DELETE_WINDOW", self.toggle_composer_panel)

        panel_frame = ttk.Frame(self.floating_panel, padding=10)
        panel_frame.pack(expand=True, fill="both")
        panel_frame.columnconfigure(0, weight=1)

        button_frame = ttk.Frame(panel_frame)
        button_frame.grid(row=0, column=0, columnspan=2, pady=(0,10), sticky="ew")
        
        self.toggle_monitoring_button = ttk.Button(button_frame, text="Bắt đầu Theo dõi Clipboard", command=self.toggle_clipboard_monitoring)
        self.toggle_monitoring_button.pack(side="left", padx=(0,5))
        
        self.save_story_button = ttk.Button(button_frame, text="Lưu .txt...", command=self.save_story_to_file)
        self.save_story_button.pack(side="left")

        prompt_suggestion_frame = ttk.LabelFrame(panel_frame, text="Gợi ý Prompt tiếp theo", padding=10)
        prompt_suggestion_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10,0))
        prompt_suggestion_frame.columnconfigure(0, weight=1)

        self.continuation_prompt_entry = ttk.Entry(prompt_suggestion_frame, textvariable=self.continuation_prompt_var, state="readonly")
        self.continuation_prompt_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        self.copy_prompt_button = ttk.Button(prompt_suggestion_frame, text="Copy Prompt", command=self.copy_continuation_prompt)
        self.copy_prompt_button.grid(row=0, column=1, sticky="e")

    def toggle_clipboard_monitoring(self):
        if self.is_monitoring_clipboard:
            self.is_monitoring_clipboard = False
            self.toggle_monitoring_button.config(text="Bắt đầu Theo dõi")
            self.main_app.log_message("Đã dừng theo dõi Clipboard.")
        else:
            if pyperclip is None:
                messagebox.showerror("Thiếu thư viện", "Vui lòng cài đặt 'pyperclip' để sử dụng tính năng này.")
                return
            
            self.is_monitoring_clipboard = True
            self.last_clipboard_content = ""
            self.toggle_monitoring_button.config(text="Dừng Theo dõi")
            self.main_app.log_message("Bắt đầu theo dõi Clipboard...")

            self.clipboard_monitoring_thread = threading.Thread(target=self._clipboard_monitor_loop, daemon=True)
            self.clipboard_monitoring_thread.start()

    def _clipboard_monitor_loop(self):
        while self.is_monitoring_clipboard:
            try:
                current_content = pyperclip.paste()
                if current_content and current_content != self.last_clipboard_content:
                    self.last_clipboard_content = current_content
                    if self._is_valid_story_chunk(current_content):
                        self.main_app.root.after_idle(self.paste_and_append_story, current_content)
            except Exception as e:
                logging.warning(f"Lỗi trong vòng lặp theo dõi clipboard: {e}")
            time.sleep(1)
            
    def _is_valid_story_chunk(self, text: str) -> bool:
        if not text: return False
        word_count = len(text.split())
        if not (500 <= word_count <= 2500):
            self.main_app.log_message(f"Nội dung bị bỏ qua: số từ ({word_count}) không nằm trong khoảng 500-2500.")
            return False
        code_keywords = ["import ", "def ", "class ", "from ."]
        if any(text.strip().startswith(kw) for kw in code_keywords):
            self.main_app.log_message("Nội dung bị bỏ qua: phát hiện từ khóa code.")
            return False
        return True

    def paste_and_append_story(self, content_to_paste):
        try:
            current_manuscript = self.composer_text.get("1.0", tk.END)
            if content_to_paste in current_manuscript:
                self.main_app.log_message("Phát hiện nội dung trùng lặp, đã bỏ qua.")
                return

            separator = "\n\n" if current_manuscript.strip() else ""
            self.composer_text.insert(tk.END, separator + content_to_paste)
            self.composer_text.yview(tk.END)
            self.update_composer_counter()
            self.main_app.log_message("Đã tự động nối nội dung hợp lệ từ clipboard.")

            new_chunk_word_count = len(content_to_paste.split())
            if "Xin chân thành cảm ơn" in content_to_paste:
                prompt = f"Bạn đã viết được {new_chunk_word_count} từ cho đoạn trên. Tổng kết."
                self.continuation_prompt_var.set(prompt)
                if self.is_monitoring_clipboard: self.toggle_clipboard_monitoring()
            else:
                prompt = f"Bạn đã viết được {new_chunk_word_count} từ cho đoạn trên. Continue."
                self.continuation_prompt_var.set(prompt)
        except Exception as e:
            self.main_app.log_message(f"Lỗi khi dán và nối: {e}")

    def copy_continuation_prompt(self):
        if pyperclip is None: return
        prompt_text = self.continuation_prompt_var.get()
        if prompt_text:
            pyperclip.copy(prompt_text)
            self.main_app.log_message(f"Đã copy prompt: '{prompt_text}'")

    def save_story_to_file(self):
        content = self.composer_text.get("1.0", tk.END).strip()
        if not content: return
        file_path = filedialog.asksaveasfilename(title="Lưu bản thảo", defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if not file_path: return
        try:
            with open(file_path, 'w', encoding='utf-8') as f: f.write(content)
            self.main_app.log_message(f"Đã lưu bản thảo ra file: {file_path}")
        except Exception as e:
            self.main_app.log_message(f"Lỗi khi lưu bản thảo: {e}")

    def update_composer_counter(self, event=None):
        content = self.composer_text.get("1.0", tk.END).strip()
        char_count = len(content)
        word_count = len(content.split()) if content else 0
        self.composer_counter_label.config(text=f"Tổng cộng: {char_count:,} ký tự | {word_count:,} từ")

    def _load_projects_into_composer_combobox(self):
        try:
            projects = self.db_manager.get_all_projects()
            project_names = [proj['name'] for proj in projects]
            self.composer_project_combobox['values'] = project_names
            if project_names:
                self.composer_project_combobox.set(project_names[0])
        except Exception as e:
            self.main_app.log_message(f"Lỗi khi tải danh sách dự án vào composer: {e}")

    def _save_composer_story_to_project(self):
        """Logic lưu truyện mới, an toàn và có xác nhận."""
        if not self.main_app.active_project_id:
            messagebox.showwarning("Chưa có Dự án hoạt động", "Lỗi logic: Không tìm thấy dự án đang hoạt động.", parent=self)
            return

        story_content = self.composer_text.get("1.0", tk.END).strip()
        if not story_content:
            messagebox.showwarning("Nội dung trống", "Không có nội dung truyện để lưu.", parent=self)
            return

        # Kiểm tra xem dự án đã có truyện chưa
        items = self.db_manager.get_items_for_project(self.main_app.active_project_id)
        existing_story = next((item for item in items if item['type'] == 'Story'), None)

        if existing_story and existing_story['content'].strip():
            if not messagebox.askyesno("Xác nhận Ghi đè", "Dự án này đã có nội dung truyện. Bạn có chắc chắn muốn ghi đè không?", parent=self):
                return # Người dùng hủy

        # Tiến hành lưu
        success = self.db_manager.add_or_update_item(self.main_app.active_project_id, 'Story', story_content)
        if success:
            messagebox.showinfo("Thành công", f"Đã lưu nội dung truyện vào dự án '{self.main_app.active_project_name}' thành công!", parent=self)
            self.main_app._check_and_update_project_status_color()
        else:
            messagebox.showerror("Thất bại", "Có lỗi xảy ra khi lưu truyện vào CSDL.", parent=self)
            
    # hotfix - 2025-07-24 - Thêm hàm công khai để chèn văn bản vào đầu bản thảo
    def insert_text_at_start(self, text_to_insert):
        """Chèn một đoạn văn bản vào đầu ô soạn thảo."""
        current_content = self.composer_text.get("1.0", tk.END).strip()
        separator = "\n\n" if current_content else ""
        
        # Chèn hook và hai dòng mới để phân tách rõ ràng
        self.composer_text.insert("1.0", text_to_insert + separator)
        self.update_composer_counter()