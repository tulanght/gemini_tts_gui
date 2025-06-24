# src/gemini_tts_app/thumbnail_preview.py
# v1.2 - 2025-06-24: Add dynamic font and size selection controls.
# Module độc lập để quản lý cửa sổ xem trước Thumbnail

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageOps
from matplotlib import font_manager
import logging
import re

class ThumbnailPreviewWindow(tk.Toplevel):
    """
    Một cửa sổ Toplevel tự quản lý để hiển thị, tùy chỉnh và xuất ảnh thumbnail.
    """
    def __init__(self, parent, text_content, log_callback):
        super().__init__(parent)
        self.parent = parent
        self.text_content = text_content
        self.log_callback = log_callback

        self.title("Xem trước Thumbnail")
        self.geometry("854x580")
        self.minsize(427, 320)

        # --- Biến điều khiển giao diện ---
        self.system_fonts = self._get_system_fonts()
        self.selected_font_family = tk.StringVar()
        self.selected_font_size = tk.IntVar(value=90) # Cỡ chữ cho file export 1280px

        self.preview_bg_photo = None
        self.preview_bg_path = None
        self.preview_overlay_alpha = tk.IntVar(value=100)

        self._setup_widgets()
        
        self.bind("<Configure>", self._on_preview_resize)
        self.update_idletasks()
        self._redraw_thumbnail_canvas()

        self.transient(parent)
        self.grab_set()
        self.wait_window(self)

    def _get_system_fonts(self):
        """Lấy danh sách các họ font (font family) có trên hệ thống."""
        try:
            font_paths = font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
            font_names = sorted(list(set([font_manager.FontProperties(fname=fname).get_name() for fname in font_paths])))
            self.log_callback(f"Tìm thấy {len(font_names)} họ font trên hệ thống.")
            return font_names
        except Exception as e:
            self.log_callback(f"Lỗi khi quét font hệ thống: {e}")
            return ['Arial', 'Times New Roman'] # Fallback

    def _find_font_path(self, font_name):
        """Tìm đường dẫn file của một họ font cụ thể."""
        try:
            # Ưu tiên tìm các phiên bản Bold, Black, ExtraBold
            for weight in ['black', 'extrabold', 'bold', 'normal']:
                try:
                    fp = font_manager.FontProperties(family=font_name, weight=weight)
                    path = font_manager.findfont(fp, fallback_to_default=False)
                    return path
                except ValueError:
                    continue
            # Nếu không có weight nào khớp, thử tìm không cần weight
            return font_manager.findfont(font_manager.FontProperties(family=font_name))
        except ValueError:
            self.log_callback(f"Không tìm thấy file cho font '{font_name}', sử dụng font mặc định.")
            return font_manager.findfont(font_manager.FontProperties(family='sans-serif'))

    def _setup_widgets(self):
        """Tạo và sắp xếp tất cả các widget trong cửa sổ."""
        # --- KHUNG ĐIỀU KHIỂN ---
        control_frame = ttk.Frame(self, padding=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        # --- Hàng 1: Ảnh nền & Xuất ảnh ---
        row1 = ttk.Frame(control_frame)
        row1.pack(fill=tk.X, pady=2)
        ttk.Button(row1, text="Chọn ảnh nền...", command=self._select_background_image).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(row1, text="Xuất ảnh PNG...", command=self._export_thumbnail, style="Accent.TButton").pack(side=tk.RIGHT)
        
        # --- Hàng 2: Font & Cỡ chữ ---
        row2 = ttk.Frame(control_frame)
        row2.pack(fill=tk.X, pady=2, expand=True)
        ttk.Label(row2, text="Font:").pack(side=tk.LEFT)
        font_combo = ttk.Combobox(row2, textvariable=self.selected_font_family, values=self.system_fonts, state='readonly')
        font_combo.pack(side=tk.LEFT, padx=(5, 10), fill=tk.X, expand=True)
        font_combo.bind('<<ComboboxSelected>>', self._redraw_thumbnail_canvas)
        
        # Thiết lập font mặc định
        if "Be Vietnam Pro" in self.system_fonts:
            self.selected_font_family.set("Be Vietnam Pro")
        elif "Segoe UI" in self.system_fonts:
            self.selected_font_family.set("Segoe UI")
        elif "Arial" in self.system_fonts:
            self.selected_font_family.set("Arial")
        elif self.system_fonts:
            self.selected_font_family.set(self.system_fonts[0])

        ttk.Label(row2, text="Cỡ chữ:").pack(side=tk.LEFT, padx=(10, 0))
        font_size_spinbox = ttk.Spinbox(row2, from_=20, to=200, increment=2, textvariable=self.selected_font_size, width=5, command=self._redraw_thumbnail_canvas)
        font_size_spinbox.pack(side=tk.LEFT, padx=5)

        # --- Hàng 3: Độ mờ ---
        row3 = ttk.Frame(control_frame)
        row3.pack(fill=tk.X, pady=2)
        ttk.Label(row3, text="Độ mờ lớp phủ:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Scale(row3, from_=0, to=255, variable=self.preview_overlay_alpha, command=self._redraw_thumbnail_canvas).pack(fill=tk.X, expand=True)

        canvas_container = ttk.Frame(self)
        canvas_container.pack(expand=True, fill="both")
        self.preview_canvas = tk.Canvas(canvas_container, bg="#1c1c1c", highlightthickness=0)
        self.preview_canvas.pack(expand=True, fill="both")

    def _on_preview_resize(self, event=None):
        if hasattr(self, '_resize_job'):
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(100, self._redraw_thumbnail_canvas)

    def _select_background_image(self):
        file_path = filedialog.askopenfilename(parent=self, title="Chọn ảnh nền", filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if file_path:
            self.preview_bg_path = file_path
            self._redraw_thumbnail_canvas()
    
    def _redraw_thumbnail_canvas(self, event=None):
        if not self.winfo_exists(): return
        canvas = self.preview_canvas
        canvas.delete("all")
        
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        if canvas_width < 10 or canvas_height < 10: return

        try:
            if self.preview_bg_path: bg_image = Image.open(self.preview_bg_path).convert("RGBA")
            else: bg_image = Image.new('RGBA', (1280, 720), (80, 80, 80, 255))
        except Exception as e:
            canvas.create_text(10, 10, text=f"Lỗi ảnh: {e}", fill="red", anchor=tk.NW); return

        bg_image = ImageOps.fit(bg_image, (canvas_width, canvas_height), Image.Resampling.LANCZOS)
        alpha = self.preview_overlay_alpha.get()
        if alpha > 0:
            overlay = Image.new('RGBA', bg_image.size, (0, 0, 0, alpha))
            bg_image = Image.alpha_composite(bg_image, overlay)
        self.preview_bg_photo = ImageTk.PhotoImage(bg_image)
        canvas.create_image(0, 0, anchor=tk.NW, image=self.preview_bg_photo)

        # --- LẤY FONT VÀ CỠ CHỮ TỪ GIAO DIỆN ---
        font_name = self.selected_font_family.get()
        base_font_size = self.selected_font_size.get()
        font_path = self._find_font_path(font_name)
        if not font_path:
            canvas.create_text(10, 10, text=f"Lỗi: Không tìm thấy file font cho '{font_name}'.", fill="red", anchor=tk.NW); return

        # Tính toán cỡ chữ tương đối với kích thước canvas
        font_size_on_canvas = int(base_font_size * (canvas_width / 1280.0))
        
        pillow_font = ImageFont.truetype(font_path, font_size_on_canvas)
        font_tuple_for_canvas = (font_name, font_size_on_canvas, "bold")
        
        temp_draw = ImageDraw.Draw(Image.new("RGB", (1,1)))
        text_box = temp_draw.multiline_textbbox((0,0), self.text_content, font=pillow_font, align="center")
        text_height = text_box[3] - text_box[1]
        x = canvas_width / 2
        y = (canvas_height - text_height) / 2

        outline_color = "black"
        offset = max(2, int(font_size_on_canvas / 30))
        
        canvas.create_text(x+offset, y+offset, text=self.text_content, font=font_tuple_for_canvas, fill=outline_color, justify=tk.CENTER, anchor=tk.N, width=canvas_width * 0.95)
        canvas.create_text(x, y, text=self.text_content, font=font_tuple_for_canvas, fill="white", justify=tk.CENTER, anchor=tk.N, width=canvas_width * 0.95)
    
    def _export_thumbnail(self):
        try:
            if self.preview_bg_path: bg_image = Image.open(self.preview_bg_path).convert("RGBA")
            else: bg_image = Image.new('RGBA', (1280, 720), (80, 80, 80, 255))
            bg_image = ImageOps.fit(bg_image, (1280, 720), Image.Resampling.LANCZOS)

            alpha = self.preview_overlay_alpha.get()
            if alpha > 0:
                overlay = Image.new('RGBA', bg_image.size, (0, 0, 0, alpha))
                bg_image = Image.alpha_composite(bg_image, overlay)

            draw = ImageDraw.Draw(bg_image)
            
            # Lấy font và cỡ chữ từ giao diện để xuất ảnh chất lượng cao
            font_name = self.selected_font_family.get()
            font_size = self.selected_font_size.get()
            font_path = self._find_font_path(font_name)
            if not font_path:
                messagebox.showerror("Lỗi Font", "Không tìm thấy font phù hợp để xuất ảnh.", parent=self); return
            
            font = ImageFont.truetype(font_path, font_size)

            text_bbox = draw.multiline_textbbox((0,0), self.text_content, font=font, align="center")
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            x = (1280 - text_width) / 2
            y = (720 - text_height) / 2
            
            outline_color = "black"
            main_color = "white"
            offset = max(3, int(font_size / 30))

            for dx in range(-offset, offset+1, offset):
                for dy in range(-offset, offset+1, offset):
                    if dx != 0 or dy != 0:
                        draw.multiline_text((x+dx, y+dy), self.text_content, font=font, fill=outline_color, align="center")
            draw.multiline_text((x, y), self.text_content, font=font, fill=main_color, align="center")

            file_path = filedialog.asksaveasfilename(parent=self, title="Xuất ảnh Thumbnail", defaultextension=".png", filetypes=[("PNG Image", "*.png")])
            if file_path:
                bg_image.convert("RGB").save(file_path, quality=95)
                messagebox.showinfo("Thành công", f"Đã xuất ảnh thumbnail thành công tại:\n{file_path}", parent=self)
                self.log_callback(f"Đã xuất thumbnail: {file_path}")

        except Exception as e:
            messagebox.showerror("Lỗi xuất ảnh", f"Đã có lỗi xảy ra: {e}", parent=self)