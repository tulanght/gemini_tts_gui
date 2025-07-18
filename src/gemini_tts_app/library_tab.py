# file-path: src/gemini_tts_app/library_tab.py
# version: 6.1
# last-updated: 2025-07-15
# description: Thêm nút "Làm việc với Dự án này" để kích hoạt một dự án.

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext

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
        self._create_widgets()
        self.bind("<Visibility>", self._on_tab_visible)

    def _create_widgets(self):
        tree_frame = ttk.Frame(self)
        tree_frame.pack(expand=True, fill="both", pady=(0, 10))
        columns = ("id", "name", "title", "thumbnail", "story")
        self.library_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.library_tree.heading("id", text="ID")
        self.library_tree.heading("name", text="Tên Dự án")
        self.library_tree.heading("title", text="Tiêu đề")
        self.library_tree.heading("thumbnail", text="Kịch bản Thumbnail")
        self.library_tree.heading("story", text="Nội dung Truyện")
        self.library_tree.column("id", width=50, anchor="center", stretch=False)
        self.library_tree.column("name", width=200)
        self.library_tree.column("title", width=250)
        self.library_tree.column("thumbnail", width=250)
        self.library_tree.column("story", width=200)
        self.library_tree.bind("<Double-1>", self._on_project_double_click)
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.library_tree.yview)
        self.library_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.library_tree.pack(side="left", expand=True, fill="both")
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", pady=(10,0))
        # NÚT MỚI
        self.work_on_project_button = ttk.Button(button_frame, text="Làm việc với Dự án này", style="Accent.TButton", command=self._set_active_project)
        self.work_on_project_button.pack(side="left", padx=(0, 10))
        self.add_project_button = ttk.Button(button_frame, text="Tạo Dự án Mới...", command=self._create_new_project)
        self.add_project_button.pack(side="left")
        self.delete_project_button = ttk.Button(button_frame, text="Xóa Dự án", style="Accent.TButton", command=self._delete_selected_project)
        self.delete_project_button.pack(side="right")
        # NÚT MỚI
        self.sync_button = ttk.Button(button_frame, text="Đồng bộ từ Google Drive", command=self._sync_from_gdrive)
        self.sync_button.pack(side="left", padx=5)

        self.delete_project_button = ttk.Button(button_frame, text="Xóa Dự án", command=self._delete_selected_project)
        self.delete_project_button.pack(side="right")

    def _sync_from_gdrive(self):
        """Placeholder cho chức năng đồng bộ hóa từ Google Drive."""
        messagebox.showinfo(
            "Sắp ra mắt", 
            "Tính năng đồng bộ hóa từ Google Drive sẽ được kết nối ở bước tiếp theo.", 
            parent=self
        )
    
    def _set_active_project(self):
        """Lấy dự án được chọn và đặt nó làm dự án hoạt động trong ứng dụng chính."""
        selected_iid = self.library_tree.focus()
        if not selected_iid:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một dự án để bắt đầu làm việc.", parent=self)
            return

        project_id = int(selected_iid)
        project_name = self.library_tree.item(selected_iid)['values'][1]

        # Gọi hàm trong main_app để xử lý
        self.main_app.set_active_project(project_id, project_name)


    def _on_tab_visible(self, event):
        self._load_project_data()

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
            self.library_tree.insert("", "end", iid=project['id'], values=(
                project['id'], project['name'], 
                content_map['Title'], 
                content_map['Thumbnail'].replace('\n', ' '), 
                story_preview
            ))
        if selected_iid and self.library_tree.exists(selected_iid):
            self.library_tree.focus(selected_iid)
            self.library_tree.selection_set(selected_iid)

    def _on_project_double_click(self, event):
        region = self.library_tree.identify("region", event.x, event.y)
        if region != "cell": return
        project_id = self.library_tree.focus()
        if not project_id: return

        column_id = self.library_tree.identify_column(event.x)
        project_id = int(project_id)

        column_map = {
            '#2': ('Tên Dự án', self._edit_project_name),
            '#3': ('Title', self._edit_project_item),
            '#4': ('Thumbnail', self._edit_project_item),
            '#5': ('Story', self._edit_project_item),
        }

        if column_id in column_map:
            item_type, handler = column_map[column_id]
            handler(project_id, item_type)

    def _edit_project_name(self, project_id, item_type=None):
        current_name = self.library_tree.item(project_id)['values'][1]
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
        project_name = self.library_tree.item(selected_iid)['values'][1]
        if messagebox.askyesno("Xác nhận Xóa", f"Bạn có chắc chắn muốn xóa toàn bộ dự án '{project_name}' không?\nMọi dữ liệu liên quan sẽ bị mất vĩnh viễn."):
            if self.db_manager.delete_project(project_id):
                self._load_project_data()
            else:
                messagebox.showerror("Lỗi", "Không thể xóa dự án.")