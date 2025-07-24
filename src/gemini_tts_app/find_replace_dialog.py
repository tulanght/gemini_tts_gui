# file-path: src/gemini_tts_app/find_replace_dialog.py
# version: 2.1
# last-updated: 2025-07-24
# description: Hoàn thiện tính năng - Thêm màu highlight, tìm bằng Enter.

import tkinter as tk
from tkinter import ttk, messagebox
import re

class FindReplaceDialog(tk.Toplevel):
    def __init__(self, parent, target_widget):
        super().__init__(parent)
        self.transient(parent)
        self.title("Tìm & Thay thế")
        self.target_widget = target_widget

        # --- BIẾN ---
        self.find_what_var = tk.StringVar()
        self.replace_with_var = tk.StringVar()
        self.match_case_var = tk.BooleanVar()
        self.whole_word_var = tk.BooleanVar()
        self.search_results = []
        self.current_result_index = -1
        self.results_count_var = tk.StringVar(value="Chưa tìm kiếm")

        # --- THÊM MỚI: Định nghĩa tag highlight ---
        self.target_widget.tag_configure("found", background="lightyellow")

        self._create_widgets()
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.find_what_var.trace_add("write", self._update_search_results)

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(expand=True, fill="both")
        main_frame.columnconfigure(1, weight=1)

        ttk.Label(main_frame, text="Tìm kiếm:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        find_entry = ttk.Entry(main_frame, textvariable=self.find_what_var, width=40)
        find_entry.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5, pady=2)
        find_entry.focus_set()
        # --- THÊM MỚI: Bắt sự kiện nhấn Enter ---
        find_entry.bind("<Return>", lambda event: self._find_next())

        ttk.Label(main_frame, text="Thay thế bằng:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        replace_entry = ttk.Entry(main_frame, textvariable=self.replace_with_var, width=40)
        replace_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=2)
        replace_entry.bind("<Return>", lambda event: self._replace_one())


        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=2, column=1, sticky="w", pady=2)
        ttk.Checkbutton(options_frame, text="Phân biệt chữ hoa/thường", variable=self.match_case_var, command=self._update_search_results).pack(side="left")
        ttk.Checkbutton(options_frame, text="Toàn bộ từ", variable=self.whole_word_var, command=self._update_search_results).pack(side="left", padx=10)
        
        results_label = ttk.Label(main_frame, textvariable=self.results_count_var, foreground="gray")
        results_label.grid(row=3, column=1, sticky="w", padx=5, pady=(5,0))

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=1, sticky="e", pady=(10, 0))
        ttk.Button(button_frame, text="Tìm tiếp", command=self._find_next).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Thay thế", command=self._replace_one).pack(side="left")
        ttk.Button(button_frame, text="Thay thế tất cả", command=self._replace_all).pack(side="left", padx=5)

    def _update_search_results(self, *args):
        self.search_results = []
        self.current_result_index = -1
        self.target_widget.tag_remove("found", "1.0", "end")

        find_text = self.find_what_var.get()
        if not find_text:
            self.results_count_var.set("Chưa tìm kiếm")
            return

        is_nocase = not self.match_case_var.get()
        is_whole_word = self.whole_word_var.get()
        search_pattern = r'\b' + re.escape(find_text) + r'\b' if is_whole_word else re.escape(find_text)
        flags = re.IGNORECASE if is_nocase else 0

        content = self.target_widget.get("1.0", "end-1c")
        
        for match in re.finditer(search_pattern, content, flags=flags):
            start_index = f"1.0+{match.start()}c"
            end_index = f"1.0+{match.end()}c"
            self.search_results.append((start_index, end_index))
        
        self.results_count_var.set(f"Tìm thấy {len(self.search_results)} kết quả")
        if self.search_results:
            self._find_next(navigate_forward=False)

    def _highlight_result(self, index):
        if not (0 <= index < len(self.search_results)):
            return

        self.current_result_index = index
        start_pos, end_pos = self.search_results[index]

        self.target_widget.tag_remove("found", "1.0", "end")
        self.target_widget.tag_add("found", start_pos, end_pos)
        self.target_widget.mark_set("insert", start_pos)
        self.target_widget.see(start_pos)
        
        self.results_count_var.set(f"{index + 1} / {len(self.search_results)}")

    def _find_next(self, navigate_forward=True):
        if not self.search_results:
            return

        next_index = self.current_result_index
        if navigate_forward:
            next_index += 1
        
        if not (0 <= next_index < len(self.search_results)):
            next_index = 0

        self._highlight_result(next_index)

    def _replace_one(self):
        if not self.search_results or self.current_result_index == -1:
            self._find_next()
            return
        
        replace_text = self.replace_with_var.get()
        start_pos, end_pos = self.search_results[self.current_result_index]
        
        self.target_widget.delete(start_pos, end_pos)
        self.target_widget.insert(start_pos, replace_text)
        
        self._update_search_results()

    def _replace_all(self):
        find_text = self.find_what_var.get()
        if not find_text or not self.search_results:
            return
        
        replace_text = self.replace_with_var.get()
        count = len(self.search_results)

        for start_pos, end_pos in reversed(self.search_results):
            self.target_widget.delete(start_pos, end_pos)
            self.target_widget.insert(start_pos, replace_text)
        
        messagebox.showinfo("Hoàn tất", f"Đã thực hiện {count} lần thay thế.", parent=self)
        self._on_close()

    def _on_close(self):
        self.target_widget.tag_remove("found", "1.0", "end")
        self.destroy()  