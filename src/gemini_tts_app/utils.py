# src/gemini_tts_app/utils.py
import sys
import os

def get_resource_path(relative_path: str) -> str:
    """
    Lấy đường dẫn tuyệt đối đến resource.
    Hoạt động cả khi chạy code trực tiếp (development) và khi đóng gói bằng PyInstaller.
    """
    try:
        # PyInstaller tạo thư mục tạm và lưu đường dẫn trong sys._MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Chạy ở chế độ development
        # Giả định utils.py nằm trong src/gemini_tts_app/
        # và thư mục resources/ nằm ở thư mục gốc của project (cùng cấp với src/)
        # src/gemini_tts_app/ -> src/ -> project_root/
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    return os.path.join(base_path, "resources", relative_path)

# Bạn có thể thêm các hàm tiện ích khác ở đây