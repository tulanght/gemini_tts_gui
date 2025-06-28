# src/gemini_tts_app/init_pydub.py
import os
import shutil
from tkinter import messagebox

# Hàm này sẽ được gọi trước khi pydub được import ở bất kỳ đâu khác
def configure_pydub():
    # Tìm kiếm ffmpeg trong PATH hệ thống
    ffmpeg_executable = shutil.which("ffmpeg")
    if ffmpeg_executable:
        # Nếu tìm thấy, chúng ta không cần làm gì cả, pydub sẽ tự tìm thấy
        # Đây là một "noop" nhưng để đảm bảo logic được rõ ràng
        print(f"INFO: [init_pydub] FFMPEG found at: {ffmpeg_executable}. Pydub should work correctly.")
    else:
        # Nếu không tìm thấy, thử chỉ định đường dẫn thủ công
        # THAY THẾ ĐƯỜNG DẪN NÀY BẰNG ĐƯỜNG DẪN THẬT TRÊN MÁY CỦA BẠN
        manual_ffmpeg_path = "D:/Tools/ffmpeg-7.1/bin"

        if os.path.isdir(manual_ffmpeg_path):
            print(f"INFO: [init_pydub] FFMPEG not in PATH, adding manually: {manual_ffmpeg_path}")
            os.environ["PATH"] += os.pathsep + manual_ffmpeg_path
        else:
            print(f"ERROR: [init_pydub] FFMPEG not found in system PATH or manual path.")
            messagebox.showerror(
                "Lỗi Thiếu FFMPEG",
                "Không tìm thấy ffmpeg.exe. Vui lòng đảm bảo nó đã được cài đặt và thêm vào PATH, hoặc cập nhật đường dẫn trong 'src/gemini_tts_app/init_pydub.py'."
            )

# Chạy cấu hình ngay khi file này được import
configure_pydub()