# src/gemini_tts_app/thumbnail_preview.py
# v7.1 - 2025-06-25: Add Font Weight, Line Spacing controls and other UX refinements.

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
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

        # --- Dữ liệu & Trạng thái ---
        self.system_fonts = self._get_system_fonts()
        self.font_weights = ['Normal', 'Bold', 'Black'] # Các tùy chọn kiểu chữ
        
        self.selected_font_family = tk.StringVar()
        self.selected_font_weight = tk.StringVar(value='Bold') # Mặc định là Bold
        self.font_size = tk.IntVar(value=100)
        self.line_spacing_multiplier = tk.DoubleVar(value=1.15) # Mặc định giãn dòng 115%

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
        """Tìm đường dẫn file của một font với family và weight cụ thể."""
        try:
            # Chuyển đổi tên thân thiện sang tham số của thư viện
            weight_map = {'normal': 'normal', 'bold': 'bold', 'black': 'black'}
            lookup_weight = weight_map.get(weight.lower(), 'normal')

            fp = font_manager.FontProperties(family=font_name, weight=lookup_weight)
            return font_manager.findfont(fp, fallback_to_default=False)
        except ValueError:
            # Nếu không tìm thấy weight cụ thể, thử tìm chỉ với family name
            try:
                return font_manager.findfont(font_manager.FontProperties(family=font_name))
            except ValueError:
                # Fallback cuối cùng
                return font_manager.findfont(font_manager.FontProperties(family='sans-serif'))

    # --- START REPLACEMENT FOR _setup_widgets ---
    def _setup_widgets(self):
        control_frame = ttk.Frame(self, padding=10)
        control_frame.pack(side=tk.TOP, fill=tk.X, expand=False)
        
        # --- Hàng 1: Các nút chính ---
        row1 = ttk.Frame(control_frame); row1.pack(fill=tk.X, pady=2)
        ttk.Button(row1, text="Chọn ảnh nền...", command=self._select_background_image).pack(side=tk.LEFT)
        ttk.Button(row1, text="Xuất ảnh...", command=self._export_thumbnail, style="Accent.TButton").pack(side=tk.RIGHT)
        
        # --- Hàng 2: Tất cả các control về Font ---
        font_controls_frame = ttk.Frame(control_frame)
        font_controls_frame.pack(fill=tk.X, pady=(5,2), expand=True)

        # Widget Font Family
        ttk.Label(font_controls_frame, text="Font:").pack(side=tk.LEFT, padx=(0,2))
        font_combo = ttk.Combobox(font_controls_frame, textvariable=self.selected_font_family, values=self.system_fonts, state='readonly', width=22)
        font_combo.pack(side=tk.LEFT, padx=(0, 5))
        font_combo.bind('<<ComboboxSelected>>', self._redraw_canvas)
        
        if "Be Vietnam Pro" in self.system_fonts: self.selected_font_family.set("Be Vietnam Pro")
        elif "Arial" in self.system_fonts: self.selected_font_family.set("Arial")
        elif self.system_fonts: self.selected_font_family.set(self.system_fonts[0])

        # Widget Font Weight
        ttk.Label(font_controls_frame, text="Kiểu:").pack(side=tk.LEFT, padx=(5, 2))
        weight_combo = ttk.Combobox(font_controls_frame, textvariable=self.selected_font_weight, values=self.font_weights, state='readonly', width=8)
        weight_combo.pack(side=tk.LEFT, padx=(0, 5))
        weight_combo.bind('<<ComboboxSelected>>', self._redraw_canvas)

        # Widget Font Size
        ttk.Label(font_controls_frame, text="Cỡ:").pack(side=tk.LEFT, padx=(5, 2))
        font_size_spinbox = ttk.Spinbox(font_controls_frame, from_=20, to=500, increment=2, textvariable=self.font_size, width=5)
        font_size_spinbox.pack(side=tk.LEFT, padx=(0, 5))
        font_size_spinbox.configure(command=self._redraw_canvas) # Gán command sau khi tạo
        font_size_spinbox.bind("<Return>", self._redraw_canvas)

        # Widget Line Spacing
        ttk.Label(font_controls_frame, text="Giãn dòng:").pack(side=tk.LEFT, padx=(5, 2))
        line_height_spinbox = ttk.Spinbox(font_controls_frame, from_=0.8, to=3.0, increment=0.05, textvariable=self.line_spacing_multiplier, width=4)
        line_height_spinbox.pack(side=tk.LEFT, padx=(0, 5))
        line_height_spinbox.configure(command=self._redraw_canvas)
        line_height_spinbox.bind("<Return>", self._redraw_canvas)

        # Widget Opacity (sẽ chiếm hết phần còn lại)
        ttk.Label(font_controls_frame, text="Độ mờ:").pack(side=tk.LEFT, padx=(10, 2))
        ttk.Scale(font_controls_frame, from_=0, to=255, variable=self.preview_overlay_alpha, command=self._redraw_canvas).pack(fill=tk.X, expand=True, padx=(0,5))

        # Canvas chiếm phần còn lại của cửa sổ
        self.preview_canvas = tk.Canvas(self, bg="#1c1c1c", highlightthickness=0, width=self.canvas_width, height=self.canvas_height)
        self.preview_canvas.pack(expand=True, fill="both")
    # --- END REPLACEMENT FOR _setup_widgets ---

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

            font_name = self.selected_font_family.get()
            font_weight = self.selected_font_weight.get()
            font_size = self.font_size.get()
            font_path = self._find_font_path(font_name, font_weight)
            
            if not font_path or font_size <= 0: return None
            
            font = ImageFont.truetype(font_path, font_size)

            stroke_width = max(3, int(font_size / 30))
            # Tính toán khoảng cách pixel dựa trên hệ số nhân
            # Pillow's `spacing` is the *additional* pixels between lines.
            # A multiplier of 1.2 means 20% of the font height is added as space.
            # We can approximate font height with font size for this.
            line_spacing = int(font_size * (self.line_spacing_multiplier.get() - 1.0))

            draw.multiline_text(
                (self.canvas_width / 2, self.canvas_height / 2),
                self.text_content,
                font=font,
                fill="white",
                anchor="mm",
                align="center",
                stroke_width=stroke_width,
                stroke_fill="black",
                spacing=line_spacing
            )
            return bg_image
        except Exception as e:
            self.log_callback(f"Lỗi khi tạo ảnh thumbnail: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return None

    def _redraw_canvas(self, event=None):
        """Hàm vẽ lại preview - Chỉ hiển thị ảnh do Pillow tạo ra."""
        final_image_pil = self._generate_final_image()
        
        if final_image_pil is None:
            self.preview_canvas.delete("all")
            self.preview_canvas.create_text(10, 10, text="Lỗi render ảnh", fill="red", anchor=tk.NW)
            return

        self.preview_bg_photo = ImageTk.PhotoImage(final_image_pil)
        self.preview_canvas.delete("all")
        self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=self.preview_bg_photo)

    def _export_thumbnail(self):
        """Hàm xuất ảnh - Chỉ lấy ảnh đã render và lưu lại."""
        try:
            final_image_to_save = self._generate_final_image()

            if final_image_to_save is None:
                messagebox.showerror("Lỗi", "Không thể tạo ảnh để xuất. Vui lòng kiểm tra lại thông số.", parent=self)
                return

            file_path = filedialog.asksaveasfilename(parent=self, title="Xuất ảnh Thumbnail", defaultextension=".jpg", filetypes=[("JPEG Image", "*.jpg"), ("PNG Image", "*.png")])
            if file_path:
                output_format = 'jpeg' if file_path.lower().endswith(('.jpg', '.jpeg')) else 'png'
                final_image_to_save.convert("RGB").save(file_path, format=output_format, quality=95)
                messagebox.showinfo("Thành công", f"Đã xuất ảnh thumbnail ({self.canvas_width}x{self.canvas_height}) thành công!", parent=self)
                self.log_callback(f"Đã xuất ảnh: {file_path}")
        except Exception as e:
            messagebox.showerror("Lỗi xuất ảnh", f"Đã có lỗi xảy ra: {e}", parent=self)