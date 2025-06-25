# src/gemini_tts_app/thumbnail_preview.py
# Version: 2.0.0
# Last-Modified: 2025-06-25 23:55:00 (Giờ địa phương)
# Description: Phiên bản kiến trúc lại toàn diện. Sửa lỗi layout, font, và triển khai đầy đủ tính năng tùy chỉnh từng dòng.

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageOps
from matplotlib import font_manager
import logging
from collections import defaultdict

class ThumbnailPreviewWindow(tk.Toplevel):
    """
    Cửa sổ chính cho việc xem trước và tùy chỉnh thumbnail.
    Kiến trúc này sử dụng một canvas có kích thước cố định và các control để tùy chỉnh style.
    """
    def __init__(self, parent, text_content, log_callback):
        super().__init__(parent)
        self.parent = parent
        self.log_callback = log_callback
        
        # // FIX: LAYOUT - Định nghĩa kích thước canvas chuẩn ngay từ đầu.
        self.canvas_width = 1280
        self.canvas_height = 720
        self.title(f"Xem trước Thumbnail ({self.canvas_width}x{self.canvas_height})")

        # --- Dữ liệu & Trạng thái ---
        # // FEAT: FONT_LOGIC - Xây dựng một sơ đồ font chi tiết và đáng tin cậy khi khởi tạo.
        self.font_map = self._build_font_map()
        self.font_families = sorted(self.font_map.keys())
        
        # Các biến style chung
        self.selected_font_family = tk.StringVar()
        self.selected_font_weight = tk.StringVar()
        self.line_spacing_multiplier = tk.DoubleVar(value=1.2) # Tăng khoảng cách dòng mặc định
        self.swap_colors_var = tk.BooleanVar(value=False)
        self.preview_overlay_alpha = tk.IntVar(value=100)
        self.global_font_size = tk.IntVar(value=100) # Biến cho chức năng Cỡ chữ chung

        # Các thuộc tính hệ thống
        self.preview_bg_photo = None
        self.preview_bg_path = None
        
        # // FEAT: PER_LINE_SIZE - Cấu trúc dữ liệu cho phép mỗi dòng có size/color riêng.
        self.lines = []
        self._parse_text_to_lines(text_content)

        # Thiết lập toàn bộ giao diện
        self._setup_widgets()
        self.resizable(False, False) # Không cho phép resize cửa sổ
        
        # Chạy các hàm khởi tạo trạng thái giao diện sau khi cửa sổ đã được vẽ
        self.after(100, self._initial_load)

        self.transient(parent)
        self.grab_set()
        self.wait_window(self)

    def _initial_load(self):
        """Hàm này được gọi một lần sau khi UI đã được tạo để thiết lập trạng thái ban đầu."""
        self._on_font_family_selected()
        if self.lines:
            self.lines_listbox.selection_set(0)
            self.lines_listbox.event_generate("<<ListboxSelect>>")

    def _parse_text_to_lines(self, text_content):
        """
        Hàm này chuyển đổi chuỗi text đầu vào thành cấu trúc dữ liệu self.lines.
        Mỗi dòng là một object với các thuộc tính riêng, bao gồm size và color.
        """
        self.lines = []
        base_size = self.global_font_size.get()
        for line_text in text_content.split('\n'):
            if line_text.strip():
                self.lines.append({
                    'text': line_text,
                    'color': tk.StringVar(value='#FFFFFF'),
                    'size': tk.IntVar(value=base_size)
                })

    def _build_font_map(self):
        """
        // FEAT: FONT_LOGIC - Quét font hệ thống và xây dựng một sơ đồ chi tiết.
        Phân loại các weight (Normal, Bold, Black...) một cách chính xác để người dùng lựa chọn.
        """
        font_map = defaultdict(dict)
        font_paths = font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
        weight_name_map = {
            400: "Normal", 600: "SemiBold", 700: "Bold", 900: "Black",
            100: "Thin", 200: "Extra Light", 300: "Light", 500: "Medium", 800: "Extra Bold"
        }
        for font_path in font_paths:
            try:
                properties = font_manager.FontProperties(fname=font_path)
                family = properties.get_name()
                style = properties.get_style()
                weight_num = properties.get_weight()
                
                if style in ['italic', 'oblique']: continue

                weight_name = "Normal"
                if isinstance(weight_num, (int, float)):
                    weight_name = weight_name_map.get(weight_num, "Normal")
                elif isinstance(weight_num, str):
                    w_lower = weight_num.lower()
                    if 'black' in w_lower or 'heavy' in w_lower: weight_name = "Black"
                    elif 'bold' in w_lower: weight_name = "Bold"
                    elif 'semibold' in w_lower or 'demibold' in w_lower: weight_name = "SemiBold"
                
                if weight_name not in font_map[family]:
                    font_map[family][weight_name] = font_path
            except RuntimeError:
                continue
        return font_map

    def _setup_widgets(self):
        """
        // FIX: LAYOUT - Bố cục ổn định dùng .pack() cho các khu vực chính, và một container
        có kích thước được set cứng cho canvas để đảm bảo không bị co rút.
        """
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        control_frame = ttk.Frame(main_frame, padding=10)
        control_frame.pack(side=tk.TOP, fill=tk.X, expand=False, pady=5)
        
        # Khu vực tùy chỉnh dòng được chọn
        line_editor_frame = ttk.LabelFrame(control_frame, text="Tùy chỉnh Dòng được chọn", padding=10)
        line_editor_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), anchor='n')
        
        # Khu vực tùy chỉnh chung
        general_controls_frame = ttk.LabelFrame(control_frame, text="Tùy chỉnh Chung", padding=10)
        general_controls_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # --- Các widget trong khu vực TÙY CHỈNH DÒNG ---
        self.lines_listbox = tk.Listbox(line_editor_frame, height=5, exportselection=False, width=35)
        for line_obj in self.lines: self.lines_listbox.insert(tk.END, line_obj['text'])
        self.lines_listbox.pack(side=tk.TOP, fill=tk.X, expand=True, pady=5)
        self.lines_listbox.bind('<<ListboxSelect>>', self._on_line_selected)
        
        line_controls_frame = ttk.Frame(line_editor_frame)
        line_controls_frame.pack(pady=5)
        ttk.Label(line_controls_frame, text="Cỡ chữ dòng:").pack(side=tk.LEFT)
        self.line_size_spinbox = ttk.Spinbox(line_controls_frame, from_=20, to=500, increment=2, width=5)
        self.line_size_spinbox.pack(side=tk.LEFT, padx=5)
        self.line_size_spinbox.configure(command=self._on_line_size_change)
        self.line_size_spinbox.bind("<Return>", self._on_line_size_change)

        # --- Các widget trong khu vực TÙY CHỈNH CHUNG ---
        row1 = ttk.Frame(general_controls_frame); row1.pack(fill=tk.X, expand=True, pady=2)
        ttk.Button(row1, text="Chọn ảnh nền...", command=self._select_background_image).pack(side=tk.LEFT)
        ttk.Checkbutton(row1, text="Tráo màu 1&2", variable=self.swap_colors_var, command=self._redraw_canvas).pack(side=tk.LEFT, padx=20)
        ttk.Button(row1, text="Xuất ảnh...", command=self._export_thumbnail, style="Accent.TButton").pack(side=tk.RIGHT)

        row2 = ttk.Frame(general_controls_frame); row2.pack(fill=tk.X, expand=True, pady=5)
        ttk.Label(row2, text="Font:").pack(side=tk.LEFT)
        self.font_combo = ttk.Combobox(row2, textvariable=self.selected_font_family, values=self.font_families, state='readonly', width=20)
        self.font_combo.pack(side=tk.LEFT, padx=(5, 10))
        self.font_combo.bind('<<ComboboxSelected>>', self._on_font_family_selected)
        
        ttk.Label(row2, text="Kiểu:").pack(side=tk.LEFT)
        self.weight_combo = ttk.Combobox(row2, textvariable=self.selected_font_weight, state='readonly', width=10)
        self.weight_combo.pack(side=tk.LEFT, padx=(5,10))
        self.weight_combo.bind('<<ComboboxSelected>>', self._redraw_canvas)
        
        ttk.Label(row2, text="Giãn dòng:").pack(side=tk.LEFT)
        line_height_spinbox = ttk.Spinbox(row2, from_=0.8, to=3.0, increment=0.05, textvariable=self.line_spacing_multiplier, width=4, command=self._redraw_canvas)
        line_height_spinbox.pack(side=tk.LEFT, padx=5)
        line_height_spinbox.bind("<Return>", self._redraw_canvas)
        
        # // FEAT: GLOBAL_SIZE - Thêm lại control cho cỡ chữ chung
        row3 = ttk.Frame(general_controls_frame); row3.pack(fill=tk.X, expand=True, pady=2)
        ttk.Label(row3, text="Cỡ chữ chung:").pack(side=tk.LEFT)
        global_size_spinbox = ttk.Spinbox(row3, from_=20, to=500, increment=2, textvariable=self.global_font_size, width=5)
        global_size_spinbox.pack(side=tk.LEFT, padx=(5,2))
        ttk.Button(row3, text="Áp dụng cho tất cả", command=self._apply_global_size).pack(side=tk.LEFT)

        row4 = ttk.Frame(general_controls_frame); row4.pack(fill=tk.X, expand=True, pady=2)
        ttk.Label(row4, text="Độ mờ:").pack(side=tk.LEFT)
        ttk.Scale(row4, from_=0, to=255, variable=self.preview_overlay_alpha, command=self._redraw_canvas).pack(fill=tk.X, expand=True, padx=5)

        # CANVAS PREVIEW
        canvas_container = ttk.Frame(main_frame, width=self.canvas_width, height=self.canvas_height)
        canvas_container.pack(expand=True, fill="both")
        canvas_container.pack_propagate(False)
        self.preview_canvas = tk.Canvas(canvas_container, bg="#1c1c1c", highlightthickness=0)
        self.preview_canvas.pack(expand=True, fill="both")

        # Chọn font mặc định
        preferred_fonts_order = ["Oswald", "Anton", "Roboto Condensed", "Be Vietnam Pro", "Arial"]
        for p_font in preferred_fonts_order:
            if p_font in self.font_families: self.selected_font_family.set(p_font); break
        else:
            if self.font_families: self.selected_font_family.set(self.font_families[0])
    
    def _apply_global_size(self):
        """Gán giá trị từ Cỡ chữ chung cho tất cả các dòng."""
        new_size = self.global_font_size.get()
        for line in self.lines:
            line['size'].set(new_size)
        self._on_line_selected()
        self._redraw_canvas()

    def _on_font_family_selected(self, event=None):
        """Cập nhật dropdown Kiểu chữ và redraw."""
        family = self.selected_font_family.get()
        if family in self.font_map:
            weights = sorted(self.font_map[family].keys())
            self.weight_combo['values'] = weights
            if self.selected_font_weight.get() not in weights:
                if 'Bold' in weights: self.selected_font_weight.set('Bold')
                elif 'Normal' in weights: self.selected_font_weight.set('Normal')
                elif weights: self.selected_font_weight.set(weights[0])
                else: self.selected_font_weight.set('')
        self._redraw_canvas()

    def _on_line_selected(self, event=None):
        """Cập nhật Spinbox Cỡ chữ để hiển thị size của dòng được chọn."""
        selected_indices = self.lines_listbox.curselection()
        if not selected_indices: return
        selected_index = selected_indices[0]
        if 0 <= selected_index < len(self.lines):
            self.line_size_spinbox.configure(textvariable=self.lines[selected_index]['size'])

    def _on_line_size_change(self, event=None):
        """Vẽ lại canvas khi cỡ chữ của một dòng được thay đổi."""
        self._redraw_canvas()
    
    def _select_background_image(self):
        file_path = filedialog.askopenfilename(parent=self, title="Chọn ảnh nền", filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if file_path:
            self.preview_bg_path = file_path
            self._redraw_canvas()
    
    def _generate_final_image(self):
        """
        Hàm master, dùng Pillow để tạo ra ảnh thumbnail cuối cùng trong bộ nhớ.
        Logic render và căn giữa đã được sửa lại hoàn toàn để đảm bảo chính xác.
        """
        try:
            image_size = (self.canvas_width, self.canvas_height)
            if self.preview_bg_path: bg_image = Image.open(self.preview_bg_path).convert("RGBA")
            else: bg_image = Image.new('RGBA', image_size, (80, 80, 80, 255))
            bg_image = ImageOps.fit(bg_image, image_size, Image.Resampling.LANCZOS)
            alpha = self.preview_overlay_alpha.get()
            if alpha > 0:
                overlay = Image.new('RGBA', bg_image.size, (0, 0, 0, alpha))
                bg_image = Image.alpha_composite(bg_image, overlay)
            draw = ImageDraw.Draw(bg_image)

            font_family = self.selected_font_family.get()
            font_weight = self.selected_font_weight.get()
            font_path = self.font_map.get(font_family, {}).get(font_weight)
            if not font_path: return None

            # Áp dụng bảng màu cố định
            color_palette = ['#fbe959', '#ffffff', '#ff322f', '#fbe959', '#ffffff']
            if self.swap_colors_var.get():
                color_palette[0], color_palette[1] = color_palette[1], color_palette[0]
            for i, line_obj in enumerate(self.lines):
                line_obj['color'].set(color_palette[i % len(color_palette)])

            # // FEAT: PER_LINE_SIZE - Tạo các đối tượng font với size riêng cho mỗi dòng
            fonts = [ImageFont.truetype(font_path, line['size'].get()) for line in self.lines]
            
            # // FIX: V_CENTER - Logic tính toán chiều cao và vị trí căn giữa chính xác
            line_heights = [font.getbbox(line['text'])[3] - font.getbbox(line['text'])[1] for font, line in zip(fonts, self.lines)]
            line_spacing_multiplier = self.line_spacing_multiplier.get()
            
            total_text_height = 0
            spacings = []
            for i in range(len(self.lines)):
                total_text_height += line_heights[i]
                if i > 0:
                    spacing = int(fonts[i-1].size * (line_spacing_multiplier - 1.0))
                    spacings.append(spacing)
                    total_text_height += spacing
            
            y = (self.canvas_height - total_text_height) / 2

            # Vẽ từng dòng với các thuộc tính riêng
            for i, line_obj in enumerate(self.lines):
                font = fonts[i]
                line_height = line_heights[i]
                
                # Tính vị trí tâm theo chiều dọc của mỗi dòng
                draw_y = y + line_height / 2
                
                stroke_width = max(3, int(font.size / 30))
                draw.text(
                    (self.canvas_width / 2, draw_y), line_obj['text'], font=font,
                    fill=line_obj['color'].get(), anchor="ma", align="center",
                    stroke_width=stroke_width, stroke_fill="black"
                )
                
                # Cập nhật vị trí y cho dòng tiếp theo
                y += line_height
                if i < len(spacings):
                    y += spacings[i]
            
            return bg_image
        except Exception as e:
            self.log_callback(f"Lỗi khi tạo ảnh: {e}"); import traceback; logging.error(traceback.format_exc()); return None

    def _redraw_canvas(self, event=None):
        """Hàm vẽ lại preview - Chỉ hiển thị ảnh do Pillow tạo ra."""
        final_image_pil = self._generate_final_image()
        if final_image_pil is None:
            self.preview_canvas.delete("all"); self.preview_canvas.create_text(10, 10, text="Lỗi render ảnh", fill="red", anchor=tk.NW); return
        self.preview_bg_photo = ImageTk.PhotoImage(final_image_pil)
        self.preview_canvas.delete("all")
        self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=self.preview_bg_photo)

    def _export_thumbnail(self):
        """Hàm xuất ảnh - Chỉ lấy ảnh đã render và lưu lại, đảm bảo WYSIWYG."""
        try:
            final_image_to_save = self._generate_final_image()
            if final_image_to_save is None:
                messagebox.showerror("Lỗi", "Không thể tạo ảnh để xuất.", parent=self); return
            
            file_path = filedialog.asksaveasfilename(parent=self, title="Xuất ảnh Thumbnail", defaultextension=".jpg", filetypes=[("JPEG Image", "*.jpg"), ("PNG Image", "*.png")])
            if file_path:
                output_format = 'jpeg' if file_path.lower().endswith(('.jpg', '.jpeg')) else 'png'
                final_image_to_save.convert("RGB").save(file_path, format=output_format, quality=95)
                messagebox.showinfo("Thành công", f"Đã xuất ảnh thumbnail ({self.canvas_width}x{self.canvas_height}) thành công!", parent=self)
                self.log_callback(f"Đã xuất ảnh: {file_path}")
        except Exception as e:
            messagebox.showerror("Lỗi xuất ảnh", f"Đã có lỗi xảy ra: {e}", parent=self)