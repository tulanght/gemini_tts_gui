# file-path: src/gemini_tts_app/settings_tab.py
# version: 1.0
# last-updated: 2025-07-23
# description: Module chuyên trách cho tab Settings.

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import threading

from .settings_manager import (
    load_project_groups, add_project_group, update_project_group,
    delete_project_group, save_settings, save_project_groups
)
from . import google_api_handler
from .constants import NUM_API_KEYS

class SettingsTab(ttk.Frame):
    def __init__(self, parent, main_app_instance):
        super().__init__(parent, padding="10")
        self.main_app = main_app_instance
        self.settings = self.main_app.settings
        self.project_groups = []

        self._create_widgets()

    # hotfix - 2025-07-24 - Sắp xếp lại layout của API key cho nhỏ gọn
    def _create_widgets(self):
        self.columnconfigure(0, weight=1)

        # --- Mục 1: API Key Management ---
        api_keys_frame = ttk.LabelFrame(self, text="API Key Management", padding="10")
        api_keys_frame.grid(row=0, column=0, padx=5, pady=10, sticky="ew")
        # Cấu hình cột để Entry chiếm nhiều không gian hơn
        api_keys_frame.columnconfigure(1, weight=1)
        api_keys_frame.columnconfigure(3, weight=2)
        
        for i in range(NUM_API_KEYS):
            # Gộp thành 1 hàng, 4 cột
            label_of_label = ttk.Label(api_keys_frame, text=f"Label {i+1}:")
            label_of_label.grid(row=i, column=0, padx=(0,5), pady=5, sticky="w")

            label_entry = ttk.Entry(api_keys_frame, textvariable=self.main_app.api_label_vars[i])
            label_entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")

            label_of_key = ttk.Label(api_keys_frame, text=f"API Key {i+1}:")
            label_of_key.grid(row=i, column=2, padx=(10,5), pady=5, sticky="w")

            key_entry = ttk.Entry(api_keys_frame, textvariable=self.main_app.api_key_vars[i], show="*")
            key_entry.grid(row=i, column=3, padx=5, pady=5, sticky="ew")

        # --- Mục 3: Google Drive Sync ---
        self._create_gdrive_settings_widgets()

        # --- Mục 4: Nút Save và Ghi chú ---
        self.save_settings_button = ttk.Button(self, text="Save All Settings", command=self.save_app_settings, style="Accent.TButton")
        self.save_settings_button.grid(row=4, column=0, padx=5, pady=15)
        ttk.Label(self, text="Note: Settings are saved automatically on exit.").grid(row=5, column=0, padx=5, pady=5, sticky="w")

    def _create_gdrive_settings_widgets(self):
        gdrive_frame = ttk.LabelFrame(self, text="Quản lý Nhóm Dự án", padding="10")
        gdrive_frame.grid(row=2, column=0, padx=5, pady=10, sticky="ew")
        gdrive_frame.columnconfigure(0, weight=1)

        tree_frame = ttk.Frame(gdrive_frame)
        tree_frame.grid(row=0, column=0, columnspan=3, sticky="nsew", pady=(0, 10))
        tree_frame.columnconfigure(0, weight=1)

        columns = ("group_name", "type", "folder_id")
        self.gdrive_group_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=5)
        self.gdrive_group_tree.heading("group_name", text="Tên Nhóm Dự án")
        self.gdrive_group_tree.heading("type", text="Loại")
        self.gdrive_group_tree.heading("folder_id", text="Google Drive Folder ID")
        self.gdrive_group_tree.column("group_name", width=150)
        self.gdrive_group_tree.column("type", width=100, anchor="center")
        self.gdrive_group_tree.column("folder_id", width=250)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.gdrive_group_tree.yview)
        self.gdrive_group_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.gdrive_group_tree.pack(side="left", expand=True, fill="both")

        button_frame = ttk.Frame(gdrive_frame)
        button_frame.grid(row=1, column=0, columnspan=3, sticky="w")
        add_button = ttk.Button(button_frame, text="Thêm Nhóm Mới...", command=self._add_project_group)
        add_button.pack(side="left")
        auth_button = ttk.Button(button_frame, text="Kết nối với Google", style="Accent.TButton", command=self._authenticate_google)
        auth_button.pack(side="left", padx=(20, 0))
        edit_button = ttk.Button(button_frame, text="Sửa Nhóm...", command=self._edit_project_group)
        edit_button.pack(side="left", padx=5)
        delete_button = ttk.Button(button_frame, text="Xóa Nhóm", command=self._delete_project_group)
        delete_button.pack(side="left", padx=5)

        self._load_gdrive_groups_to_treeview()

    def _load_gdrive_groups_to_treeview(self):
        for item in self.gdrive_group_tree.get_children():
            self.gdrive_group_tree.delete(item)
        self.project_groups = load_project_groups()
        for group in self.project_groups:
            self.gdrive_group_tree.insert("", "end", values=(
                group.get('name', ''),
                group.get('type', 'Local'),
                group.get('folder_id', ''),
            ))

    def _add_project_group(self):
        name = simpledialog.askstring("Bước 1/2: Tên Nhóm", "Nhập Tên Nhóm:", parent=self)
        if not name or not name.strip(): return
        group_type = self._ask_group_type()
        if not group_type: return
        folder_id = ""
        if group_type == "Google Drive":
            folder_id = simpledialog.askstring("Bước 2/2: Google Drive", "Nhập Google Drive Folder ID:", parent=self)
            if folder_id is None: return
        new_group = {'name': name.strip(), 'type': group_type, 'folder_id': folder_id.strip()}
        try:
            add_project_group(new_group)
            self._load_gdrive_groups_to_treeview()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e), parent=self)

    def _edit_project_group(self):
        selected_item = self.gdrive_group_tree.focus()
        if not selected_item:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một nhóm dự án để sửa.", parent=self)
            return
        original_name = self.gdrive_group_tree.item(selected_item)['values'][0]
        group_to_edit = next((g for g in self.project_groups if g.get('name') == original_name), None)
        if not group_to_edit: return
        name = simpledialog.askstring("Sửa Nhóm Dự án", "Tên Nhóm:", initialvalue=group_to_edit.get('name', ''), parent=self)
        if name is None: return
        group_type = self._ask_group_type(initial_type=group_to_edit.get('type', 'Local'))
        folder_id = group_to_edit.get('folder_id', '')
        if group_type == "Google Drive":
            folder_id = simpledialog.askstring("Sửa Nhóm Dự án", "Google Drive Folder ID:", initialvalue=folder_id, parent=self)
            if folder_id is None: return
        new_data = {'name': name.strip(), 'type': group_type, 'folder_id': folder_id.strip()}
        try:
            if update_project_group(original_name, new_data):
                self._load_gdrive_groups_to_treeview()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e), parent=self)

    def _delete_project_group(self):
        selected_item = self.gdrive_group_tree.focus()
        if not selected_item:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một nhóm dự án để xóa.", parent=self)
            return
        group_name = self.gdrive_group_tree.item(selected_item)['values'][0]
        if messagebox.askyesno("Xác nhận Xóa", f"Bạn có chắc chắn muốn xóa nhóm '{group_name}' không?"):
            if delete_project_group(group_name):
                self._load_gdrive_groups_to_treeview()

    def _ask_group_type(self, initial_type="Local"):
        dialog = tk.Toplevel(self)
        dialog.title("Chọn Loại Nhóm")
        dialog.transient(self); dialog.grab_set()
        result = tk.StringVar(value=initial_type)
        ttk.Label(dialog, text="Chọn loại cho nhóm dự án:").pack(padx=20, pady=10)
        ttk.Radiobutton(dialog, text="Local (Trên máy tính)", variable=result, value="Local").pack(anchor="w", padx=20)
        ttk.Radiobutton(dialog, text="Google Drive (Đồng bộ online)", variable=result, value="Google Drive").pack(anchor="w", padx=20)
        ttk.Button(dialog, text="Chọn", command=dialog.destroy).pack(pady=10)
        self.wait_window(dialog)
        return result.get()

    def _authenticate_google(self):
        def auth_task():
            self.main_app.log_message("Bắt đầu quá trình xác thực với Google...")
            creds, error = google_api_handler.get_credentials()
            if error:
                self.main_app.log_message(f"[ERROR] Xác thực thất bại: {error}")
                messagebox.showerror("Xác thực Thất bại", error)
            elif creds:
                self.main_app.log_message("Xác thực thành công!")
                messagebox.showinfo("Xác thực Thành công", "Kết nối với Google thành công!")
        threading.Thread(target=auth_task, daemon=True).start()

    def save_app_settings(self):
        current_settings = self.settings.copy()
        for i in range(NUM_API_KEYS):
            current_settings[f"api_key_{i+1}"] = self.main_app.api_key_vars[i].get()
            current_settings[f"label_{i+1}"] = self.main_app.api_label_vars[i].get()
        # Lưu các cài đặt khác (nếu có) vào đây
        
        # Lưu nhóm dự án riêng
        save_project_groups(self.project_groups)
        
        # Lưu các cài đặt còn lại
        if save_settings(current_settings):
            self.settings = current_settings
            self.main_app.log_message("Cài đặt đã được lưu.")
            messagebox.showinfo("Đã lưu", "Tất cả cài đặt đã được lưu thành công.")
        else:
            messagebox.showerror("Lỗi", "Không thể lưu cài đặt.")