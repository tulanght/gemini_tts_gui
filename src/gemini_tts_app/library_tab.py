# file-path: src/gemini_tts_app/library_tab.py
# version: 11.0
# last-updated: 2025-07-31
# description: Tái cấu trúc toàn diện, khôi phục logic sync GDrive, sửa lỗi tạo dự án mới.

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
import threading
import re

from .find_replace_dialog import FindReplaceDialog
from . import google_api_handler
from .settings_manager import load_project_groups
from .database import DatabaseManager

class SyncOptionsWindow(tk.Toplevel):
    """Cửa sổ con để chứa các tùy chọn đồng bộ Google Drive."""
    def __init__(self, parent, group_info, sync_callback):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.title(f"Tùy chọn Đồng bộ cho '{group_info.get('name')}'")
        
        self.group_info = group_info
        self.sync_callback = sync_callback
        self.sync_mode = tk.StringVar(value="add_new")

        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(expand=True, fill="both")

        ttk.Label(main_frame, text="Chọn chế độ đồng bộ:").pack(anchor="w", pady=(0, 10))
        
        ttk.Radiobutton(main_frame, text="Chỉ thêm mới (An toàn)",
                        variable=self.sync_mode, value="add_new").pack(anchor="w", padx=10)
        ttk.Radiobutton(main_frame, text="Làm mới toàn bộ (Xóa dự án cũ của nhóm này và tải lại)",
                        variable=self.sync_mode, value="overwrite").pack(anchor="w", padx=10)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        ok_button = ttk.Button(button_frame, text="Bắt đầu Đồng bộ", command=self._start_sync, style="Accent.TButton")
        ok_button.pack(side="right")
        cancel_button = ttk.Button(button_frame, text="Hủy", command=self.destroy)
        cancel_button.pack(side="right", padx=10)

    def _start_sync(self):
        self.sync_callback(self.group_info, self.sync_mode.get())
        self.destroy()

class EditWindow(tk.Toplevel):
    # (Nội dung class này giữ nguyên, không thay đổi)
    def __init__(self, parent, title, initial_text=""):
        super().__init__(parent)
        self.title(title); self.geometry("700x500"); self.transient(parent); self.grab_set()
        self.new_content = None; self.find_replace_window = None
        main_frame = ttk.Frame(self, padding="10"); main_frame.pack(expand=True, fill="both")
        main_frame.rowconfigure(0, weight=1); main_frame.columnconfigure(0, weight=1)
        self.text_widget = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=("Segoe UI", 10))
        self.text_widget.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.text_widget.insert("1.0", initial_text)
        button_frame = ttk.Frame(main_frame); button_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        find_replace_button = ttk.Button(button_frame, text="Tìm & Thay thế (Ctrl+F)...", command=self._open_find_replace)
        find_replace_button.pack(side="left")
        ok_button = ttk.Button(button_frame, text="Lưu thay đổi", command=self._on_ok); ok_button.pack(side="right")
        cancel_button = ttk.Button(button_frame, text="Hủy", command=self.destroy); cancel_button.pack(side="right", padx=10)
        self.bind("<Control-f>", self._open_find_replace); self.text_widget.bind("<Control-f>", self._open_find_replace)

    def _open_find_replace(self, event=None):
        if self.find_replace_window and self.find_replace_window.winfo_exists(): self.find_replace_window.lift(); return
        self.find_replace_window = FindReplaceDialog(self, target_widget=self.text_widget)

    def _on_ok(self): self.new_content = self.text_widget.get("1.0", "end-1c").strip(); self.destroy()
    def show(self): self.wait_window(); return self.new_content

class LibraryTab(ttk.Frame):
    def __init__(self, parent, db_manager: DatabaseManager, main_app_instance, **kwargs):
        super().__init__(parent, padding="10", **kwargs)
        self.db_manager = db_manager
        self.main_app = main_app_instance
        self.project_groups_data = []
        self.selected_group = tk.StringVar()
        self._create_widgets()
        self._configure_status_colors()
        self.bind("<Visibility>", self._on_tab_visible)

        
    def _create_widgets(self):
        filter_frame = ttk.LabelFrame(self, text="Bộ lọc & Tác vụ", padding="10")
        filter_frame.pack(fill="x", pady=(0, 10))
        filter_frame.columnconfigure(1, weight=1)
        ttk.Label(filter_frame, text="Chọn Nhóm Dự án:").grid(row=0, column=0, padx=(0,5), sticky="w")
        self.group_combobox = ttk.Combobox(filter_frame, textvariable=self.selected_group, state="readonly", width=40)
        self.group_combobox.grid(row=0, column=1, padx=5, sticky="ew")
        self.group_combobox.bind("<<ComboboxSelected>>", self._on_group_selected)
        self.sync_button = ttk.Button(filter_frame, text="Đồng bộ từ GDrive...", command=self._open_sync_options, state=tk.DISABLED)
        self.sync_button.grid(row=0, column=2, padx=10)
        tree_frame = ttk.Frame(self)
        tree_frame.pack(expand=True, fill="both", pady=(0, 10))
        columns = ("id", "status", "name", "title", "thumbnail", "story")
        self.library_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.library_tree.heading("id", text="ID"); self.library_tree.heading("status", text="Trạng thái"); self.library_tree.heading("name", text="Tên Dự án"); self.library_tree.heading("title", text="Tiêu đề"); self.library_tree.heading("thumbnail", text="Kịch bản Thumbnail"); self.library_tree.heading("story", text="Nội dung Truyện")
        self.library_tree.column("id", width=40, anchor="center", stretch=False); self.library_tree.column("status", width=100, anchor="center", stretch=False); self.library_tree.column("name", width=150, stretch=False); self.library_tree.column("title", width=200, stretch=False); self.library_tree.column("thumbnail", width=200, stretch=False); self.library_tree.column("story", width=350)
        self.library_tree.bind("<Double-1>", self._on_project_double_click); self.library_tree.bind("<Button-3>", self._show_status_menu)
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.library_tree.yview); self.library_tree.configure(yscroll=scrollbar.set); scrollbar.pack(side="right", fill="y"); self.library_tree.pack(side="left", expand=True, fill="both")
        button_frame = ttk.Frame(self); button_frame.pack(fill="x", pady=(10,0))
        self.send_to_tts_button = ttk.Button(button_frame, text="Gửi sang TTS", command=self._send_to_tts); self.send_to_tts_button.pack(side="left", padx=(0, 10))
        self.work_on_project_button = ttk.Button(button_frame, text="Làm việc với Dự án này", style="Accent.TButton", command=self._set_active_project); self.work_on_project_button.pack(side="left", padx=(0, 10))
        self.add_project_button = ttk.Button(button_frame, text="Tạo Dự án Mới...", command=self._create_new_project); self.add_project_button.pack(side="left")
        self.delete_project_button = ttk.Button(button_frame, text="Xóa Dự án", command=self._delete_selected_project); self.delete_project_button.pack(side="right")

    def _clean_display_text(self, text: str) -> str:
        if not text: return "Chưa có tiêu đề"
        stripped_text = text.strip();
        if re.fullmatch(r'\d+', stripped_text): return "Chưa có tiêu đề"
        cleaned_text = re.sub(r'^\d+\s*-\s*', '', stripped_text)
        return cleaned_text if cleaned_text else "Chưa có tiêu đề"

    def _configure_status_colors(self):
        self.library_tree.tag_configure('in_progress', background='#FFF9C4'); self.library_tree.tag_configure('completed', background='#C8E6C9')

    def _on_tab_visible(self, event):
        self._load_project_groups_to_combobox(); self._load_project_data()

    def _load_project_groups_to_combobox(self):
        self.project_groups_data = load_project_groups()
        group_names = [g['name'] for g in self.project_groups_data]
        self.group_combobox['values'] = ["-- Tất cả Nhóm --"] + group_names
        current_selection = self.selected_group.get()
        if current_selection not in self.group_combobox['values']: self.selected_group.set("-- Tất cả Nhóm --")
        self._on_group_selected()
        
    def _on_group_selected(self, event=None):
        selected_name = self.selected_group.get()
        selected_group_obj = next((g for g in self.project_groups_data if g.get('name') == selected_name), None)
        self.sync_button.config(state=tk.NORMAL if selected_group_obj and selected_group_obj.get('type') == 'Google Drive' else tk.DISABLED)
        self.add_project_button.config(state=tk.DISABLED if selected_group_obj and selected_group_obj.get('type') == 'Google Drive' else tk.NORMAL)
        self._load_project_data()

    def _load_project_data(self):
        selected_iid = self.library_tree.focus()
        for item in self.library_tree.get_children(): self.library_tree.delete(item)
        selected_group_name = self.selected_group.get()
        if selected_group_name == "-- Tất cả Nhóm --" or not selected_group_name: projects = self.db_manager.get_all_projects()
        else: projects = self.db_manager.get_projects_by_group(selected_group_name)
        if not projects: return
        for project in projects:
            items = self.db_manager.get_items_for_project(project['id'])
            content_map = {'Story': '', 'Title': '', 'Thumbnail': ''}
            for item in items:
                if item['type'] in content_map: content_map[item['type']] = item['content']
            story_preview = (content_map['Story'][:100] + '...') if len(content_map['Story']) > 100 else content_map['Story']
            status = project['status']
            tag = 'in_progress' if status == 'Đang làm dở' else 'completed' if status == 'Đã làm' else ''
            display_name = self._clean_display_text(project['name'])
            display_title = self._clean_display_text(content_map['Title'])
            self.library_tree.insert("", "end", iid=project['id'], tags=(tag,), values=(project['id'], status, display_name, display_title, content_map['Thumbnail'].replace('\n', ' '), story_preview))
        if selected_iid and self.library_tree.exists(selected_iid): self.library_tree.focus(selected_iid); self.library_tree.selection_set(selected_iid)

    def _open_sync_options(self):
        selected_name = self.selected_group.get()
        group_info = next((g for g in self.project_groups_data if g.get('name') == selected_name), None)
        if not group_info: return
        SyncOptionsWindow(self, group_info, self.start_gdrive_sync)

    def start_gdrive_sync(self, group_info, sync_mode):
        sync_thread = threading.Thread(target=self._gdrive_sync_task, args=(group_info, sync_mode), daemon=True)
        sync_thread.start()

     # hotfix - 2025-08-01 - Đảo ngược thứ tự logic để xác thực trước khi xóa dữ liệu
    def _gdrive_sync_task(self, group_info, sync_mode):
        group_name, folder_id = group_info.get('name'), group_info.get('folder_id')
        self.main_app.log_message(f"Bắt đầu đồng bộ từ nhóm '{group_name}' (Chế độ: {sync_mode})...")

        # BƯỚC 1: XÁC THỰC VÀ LẤY DỮ LIỆU TỪ GDRIVE TRƯỚC
        self.main_app.log_message("Đang xác thực và lấy danh sách file từ Google Drive...")
        creds, error = google_api_handler.get_credentials()
        if error:
            self.main_app.root.after(0, lambda: messagebox.showerror("Lỗi Xác thực", f"Không thể kết nối với Google. Vui lòng thử xác thực lại trong tab Cài đặt.\n\nLỗi: {error}", parent=self))
            self.main_app.log_message(f"[ERROR] Quá trình đồng bộ dừng lại do lỗi xác thực: {error}")
            return

        files, error = google_api_handler.list_files_in_folder(creds, folder_id)
        if error:
            self.main_app.root.after(0, lambda: messagebox.showerror("Lỗi Lấy File", f"Không thể lấy danh sách file từ Google Drive.\n\nLỗi: {error}", parent=self))
            self.main_app.log_message(f"[ERROR] Quá trình đồng bộ dừng lại do không lấy được danh sách file: {error}")
            return
        
        self.main_app.log_message(f"Xác thực và lấy danh sách file thành công. Tìm thấy {len(files)} file.")

        # BƯỚC 2: NẾU MỌI THỨ Ở TRÊN ĐỀU ỔN, MỚI TIẾN HÀNH XỬ LÝ DỮ LIỆU CỤC BỘ
        if sync_mode == "overwrite":
            if not messagebox.askyesno("Xác nhận Ghi đè", f"Bạn có chắc chắn muốn XÓA TẤT CẢ các dự án thuộc nhóm '{group_name}' trên máy và tải lại từ Google Drive không?\nHành động này không thể hoàn tác.", parent=self):
                self.main_app.log_message("Người dùng đã hủy bỏ thao tác ghi đè.")
                return
            self.main_app.log_message(f"Đang xóa các dự án cũ thuộc nhóm '{group_name}'...")
            self.db_manager.delete_projects_by_group(group_name)
            self.main_app.log_message("Đã xóa xong.")

        existing_projects = self.db_manager.get_project_names()
        
        if not files:
            self.main_app.root.after(0, lambda: messagebox.showinfo("Thông báo", "Không tìm thấy file Google Docs nào trong thư mục.", parent=self))
            self._load_project_data() # Vẫn tải lại để hiển thị danh sách trống (nếu đã xóa)
            return

        success_count, fail_count, skipped_count = 0, 0, 0
        for file in files:
            file_name = file.get('name')
            if sync_mode == "add_new" and file_name in existing_projects:
                skipped_count += 1
                continue
            
            self.main_app.log_message(f"Đang xử lý: {file_name}...")
            content, error = google_api_handler.get_doc_content(creds, file.get('id'))
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
        
        def on_complete():
            self._load_project_data()
            messagebox.showinfo("Hoàn tất", f"Đồng bộ hoàn tất!\n- Thành công: {success_count}\n- Thất bại: {fail_count}\n- Bỏ qua: {skipped_count}", parent=self)
            self.main_app.log_message("Hoàn tất quá trình đồng bộ.")
        
        self.main_app.root.after(0, on_complete)

    def _get_project_original_name(self, project_id):
        conn = self.db_manager.get_connection();
        if not conn: return None
        try: cursor = conn.cursor(); cursor.execute("SELECT name FROM projects WHERE id = ?", (project_id,)); result = cursor.fetchone(); return result['name'] if result else None
        finally: conn.close()

    def _send_to_tts(self):
        selected_iid = self.library_tree.focus();
        if not selected_iid: messagebox.showwarning("Chưa chọn", "Vui lòng chọn một dự án.", parent=self); return
        self.main_app.send_story_to_tts(int(selected_iid))
        
    def _show_status_menu(self, event):
        iid = self.library_tree.identify_row(event.y)
        if iid:
            self.library_tree.selection_set(iid); status_menu = tk.Menu(self, tearoff=0)
            status_menu.add_command(label="Chưa làm", command=lambda: self._change_project_status(iid, "Chưa làm"))
            status_menu.add_command(label="Đang làm dở", command=lambda: self._change_project_status(iid, "Đang làm dở"))
            status_menu.add_command(label="Đã làm", command=lambda: self._change_project_status(iid, "Đã làm"))
            status_menu.post(event.x_root, event.y_root)

    def _change_project_status(self, project_id, new_status):
        if self.db_manager.update_project_status(int(project_id), new_status): self._load_project_data()
        else: messagebox.showerror("Lỗi", "Không thể cập nhật trạng thái.", parent=self)

    def _on_project_double_click(self, event):
        region = self.library_tree.identify("region", event.x, event.y);
        if region != "cell": return
        project_id = self.library_tree.focus();
        if not project_id: return
        column_id = self.library_tree.identify_column(event.x)
        column_map = {'#3': ('Tên Dự án', self._edit_project_name), '#4': ('Title', self._edit_project_item), '#5': ('Thumbnail', self._edit_project_item), '#6': ('Story', self._edit_project_item)}
        if column_id in column_map:
            item_type, handler = column_map[column_id]
            handler(int(project_id), item_type)

    def _edit_project_name(self, project_id, item_type=None):
        original_name = self._get_project_original_name(project_id);
        if original_name is None: return
        new_name = simpledialog.askstring("Đổi tên Dự án", "Nhập tên mới:", initialvalue=original_name, parent=self)
        if new_name and new_name.strip() and new_name.strip() != original_name:
            try:
                if self.db_manager.update_project_name(project_id, new_name.strip()): self._load_project_data()
            except ValueError as e: messagebox.showerror("Lỗi", str(e), parent=self)

    def _edit_project_item(self, project_id, item_type):
        items = self.db_manager.get_items_for_project(project_id)
        current_content = next((item['content'] for item in items if item['type'] == item_type), "")
        dialog = EditWindow(self, f"Chỉnh sửa {item_type}", current_content)
        new_content = dialog.show()
        if new_content is not None and new_content != current_content:
            if self.db_manager.add_or_update_item(project_id, item_type, new_content): self._load_project_data()
            else: messagebox.showerror("Lỗi", f"Không thể cập nhật {item_type}.")
        
    def _create_new_project(self):
        project_name = simpledialog.askstring("Tạo Dự án Mới", "Nhập tên cho dự án mới:", parent=self)
        if not (project_name and project_name.strip()): return
        selected_group_name = self.selected_group.get()
        if selected_group_name == "-- Tất cả Nhóm --" or not selected_group_name:
            local_group = next((g for g in self.project_groups_data if g.get('type') == 'Local'), None)
            if not local_group: messagebox.showerror("Lỗi", "Không tìm thấy nhóm 'Local' nào. Vui lòng tạo một nhóm trong Cài đặt.", parent=self); return
            target_group = local_group['name']
        else: target_group = selected_group_name
        if self.db_manager.create_project(project_name.strip(), source_group=target_group):
            messagebox.showinfo("Thành công", f"Đã tạo dự án '{project_name}' trong nhóm '{target_group}'.", parent=self)
            self.selected_group.set(target_group); self._on_group_selected()
        else: messagebox.showerror("Lỗi", "Tên dự án có thể đã tồn tại.", parent=self)
    
    def _delete_selected_project(self):
        selected_iid = self.library_tree.focus();
        if not selected_iid: return
        project_id = int(selected_iid)
        original_name = self._get_project_original_name(project_id) or f"ID {project_id}"
        if messagebox.askyesno("Xác nhận Xóa", f"Bạn có chắc muốn xóa dự án '{original_name}' không?"):
            if self.db_manager.delete_project(project_id):
                self._load_project_data()
                if self.main_app.active_project_id == project_id: self.main_app.clear_active_project()
            else: messagebox.showerror("Lỗi", "Không thể xóa dự án.")

    def _set_active_project(self):
        selected_iid = self.library_tree.focus();
        if not selected_iid: return
        project_id = int(selected_iid)
        original_name = self._get_project_original_name(project_id)
        if original_name is None: return
        self.main_app.set_active_project(project_id, original_name)
        
    def _repair_gdrive_project_groups(self):
        """
        Hàm gỡ lỗi tạm thời để sửa chữa các dự án GDrive bị thiếu source_group.
        """
        selected_group_name = self.selected_group.get()
        if not selected_group_name or selected_group_name == "-- Tất cả Nhóm --":
            messagebox.showwarning("Yêu cầu", "Vui lòng chọn một Nhóm dự án Google Drive cụ thể để sửa chữa.", parent=self)
            return

        group_info = next((g for g in self.project_groups_data if g.get('name') == selected_group_name), None)
        if not (group_info and group_info.get('type') == 'Google Drive'):
            messagebox.showwarning("Yêu cầu", "Chức năng này chỉ dành cho các Nhóm dự án loại Google Drive.", parent=self)
            return
            
        threading.Thread(target=self._repair_task, args=(group_info,), daemon=True).start()

    def _repair_task(self, group_info):
        """Tác vụ chạy ngầm để sửa chữa dữ liệu."""
        group_name = group_info['name']
        folder_id = group_info['folder_id']
        self.main_app.log_message(f"--- BẮT ĐẦU SỬA CHỮA DỮ LIỆU CHO NHÓM: '{group_name}' ---")

        # 1. Lấy danh sách file từ Google Drive
        self.main_app.log_message("Đang lấy danh sách file từ Google Drive...")
        creds, error = google_api_handler.get_credentials()
        if error:
            self.main_app.log_message(f"[ERROR] Không thể xác thực Google: {error}")
            self.main_app.root.after_idle(lambda: messagebox.showerror("Lỗi", f"Xác thực Google thất bại: {error}", parent=self))
            return
        
        drive_files, error = google_api_handler.list_files_in_folder(creds, folder_id)
        if error:
            self.main_app.log_message(f"[ERROR] Không thể lấy danh sách file: {error}")
            self.main_app.root.after_idle(lambda: messagebox.showerror("Lỗi", f"Không thể lấy danh sách file: {error}", parent=self))
            return
            
        drive_file_names = {file['name'] for file in drive_files}
        self.main_app.log_message(f"Tìm thấy {len(drive_file_names)} file trên Google Drive.")

        # 2. Lấy danh sách dự án "mồ côi" từ CSDL
        all_projects = self.db_manager.get_all_projects()
        orphan_projects = [p for p in all_projects if p.get('source_group') is None or p.get('source_group') == '']
        self.main_app.log_message(f"Tìm thấy {len(orphan_projects)} dự án bị thiếu thông tin nhóm trong CSDL.")

        # 3. So sánh và cập nhật
        repaired_count = 0
        for project in orphan_projects:
            project_name = project['name']
            if project_name in drive_file_names:
                self.main_app.log_message(f"  -> Sửa chữa dự án '{project_name}', gán vào nhóm '{group_name}'...")
                if self.db_manager.update_project_source_group(project_name, group_name):
                    repaired_count += 1
                else:
                    self.main_app.log_message(f"  -> [LỖI] Không thể cập nhật dự án '{project_name}'.")

        self.main_app.log_message(f"--- KẾT THÚC SỬA CHỮA ---")
        self.main_app.log_message(f"Đã sửa chữa thành công {repaired_count} dự án.")
        
        # Lên lịch cập nhật UI trên luồng chính
        def on_complete():
            messagebox.showinfo("Hoàn tất", f"Quá trình sửa chữa dữ liệu đã hoàn tất.\nĐã cập nhật thông tin cho {repaired_count} dự án.", parent=self)
            self._load_project_data() # Tải lại danh sách để thấy kết quả
            
        self.main_app.root.after_idle(on_complete)
        
    def _force_assign_group_to_orphans(self):
        """Hàm gỡ lỗi: Gán cưỡng bức nhóm đang chọn cho tất cả các dự án mồ côi."""
        selected_group_name = self.selected_group.get()
        if not selected_group_name or selected_group_name == "-- Tất cả Nhóm --":
            messagebox.showwarning("Yêu cầu", "Vui lòng chọn một Nhóm dự án cụ thể (ví dụ: 'Radio Gia Đình') để gán.", parent=self)
            return

        if not messagebox.askyesno("Xác nhận Cưỡng bức", f"Hành động này sẽ gán nhóm '{selected_group_name}' cho TẤT CẢ các dự án chưa có nhóm.\n\nĐây là thao tác không thể hoàn tác.\nBạn có chắc chắn muốn tiếp tục?", parent=self):
            return

        threading.Thread(target=self._force_assign_task, args=(selected_group_name,), daemon=True).start()

    # hotfix - 2025-07-31 - Sửa lỗi 'sqlite3.Row' object has no attribute 'get' lần 2
    def _force_assign_task(self, target_group):
        self.main_app.log_message(f"--- BẮT ĐẦU GÁN NHÓM CƯỠNG BỨC CHO '{target_group}' ---")
        all_projects = self.db_manager.get_all_projects()
        
        orphan_projects = []
        if all_projects:
            for p in all_projects:
                try:
                    # SỬA LỖI TẠI ĐÂY: Truy cập bằng key và kiểm tra None
                    if p['source_group'] is None or p['source_group'] == '':
                        orphan_projects.append(p)
                except IndexError:
                    # Bắt lỗi nếu cột 'source_group' không tồn tại cho bản ghi cũ
                    orphan_projects.append(p)

        if not orphan_projects:
            self.main_app.log_message("Không tìm thấy dự án mồ côi nào.")
            self.main_app.root.after_idle(lambda: messagebox.showinfo("Hoàn tất", "Không tìm thấy dự án nào cần sửa chữa.", parent=self))
            return
            
        self.main_app.log_message(f"Tìm thấy {len(orphan_projects)} dự án mồ côi. Bắt đầu cập nhật...")
        
        success_count = 0
        for project in orphan_projects:
            project_id = project['id']
            if self.db_manager.update_project_source_group_by_id(project_id, target_group):
                success_count += 1
        
        self.main_app.log_message(f"Đã cập nhật thành công {success_count} / {len(orphan_projects)} dự án.")
        self.main_app.log_message("--- KẾT THÚC GÁN NHÓM ---")
        def on_complete():
            messagebox.showinfo("Hoàn tất", f"Đã gán nhóm '{target_group}' cho {success_count} dự án thành công.", parent=self)
            self._load_project_data()
        
        self.main_app.root.after_idle(on_complete)