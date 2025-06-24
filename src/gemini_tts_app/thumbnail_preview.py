# src/gemini_tts_app/thumbnail_preview.py
# v1.3 - 2025-06-24: Implement fixed-size window and fit-to-frame text logic.
# Module độc lập để quản lý cửa sổ xem trước Thumbnail

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageOps
from matplotlib import font_manager
import logging

class ThumbnailPreviewWindow(tk.Toplevel):
    """
    Một cửa sổ Toplevel tự quản lý để hiển thị, tùy chỉnh và xuất ảnh thumbnail.
    Cửa sổ này có kích thước cố định để đảm bảo tính nhất quán của preview.
    """
    def __init__(self, parent, text_content, log_callback):
        super().__init__(parent)
        self.parent = parent
        self.text_content = text_content
        self.log_callback = log_callback

        # --- Định nghĩa kích thước cố định cho vùng vẽ ---
        self.canvas_width = 854
        self.canvas_height = int(self.canvas_width * 9 / 16) # ~480

        self.title("Xem trước Thumbnail")
        # Không đặt geometry cố định, để Tkinter tự tính toán chiều cao tổng thể

        # --- Biến điều khiển giao diện ---
        self.system_fonts = self._get_system_fonts()
        self.selected_font_family = tk.StringVar()
        self.selected_font_size = tk.IntVar(value=90) # Cỡ chữ cơ sở cho file export

        self.preview_bg_photo = None
        self.preview_bg_path = None
        self.preview_overlay_alpha = tk.IntVar(value=100)

        self._setup_widgets()
        
        # Sau khi các widget đã được tạo, ta có thể ngăn không cho resize
        self.resizable(False, False)
        
        # Vẽ canvas lần đầu
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
            return ['Arial', 'Times New Roman']

    def _find_font_path(self, font_name):
        """Tìm đường dẫn file của một họ font cụ thể."""
        try:
            for weight in ['black', 'extrabold', 'bold', 'normal']:
                try:
                    fp = font_manager.FontProperties(family=font_name, weight=weight)
                    return font_manager.findfont(fp, fallback_to_default=False)
                except ValueError: continue
            return font_manager.findfont(font_manager.FontProperties(family=font_name))
        except ValueError:
            self.log_callback(f"Không tìm thấy file cho font '{font_name}', sử dụng font mặc định.")
            return font_manager.findfont(font_manager.FontProperties(family='sans-serif'))

    def _setup_widgets(self):
        """Tạo và sắp xếp tất cả các widget trong cửa sổ."""
        control_frame = ttk.Frame(self, padding=10)
        control_frame.pack(side=tk.TOP, fill=tk.X, expand=False)
        
        row1 = ttk.Frame(control_frame); row1.pack(fill=tk.X, pady=2)
        ttk.Button(row1, text="Chọn ảnh nền...", command=self._select_background_image).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(row1, text="Xuất ảnh PNG...", command=self._export_thumbnail, style="Accent.TButton").pack(side=tk.RIGHT)
        
        row2 = ttk.Frame(control_frame); row2.pack(fill=tk.X, pady=(5,2), expand=True)
        ttk.Label(row2, text="Font:").pack(side=tk.LEFT)
        font_combo = ttk.Combobox(row2, textvariable=self.selected_font_family, values=self.system_fonts, state='readonly', width=30)
        font_combo.pack(side=tk.LEFT, padx=(5, 10), fill=tk.X, expand=True)
        font_combo.bind('<<ComboboxSelected>>', self._redraw_thumbnail_canvas)
        
        if "Be Vietnam Pro" in self.system_fonts: self.selected_font_family.set("Be Vietnam Pro")
        elif "Segoe UI" in self.system_fonts: self.selected_font_family.set("Segoe UI")
        elif "Arial" in self.system_fonts: self.selected_font_family.set("Arial")
        elif self.system_fonts: self.selected_font_family.set(self.system_fonts[0])

        ttk.Label(row2, text="Cỡ chữ:").pack(side=tk.LEFT, padx=(10, 0))
        font_size_spinbox = ttk.Spinbox(row2, from_=20, to=200, increment=2, textvariable=self.selected_font_size, width=5, command=self._redraw_thumbnail_canvas)
        font_size_spinbox.pack(side=tk.LEFT, padx=5)

        row3 = ttk.Frame(control_frame); row3.pack(fill=tk.X, pady=2)
        ttk.Label(row3, text="Độ mờ lớp phủ:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Scale(row3, from_=0, to=255, variable=self.preview_overlay_alpha, command=self._redraw_thumbnail_canvas).pack(fill=tk.X, expand=True)

        # Thiết lập Vùng vẽ Thumbnail với kích thước 16:9 cố định
        canvas_container = ttk.Frame(self, width=self.canvas_width, height=self.canvas_height)
        canvas_container.pack(side=tk.BOTTOM, expand=True, fill="both")
        canvas_container.pack_propagate(False) # Ngăn container co lại theo canvas
        
        self.preview_canvas = tk.Canvas(canvas_container, bg="#1c1c1c", highlightthickness=0, width=self.canvas_width, height=self.canvas_height)
        self.preview_canvas.pack()

    def _select_background_image(self):
        file_path = filedialog.askopenfilename(parent=self, title="Chọn ảnh nền", filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if file_path:
            self.preview_bg_path = file_path
            self._redraw_thumbnail_canvas()
    
    # --- START REPLACEMENT FOR _redraw_thumbnail_canvas ---
    def _redraw_thumbnail_canvas(self, event=None):
        if not self.winfo_exists(): return
        canvas = self.preview_canvas
        canvas.delete("all")
        
        try:
            if self.preview_bg_path: bg_image = Image.open(self.preview_bg_path).convert("RGBA")
            else: bg_image = Image.new('RGBA', (1280, 720), (80, 80, 80, 255))
        except Exception as e:
            canvas.create_text(10, 10, text=f"Lỗi ảnh: {e}", fill="red", anchor=tk.NW); return

        bg_image = ImageOps.fit(bg_image, (self.canvas_width, self.canvas_height), Image.Resampling.LANCZOS)
        alpha = self.preview_overlay_alpha.get()
        if alpha > 0:
            overlay = Image.new('RGBA', bg_image.size, (0, 0, 0, alpha))
            bg_image = Image.alpha_composite(bg_image, overlay)
        self.preview_bg_photo = ImageTk.PhotoImage(bg_image)
        canvas.create_image(0, 0, anchor=tk.NW, image=self.preview_bg_photo)

        font_name = self.selected_font_family.get()
        font_path = self._find_font_path(font_name)
        if not font_path:
            canvas.create_text(10, 10, text=f"Lỗi: Không tìm thấy file font cho '{font_name}'.", fill="red", anchor=tk.NW); return

        current_font_size = self.selected_font_size.get()
        padding = 20
        
        # Tạo một đối tượng Draw tạm thời để tính toán
        temp_draw = ImageDraw.Draw(Image.new("RGB", (1,1)))

        while current_font_size > 10:
            test_font = ImageFont.truetype(font_path, current_font_size)
            # SỬA LỖI: Dùng đúng hàm multiline_textbbox từ đối tượng Draw
            text_box = temp_draw.multiline_textbbox((0,0), self.text_content, font=test_font, align='center')
            text_height = text_box[3] - text_box[1]

            if text_height <= (self.canvas_height - padding):
                break
            current_font_size -= 2
        
        font_tuple_for_canvas = (font_name, current_font_size, "bold")
        
        x = self.canvas_width / 2
        y = self.canvas_height / 2

        outline_color = "black"
        offset = max(2, int(current_font_size / 30))
        
        # Dùng anchor='mm' (middle-middle) để căn giữa chính xác
        canvas.create_text(x, y, text=self.text_content, font=font_tuple_for_canvas, fill=outline_color, justify=tk.CENTER, anchor='mm', width=self.canvas_width * 0.95)
        canvas.create_text(x, y, text=self.text_content, font=font_tuple_for_canvas, fill="white", justify=tk.CENTER, anchor='mm', width=self.canvas_width * 0.95)
    # --- END REPLACEMENT FOR _redraw_thumbnail_canvas ---
    
    # --- START REPLACEMENT FOR _export_thumbnail ---
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
            font_name = self.selected_font_family.get()
            font_path = self._find_font_path(font_name)
            if not font_path:
                messagebox.showerror("Lỗi Font", "Không tìm thấy font phù hợp để xuất ảnh.", parent=self); return
            
            current_font_size = self.selected_font_size.get()
            padding = 40
            while current_font_size > 10:
                test_font = ImageFont.truetype(font_path, current_font_size)
                # SỬA LỖI: Dùng đúng hàm multiline_textbbox từ đối tượng Draw
                text_box = draw.multiline_textbbox((0,0), self.text_content, font=test_font, align='center')
                text_height = text_box[3] - text_box[1]
                if text_height <= (720 - padding): break # So sánh với chiều cao ảnh export
                current_font_size -= 2

            font = ImageFont.truetype(font_path, current_font_size)

            x, y = 1280 / 2, 720 / 2
            
            outline_color = "black"
            main_color = "white"
            stroke_width = max(4, int(current_font_size / 30))

            # Dùng stroke_width để tạo viền tốt hơn
            draw.text((x, y), self.text_content, font=font, fill=main_color, anchor='mm', align='center', stroke_width=stroke_width, stroke_fill=outline_color)

            file_path = filedialog.asksaveasfilename(parent=self, title="Xuất ảnh Thumbnail", defaultextension=".png", filetypes=[("PNG Image", "*.png")])
            if file_path:
                final_image = bg_image.resize((1920, 1080), Image.Resampling.LANCZOS)
                final_image.convert("RGB").save(file_path, quality=95)
                messagebox.showinfo("Thành công", f"Đã xuất ảnh thumbnail (1920x1080) thành công tại:\n{file_path}", parent=self)
                self.log_callback(f"Đã xuất thumbnail: {file_path}")

        except Exception as e:
            messagebox.showerror("Lỗi xuất ảnh", f"Đã có lỗi xảy ra: {e}", parent=self)
    # --- END REPLACEMENT FOR _export_thumbnail ---