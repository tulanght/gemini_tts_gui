# run.py
import tkinter as tk
from tkinter import ttk
from src.gemini_tts_app.main_app import TTSApp
# --- THÊM MỚI ---
from src.gemini_tts_app.logger_setup import setup_logging
import logging
# --- KẾT THÚC THÊM MỚI ---

def run_application():
    """Khởi tạo và chạy ứng dụng chính."""
    # --- THÊM MỚI ---
    # Cài đặt hệ thống logging trước khi làm bất cứ điều gì khác
    setup_logging()
    # --- KẾT THÚC THÊM MỚI ---
    
    try:
        root = tk.Tk()
        # Thử áp dụng theme 'clam' để có giao diện hiện đại hơn
        try:
            style = ttk.Style(root)
            style.theme_use('clam')
        except tk.TclError:
            print("Chủ đề 'clam' không có sẵn, sử dụng chủ đề mặc định.")
        
        app = TTSApp(root)
        root.mainloop()
    except Exception as e:
        # Ghi lại bất kỳ lỗi nghiêm trọng nào không bắt được
        logging.critical("An unhandled exception occurred at the application level.", exc_info=True)
        # Tùy chọn: Hiển thị một cửa sổ lỗi cho người dùng
        # import traceback
        # from tkinter import messagebox
        # messagebox.showerror("Lỗi nghiêm trọng", f"Một lỗi không mong muốn đã xảy ra:\n\n{traceback.format_exc()}")


if __name__ == "__main__":
    run_application()