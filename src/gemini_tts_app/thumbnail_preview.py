# src/gemini_tts_app/thumbnail_preview.py
# v1.0 - 2025-06-24: Initial refactor from main_app.py
# Module độc lập để quản lý cửa sổ xem trước Thumbnail

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageOps

class ThumbnailPreviewWindow(tk.Toplevel):
    """
    Một cửa sổ Toplevel tự quản lý để hiển thị, tùy chỉnh và xuất ảnh thumbnail.
    """
    def __init__(self, parent, text_content, log_callback):
        super().__init__(parent)
        self.parent = parent
        self.text_content = text_content
        self.log_callback = log_callback # Sử dụng callback để log thay vì phụ thuộc vào main_app

        self.title("Xem trước Thumbnail")
        self.geometry("854x580")
        self.minsize(427, 320)

        # Các biến trạng thái của riêng cửa sổ này
        self.preview_bg_photo = None # Tham chiếu đến đối tượng PhotoImage của Tkinter
        self.preview_bg_path = None  # Đường dẫn đến file ảnh nền
        self.preview_overlay_alpha = tk.IntVar(value=100) # Biến cho thanh trượt độ mờ

        self._setup_widgets()
        
        self.bind("<Configure>", self._on_preview_resize)
        self.update_idletasks() # Đảm bảo winfo_width/height trả về giá trị đúng
        self._redraw_thumbnail_canvas()

        # Cài đặt để cửa sổ này hoạt động như một dialog modal
        self.transient(parent)
        self.grab_set()
        self.wait_window(self) # Chờ cho đến khi cửa sổ này bị đóng

    def _setup_widgets(self):
        """Tạo và sắp xếp tất cả các widget trong cửa sổ."""
        # --- KHUNG ĐIỀU KHIỂN ---
        control_frame = ttk.Frame(self, padding=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        ttk.Button(control_frame, text="Chọn ảnh nền...", command=self._select_background_image).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(control_frame, text="Độ mờ lớp phủ:").pack(side=tk.LEFT, padx=5)
        ttk.Scale(control_frame, from_=0, to=255, variable=self.preview_overlay_alpha, command=lambda e: self._redraw_thumbnail_canvas()).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        ttk.Button(control_frame, text="Xuất ảnh PNG...", command=self._export_thumbnail, style="Accent.TButton").pack(side=tk.RIGHT, padx=5)

        # --- CANVAS XEM TRƯỚC ---
        canvas_container = ttk.Frame(self)
        canvas_container.pack(expand=True, fill="both")
        self.preview_canvas = tk.Canvas(canvas_container, bg="#1c1c1c", highlightthickness=0)
        self.preview_canvas.pack(expand=True, fill="both")

    def _on_preview_resize(self, event=None):
        """Gọi lại hàm vẽ sau một khoảng trễ ngắn khi kích thước cửa sổ thay đổi."""
        if hasattr(self, '_resize_job'):
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(300, self._redraw_thumbnail_canvas)

    def _select_background_image(self):
        """Mở dialog để người dùng chọn ảnh nền."""
        file_path = filedialog.askopenfilename(
            parent=self,
            title="Chọn ảnh nền", 
            filetypes=[("Image Files", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            self.preview_bg_path = file_path
            self._redraw_thumbnail_canvas()
    
    def _redraw_thumbnail_canvas(self):
        """Vẽ lại toàn bộ canvas, bao gồm ảnh nền, lớp phủ và văn bản."""
        if not self.winfo_exists(): return
        canvas = self.preview_canvas
        canvas.delete("all")
        
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        if canvas_width < 10 or canvas_height < 10: return

        try:
            if self.preview_bg_path:
                bg_image = Image.open(self.preview_bg_path).convert("RGBA")
            else:
                bg_image = Image.new('RGBA', (1280, 720), (80, 80, 80, 255))
        except Exception as e:
            canvas.create_text(10, 10, text=f"Lỗi ảnh: {e}", fill="red", anchor=tk.NW)
            return

        bg_image = ImageOps.fit(bg_image, (canvas_width, canvas_height), Image.Resampling.LANCZOS)
        
        alpha = self.preview_overlay_alpha.get()
        if alpha > 0:
            overlay = Image.new('RGBA', bg_image.size, (0, 0, 0, alpha))
            bg_image = Image.alpha_composite(bg_image, overlay)
        
        self.preview_bg_photo = ImageTk.PhotoImage(bg_image)
        canvas.create_image(0, 0, anchor=tk.NW, image=self.preview_bg_photo)

        text_content = self.text_content
        font_size = int(canvas_width / 16)
        try:
            pillow_font = ImageFont.truetype("impact.ttf", font_size)
            font_tuple = ("Impact", font_size, "normal")
        except IOError:
            pillow_font = ImageFont.truetype("arialbd.ttf", font_size)
            font_tuple = ("Arial Black", font_size, "bold")

        temp_draw = ImageDraw.Draw(Image.new("RGB", (1,1)))
        text_box = temp_draw.multiline_textbbox((0,0), text_content, font=pillow_font, align="center")
        text_height = text_box[3] - text_box[1]

        x = canvas_width / 2
        y = (canvas_height - text_height) / 2

        outline_color = "black"
        offset = max(2, int(font_size / 25))
        
        canvas.create_text(x, y, text=text_content, font=font_tuple, fill=outline_color, justify=tk.CENTER, anchor=tk.N, width=canvas_width * 0.9)
        canvas.create_text(x, y, text=text_content, font=font_tuple, fill="white", justify=tk.CENTER, anchor=tk.N, width=canvas_width * 0.9)
    
    def _export_thumbnail(self):
        """Xuất thumbnail hiện tại ra file ảnh PNG chất lượng cao."""
        try:
            if self.preview_bg_path:
                bg_image = Image.open(self.preview_bg_path).convert("RGBA")
            else:
                bg_image = Image.new('RGBA', (1280, 720), (80, 80, 80, 255))

            bg_image = ImageOps.fit(bg_image, (1280, 720), Image.Resampling.LANCZOS)
            alpha = self.preview_overlay_alpha.get()
            if alpha > 0:
                overlay = Image.new('RGBA', bg_image.size, (0, 0, 0, alpha))
                bg_image = Image.alpha_composite(bg_image, overlay)

            draw = ImageDraw.Draw(bg_image)
            font_size = int(1280 / 16)
            try:
                font = ImageFont.truetype("impact.ttf", font_size)
            except IOError:
                font = ImageFont.truetype("arialbd.ttf", font_size)

            text_bbox = draw.multiline_textbbox((0,0), self.text_content, font=font, align="center")
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            x = (1280 - text_width) / 2
            y = (720 - text_height) / 2
            
            outline_color = "black"
            main_color = "white"
            offset = max(3, int(font_size / 25))

            for dx in range(-offset, offset+1, offset):
                for dy in range(-offset, offset+1, offset):
                    if dx != 0 or dy != 0:
                        draw.multiline_text((x+dx, y+dy), self.text_content, font=font, fill=outline_color, align="center")
            draw.multiline_text((x, y), self.text_content, font=font, fill=main_color, align="center")

            file_path = filedialog.asksaveasfilename(
                parent=self,
                title="Xuất ảnh Thumbnail", 
                defaultextension=".png", 
                filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg")]
            )
            if file_path:
                bg_image.convert("RGB").save(file_path, quality=95)
                messagebox.showinfo("Thành công", f"Đã xuất ảnh thumbnail thành công tại:\n{file_path}", parent=self)
                self.log_callback(f"Đã xuất thumbnail: {file_path}")

        except Exception as e:
            messagebox.showerror("Lỗi xuất ảnh", f"Đã có lỗi xảy ra: {e}", parent=self)