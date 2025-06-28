# src/gemini_tts_app/thumbnail_preview.py
# Version: 5.0.0 (Stable Static Fonts)
# Last-Modified: 2025-06-28 15:00:00 (Giờ địa phương)
# Description: Tái cấu trúc logic để chỉ làm việc với các font tĩnh riêng biệt,
#              bỏ qua Variable Fonts để đảm bảo sự ổn định và tương thích tuyệt đối.

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageOps
from fontTools.ttLib import TTFont
import os
import logging
from collections import defaultdict

# Ánh xạ từ usWeightClass sang tên
WEIGHT_CLASS_MAP = {
    100: "Thin", 200: "Extra Light", 300: "Light", 400: "Normal",
    500: "Medium", 600: "SemiBold", 700: "Bold", 800: "Extra Bold", 900: "Black"
}

class ThumbnailPreviewWindow(tk.Toplevel):
    def __init__(self, parent, text_content, log_callback):
        super().__init__(parent)
        self.parent = parent
        self.log_callback = log_callback
        self.canvas_width, self.canvas_height = 1280, 720
        self.title(f"Xem trước Thumbnail ({self.canvas_width}x{self.canvas_height})")

        self.font_map = self._build_font_map()
        self.font_families = sorted(self.font_map.keys())
        
        self.selected_font_family = tk.StringVar()
        self.selected_font_weight_name = tk.StringVar()
        self.line_spacing_multiplier = tk.DoubleVar(value=1.2)
        self.swap_colors_var = tk.BooleanVar(value=False)
        self.preview_overlay_alpha = tk.IntVar(value=100)
        self.global_font_size = tk.IntVar(value=100)

        self.preview_bg_photo, self.preview_bg_path = None, None
        
        self.lines = []
        self._parse_text_to_lines(text_content)

        self._setup_widgets()
        self.resizable(False, False)
        self.after(100, self._initial_load)
        self.transient(parent); self.grab_set(); self.wait_window(self)

    def _initial_load(self):
        self._on_font_family_selected()
        if self.lines:
            self.lines_listbox.selection_set(0)
            self.lines_listbox.event_generate("<<ListboxSelect>>")

    def _parse_text_to_lines(self, text_content):
        self.lines = []
        base_size = self.global_font_size.get()
        for line_text in text_content.split('\n'):
            if line_text.strip():
                self.lines.append({
                    'text': line_text, 'color': tk.StringVar(value='#FFFFFF'),
                    'size': tk.IntVar(value=base_size), 'is_edited': False
                })

    def _build_font_map(self):
        """
        FIX: Quét và chỉ nhóm các file font tĩnh, bỏ qua hoàn toàn Variable Fonts.
        """
        font_map = defaultdict(dict)
        font_dirs = [os.path.join(os.environ['WINDIR'], 'Fonts')]
        user_font_dir = os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Windows', 'Fonts')
        if os.path.isdir(user_font_dir): font_dirs.append(user_font_dir)

        for font_dir in font_dirs:
            for filename in os.listdir(font_dir):
                if not filename.lower().endswith(('.ttf', '.otf')): continue
                font_path = os.path.join(font_dir, filename)
                try:
                    ttFont = TTFont(font_path, lazy=True)
                    # BỎ QUA VARIABLE FONTS ĐỂ TRÁNH LỖI
                    if 'fvar' in ttFont:
                        self.log_callback(f"Cảnh báo: Bỏ qua Variable Font không được hỗ trợ: {filename}")
                        continue
                        
                    name_records = ttFont['name'].names
                    family_name = ""
                    for record_id in [16, 1]:
                        for record in name_records:
                            if record.nameID == record_id:
                                family_name = record.toUnicode(); break
                        if family_name: break
                    if not family_name: continue
                    
                    weight_value = ttFont['OS/2'].usWeightClass
                    weight_name = WEIGHT_CLASS_MAP.get(weight_value, "Normal")
                    font_map[family_name][weight_name] = font_path
                except Exception as e:
                    # Ghi log nếu có font không đọc được
                    self.log_callback(f"Không thể đọc font: {filename}. Lỗi: {e}")
                    continue
        return font_map

    def _setup_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        control_frame = ttk.Frame(main_frame, padding=10)
        control_frame.pack(side=tk.TOP, fill=tk.X, expand=False, pady=5)
        line_editor_frame = ttk.LabelFrame(control_frame, text="Tùy chỉnh Dòng được chọn", padding=10)
        line_editor_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), anchor='n')
        general_controls_frame = ttk.LabelFrame(control_frame, text="Tùy chỉnh Chung", padding=10)
        general_controls_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.lines_listbox = tk.Listbox(line_editor_frame, height=5, exportselection=False, width=35)
        for line_obj in self.lines: self.lines_listbox.insert(tk.END, line_obj['text'])
        self.lines_listbox.pack(side=tk.TOP, fill=tk.X, expand=True, pady=5)
        self.lines_listbox.bind('<<ListboxSelect>>', self._on_line_selected)
        line_controls_frame = ttk.Frame(line_editor_frame)
        line_controls_frame.pack(pady=5, fill=tk.X)
        ttk.Label(line_controls_frame, text="Cỡ chữ:").pack(side=tk.LEFT)
        self.line_size_spinbox = ttk.Spinbox(line_controls_frame, from_=20, to=500, increment=2, width=5)
        self.line_size_spinbox.pack(side=tk.LEFT, padx=(5, 10))
        self.line_size_spinbox.configure(command=self._on_line_size_changed_by_user)
        self.line_size_spinbox.bind("<Return>", self._on_line_size_changed_by_user)
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
        self.weight_combo = ttk.Combobox(row2, textvariable=self.selected_font_weight_name, state='readonly', width=10)
        self.weight_combo.pack(side=tk.LEFT, padx=(5,10))
        self.weight_combo.bind('<<ComboboxSelected>>', self._redraw_canvas)
        ttk.Label(row2, text="Giãn dòng:").pack(side=tk.LEFT)
        line_height_spinbox = ttk.Spinbox(row2, from_=0.8, to=3.0, increment=0.05, textvariable=self.line_spacing_multiplier, width=4, command=self._redraw_canvas)
        line_height_spinbox.pack(side=tk.LEFT, padx=5)
        line_height_spinbox.bind("<Return>", self._redraw_canvas)
        row3 = ttk.Frame(general_controls_frame); row3.pack(fill=tk.X, expand=True, pady=2)
        ttk.Label(row3, text="Cỡ chữ chung:").pack(side=tk.LEFT)
        global_size_spinbox = ttk.Spinbox(row3, from_=20, to=500, increment=2, textvariable=self.global_font_size, width=5, command=self._apply_global_size)
        global_size_spinbox.pack(side=tk.LEFT, padx=5)
        global_size_spinbox.bind("<Return>", self._apply_global_size)
        row4 = ttk.Frame(general_controls_frame); row4.pack(fill=tk.X, expand=True, pady=2)
        ttk.Label(row4, text="Độ mờ:").pack(side=tk.LEFT)
        ttk.Scale(row4, from_=0, to=255, variable=self.preview_overlay_alpha, command=self._redraw_canvas).pack(fill=tk.X, expand=True, padx=5)
        canvas_container = ttk.Frame(main_frame, width=self.canvas_width, height=self.canvas_height)
        canvas_container.pack(expand=True, fill="both")
        canvas_container.pack_propagate(False)
        self.preview_canvas = tk.Canvas(canvas_container, bg="#1c1c1c", highlightthickness=0)
        self.preview_canvas.pack(expand=True, fill="both")
        
        # Thiết lập font mặc định
        if "Anton" in self.font_families:
            self.selected_font_family.set("Anton")
        elif self.font_families:
            self.selected_font_family.set(self.font_families[0])
    
    def _apply_global_size(self, event=None):
        new_size = self.global_font_size.get()
        for line in self.lines:
            if not line['is_edited']: line['size'].set(new_size)
        self._on_line_selected(); self._redraw_canvas()

    def _on_font_family_selected(self, event=None):
        family = self.selected_font_family.get()
        font_info = self.font_map.get(family)
        if not font_info: return
        weights = sorted(font_info.keys())
        self.weight_combo['values'] = weights
        # Ưu tiên "Normal" rồi đến "Bold"
        if 'Normal' in weights: self.selected_font_weight_name.set('Normal')
        elif 'Bold' in weights: self.selected_font_weight_name.set('Bold')
        elif weights: self.selected_font_weight_name.set(weights[0])
        else: self.selected_font_weight_name.set('')
        self._redraw_canvas()

    def _on_line_selected(self, event=None):
        selected_indices = self.lines_listbox.curselection()
        if not selected_indices: return
        selected_index = selected_indices[0]
        if 0 <= selected_index < len(self.lines):
            self.line_size_spinbox.configure(textvariable=self.lines[selected_index]['size'])

    def _on_line_size_changed_by_user(self, event=None):
        selected_indices = self.lines_listbox.curselection()
        if not selected_indices: return
        selected_index = selected_indices[0]
        if 0 <= selected_index < len(self.lines):
            self.lines[selected_index]['is_edited'] = True
        self._redraw_canvas()
    
    def _select_background_image(self):
        file_path = filedialog.askopenfilename(parent=self, title="Chọn ảnh nền", filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if file_path: self.preview_bg_path = file_path; self._redraw_canvas()
    
    def _generate_final_image(self):
        """
        FIX: Đơn giản hóa, không dùng 'variation'.
        Tìm chính xác file font tĩnh cho weight được chọn.
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

            font_family = self.selected_font_family.get()
            font_weight_name = self.selected_font_weight_name.get()
            font_path = self.font_map.get(font_family, {}).get(font_weight_name)
            
            if not font_path:
                self.log_callback(f"Lỗi: Không tìm thấy file font cho {font_family} - {font_weight_name}.")
                return None

            color_palette = ['#fbe959', '#ffffff', '#ff322f', '#fbe959', '#ffffff']
            if self.swap_colors_var.get(): color_palette[0], color_palette[1] = color_palette[1], color_palette[0]
            for i, line_obj in enumerate(self.lines): line_obj['color'].set(color_palette[i % len(color_palette)])

            text_layer = Image.new('RGBA', image_size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(text_layer)
            
            current_y = 0
            for line in self.lines:
                line_size = line['size'].get()
                font = ImageFont.truetype(font_path, size=line_size)
                
                draw.text((self.canvas_width / 2, current_y), line['text'], font=font,
                          fill=line['color'].get(), anchor="mt", align="center",
                          stroke_width=max(2, int(font.size / 35)), stroke_fill="black")
                
                bbox = draw.textbbox((self.canvas_width / 2, current_y), line['text'], font=font, anchor="mt", align="center")
                line_height = bbox[3] - bbox[1]
                current_y += line_height * self.line_spacing_multiplier.get()

            bbox = text_layer.getbbox()
            if not bbox: return bg_image
            text_block_image = text_layer.crop(bbox)
            block_width, block_height = text_block_image.size
            paste_x = (self.canvas_width - block_width) // 2
            paste_y = (self.canvas_height - block_height) // 2
            bg_image.paste(text_block_image, (paste_x, paste_y), text_block_image)
            
            return bg_image
            
        except Exception as e:
            self.log_callback(f"Lỗi khi tạo ảnh: {e}"); import traceback; logging.error(traceback.format_exc())
            return None

    def _redraw_canvas(self, event=None):
        final_image_pil = self._generate_final_image()
        if final_image_pil is None:
            self.preview_canvas.delete("all")
            self.preview_canvas.create_text(self.canvas_width/2, self.canvas_height/2, text="Lỗi render ảnh.\nVui lòng kiểm tra Log.", fill="red", anchor=tk.CENTER)
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
            file_path = filedialog.asksaveasfilename(parent=self, title="Xuất ảnh Thumbnail", defaultextension=".jpg", filetypes=[("JPEG Image", "*.jpg"), ("PNG Image", ".png")])
            if file_path:
                output_format = 'jpeg' if file_path.lower().endswith(('.jpg', '.jpeg')) else 'png'
                final_image_to_save.convert("RGB").save(file_path, format=output_format, quality=95)
                messagebox.showinfo("Thành công", "Đã xuất ảnh thumbnail thành công!", parent=self)
                self.log_callback(f"Đã xuất ảnh: {file_path}")
        except Exception as e:
            messagebox.showerror("Lỗi xuất ảnh", f"Đã có lỗi xảy ra: {e}", parent=self)