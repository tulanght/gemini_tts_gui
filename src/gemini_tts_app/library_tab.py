# file-path: src/gemini_tts_app/library_tab.py
# version: 8.0
# last-updated: 2025-07-19
# description: Hoàn thiện Hệ thống Trạng thái Dự án với Menu Chuột phải và tô màu hàng.

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
import threading

from . import google_api_handler
from .settings_manager import load_project_groups

class EditWindow(tk.Toplevel):
    def __init__(self, parent, title, initial_text=""):
        super().__init__(parent)
        self.title(title)
        self.geometry("600x400")
        self.transient(parent)
        self.grab_set()
        self.new_content = None
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(expand=True, fill="both")
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        self.text_widget = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=("Segoe UI", 10))
        self.text_widget.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.text_widget.insert("1.0", initial_text)
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky="e")
        ok_button = ttk.Button(button_frame, text="Lưu thay đổi", command=self._on_ok)
        ok_button.pack(side="right")
        cancel_button = ttk.Button(button_frame, text="Hủy", command=self.destroy)
        cancel_button.pack(side="right", padx=10)

    def _on_ok(self):
        self.new_content = self.text_widget.get("1.0", "end-1c").strip()
        self.destroy()

    def show(self):
        self.wait_window()
        return self.new_content

class LibraryTab(ttk.Frame):
    def __init__(self, parent, db_manager, main_app_instance, **kwargs):
        super().__init__(parent, padding="10", **kwargs)
        self.db_manager = db_manager
        self.main_app = main_app_instance
        self.gdrive_groups = []
        self.sync_mode = tk.StringVar(value="add_new")

        self._create_widgets()
        self._configure_status_colors() # Cấu hình màu sắc
        self.bind("<Visibility>", self._on_tab_visible)

    def _configure_status_colors(self):
        """Định nghĩa các tag màu cho TreeView."""
        self.library_tree.tag_configure('in_progress', background='#FFF9C4') # Vàng nhạt
        self.library_tree.tag_configure('completed', background='#C8E6C9')   # Xanh lá nhạt

    def _create_widgets(self):
        # --- KHUNG ĐỒNG BỘ GOOGLE DRIVE ---
        sync_frame = ttk.LabelFrame(self, text="Đồng bộ hóa từ Google Drive", padding="10")
        sync_frame.pack(fill="x", pady=(0, 10))
        sync_frame.columnconfigure(1, weight=1)

        ttk.Label(sync_frame, text="Chọn Nhóm Dự án:").grid(row=0, column=0, padx=(0,5), sticky="w")
        self.gdrive_group_combobox = ttk.Combobox(sync_frame, state="readonly", width=40)
        self.gdrive_group_combobox.grid(row=0, column=1, padx=5, sticky="ew")
        
        options_frame = ttk.Frame(sync_frame)
        options_frame.grid(row=1, column=1, pady=(5,0), sticky="w")
        ttk.Radiobutton(options_frame, text="Chỉ thêm mới", variable=self.sync_mode, value="add_new").pack(side="left", padx=(0, 10))
        ttk.Radiobutton(options_frame, text="Làm mới toàn bộ (Ghi đè)", variable=self.sync_mode, value="overwrite").pack(side="left")

        self.sync_button = ttk.Button(sync_frame, text="Bắt đầu Đồng bộ", style="Accent.TButton", command=self._sync_from_gdrive)
        self.sync_button.grid(row=0, column=2, rowspan=2, padx=5, sticky="ns")

        # --- KHUNG DANH SÁCH DỰ ÁN ---
        tree_frame = ttk.Frame(self)
        tree_frame.pack(expand=True, fill="both", pady=(0, 10))
        
        columns = ("id", "status", "name", "title", "thumbnail", "story")
        self.library_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.library_tree.heading("id", text="ID")
        self.library_tree.heading("status", text="Trạng thái")
        self.library_tree.heading("name", text="Tên Dự án")
        self.library_tree.heading("title", text="Tiêu đề")
        self.library_tree.heading("thumbnail", text="Kịch bản Thumbnail")
        self.library_tree.heading("story", text="Nội dung Truyện")

        self.library_tree.column("id", width=40, anchor="center", stretch=False)
        self.library_tree.column("status", width=100, anchor="center")
        self.library_tree.column("name", width=200)
        self.library_tree.column("title", width=250)
        self.library_tree.column("thumbnail", width=250)
        self.library_tree.column("story", width=200)

        self.library_tree.bind("<Double-1>", self._on_project_double_click)
        self.library_tree.bind("<Button-3>", self._show_status_menu)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.library_tree.yview)
        self.library_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.library_tree.pack(side="left", expand=True, fill="both")

        # --- KHUNG NÚT BẤM ---
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", pady=(10,0))
        self.work_on_project_button = ttk.Button(button_frame, text="Làm việc với Dự án này", style="Accent.TButton", command=self._set_active_project)
        self.work_on_project_button.pack(side="left", padx=(0, 10))
        self.add_project_button = ttk.Button(button_frame, text="Tạo Dự án Mới...", command=self._create_new_project)
        self.add_project_button.pack(side="left")
        self.delete_project_button = ttk.Button(button_frame, text="Xóa Dự án", command=self._delete_selected_project)
        self.delete_project_button.pack(side="right")

    def _on_tab_visible(self, event):
        self._load_gdrive_groups_to_combobox()
        self._load_project_data()

    def _load_gdrive_groups_to_combobox(self):
        """Tải danh sách các nhóm Google Drive vào Combobox."""
        all_groups = load_project_groups()
        self.gdrive_groups = [g for g in all_groups if g.get('type') == 'Google Drive']
        group_names = [g['name'] for g in self.gdrive_groups]
        self.gdrive_group_combobox['values'] = group_names
        if group_names:
            self.gdrive_group_combobox.set(group_names[0])

    def _sync_from_gdrive(self):
        """Bắt đầu quá trình đồng bộ Google Drive trong một luồng riêng."""
        selected_group_name = self.gdrive_group_combobox.get()
        if not selected_group_name:
            messagebox.showwarning("Chưa chọn Nhóm", "Vui lòng chọn một Nhóm Dự án để đồng bộ.", parent=self)
            return
        group_info = next((g for g in self.gdrive_groups if g['name'] == selected_group_name), None)
        if not group_info or not group_info.get('folder_id'):
            messagebox.showerror("Thiếu thông tin", "Nhóm dự án này không phải loại Google Drive hoặc thiếu Folder ID.", parent=self)
            return
        sync_thread = threading.Thread(target=self._gdrive_sync_task, args=(group_info,), daemon=True)
        sync_thread.start()

    def _gdrive_sync_task(self, group_info):
        """Tác vụ chạy ngầm để đồng bộ hóa với logic thông minh."""
        group_name = group_info.get('name')
        folder_id = group_info.get('folder_id')
        sync_mode = self.sync_mode.get()
        self.main_app.log_message(f"Bắt đầu đồng bộ từ nhóm '{group_name}' (Chế độ: {sync_mode})...")

        creds, error = google_api_handler.get_credentials()
        if error:
            self.main_app.root.after(0, lambda: messagebox.showerror("Lỗi Xác thực", error, parent=self.main_app.root))
            return

        if sync_mode == "overwrite":
            self.main_app.log_message(f"Đang xóa các dự án cũ thuộc nhóm '{group_name}'...")
            self.db_manager.delete_projects_by_group(group_name)
            self.main_app.log_message("Đã xóa xong.")

        existing_projects = self.db_manager.get_project_names()

        files, error = google_api_handler.list_files_in_folder(creds, folder_id)
        if error:
            self.main_app.root.after(0, lambda: messagebox.showerror("Lỗi Lấy File", error, parent=self.main_app.root))
            return
        if not files:
            self.main_app.root.after(0, lambda: messagebox.showinfo("Thông báo", "Không tìm thấy file Google Docs nào trong thư mục.", parent=self.main_app.root))
            return

        success_count, fail_count, skipped_count = 0, 0, 0
        for file in files:
            file_name = file.get('name')
            if sync_mode == "add_new" and file_name in existing_projects:
                skipped_count += 1
                continue
            
            self.main_app.log_message(f"Đang xử lý: {file_name}...")
            file_id = file.get('id')
            content, error = google_api_handler.get_doc_content(creds, file_id)
            if error:
                self.main_app.log_message(f"[WARNING] Lỗi đọc file '{file_name}': {error}")
                fail_count += 1
                continue
            
            project_id = self.db_manager.create_project(file_name, source_group=group_name)
            if project_id:
                self.db_manager.add_or_update_item(project_id, 'Title', file_name)
                self.db_manager.add_or_update_item(project_id, 'Story', content)
                success_count += 1
            else:
                self.main_app.log_message(f"[WARNING] Lỗi tạo dự án cho: {file_name}")
                fail_count += 1
        
        def update_ui_on_complete():
            self._load_project_data()
            messagebox.showinfo("Hoàn tất Đồng bộ",
                              f"Đồng bộ hoàn tất!\n- Thành công: {success_count}\n- Thất bại: {fail_count}\n- Bỏ qua: {skipped_count}",
                              parent=self.main_app.root)
            self.main_app.log_message("Hoàn tất quá trình đồng bộ.")
        
        self.main_app.root.after(0, update_ui_on_complete)

    def _load_project_data(self):
        selected_iid = self.library_tree.focus()
        for item in self.library_tree.get_children():
            self.library_tree.delete(item)
        projects = self.db_manager.get_all_projects()
        if not projects: return
        for project in projects:
            items = self.db_manager.get_items_for_project(project['id'])
            content_map = {'Story': '', 'Title': '', 'Thumbnail': ''}
            for item in items:
                if item['type'] in content_map:
                    content_map[item['type']] = item['content']
            story_preview = (content_map['Story'][:100] + '...') if len(content_map['Story']) > 100 else content_map['Story']
            
            status = project['status']
            tag = ''
            if status == 'Đang làm dở':
                tag = 'in_progress'
            elif status == 'Đã làm':
                tag = 'completed'

            self.library_tree.insert("", "end", iid=project['id'], tags=(tag,), values=(
                project['id'],
                status,
                project['name'], 
                content_map['Title'], 
                content_map['Thumbnail'].replace('\n', ' '), 
                story_preview
            ))
        if selected_iid and self.library_tree.exists(selected_iid):
            self.library_tree.focus(selected_iid)
            self.library_tree.selection_set(selected_iid)

    def _show_status_menu(self, event):
        """Hiển thị menu chuột phải để thay đổi trạng thái."""
        iid = self.library_tree.identify_row(event.y)
        if iid:
            self.library_tree.selection_set(iid)
            status_menu = tk.Menu(self, tearoff=0)
            status_menu.add_command(
                label="Chưa làm",
                command=lambda: self._change_project_status(iid, "Chưa làm")
            )
            status_menu.add_command(
                label="Đang làm dở",
                command=lambda: self._change_project_status(iid, "Đang làm dở")
            )
            status_menu.add_command(
                label="Đã làm",
                command=lambda: self._change_project_status(iid, "Đã làm")
            )
            status_menu.post(event.x_root, event.y_root)

    def _change_project_status(self, project_id, new_status):
        """Gọi DB để cập nhật trạng thái và làm mới giao diện."""
        if self.db_manager.update_project_status(int(project_id), new_status):
            self._load_project_data()
        else:
            messagebox.showerror("Lỗi", "Không thể cập nhật trạng thái dự án.", parent=self)

    def _on_project_double_click(self, event):
        region = self.library_tree.identify("region", event.x, event.y)
        if region != "cell": return
        project_id = self.library_tree.focus()
        if not project_id: return
        
        column_id = self.library_tree.identify_column(event.x)
        project_id = int(project_id)
        
        # Cập nhật map để loại bỏ cột status
        column_map = {
            '#3': ('Tên Dự án', self._edit_project_name),
            '#4': ('Title', self._edit_project_item),
            '#5': ('Thumbnail', self._edit_project_item),
            '#6': ('Story', self._edit_project_item),
        }

        if column_id in column_map:
            item_type, handler = column_map[column_id]
            handler(project_id, item_type)

    def _edit_project_name(self, project_id, item_type=None):
        current_name = self.library_tree.item(project_id)['values'][2] # Tên dự án giờ ở cột 3 (index 2)
        new_name = simpledialog.askstring("Đổi tên Dự án", "Nhập tên mới:", initialvalue=current_name)
        if new_name and new_name.strip() and new_name.strip() != current_name:
            try:
                if self.db_manager.update_project_name(project_id, new_name.strip()):
                    self._load_project_data()
            except ValueError as e:
                messagebox.showerror("Lỗi", str(e), parent=self)

    def _edit_project_item(self, project_id, item_type):
        items = self.db_manager.get_items_for_project(project_id)
        current_content = ""
        for item in items:
            if item['type'] == item_type:
                current_content = item['content']
                break
        
        dialog = EditWindow(self, f"Chỉnh sửa {item_type} cho Dự án ID: {project_id}", current_content)
        new_content = dialog.show()
        if new_content is not None and new_content != current_content:
            if self.db_manager.add_or_update_item(project_id, item_type, new_content):
                self._load_project_data()
            else:
                messagebox.showerror("Lỗi", f"Không thể cập nhật {item_type}.")
        
    def _create_new_project(self):
        project_name = simpledialog.askstring("Tạo Dự án Mới", "Nhập tên cho dự án mới:")
        if project_name and project_name.strip():
            if self.db_manager.create_project(project_name.strip()):
                messagebox.showinfo("Thành công", f"Đã tạo dự án '{project_name}' thành công.")
                self._load_project_data()
            else:
                messagebox.showerror("Lỗi", "Tên dự án có thể đã tồn tại hoặc có lỗi xảy ra.")
    
    def _delete_selected_project(self):
        selected_iid = self.library_tree.focus()
        if not selected_iid:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một dự án để xóa.")
            return
        project_id = int(selected_iid)
        project_name = self.library_tree.item(selected_iid)['values'][2] # Tên dự án giờ ở cột 3 (index 2)
        if messagebox.askyesno("Xác nhận Xóa", f"Bạn có chắc chắn muốn xóa toàn bộ dự án '{project_name}' không?\nMọi dữ liệu liên quan sẽ bị mất vĩnh viễn."):
            if self.db_manager.delete_project(project_id):
                self._load_project_data()
            else:
                messagebox.showerror("Lỗi", "Không thể xóa dự án.")

    def _set_active_project(self):
        selected_iid = self.library_tree.focus()
        if not selected_iid:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một dự án để bắt đầu làm việc.", parent=self)
            return
        project_id = int(selected_iid)
        project_name = self.library_tree.item(selected_iid)['values'][2] # Tên dự án giờ ở cột 3 (index 2)
        self.main_app.set_active_project(project_id, project_name)