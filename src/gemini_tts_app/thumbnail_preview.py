# src/gemini_tts_app/thumbnail_preview.py
# v8.0 (Final for Task 4.1) - 2025-06-25: Implement strategic fixed color palette and swap toggle.

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageOps
from matplotlib import font_manager
import logging

class ThumbnailPreviewWindow(tk.Toplevel):
    def __init__(self, parent, text_content, log_callback):
        super().__init__(parent)
        self.parent = parent
        self.log_callback = log_callback
        self.text_content = text_content if text_content.strip() else " "

        self.canvas_width = 1280
        self.canvas_height = 720
        self.title(f"Xem trước Thumbnail ({self.canvas_width}x{self.canvas_height})")

        self.system_fonts = self._get_system_fonts()
        self.font_weights = ['Normal', 'Bold', 'Black']
        
        self.selected_font_family = tk.StringVar()
        self.selected_font_weight = tk.StringVar(value='Bold')
        self.font_size = tk.IntVar(value=100)
        self.line_spacing_multiplier = tk.DoubleVar(value=1.15)
        self.swap_colors_var = tk.BooleanVar(value=False) # Biến cho nút tráo màu

        self.preview_bg_photo = None
        self.preview_bg_path = None
        self.preview_overlay_alpha = tk.IntVar(value=100)

        self._setup_widgets()
        self.resizable(False, False)
        
        self.update_idletasks() 
        self._redraw_canvas()

        self.transient(parent)
        self.grab_set()
        self.wait_window(self)

    def _get_system_fonts(self):
        try:
            font_paths = font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
            return sorted(list(set([font_manager.FontProperties(fname=fname).get_name() for fname in font_paths])))
        except Exception as e:
            self.log_callback(f"Lỗi khi quét font: {e}")
            return ['Arial']

    def _find_font_path(self, font_name, weight='normal'):
        try:
            weight_map = {'normal': 'normal', 'bold': 'bold', 'black': 'black'}
            lookup_weight = weight_map.get(weight.lower(), 'normal')
            fp = font_manager.FontProperties(family=font_name, weight=lookup_weight)
            return font_manager.findfont(fp, fallback_to_default=False)
        except ValueError:
            try:
                return font_manager.findfont(font_manager.FontProperties(family=font_name))
            except ValueError:
                return font_manager.findfont(font_manager.FontProperties(family='sans-serif'))

    def _setup_widgets(self):
        control_frame = ttk.Frame(self, padding=10)
        control_frame.pack(side=tk.TOP, fill=tk.X, expand=False)
        
        row1 = ttk.Frame(control_frame); row1.pack(fill=tk.X, pady=2)
        ttk.Button(row1, text="Chọn ảnh nền...", command=self._select_background_image).pack(side=tk.LEFT)
        ttk.Button(row1, text="Xuất ảnh...", command=self._export_thumbnail, style="Accent.TButton").pack(side=tk.RIGHT)
        
        row2 = ttk.Frame(control_frame); row2.pack(fill=tk.X, pady=(5,2), expand=True)
        ttk.Label(row2, text="Font:").pack(side=tk.LEFT)
        font_combo = ttk.Combobox(row2, textvariable=self.selected_font_family, values=self.system_fonts, state='readonly', width=25)
        font_combo.pack(side=tk.LEFT, padx=(5, 10))
        font_combo.bind('<<ComboboxSelected>>', self._redraw_canvas)
        
        # --- Cập nhật danh sách font ưu tiên ---
        preferred_fonts_order = ["Oswald", "Anton", "Roboto Condensed", "Be Vietnam Pro", "Arial"]
        for p_font in preferred_fonts_order:
            if p_font in self.system_fonts:
                self.selected_font_family.set(p_font)
                break
        else: # Nếu không có font nào trong list ưu tiên
             if self.system_fonts: self.selected_font_family.set(self.system_fonts[0])

        ttk.Label(row2, text="Kiểu chữ:").pack(side=tk.LEFT, padx=(5, 0))
        weight_combo = ttk.Combobox(row2, textvariable=self.selected_font_weight, values=self.font_weights, state='readonly', width=10)
        weight_combo.pack(side=tk.LEFT, padx=5)
        weight_combo.bind('<<ComboboxSelected>>', self._redraw_canvas)

        # --- Thêm nút tráo màu ---
        ttk.Checkbutton(row2, text="Tráo màu 1 & 2", variable=self.swap_colors_var, command=self._redraw_canvas).pack(side=tk.LEFT, padx=(10,0))
        
        row3 = ttk.Frame(control_frame); row3.pack(fill=tk.X, pady=2, expand=True)
        ttk.Label(row3, text="Cỡ chữ:").pack(side=tk.LEFT)
        font_size_spinbox = ttk.Spinbox(row3, from_=20, to=500, increment=2, textvariable=self.font_size, width=5, command=self._redraw_canvas)
        font_size_spinbox.pack(side=tk.LEFT, padx=(5,10))
        font_size_spinbox.bind("<Return>", self._redraw_canvas)
        
        ttk.Label(row3, text="Giãn dòng:").pack(side=tk.LEFT, padx=(10, 0))
        line_height_spinbox = ttk.Spinbox(row3, from_=0.8, to=3.0, increment=0.05, textvariable=self.line_spacing_multiplier, width=4, command=self._redraw_canvas)
        line_height_spinbox.pack(side=tk.LEFT, padx=5)
        line_height_spinbox.bind("<Return>", self._redraw_canvas)

        ttk.Label(row3, text="Độ mờ:").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Scale(row3, from_=0, to=255, variable=self.preview_overlay_alpha, command=self._redraw_canvas).pack(fill=tk.X, expand=True, padx=5)

        self.preview_canvas = tk.Canvas(self, bg="#1c1c1c", highlightthickness=0, width=self.canvas_width, height=self.canvas_height)
        self.preview_canvas.pack(expand=True, fill="both")

    def _select_background_image(self):
        file_path = filedialog.askopenfilename(parent=self, title="Chọn ảnh nền", filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if file_path:
            self.preview_bg_path = file_path
            self._redraw_canvas()
    
    def _generate_final_image(self):
        """Hàm master: Dùng Pillow để tạo ra ảnh thumbnail cuối cùng trong bộ nhớ."""
        try:
            if self.preview_bg_path: bg_image = Image.open(self.preview_bg_path).convert("RGBA")
            else: bg_image = Image.new('RGBA', (self.canvas_width, self.canvas_height), (80, 80, 80, 255))
            bg_image = ImageOps.fit(bg_image, (self.canvas_width, self.canvas_height), Image.Resampling.LANCZOS)

            alpha = self.preview_overlay_alpha.get()
            if alpha > 0:
                overlay = Image.new('RGBA', bg_image.size, (0, 0, 0, alpha))
                bg_image = Image.alpha_composite(bg_image, overlay)
            
            draw = ImageDraw.Draw(bg_image)

            font_path = self._find_font_path(self.selected_font_family.get(), self.selected_font_weight.get())
            font_size = self.font_size.get()
            if not font_path or font_size <= 0: return None
            
            font = ImageFont.truetype(font_path, font_size)

            # --- LOGIC BẢNG MÀU CỐ ĐỊNH ---
            color_palette = ['#fbe959', '#ffffff', '#ff322f', '#fbe959', '#ffffff']
            if self.swap_colors_var.get():
                color_palette[0], color_palette[1] = color_palette[1], color_palette[0] # Hoán đổi

            lines_to_draw = self.text_content.split('\n')
            
            # Tính toán tổng chiều cao và vị trí bắt đầu để căn giữa cả khối
            line_spacing_multiplier = self.line_spacing_multiplier.get()
            line_heights = [draw.textbbox((0,0), line, font=font)[3] - draw.textbbox((0,0), line, font=font)[1] for line in lines_to_draw]
            total_text_height = sum(h * line_spacing_multiplier for h in line_heights)
            if len(line_heights) > 1:
                total_text_height -= line_heights[-1] * (line_spacing_multiplier - 1.0)
            
            current_y = (self.canvas_height - total_text_height) / 2

            # Vẽ từng dòng với màu tương ứng
            for i, line_text in enumerate(lines_to_draw):
                line_color = color_palette[i % len(color_palette)] # Lặp lại pattern màu
                stroke_width = max(3, int(font_size / 30))
                
                # anchor 'ma' (middle-ascent) để các dòng căn với nhau theo chiều dọc
                draw.text(
                    (self.canvas_width / 2, current_y),
                    line_text,
                    font=font,
                    fill=line_color,
                    anchor="ma",
                    align="center",
                    stroke_width=stroke_width,
                    stroke_fill="black"
                )
                current_y += line_heights[i] * line_spacing_multiplier
            
            return bg_image
        except Exception as e:
            self.log_callback(f"Lỗi khi tạo ảnh thumbnail: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return None

    def _redraw_canvas(self, event=None):
        final_image_pil = self._generate_final_image()
        if final_image_pil is None:
            self.preview_canvas.delete("all")
            self.preview_canvas.create_text(10, 10, text="Lỗi render ảnh", fill="red", anchor=tk.NW)
            return
        self.preview_bg_photo = ImageTk.PhotoImage(final_image_pil)
        self.preview_canvas.delete("all")
        self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=self.preview_bg_photo)

    def _export_thumbnail(self):
        try:
            final_image_to_save = self._generate_final_image()
            if final_image_to_save is None:
                messagebox.showerror("Lỗi", "Không thể tạo ảnh để xuất.", parent=self)
                return
                
            file_path = filedialog.asksaveasfilename(parent=self, title="Xuất ảnh Thumbnail", defaultextension=".jpg", filetypes=[("JPEG Image", "*.jpg"), ("PNG Image", "*.png")])
            if file_path:
                output_format = 'jpeg' if file_path.lower().endswith(('.jpg', '.jpeg')) else 'png'
                final_image_to_save.convert("RGB").save(file_path, format=output_format, quality=95)
                messagebox.showinfo("Thành công", f"Đã xuất ảnh thumbnail ({self.canvas_width}x{self.canvas_height}) thành công!", parent=self)
                self.log_callback(f"Đã xuất ảnh: {file_path}")
        except Exception as e:
            messagebox.showerror("Lỗi xuất ảnh", f"Đã có lỗi xảy ra: {e}", parent=self)