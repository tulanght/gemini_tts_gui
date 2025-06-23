# src/gemini_tts_app/__main__.py
import sys # <--- THÊM DÒNG NÀY
import os  # <--- THÊM DÒNG NÀY
import tkinter as tk
from .main_app import TTSApp
from .utils import get_resource_path # Giả sử bạn cần set icon từ đây
from .constants import APP_NAME # Nếu bạn định nghĩa APP_NAME trong constants

def main():
    """Main function to launch the GUI application."""
    root = tk.Tk()
    app = TTSApp(root)

    # Cố gắng đặt icon (ví dụ)
    try:
        icon_path_ico = get_resource_path("icons/app_icon.ico")
        # Icon cho Windows (ưu tiên .ico)
        if sys.platform.startswith('win'):
             root.iconbitmap(icon_path_ico)
        else:
            # Icon cho các HĐH khác (thường là .png hoặc .xbm)
            # Tkinter có thể cần PhotoImage cho .png
            icon_path_png = get_resource_path("icons/app_icon.png")
            if os.path.exists(icon_path_png): # Kiểm tra file tồn tại
                photo = tk.PhotoImage(file=icon_path_png)
                root.iconphoto(False, photo) # False cho cửa sổ chính
    except Exception as e:
        print(f"Could not set window icon: {e}")
        # app.log_message(f"Could not set window icon: {e}") # Nếu muốn log vào UI

    root.mainloop()

if __name__ == "__main__":
    main()