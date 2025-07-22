# file-path: run.py
# version: 2.0
# last-updated: 2025-07-22
# description: Tích hợp thư viện sv-ttk để áp dụng theme hiện đại cho toàn bộ ứng dụng.

import tkinter as tk
import sv_ttk # Import thư viện theme
from src.gemini_tts_app.main_app import TTSApp
from src.gemini_tts_app.logger_setup import setup_logging
import logging

def run_application():
    """Khởi tạo và chạy ứng dụng chính."""
    # Cài đặt hệ thống logging trước khi làm bất cứ điều gì khác
    setup_logging()
    
    try:
        root = tk.Tk()
        
        # Áp dụng theme sv-ttk ngay từ đầu
        # Điều này phải được thực hiện trước khi bất kỳ widget nào được tạo
        sv_ttk.set_theme("light") 
        
        app = TTSApp(root)
        root.mainloop()
    except Exception as e:
        # Ghi lại bất kỳ lỗi nghiêm trọng nào không bắt được
        logging.critical("An unhandled exception occurred at the application level.", exc_info=True)

if __name__ == "__main__":
    run_application()