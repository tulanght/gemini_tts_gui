# Project Handover v2.0: Gemini Creative Suite

**Ngày tạo:** 23/06/2025
**Phiên bản dự án:** 2.0
**Mục đích:** Đây là tài liệu bàn giao dự án toàn diện, đóng vai trò là "bộ nhớ" và "nguồn sự thật duy nhất" (single source of truth) cho AI (Gemini) khi bắt đầu một phiên làm việc mới, nhằm đảm bảo tính nhất quán, kế thừa toàn bộ lịch sử phát triển và tránh lặp lại các sai sót cũ.

---

## Phần 1: Tổng quan Dự án (Đã mở rộng)

### 1.1. Tóm Tắt & Bối cảnh
Đây là dự án xây dựng một bộ công cụ đa năng **"Gemini Creative Suite"** trên máy tính bằng Python và Tkinter. Ứng dụng được thiết kế để phục vụ quy trình sản xuất video cho kênh YouTube **"Radio Gia Đình"**, tập trung vào thể loại **truyện tâm lý xã hội, gia đình**.

Bộ công cụ bao gồm 3 module chính đã được phát triển ở các mức độ khác nhau:
1.  **Gemini TTS:** Chức năng cốt lõi, dùng để chuyển văn bản thành file audio voice-over.
2.  **Trợ Lý Biên Tập:** Công cụ phân tích, soạn thảo, và tối ưu hóa Tiêu đề & Text Thumbnail.
3.  **Soạn Truyện Dài:** Công cụ hỗ trợ quá trình sáng tác truyện dài, giúp nối các đoạn văn bản và tạo prompt tiếp nối một cách bán tự động.

### 1.2. Model & Thư viện chính
* **Model Gemini:** `models/gemini-2.5-pro-preview-tts`
* **Thư viện Python:**
    * `google-generativeai==0.8.5`: Tương tác với API Gemini.
    * `tkinter`, `tkhtmlview`: Xây dựng giao diện người dùng.
    * `pydub`: Xử lý, ghép file audio (yêu cầu `ffmpeg` trên hệ thống).
    * `audioop-lts`: Hỗ trợ tương thích `pydub` trên Python 3.13+.
    * `appdirs`: Quản lý thư mục chứa file cài đặt, log, CSDL một cách chuẩn hóa.
    * `Pillow`: Xử lý ảnh cho tính năng xem trước thumbnail.
    * `matplotlib`: Lấy danh sách font chữ hệ thống.
    * `pyperclip`: Tương tác với clipboard hệ thống.
    * `python-docx`: Đọc nội dung từ file `.docx`.

---

## Phần 2: Trạng thái Code Ổn định Hiện tại

### 2.1. Cấu trúc Thư mục Dự án (Đã loại bỏ `ui_preview`)
```
gemini_tts_gui/
├── run.py
├── requirements.txt
├── .gitignore
└── src/
    └── gemini_tts_app/
        ├── __init__.py
        ├── __main__.py
        ├── constants.py
        ├── database.py
        ├── logger_setup.py
        ├── main_app.py
        ├── settings_manager.py
        ├── tts_logic.py
        └── utils.py
```

### 2.2. Mô tả Logic Hoạt động các File chính
* **`run.py`:** Điểm khởi chạy ứng dụng, gọi `setup_logging()` trước tiên, sau đó tạo và chạy `TTSApp`.
* **`logger_setup.py`:** Thiết lập hệ thống logging tập trung, tự động lưu log ra file theo ngày giờ.
* **`database.py`:** Quản lý kết nối và các thao tác với CSDL `assistant_data.db` (SQLite).
* **`tts_logic.py`:** Chứa logic xử lý TTS, nổi bật với kiến trúc **"Quản lý - Nhân viên"** và cơ chế **tự động giảm số luồng** khi gặp lỗi `ResourceExhausted`.
* **`main_app.py`:** Chứa toàn bộ giao diện và logic tương tác người dùng, bao gồm:
    * **Module "Soạn Truyện Dài":** Sử dụng một **panel nổi** và một **luồng chạy nền** để theo dõi clipboard, áp dụng "bộ lọc thông minh" để tự động nối truyện và tạo prompt.
    * **Module "Trợ Lý Biên Tập":** Sử dụng logic bóc tách thông minh để xử lý các định dạng output khác nhau của Gemini. Tích hợp tính năng **xem trước thumbnail bằng `Tkinter Canvas`**.

### 2.3. Mã nguồn các file chính (Nền tảng Vàng)

**Lưu ý:** Bạn sẽ dán nội dung các file đang hoạt động tốt nhất của mình vào các khối code dưới đây.

#### **`run.py`**
```python
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
```

#### **`src/gemini_tts_app/constants.py`**
```python
# src/gemini_tts_app/constants.py
# Phiên bản: constants_v7.0_assistant_setup
APP_NAME = "Gemini TTS GUI"
APP_VERSION = "0.7.0" # Nâng version cho tính năng mới
APP_AUTHOR = "Cuong Tran" 

# --- API Key Settings ---
NUM_API_KEYS = 3 

# --- TTS Settings ---
DEFAULT_VOICE = "Algieba"
DEFAULT_TEMPERATURE = 1.0
MIN_TEMPERATURE = 0.0
MAX_TEMPERATURE = 2.0
DEFAULT_TOP_P = 0.95
MIN_TOP_P = 0.0
MAX_TOP_P = 1.0

# --- MỚI: Hằng số cho Trợ lý Biên tập ---
DATABASE_FILE = "assistant_data.db"

# Ngưỡng ký tự cho Tiêu đề
TITLE_CHAR_LIMIT_GOOD_MIN = 90
TITLE_CHAR_LIMIT_GOOD_MAX = 100
TITLE_CHAR_LIMIT_MAX = 100

# Màu sắc cảnh báo
COLOR_OK = "#2E7D32"      # Xanh lá đậm
COLOR_WARN = "#FF8F00"   # Vàng cam
COLOR_ERROR = "#D32F2F"   # Đỏ đậm
COLOR_NORMAL = "black"

# Regex để bóc tách các lựa chọn
GEMINI_RESPONSE_PATTERN = r"\*\*LỰA CHỌN \d+.*?\*\*([\s\S]*?)(?=\*\*LỰA CHỌN|\Z)"

GEMINI_TTS_VOICES_DETAILED = [
    {'name': 'Orus', 'gender': 'Nam', 'description': 'Nghiêm túc, đĩnh đạc - Giới thiệu sản phẩm, chuyên sâu'},
    {'name': 'Lapetus', 'gender': 'Nam', 'description': 'Rõ ràng, dễ hiểu - Hướng dẫn kỹ thuật, bài giảng'},
    {'name': 'Rasalgethi', 'gender': 'Nam', 'description': 'Mạch lạc, logic - Voice cho trợ lý ảo, đào tạo nội bộ'},
    {'name': 'Schedar', 'gender': 'Nam', 'description': 'Ổn định, tin cậy - Đọc tài liệu, nội dung AI'},
    {'name': 'Kore', 'gender': 'Nam', 'description': 'Chuyên nghiệp, gãy gọn - Video thuyết trình, sản phẩm'},
    {'name': 'Erinome', 'gender': 'Nam', 'description': 'Trung tính, dễ tiếp cận - Video khoa học, giáo dục'},
    {'name': 'Charon', 'gender': 'Nam', 'description': 'Trẻ trung, dễ nghe - Video học tập, chia sẻ kiến thức'},
    {'name': 'Anilam', 'gender': 'Nam', 'description': 'Kiên định, chắc chắn - Dẫn dắt nội dung chuyên môn'},
    {'name': 'Enceladus', 'gender': 'Nam', 'description': 'Êm ái, thư giãn - Voice đọc sách, kiến thức nhẹ nhàng'},
    {'name': 'Sadaltager', 'gender': 'Nữ', 'description': 'Lôi cuốn, trò chuyện - Giải thích công nghệ, nội dung chuyên sâu'},
    {'name': 'Leda', 'gender': 'Nữ', 'description': 'Tươi mới, rõ ràng - Nội dung học tập cho Gen Z'},
    {'name': 'Autonoe', 'gender': 'Nữ', 'description': 'Ấm áp, truyền cảm - Video startup, khởi nghiệp'},
    {'name': 'Despina', 'gender': 'Nữ', 'description': 'Êm dịu, dễ tiếp thu - Storytelling nhẹ nhàng, kể chuyện giáo dục'},
    {'name': 'Umbriel', 'gender': 'Nam', 'description': 'Bình tĩnh, thân thiện - Podcast cuộc sống, chia sẻ cá nhân'},
    {'name': 'Algenib', 'gender': 'Nam', 'description': 'Trầm lắng, nghiêm túc - Podcast chủ đề sâu'},
    {'name': 'Pulcherrima', 'gender': 'Nữ', 'description': 'Nhiệt huyết, truyền cảm - Call-to-action, podcast mạnh mẽ'},
    {'name': 'Callirrhoe', 'gender': 'Nữ', 'description': 'Nhẹ nhàng, sâu lắng - Healing content, podcast thư giãn'},
    {'name': 'Achernar', 'gender': 'Nữ', 'description': 'Trầm sâu, cảm xúc - Podcast ban đêm, chủ đề sâu sắc'},
    {'name': 'Sulafar', 'gender': 'Nữ', 'description': 'Truyền cảm, ấm áp - Podcast tâm sự, đài tập'},
    {'name': 'Fenrir', 'gender': 'Nam', 'description': 'Sôi nổi, mạnh mẽ - Video giới thiệu sản phẩm, quảng cáo'},
    {'name': 'Algieba', 'gender': 'Nam', 'description': 'Đậm chất truyền cảm - Giọng kể chuyện bán hàng'},
    {'name': 'Achird', 'gender': 'Nữ', 'description': 'Thân thiện, gần gũi - Video giới thiệu sản phẩm nhẹ nhàng'},
    {'name': 'Sadachbia', 'gender': 'Nữ', 'description': 'Tươi sáng, nhiệt huyết - Quảng cáo năng lượng, truyền động lực'},
    {'name': 'Zephyr', 'gender': 'Nữ', 'description': 'Ngọt ngào, cảm xúc - Giới thiệu sản phẩm thiên về cảm nhận'},
    {'name': 'Laomedeia', 'gender': 'Nữ', 'description': 'Trẻ trung, hiện đại - TikTok giới thiệu sản phẩm'},
    {'name': 'Puck', 'gender': 'Nam', 'description': 'Hóm hỉnh, vui vẻ - Video TikTok, giải trí ngắn'},
    {'name': 'Zubenelgenubi', 'gender': 'Nam', 'description': 'Tự nhiên, sinh động - TikTok đời thường, chia sẻ cuộc sống'},
    {'name': 'Aoede', 'gender': 'Nữ', 'description': 'Dễ chịu, vui vẻ - Voice cho lifestyle, game, giải trí'},
    {'name': 'Vindemiatrix', 'gender': 'Nữ', 'description': 'Nhẹ nhàng, chuyên nghiệp - Voice trợ lý ảo, CSKH'},
    {'name': 'Gacrux', 'gender': 'Nam', 'description': 'Tự tin, có chiều sâu - Voice review, đánh giá sản phẩm'},
]

PREDEFINED_READING_STYLES = [
    # Prompt 1: Tối ưu cho truyện tâm sự gia đình, đêm khuya - Tự nhiên & Khách quan
    "Phong cách: kể chuyện một cách bình tĩnh, khách quan. Tông giọng: đều, không quá nhấn nhá, giữ sự trung lập. Tốc độ: vừa phải, trôi chảy. Yêu cầu quan trọng: không tự ý thêm cảm xúc cá nhân vào lời kể, tránh các khoảng ngừng dài không cần thiết, đọc như một người quan sát và tường thuật lại câu chuyện.",
    # Prompt 2: Phong cách Radio tâm sự - Ấm áp nhưng kiểm soát
    "Vai trò: người dẫn chương trình radio tâm sự. Giọng đọc ấm, rõ ràng nhưng có kiểm soát, không bi lụy. Nhịp điệu chậm rãi, đều đặn. Ngắt nghỉ ngắn gọn tại các dấu câu. Mục tiêu là tạo sự tin cậy và đồng cảm một cách tinh tế, không phải diễn kịch.",
    # Prompt 3: Kể chuyện đời thường - Gần gũi, không màu mè
    "Phong cách: như đang trò chuyện, kể lại một câu chuyện đời thường. Giọng nói tự nhiên, không màu mè, không cần quá trau chuốt. Tốc độ nói nhanh hơn một chút, thể hiện sự gần gũi. Tránh sử dụng ngữ điệu của người kể chuyện chuyên nghiệp.",
    # Prompt 4: Đọc tin tức xã hội - Rõ ràng, trung lập
    "Phong cách của một biên tập viên đọc tin tức xã hội: rõ ràng, mạch lạc, dứt khoát. Giọng đọc giữ thái độ trung lập, không thể hiện quan điểm cá nhân. Tập trung vào việc truyền đạt thông tin một cách chính xác.",
    ""
]
```

#### **`src/gemini_tts_app/settings_manager.py`**
```python
# src/gemini_tts_app/settings_manager.py
# Phiên bản: settings_manager_v3.1_add_chunk_size
import configparser
import os
from appdirs import user_config_dir

from .constants import (
    APP_NAME as APP_NAME_CONST, 
    APP_AUTHOR as APP_AUTHOR_CONST, 
    DEFAULT_VOICE as DEFAULT_VOICE_CONST, 
    DEFAULT_TEMPERATURE as DEFAULT_TEMPERATURE_CONST,
    DEFAULT_TOP_P as DEFAULT_TOP_P_CONST,
    NUM_API_KEYS
)

CONFIG_DIR = user_config_dir(APP_NAME_CONST, APP_AUTHOR_CONST)
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.ini")

DEFAULT_SETTINGS = {
    "default_voice": DEFAULT_VOICE_CONST,
    "temperature": DEFAULT_TEMPERATURE_CONST,
    "top_p": DEFAULT_TOP_P_CONST,
    "save_dir": os.path.expanduser("~"),
    "max_words_per_part": 1000 # Thêm cài đặt kích thước chunk
}
for i in range(1, NUM_API_KEYS + 1):
    DEFAULT_SETTINGS[f"api_key_{i}"] = ""
    DEFAULT_SETTINGS[f"label_{i}"] = f"API Key {i}"

def _ensure_config_dir_exists():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR, exist_ok=True)
    return True

def save_settings(settings_dict: dict):
    if not _ensure_config_dir_exists(): return False
                
    config = configparser.ConfigParser()
    general_settings = {}
    api_key_settings = {}

    for key, value in settings_dict.items():
        if key.startswith("api_key_") or key.startswith("label_"):
            api_key_settings[key] = str(value)
        else:
            general_settings[key] = str(value)
                
    config["GEMINI_TTS_GENERAL"] = general_settings
    config["GEMINI_TTS_API_KEYS"] = api_key_settings
            
    try:
        with open(CONFIG_FILE, "w", encoding='utf-8') as configfile:
            config.write(configfile)
        return True
    except IOError as e:
        print(f"Error writing to config file: {e}")
        return False

def load_settings() -> dict:
    if not os.path.exists(CONFIG_FILE):
        save_settings(DEFAULT_SETTINGS) 
        return DEFAULT_SETTINGS.copy()

    config = configparser.ConfigParser(defaults=DEFAULT_SETTINGS)
    try:
        config.read(CONFIG_FILE, encoding='utf-8')
    except Exception as e:
        print(f"Error reading config, using defaults: {e}")
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

    loaded_settings = {}
    general_section = "GEMINI_TTS_GENERAL"
    if general_section not in config:
        config.add_section(general_section)
        
    for key, default_value in DEFAULT_SETTINGS.items():
         if not (key.startswith("api_key_") or key.startswith("label_")):
            if isinstance(default_value, int):
                loaded_settings[key] = config.getint(general_section, key, fallback=default_value)
            elif isinstance(default_value, float):
                loaded_settings[key] = config.getfloat(general_section, key, fallback=default_value)
            else:
                 loaded_settings[key] = config.get(general_section, key, fallback=str(default_value))
    
    api_section = "GEMINI_TTS_API_KEYS"
    if api_section not in config:
        config.add_section(api_section)

    for i in range(1, NUM_API_KEYS + 1):
        loaded_settings[f"api_key_{i}"] = config.get(api_section, f"api_key_{i}", fallback="")
        loaded_settings[f"label_{i}"] = config.get(api_section, f"label_{i}", fallback=f"API Key {i}")
            
    return loaded_settings
```

#### **`src/gemini_tts_app/database.py`**
```python
# src/gemini_tts_app/database.py
# Module quản lý cơ sở dữ liệu SQLite cho Trợ lý Biên Tập

import sqlite3
import os
from datetime import datetime
from appdirs import user_data_dir

# Sử dụng appdirs để có đường dẫn lưu trữ nhất quán và phù hợp với HĐH
from .constants import APP_NAME as APP_NAME_CONST, APP_AUTHOR as APP_AUTHOR_CONST

class DatabaseManager:
    def __init__(self, db_name="assistant_data.db"):
        """
        Khởi tạo và kết nối tới cơ sở dữ liệu.
        CSDL sẽ được lưu trong thư mục dữ liệu của ứng dụng.
        """
        data_dir = user_data_dir(APP_NAME_CONST, APP_AUTHOR_CONST)
        os.makedirs(data_dir, exist_ok=True)
        self.db_path = os.path.join(data_dir, db_name)
        self.conn = None
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.create_tables()
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")

    def create_tables(self):
        """
        Tạo các bảng cần thiết nếu chúng chưa tồn tại.
        """
        if not self.conn:
            return
        
        cursor = self.conn.cursor()
        # Bảng cho các tiêu đề đã chốt
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS final_titles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title_text TEXT NOT NULL,
                char_count INTEGER NOT NULL,
                word_count INTEGER NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        
        # Bảng cho các text thumbnail đã chốt
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS final_thumbnails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thumbnail_text TEXT NOT NULL,
                char_count INTEGER NOT NULL,
                word_count INTEGER NOT NULL,
                line_count INTEGER NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        self.conn.commit()
        cursor.close()

    def add_final_title(self, title_text, char_count, word_count):
        """
        Thêm một tiêu đề đã chốt vào cơ sở dữ liệu.
        """
        if not self.conn:
            return False
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = '''INSERT INTO final_titles(title_text, char_count, word_count, timestamp)
                 VALUES(?,?,?,?)'''
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, (title_text, char_count, word_count, timestamp))
            self.conn.commit()
            cursor.close()
            return True
        except sqlite3.Error as e:
            print(f"Failed to add title: {e}")
            return False

    def add_final_thumbnail(self, thumbnail_text, char_count, word_count, line_count):
        """
        Thêm một text thumbnail đã chốt vào cơ sở dữ liệu.
        """
        if not self.conn:
            return False

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = '''INSERT INTO final_thumbnails(thumbnail_text, char_count, word_count, line_count, timestamp)
                 VALUES(?,?,?,?,?)'''
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, (thumbnail_text, char_count, word_count, line_count, timestamp))
            self.conn.commit()
            cursor.close()
            return True
        except sqlite3.Error as e:
            print(f"Failed to add thumbnail text: {e}")
            return False

    def close(self):
        """
        Đóng kết nối CSDL khi ứng dụng thoát.
        """
        if self.conn:
            self.conn.close()
```

#### **`src/gemini_tts_app/logger_setup.py`**
```python
# src/gemini_tts_app/logger_setup.py
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from appdirs import user_log_dir
from .constants import APP_NAME, APP_AUTHOR

def setup_logging():
    """Cài đặt hệ thống logging tập trung cho toàn bộ ứng dụng."""
    log_dir = user_log_dir(APP_NAME, APP_AUTHOR)
    os.makedirs(log_dir, exist_ok=True)
    
    log_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log"
    log_filepath = os.path.join(log_dir, log_filename)

    # Định dạng cho log
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Thiết lập root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Ngăn việc logger bị thêm handler nhiều lần nếu hàm được gọi lại
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Handler để ghi ra file, tự động xoay vòng khi file quá lớn
    file_handler = RotatingFileHandler(
        log_filepath, 
        maxBytes=5*1024*1024, # 5 MB
        backupCount=3, 
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Handler để in ra console (cho mục đích gỡ lỗi)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    logging.info("Logging system initialized.")
    logging.info(f"Log file located at: {log_filepath}")
```

#### **`src/gemini_tts_app/tts_logic.py`**
```python
# src/gemini_tts_app/tts_logic.py
# Phiên bản: tts_logic_v39_rework_progress
import mimetypes
import os
import struct
import traceback
import base64
import time
import queue 
import threading

import google.generativeai as genai
from google.generativeai import types
from google.api_core import exceptions as core_exceptions
from pydub import AudioSegment
# Thêm dòng này để import các hằng số màu
from .constants import COLOR_OK, COLOR_WARN, COLOR_ERROR, COLOR_NORMAL
gemini_api_config_lock = threading.Lock()

def save_binary_file(file_name, data, log_callback=None):
    try:
        norm_file_name = os.path.normpath(file_name)
        with open(norm_file_name, "wb") as f: f.write(data)
        if log_callback: log_callback(f"File saved to: {norm_file_name}")
        return True
    except Exception as e:
        if log_callback: log_callback(f"Error saving file '{os.path.normpath(file_name)}': {e}")
        return False

def parse_audio_mime_type(mime_type: str) -> dict[str, int | None]:
    bits_per_sample = 16; rate = 24000
    main_type_params = mime_type.split(";", 1); main_type = main_type_params[0].strip()
    if main_type.startswith("audio/L"):
        try: bits_per_sample = int(main_type.split("L", 1)[1])
        except (ValueError, IndexError): pass
    if len(main_type_params) > 1:
        params_str = main_type_params[1]; params = params_str.split(";")
        for param in params:
            param = param.strip()
            if param.lower().startswith("rate="):
                try: rate = int(param.split("=", 1)[1])
                except (ValueError, IndexError): pass
    return {"bits_per_sample": bits_per_sample, "rate": rate}

def convert_to_wav(audio_data: bytes, assumed_pcm_mime_type: str, log_callback=None) -> bytes | None:
    parameters = parse_audio_mime_type(assumed_pcm_mime_type)
    bits_per_sample = parameters.get("bits_per_sample", 16); sample_rate = parameters.get("rate", 24000)
    num_channels = 1; data_size = len(audio_data);
    if data_size == 0: return None
    bytes_per_sample = bits_per_sample // 8
    block_align = num_channels * bytes_per_sample; byte_rate = sample_rate * block_align
    riff_chunk_data_size = 36 + data_size
    header = struct.pack("<4sI4s4sIHHIIHH4sI", b"RIFF", riff_chunk_data_size, b"WAVE", b"fmt ", 16, 1, num_channels, sample_rate, byte_rate, block_align, bits_per_sample, b"data", data_size)
    return header + audio_data

def count_tokens_for_model(model_instance: genai.GenerativeModel, text_or_content, log_callback=None) -> int | None:
    try:
        token_count_obj = model_instance.count_tokens(text_or_content)
        return getattr(token_count_obj, 'total_tokens', None)
    except Exception as e:
        if log_callback: log_callback(f"Error counting tokens: {e}")
        return None

def count_words(text: str) -> int: return len(text.split()) if text else 0

def split_text_into_chunks(model_instance: genai.GenerativeModel, full_text: str, max_words_per_chunk: int, max_tokens_fallback: int, log_callback=None) -> list[str]:
    if log_callback: log_callback(f"Splitting text (length: {len(full_text)} chars, ~{count_words(full_text)} words) into chunks of max ~{max_words_per_chunk} words, fallback max ~{max_tokens_fallback} tokens.")
    chunks = []; current_char_offset = 0
    while current_char_offset < len(full_text):
        words_in_remaining_text = full_text[current_char_offset:].split()
        current_chunk_words = words_in_remaining_text[:max_words_per_chunk]
        candidate_chunk_text = " ".join(current_chunk_words)
        end_char_offset_candidate = current_char_offset + len(candidate_chunk_text)
        
        temp_search_offset = current_char_offset
        if current_chunk_words:
            for i, word in enumerate(current_chunk_words):
                found_pos = full_text.find(word, temp_search_offset)
                if found_pos != -1:
                    temp_search_offset = found_pos + len(word)
                else:
                    temp_search_offset = current_char_offset + len(" ".join(current_chunk_words[:i+1]))
                    break
            end_char_offset_candidate = temp_search_offset

        text_for_token_check = full_text[current_char_offset : end_char_offset_candidate]
        num_tokens = count_tokens_for_model(model_instance, text_for_token_check, log_callback)
        
        while (num_tokens is None or num_tokens > max_tokens_fallback) and len(current_chunk_words) > 1:
            current_chunk_words = current_chunk_words[:-10]
            if not current_chunk_words: break
            
            temp_search_offset = current_char_offset
            for i, word in enumerate(current_chunk_words):
                found_pos = full_text.find(word, temp_search_offset)
                if found_pos != -1:
                    temp_search_offset = found_pos + len(word)
                else:
                    temp_search_offset = current_char_offset + len(" ".join(current_chunk_words[:i+1]))
                    break
            end_char_offset_candidate = temp_search_offset
            text_for_token_check = full_text[current_char_offset : end_char_offset_candidate]
            num_tokens = count_tokens_for_model(model_instance, text_for_token_check, log_callback)

        final_text_segment = full_text[current_char_offset : end_char_offset_candidate]
        actual_end_char_offset = end_char_offset_candidate

        if end_char_offset_candidate < len(full_text):
            best_split_pos = -1
            for punc in ['\n\n', '\n', '.', '!', '?']:
                pos = final_text_segment.rfind(punc)
                if pos != -1:
                    best_split_pos = pos + len(punc)
                    break
            
            if best_split_pos != -1 and best_split_pos > len(final_text_segment) * 0.5:
                actual_end_char_offset = current_char_offset + best_split_pos

        final_chunk_to_add = full_text[current_char_offset : actual_end_char_offset].strip()
        if final_chunk_to_add:
            chunks.append(final_chunk_to_add)
            if log_callback:
                final_tokens = count_tokens_for_model(model_instance, final_chunk_to_add, None)
                log_msg = f"  Added chunk {len(chunks)}: {count_words(final_chunk_to_add)} words, {len(final_chunk_to_add)} chars, ~{final_tokens} tokens."
                if len(final_chunk_to_add) > 30: log_msg += f" Ends: '...{final_chunk_to_add[-30:]}'"
                log_callback(log_msg)
        
        current_char_offset = actual_end_char_offset
        if current_char_offset >= len(full_text): break

    if log_callback: log_callback(f"Text split into {len(chunks)} final chunk(s).")
    return chunks

# --- HOTFIX [2025-06-08 22:00]: Thêm khoảng lặng 2 giây giữa các part khi ghép file. Thay thế toàn bộ hàm này. ---
def merge_audio_files(audio_file_paths: list[str], output_merged_path: str, output_format: str = "wav", log_callback=None) -> bool:
    actual_files_to_merge = [f for f in audio_file_paths if f and os.path.exists(os.path.normpath(f))]
    if not actual_files_to_merge:
        if log_callback: log_callback("No valid audio part files to merge.")
        return False
    
    silence_duration_ms = 2000 
    silence_segment = AudioSegment.silent(duration=silence_duration_ms)
    
    if log_callback: log_callback(f"Merging {len(actual_files_to_merge)} files with a {silence_duration_ms}ms silence...")
    
    try:
        combined_audio = AudioSegment.from_file(actual_files_to_merge[0])
        for i in range(1, len(actual_files_to_merge)):
            segment = AudioSegment.from_file(actual_files_to_merge[i])
            combined_audio += silence_segment + segment
        
        if len(combined_audio) == 0: return False
            
        combined_audio.export(os.path.normpath(output_merged_path), format=output_format)
        if log_callback: log_callback(f"Successfully merged to {os.path.normpath(output_merged_path)}")
        return True
    except Exception as e:
        if log_callback: log_callback(f"Error merging audio: {e}")
        return False

def _generate_audio_for_single_chunk(model_instance, text_chunk, reading_style_prompt, voice_name, part_filename_base, part_num, total_parts, temp_setting_from_ui, top_p_from_ui, max_retries, part_timeout, log_callback_main, progress_callback_part):
    part_start_time = time.time()
    text_for_api = f"{reading_style_prompt.strip()}: {text_chunk}" if reading_style_prompt and reading_style_prompt.strip() else text_chunk
    
    for attempt in range(max_retries + 1):
        try:
            status_msg = f"Đang xử lý Part {part_num}/{total_parts}"
            if attempt > 0: status_msg += f" (Thử lại {attempt})"
            progress_callback_part(status_msg, "blue")

            tts_contents = [{"role": "user", "parts": [{"text": text_for_api}]}]
            ai_studio_config = {"temperature": temp_setting_from_ui, "top_p": top_p_from_ui, "response_modalities": ["AUDIO"], "speech_config": {"voice_config": {"prebuilt_voice_config": {"voice_name": voice_name}}}}
            request_options = types.RequestOptions(timeout=part_timeout)
            
            response_stream = model_instance.generate_content(tts_contents, generation_config=ai_studio_config, stream=True, request_options=request_options)
            
            all_audio_data_part = bytearray()
            for chunk in response_stream:
                if hasattr(chunk, 'parts') and chunk.parts and hasattr(chunk.parts[0], 'inline_data'):
                    all_audio_data_part.extend(chunk.parts[0].inline_data.data)

            if len(all_audio_data_part) < 1024 or (bytes(all_audio_data_part).count(b'\x00') / len(all_audio_data_part) > 0.99):
                raise genai.types.generation_types.StopCandidateException("Insufficient or silent audio data")

            data_buffer = bytes(all_audio_data_part)
            if not data_buffer.startswith(b'RIFF'):
                data_buffer = convert_to_wav(data_buffer, "audio/L16;rate=24000", log_callback_main)
            
            if data_buffer and save_binary_file(f"{part_filename_base}.wav", data_buffer, log_callback_main):
                time_taken = time.time() - part_start_time
                progress_callback_part(f"Hoàn thành Part {part_num} (mất {time_taken:.1f}s)", COLOR_OK)
                return f"{part_filename_base}.wav", time_taken
            else:
                raise IOError("Failed to save audio")

        except core_exceptions.ResourceExhausted as e:
            progress_callback_part(f"Lỗi Part {part_num}: Resource Exhausted!", COLOR_ERROR)
            raise e
        except Exception as e:
            log_callback_main(f"Part {part_num}, Attempt {attempt + 1} FAILED with {e.__class__.__name__}")
            if attempt < max_retries:
                progress_callback_part(f"Lỗi Part {part_num}, đang thử lại...", COLOR_WARN)
                time.sleep(2.0 * (2**attempt))
            else:
                progress_callback_part(f"Thất bại Part {part_num}", COLOR_ERROR)
                return None, time.time() - part_start_time
    return None, time.time() - part_start_time

def _process_text_chunk_worker(api_key_info, job_queue, results_list, feedback_queue, thread_id, reading_style_prompt, voice_name, temp_audio_dir, base_filename_no_ext, total_chunks, temp_setting, top_p_setting, max_retries_per_part, part_timeout, log_callback_ui, progress_callback_ui_thread, part_times_list, api_key_config_lock):
    try:
        with api_key_config_lock: 
            genai.configure(api_key=api_key_info["key"])
            model_instance_for_thread = genai.GenerativeModel(model_name="models/gemini-2.5-pro-preview-tts")
        progress_callback_ui_thread("Sẵn sàng", COLOR_NORMAL)
    except Exception as e:
        progress_callback_ui_thread("Lỗi khởi tạo", COLOR_ERROR)
        feedback_queue.put({"type": "FATAL_ERROR", "thread_id": thread_id})
        return

    while True: 
        try:
            part_index, text_chunk = job_queue.get(block=True, timeout=2.0)
        except queue.Empty:
            progress_callback_ui_thread("Hoàn thành, không còn việc.", COLOR_NORMAL)
            break
        
        try:
            file_path, time_taken = _generate_audio_for_single_chunk(
                model_instance_for_thread, text_chunk, reading_style_prompt,
                voice_name, os.path.normpath(os.path.join(temp_audio_dir, f"{base_filename_no_ext}_part_{part_index + 1:03d}")),
                part_index + 1, total_chunks, temp_setting, top_p_setting,
                max_retries_per_part, part_timeout, log_callback_ui,
                progress_callback_ui_thread
            )
            results_list[part_index] = file_path 
            part_times_list[part_index] = time_taken
            feedback_queue.put({"type": "TASK_DONE", "success": bool(file_path)})
            if file_path:
                time.sleep(5) # Dừng 3 giây để người dùng thấy trạng thái "Hoàn thành"
                
        except core_exceptions.ResourceExhausted:
            job_queue.put((part_index, text_chunk))
            feedback_queue.put({"type": "RESOURCE_EXHAUSTED", "thread_id": thread_id})
            break
        except Exception as e:
            results_list[part_index] = None
            part_times_list[part_index] = -1.0
            progress_callback_ui_thread(f"Lỗi không xác định Part {part_index + 1}", COLOR_ERROR)
            feedback_queue.put({"type": "TASK_DONE", "success": False})

def generate_tts_audio_multithreaded(
                    active_api_keys_info: list[dict], 
                    text_to_speak: str, 
                    voice_name: str,
                    output_file_path_base: str, 
                    log_callback_ui, 
                    progress_callback_ui_total, progress_callbacks_ui_thread: list,
                    reading_style_prompt: str = "",
                    temp_setting: float = 1.0, 
                    top_p_setting: float = 0.95,
                    max_words_per_part: int = 1000, 
                    max_tokens_fallback: int = 4800, 
                    max_retries_per_part: int = 1, 
                    part_timeout: int = 600
                    ):
    total_start_time = time.time()
    log_callback_ui(f"--- generate_tts_audio_multithreaded (v38.1) called ---")
    
    if not active_api_keys_info: log_callback_ui("No active API Keys provided."); return False, None
    norm_output_file_path_base = os.path.normpath(output_file_path_base)
    temp_audio_dir = os.path.normpath(os.path.join(os.path.dirname(norm_output_file_path_base), f"{os.path.basename(norm_output_file_path_base)}_parts_temp"))
    try:
        os.makedirs(temp_audio_dir, exist_ok=True)
        log_callback_ui(f"Created temp dir: {temp_audio_dir}")
    except Exception as e: log_callback_ui(f"Error creating temp dir: {e}"); return False, None

    try:
        genai.configure(api_key=active_api_keys_info[0]["key"])
        model_for_splitting = genai.GenerativeModel(model_name="models/gemini-2.5-pro-preview-tts")
        text_chunks = split_text_into_chunks(model_for_splitting, text_to_speak, max_words_per_part, max_tokens_fallback, log_callback_ui)
    except Exception as e:
        log_callback_ui(f"Failed during text splitting setup: {e}")
        return False, None
        
    if not text_chunks: log_callback_ui("Text could not be split."); return False, None

    total_chunks = len(text_chunks)
    job_queue = queue.Queue()
    for i, chunk in enumerate(text_chunks): job_queue.put((i, chunk))
    
    feedback_queue = queue.Queue()
    results_list = [None] * total_chunks
    part_times_list = [-1.0] * total_chunks
    
    num_worker_threads = len(active_api_keys_info)
    log_callback_ui(f"Initializing {num_worker_threads} worker threads with dynamic scaling...")
    
    threads = []
    for i in range(num_worker_threads):
        worker_thread = threading.Thread(
            target=_process_text_chunk_worker,
            args=(
                active_api_keys_info[i], job_queue, results_list, feedback_queue, i,
                reading_style_prompt, voice_name, temp_audio_dir, os.path.basename(norm_output_file_path_base),
                total_chunks, temp_setting, top_p_setting, max_retries_per_part, part_timeout, log_callback_ui,
                progress_callbacks_ui_thread[i] if i < len(progress_callbacks_ui_thread) else None,
                part_times_list, gemini_api_config_lock
            ),
            daemon=True
        )
        threads.append(worker_thread)
        worker_thread.start()
        log_callback_ui(f"Thread {i+1} started.")
        if i < num_worker_threads - 1:
            time.sleep(5)

    tasks_done_count = 0
    active_thread_count = num_worker_threads
    
    progress_callback_ui_total(0) # Bắt đầu ở 0%

    while tasks_done_count < total_chunks:
        try:
            feedback = feedback_queue.get(timeout=part_timeout + 30)
            
            if feedback["type"] == "TASK_DONE":
                tasks_done_count += 1
                progress_percent = int((tasks_done_count / total_chunks) * 100)
                progress_callback_ui_total(progress_percent)
            
            elif feedback["type"] == "RESOURCE_EXHAUSTED":
                active_thread_count -= 1
                log_callback_ui(f"MANAGER: Received ResourceExhausted signal. Active worker count reduced to: {active_thread_count}")
                if active_thread_count == 0:
                    log_callback_ui("MANAGER: All workers failed. Aborting.")
                    return False, None
            
            elif feedback["type"] == "FATAL_ERROR":
                 log_callback_ui(f"MANAGER: Worker reported fatal error. Aborting.")
                 return False, None
                 
        except queue.Empty:
            log_callback_ui(f"MANAGER: Timeout waiting for feedback. Process seems stuck. Aborting.")
            return False, None

    log_callback_ui("MANAGER: All tasks reported as done. Finalizing.")

    successful_parts = [res for res in results_list if res is not None]
    if len(successful_parts) != total_chunks:
        log_callback_ui("Error: Not all parts were generated successfully. Cannot merge.")
        return False, None

    log_callback_ui("All parts generated successfully. Starting merge process...")
    final_output_filename_with_ext = os.path.normpath(f"{output_file_path_base}.wav") 
    
    if merge_audio_files(results_list, final_output_filename_with_ext, "wav", log_callback_ui):
        total_time_taken = time.time() - total_start_time
        log_callback_ui(f"Successfully merged all parts into WAV. (Total time: {total_time_taken:.2f}s)")
        return True, final_output_filename_with_ext
    else:
        log_callback_ui("Error: Failed to merge audio parts.");
        return False, None
```

#### **`src/gemini_tts_app/main_app.py`**
```python
# src/gemini_tts_app/main_app.py
# Phiên bản: main_app_v18_advanced_preview <-- thực ra đây không phải là phiên bản 18 vì đã lâu bạn không còn ghi phiên bản. trước đó lâu hơn thì bạn đã ghi phiên bản thứ 21...
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import os
import sys
import platform
import subprocess
import datetime
import traceback
import re
import time
import logging

import json
try:
    import docx
except ImportError:
    docx = None
try:
    import pyperclip
except ImportError:
    pyperclip = None
# --- HOTFIX [2025-06-23]: Thêm import cho tính năng preview. Thêm các dòng này. ---
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageOps  
from .tts_logic import generate_tts_audio_multithreaded
from .settings_manager import save_settings, load_settings, NUM_API_KEYS
from .constants import (
    DEFAULT_VOICE, MIN_TEMPERATURE, MAX_TEMPERATURE,
    APP_NAME, APP_VERSION, PREDEFINED_READING_STYLES,
    GEMINI_TTS_VOICES_DETAILED, DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P, MIN_TOP_P, MAX_TOP_P,
    TITLE_CHAR_LIMIT_GOOD_MIN, TITLE_CHAR_LIMIT_GOOD_MAX, TITLE_CHAR_LIMIT_MAX,
    COLOR_OK, COLOR_WARN, COLOR_ERROR, COLOR_NORMAL
)
from .utils import get_resource_path
from .database import DatabaseManager

class TkinterLogHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_widget.configure(state='normal')
            self.text_widget.insert(tk.END, msg + '\n')
            self.text_widget.configure(state='disabled')
            self.text_widget.yview(tk.END)
        self.text_widget.after_idle(append)

class TTSApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("950x850")

        style = ttk.Style(self.root)
        style.layout("thin.Horizontal.TProgressbar",
                    [('thin.Horizontal.TProgressbar.trough',
                        {'children': [('thin.Horizontal.TProgressbar.pbar',
                                        {'side': 'left', 'sticky': 'ns'})],
                        'sticky': 'nswe'})])
        style.configure("thin.Horizontal.TProgressbar", thickness=4, background=COLOR_OK, troughcolor='#E0E0E0')

        self.db_manager = DatabaseManager()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.settings = load_settings()
        
        self.voice_display_list = [f"{v['name']} ({v['gender']}) - {v['description']}" for v in GEMINI_TTS_VOICES_DETAILED]
        self.voice_name_list = [v['name'] for v in GEMINI_TTS_VOICES_DETAILED]
        
        self.api_key_vars = [tk.StringVar(value=self.settings.get(f"api_key_{i+1}", "")) for i in range(NUM_API_KEYS)]
        self.api_label_vars = [tk.StringVar(value=self.settings.get(f"label_{i+1}", f"API Key {i+1}")) for i in range(NUM_API_KEYS)]
        self.selected_voice_name = tk.StringVar(value=self.settings.get("default_voice", DEFAULT_VOICE))
        self.selected_voice_display = tk.StringVar() 
        self.temperature_var = tk.DoubleVar(value=self.settings.get("temperature", DEFAULT_TEMPERATURE))
        self.top_p_var = tk.DoubleVar(value=self.settings.get("top_p", DEFAULT_TOP_P))
        self.words_per_chunk_var = tk.IntVar(value=self.settings.get("max_words_per_part", 1000))
        self.output_dir_var = tk.StringVar(value=self.settings.get("save_dir", os.path.expanduser("~")))
        self.story_name_var = tk.StringVar(value="MyStory")
        self.reading_style_prompt_var = tk.StringVar(value=PREDEFINED_READING_STYLES[0])
        self.last_saved_output_dir = None
        self.thread_status_labels = []
        self._full_options_text = []
        self.continuation_prompt_var = tk.StringVar()
        self.floating_panel = None
        self.clipboard_monitoring_thread = None
        self.is_monitoring_clipboard = False
        self.last_clipboard_content = ""
        # Biến cho cửa sổ preview
        self.preview_window = None 
        self.preview_canvas = None
        self.preview_bg_photo = None # Phải lưu tham chiếu đến ảnh
        self.preview_bg_path = None
        # Biến cho các tùy chỉnh preview
        self.preview_font_size = tk.IntVar(value=60)
        self.preview_font_color = tk.StringVar(value="white")
        self.preview_outline_color = tk.StringVar(value="black")
        self.preview_overlay_alpha = tk.IntVar(value=100) # 0-255
        self._set_window_icon()
        self.notebook = ttk.Notebook(root)
        
        self.main_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.main_tab, text="Text-to-Speech")
        self.create_main_tab_widgets()
        
        self.assistant_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.assistant_tab, text="Trợ Lý Biên Tập")
        self.create_assistant_tab_widgets()

        self.composer_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.composer_tab, text="Soạn Truyện Dài")
        self.create_composer_tab_widgets()

        self.settings_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.settings_tab, text="Settings")
        self.create_settings_tab_widgets()

        self.setup_ui_logging()
        self.update_voice_display(self.selected_voice_name.get())
        self.notebook.pack(expand=True, fill="both", padx=5, pady=5)
        self.update_word_count()

    
    def setup_ui_logging(self):
        """Tạo và thêm handler để hiển thị log trên giao diện."""
        tkinter_handler = TkinterLogHandler(self.log_area)
        # Định dạng cho log trên UI, đơn giản hơn
        formatter = logging.Formatter('%(message)s')
        tkinter_handler.setFormatter(formatter)
        tkinter_handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(tkinter_handler)
            
    # --- Phiên bản chính xác cho hàm create_composer_tab_widgets ---
    def create_composer_tab_widgets(self):
        """Thiết kế lại tab Soạn Truyện Dài để chứa nút mở panel."""
        frame = self.composer_tab
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        # Khung chính chứa ô văn bản và bộ đếm
        main_pane = ttk.LabelFrame(frame, text="Bản thảo truyện", padding=10)
        main_pane.grid(row=0, column=0, sticky="nsew")
        main_pane.rowconfigure(0, weight=1)
        main_pane.columnconfigure(0, weight=1)

        self.composer_text = scrolledtext.ScrolledText(main_pane, wrap=tk.WORD, height=15)
        self.composer_text.grid(row=0, column=0, sticky="nsew")
        self.composer_text.bind("<KeyRelease>", self.update_composer_counter)

        # 1. Giữ lại BỘ ĐẾM TỔNG: Nó hiển thị số từ/ký tự của toàn bộ bản thảo
        self.composer_counter_label = ttk.Label(main_pane, text="Tổng cộng: 0 ký tự | 0 từ")
        self.composer_counter_label.grid(row=1, column=0, sticky="w", pady=(5,0))

        # 2. Giữ lại NÚT MỞ PANEL: Đây là nút duy nhất để bạn kích hoạt bảng điều khiển
        self.toggle_panel_button = ttk.Button(frame, text="Mở Bảng điều khiển Viết truyện", command=self.toggle_composer_panel, style="Accent.TButton")
        self.toggle_panel_button.grid(row=1, column=0, pady=(10,0))
        
    def toggle_clipboard_monitoring(self):
        """Bật hoặc tắt chế độ theo dõi clipboard."""
        if self.is_monitoring_clipboard:
            # --- Dừng theo dõi ---
            self.is_monitoring_clipboard = False
            self.toggle_monitoring_button.config(text="Bắt đầu Theo dõi")
            self.log_message("Đã dừng theo dõi Clipboard.")
        else:
            # --- Bắt đầu theo dõi ---
            if pyperclip is None:
                messagebox.showerror("Thiếu thư viện", "Vui lòng cài đặt 'pyperclip' để sử dụng tính năng này.\nChạy lệnh: pip install pyperclip")
                return
            
            self.is_monitoring_clipboard = True
            # --- SỬA LỖI: Reset last_clipboard_content để luôn bắt được lần copy đầu tiên ---
            self.last_clipboard_content = ""
            self.toggle_monitoring_button.config(text="Dừng Theo dõi")
            self.log_message("Bắt đầu theo dõi Clipboard...")

            self.clipboard_monitoring_thread = threading.Thread(target=self._clipboard_monitor_loop, daemon=True)
            self.clipboard_monitoring_thread.start()
                
    def _clipboard_monitor_loop(self):
        """Vòng lặp chạy ngầm để kiểm tra clipboard và áp dụng bộ lọc."""
        while self.is_monitoring_clipboard:
            try:
                current_content = pyperclip.paste()
                if current_content and current_content != self.last_clipboard_content:
                    # Ghi nhận nội dung mới để không xử lý lại
                    self.last_clipboard_content = current_content
                    
                    # --- ÁP DỤNG BỘ LỌC THÔNG MINH ---
                    if self._is_valid_story_chunk(current_content):
                        # Lên lịch thực hiện việc nối văn bản trên luồng chính
                        self.root.after_idle(self.paste_and_append_story, current_content)

            except Exception as e:
                logging.warning(f"Lỗi trong vòng lặp theo dõi clipboard: {e}")

            time.sleep(1)
            
    def toggle_composer_panel(self):
        """Mở hoặc đóng panel điều khiển."""
        if self.floating_panel and self.floating_panel.winfo_exists():
            self.floating_panel.destroy()
            self.floating_panel = None
            self.root.deiconify() # Khôi phục cửa sổ chính
            self.toggle_panel_button.config(text="Mở Bảng điều khiển Viết truyện")
        else:
            self.create_floating_panel()
            self.root.iconify() # Thu nhỏ cửa sổ chính
            self.toggle_panel_button.config(text="Đóng Bảng điều khiển")

    # --- HOTFIX [2025-06-18]: Cập nhật đúng nút bấm trên Panel điều khiển. Thay thế toàn bộ hàm này. ---
    def create_floating_panel(self):
        """Tạo ra panel nổi để điều khiển việc soạn truyện."""
        if self.floating_panel and self.floating_panel.winfo_exists():
            self.floating_panel.lift()
            return
            
        self.floating_panel = tk.Toplevel(self.root)
        self.floating_panel.title("Bảng điều khiển")
        self.floating_panel.geometry("450x180")
        
        # Giữ panel luôn nổi trên cùng
        self.floating_panel.attributes("-topmost", True)
        
        # Khi panel này đóng, hãy gọi hàm toggle để khôi phục cửa sổ chính
        self.floating_panel.protocol("WM_DELETE_WINDOW", self.toggle_composer_panel)

        panel_frame = ttk.Frame(self.floating_panel, padding=10)
        panel_frame.pack(expand=True, fill="both")
        panel_frame.columnconfigure(0, weight=1)

        # --- THAY ĐỔI TẠI ĐÂY ---
        # Các nút điều khiển
        button_frame = ttk.Frame(panel_frame)
        button_frame.grid(row=0, column=0, columnspan=2, pady=(0,10), sticky="ew")
        
        # Thay thế nút "Dán & Nối" bằng nút "Bắt đầu/Dừng Theo dõi"
        self.toggle_monitoring_button = ttk.Button(button_frame, text="Bắt đầu Theo dõi Clipboard", command=self.toggle_clipboard_monitoring)
        self.toggle_monitoring_button.pack(side="left", padx=(0,5))
        
        self.save_story_button = ttk.Button(button_frame, text="Lưu .txt...", command=self.save_story_to_file)
        self.save_story_button.pack(side="left")
        # --- KẾT THÚC THAY ĐỔI ---

        # Khu vực Prompt Gợi ý
        prompt_suggestion_frame = ttk.LabelFrame(panel_frame, text="Gợi ý Prompt tiếp theo", padding=10)
        prompt_suggestion_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10,0))
        prompt_suggestion_frame.columnconfigure(0, weight=1)

        self.continuation_prompt_entry = ttk.Entry(prompt_suggestion_frame, textvariable=self.continuation_prompt_var, state="readonly")
        self.continuation_prompt_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        self.copy_prompt_button = ttk.Button(prompt_suggestion_frame, text="Copy Prompt", command=self.copy_continuation_prompt)
        self.copy_prompt_button.grid(row=0, column=1, sticky="e")
        
    def update_composer_counter(self, event=None):
        """Đếm và cập nhật số liệu cho bản thảo."""
        content = self.composer_text.get("1.0", tk.END).strip()
        char_count = len(content)
        word_count = len(content.split()) if content else 0
        self.composer_counter_label.config(text=f"Tổng cộng: {char_count:,} ký tự | {word_count:,} từ")

    def paste_and_append_story(self, content_to_paste):
        """Hàm này giờ chỉ làm nhiệm vụ nối văn bản đã được xác thực."""
        try:
            # Không cần kiểm tra pyperclip ở đây nữa vì content đã được truyền vào
            if not content_to_paste: return
            
            # Kiểm tra trùng lặp lần cuối
            current_manuscript = self.composer_text.get("1.0", tk.END)
            if content_to_paste in current_manuscript:
                self.log_message("Phát hiện nội dung trùng lặp, đã bỏ qua.")
                return

            separator = "\n\n" if current_manuscript.strip() else ""
            self.composer_text.insert(tk.END, separator + content_to_paste)
            self.composer_text.yview(tk.END)
            self.update_composer_counter()
            self.log_message("Đã tự động nối nội dung hợp lệ từ clipboard.")

            new_chunk_word_count = len(content_to_paste.split())
            
            end_phrase = "Xin chân thành cảm ơn và hẹn gặp lại quý vị!"
            if end_phrase in content_to_paste:
                continuation_prompt = f"(Bạn đã viết được {new_chunk_word_count} từ cho đoạn trên. Tổng kết.)"
                self.continuation_prompt_var.set(continuation_prompt)
                self.log_message("Đã phát hiện đoạn kết truyện! Tự động dừng theo dõi.")
                if self.is_monitoring_clipboard:
                    self.toggle_clipboard_monitoring()
            else:
                continuation_prompt = f"(Đã nhận được {new_chunk_word_count} từ. Vui lòng viết tiếp phần sau của câu chuyện.)"
                self.continuation_prompt_var.set(continuation_prompt)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xử lý nội dung: {e}")
            self.log_message(f"Lỗi khi dán và nối: {e}")
            
    def copy_continuation_prompt(self):
        """Sao chép prompt gợi ý vào clipboard."""
        if pyperclip is None:
            messagebox.showerror("Thiếu thư viện", "Vui lòng cài đặt 'pyperclip'.")
            return
        
        prompt_text = self.continuation_prompt_var.get()
        if prompt_text:
            pyperclip.copy(prompt_text)
            self.log_message(f"Đã copy prompt: '{prompt_text}'")
            
            # Tạm thời đổi text của nút để xác nhận
            original_text = self.copy_prompt_button.cget("text")
            self.copy_prompt_button.config(text="Đã copy!")
            self.root.after(2000, lambda: self.copy_prompt_button.config(text=original_text))
        else:
            self.log_message("Không có prompt gợi ý để copy.")
            
    def save_story_to_file(self):
        """Lưu toàn bộ nội dung bản thảo ra file .txt."""
        content = self.composer_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Nội dung trống", "Không có nội dung để lưu.", parent=self.composer_tab)
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Lưu bản thảo truyện",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo("Thành công", f"Đã lưu bản thảo thành công tại:\n{file_path}", parent=self.composer_tab)
            self.log_message(f"Đã lưu bản thảo ra file: {file_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu file: {e}", parent=self.composer_tab)
            self.log_message(f"Lỗi khi lưu bản thảo: {e}")
                                  
    def on_closing(self):
        self.is_monitoring_clipboard = False
        if self.clipboard_monitoring_thread and self.clipboard_monitoring_thread.is_alive():
            self.clipboard_monitoring_thread.join(timeout=1.1)
        if self.db_manager:
            self.db_manager.close()
        if self.floating_panel and self.floating_panel.winfo_exists():
            self.floating_panel.destroy()
        self.root.destroy()
    # --- Hàm mới để kiểm tra nội dung clipboard ---
    def _is_valid_story_chunk(self, text: str) -> bool:
        """
        Bộ lọc thông minh để kiểm tra xem text có phải là một đoạn truyện hợp lệ không.
        """
        if not text:
            return False

        # Quy tắc 1: Kiểm tra số lượng từ
        word_count = len(text.split())
        if not (500 <= word_count <= 2500):
            self.log_message(f"Nội dung bị bỏ qua: số từ ({word_count}) không nằm trong khoảng 500-2500.")
            return False

        # Quy tắc 2: Kiểm tra từ khóa code
        code_keywords = ["import ", "def ", "class ", "from .", "const ", "let ", "var "]
        stripped_text = text.strip()
        if any(stripped_text.startswith(kw) for kw in code_keywords):
            self.log_message("Nội dung bị bỏ qua: phát hiện từ khóa code.")
            return False
            
        # Nếu vượt qua tất cả các bộ lọc
        return True
    
    def create_assistant_tab_widgets(self):
        frame = self.assistant_tab
        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        top_frame = ttk.Frame(frame)
        top_frame.grid(row=0, column=0, sticky="nsew")
        top_frame.rowconfigure(0, weight=1)
        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=1)

        input_pane = ttk.LabelFrame(top_frame, text="1. Dán toàn bộ phản hồi của Gemini tại đây", padding=10)
        input_pane.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        input_pane.rowconfigure(0, weight=1)
        input_pane.columnconfigure(0, weight=1)
        self.assistant_input_text = scrolledtext.ScrolledText(input_pane, wrap=tk.WORD, height=10)
        self.assistant_input_text.grid(row=0, column=0, sticky="nsew")
        self.parse_button = ttk.Button(input_pane, text="Bóc Tách & Phân Tích", command=self.parse_input_text)
        self.parse_button.grid(row=1, column=0, sticky="ew", pady=(10, 0))

        list_pane = ttk.LabelFrame(top_frame, text="2. Các lựa chọn đã được xử lý (Nhấp để chọn)", padding=10)
        list_pane.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        list_pane.rowconfigure(0, weight=1)
        list_pane.columnconfigure(0, weight=1)
        self.options_display_text = scrolledtext.ScrolledText(list_pane, wrap=tk.WORD, height=10)
        self.options_display_text.grid(row=0, column=0, sticky="nsew")
        self.options_display_text.tag_configure("highlight", background="lightblue")
        self.options_display_text.config(state=tk.DISABLED)
        
        bottom_frame = ttk.LabelFrame(frame, text="3. Soạn thảo & Chốt phương án", padding=10)
        bottom_frame.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        bottom_frame.rowconfigure(1, weight=1)
        bottom_frame.columnconfigure(0, weight=1)
        
        mode_frame = ttk.Frame(bottom_frame)
        mode_frame.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        self.assistant_mode = tk.StringVar(value="title")
        ttk.Label(mode_frame, text="Chế độ:").pack(side="left")
        ttk.Radiobutton(mode_frame, text="Tiêu đề", variable=self.assistant_mode, value="title", command=self.on_mode_change).pack(side="left", padx=5)
        ttk.Radiobutton(mode_frame, text="Thumbnail", variable=self.assistant_mode, value="thumbnail", command=self.on_mode_change).pack(side="left", padx=5)

        self.editor_text = scrolledtext.ScrolledText(bottom_frame, wrap=tk.WORD, height=5)
        self.editor_text.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.editor_text.bind("<KeyRelease>", self.update_editor_metrics)

        action_frame = ttk.Frame(bottom_frame)
        action_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        action_frame.columnconfigure(0, weight=1)

        self.counter_label = ttk.Label(action_frame, text="Ký tự: 0 | Từ: 0", font=("Segoe UI", 10))
        self.counter_label.grid(row=0, column=0, sticky="w", padx=5)
        # --- THÊM NÚT MỚI VÀO ĐÂY ---
        self.preview_button = ttk.Button(action_frame, text="Xem trước Thumbnail", command=self.show_thumbnail_preview)
        self.preview_button.grid(row=0, column=1, sticky="e", padx=5)
        # ---

        self.save_button = ttk.Button(action_frame, text="Chốt & Lưu", state=tk.DISABLED, command=self.save_final_version, style="Accent.TButton")
        self.save_button.grid(row=0, column=2, sticky="e", padx=5)

    def _parse_titles(self, text):
        cleaned_options = []
        # Chiến lược: Tìm tất cả các khối bắt đầu bằng header
        pattern = re.compile(r'(#### \*\*Lựa chọn \d+[\s\S]*?)(?=#### \*\*Lựa chọn \d+|\Z)')
        blocks = pattern.findall(text)
        
        for block in blocks:
            content = ""
            lines = [line.strip() for line in block.strip().split('\n') if line.strip()]
            if not lines: continue

            header_line = lines[0]
            
            # Kịch bản 1: Tiêu đề trên cùng dòng (nằm sau dấu :)
            if ":" in header_line:
                possible_title = header_line.split(":", 1)[1].strip()
                # Loại bỏ phần mô tả trong ngoặc đơn nếu có
                possible_title = re.sub(r'\s*\(.*?\)', '', possible_title).strip()
                if len(possible_title) > 20: 
                    content = possible_title
            
            # Kịch bản 2: Nếu không tìm thấy, tìm ở dòng tiếp theo
            if not content and len(lines) > 1:
                # Dòng tiếp theo không phải là dòng metadata
                if not lines[1].startswith('*'):
                    content = lines[1]
            
            if content:
                # Làm sạch cuối cùng
                cleaned_options.append(content.replace('**', '').replace('`', '').strip())
                    
        return cleaned_options

    # --- HOTFIX [2025-06-19]: Viết lại hoàn toàn logic bóc tách thumbnail cho chính xác và ổn định. Thay thế toàn bộ hàm này. ---
    def _parse_thumbnails(self, text):
        """
        Sử dụng một pattern Regex duy nhất và mạnh mẽ để tìm tất cả các kịch bản thumbnail
        và sau đó làm sạch chúng.
        """
        # Pattern tìm tất cả nội dung nằm sau "KỊCH BẢN THUMBNAIL:" và dừng lại trước Lựa chọn tiếp theo, ###, hoặc cuối văn bản.
        pattern = re.compile(r'KỊCH BẢN THUMBNAIL:([\s\S]+?)(?=Lựa chọn \d+|###|\Z)', re.IGNORECASE)
        raw_options = pattern.findall(text)
        
        cleaned_options = []
        for raw_content in raw_options:
            # Quy trình làm sạch chuyên sâu
            lines = [line.strip() for line in raw_content.strip().split('\n')]
            
            # Loại bỏ các dòng metadata và các ký tự thừa
            valid_lines = [
                line.replace('**', '').strip() 
                for line in lines 
                if line.strip() and '---' not in line and not line.strip().startswith(('*', '#'))
            ]
            
            if valid_lines:
                cleaned_options.append("\n".join(valid_lines))
                
        return cleaned_options

    def parse_input_text(self):
        self.options_display_text.config(state=tk.NORMAL)
        self.options_display_text.delete("1.0", tk.END)
        
        self.editor_text.delete("1.0", tk.END)
        self.update_editor_metrics(None)
        
        full_text = self.assistant_input_text.get("1.0", tk.END)
        if not full_text.strip():
            messagebox.showwarning("Thông báo", "Vùng nhập liệu đang trống.", parent=self.assistant_tab)
            return

        is_thumbnail_mode = "KỊCH BẢN THUMBNAIL" in full_text.upper() or "PHONG CÁCH:" in full_text.upper()
        current_mode = "thumbnail" if is_thumbnail_mode else "title"
        self.assistant_mode.set(current_mode)
        
        cleaned_options = self._parse_thumbnails(full_text) if current_mode == "thumbnail" else self._parse_titles(full_text)

        if not cleaned_options:
            messagebox.showinfo("Không tìm thấy", "Không thể bóc tách được lựa chọn nào.", parent=self.assistant_tab)
            self.options_display_text.config(state=tk.DISABLED)
            return

        self._full_options_text = cleaned_options
        self.display_parsed_options(cleaned_options, current_mode)
            
        messagebox.showinfo("Hoàn tất", f"Đã bóc tách {len(cleaned_options)} lựa chọn theo chế độ '{current_mode}'.", parent=self.assistant_tab)
        self.on_mode_change()
        
    def display_parsed_options(self, options, mode):
        self.options_display_text.config(state=tk.NORMAL)
        self.options_display_text.delete("1.0", tk.END)

        for tag in self.options_display_text.tag_names():
            if tag.startswith("option_"):
                self.options_display_text.tag_delete(tag)

        separator = "\n" + ("-" * 60) + "\n\n"

        for i, option_text in enumerate(options):
            tag_name = f"option_{i}"
            start_index = self.options_display_text.index(tk.END)
            
            prefix = "(Thumbnail)" if mode == "thumbnail" else "(Tiêu đề)"
            display_header = f"--- LỰA CHỌN {i+1} {prefix} ---\n"
            self.options_display_text.insert(tk.END, display_header, ("h2", "center"))
            self.options_display_text.insert(tk.END, option_text)
            
            end_index = self.options_display_text.index(tk.END)
            
            self.options_display_text.tag_add(tag_name, start_index, f"{end_index}-1c")
            self.options_display_text.tag_bind(tag_name, "<Button-1>", lambda e, index=i: self.on_text_option_clicked(e, index))
            
            if i < len(options) - 1:
                self.options_display_text.insert(tk.END, separator, ("separator", "center"))

        self.options_display_text.config(state=tk.DISABLED)

    def on_text_option_clicked(self, event, index):
        for tag in self.options_display_text.tag_names():
            if tag.startswith("option_"):
                self.options_display_text.tag_configure(tag, background="white")
        
        tag_name = f"option_{index}"
        self.options_display_text.tag_configure(tag_name, background="lightblue")

        if hasattr(self, '_full_options_text') and 0 <= index < len(self._full_options_text):
            full_text = self._full_options_text[index]
            self.editor_text.delete("1.0", tk.END)
            self.editor_text.insert("1.0", full_text)
            self.update_editor_metrics(None)
            
    def on_option_selected(self, event):
        # Hàm này không còn được sử dụng với ScrolledText, nhưng giữ lại để không gây lỗi nếu có binding sót
        pass
    def on_mode_change(self):
        self.update_editor_metrics(None)
        
    def update_editor_metrics(self, event):
        content = self.editor_text.get("1.0", tk.END).strip()
        char_count = len(content)
        word_count = len(content.split()) if content else 0
        line_count = len([line for line in content.splitlines() if line.strip()])

        mode = self.assistant_mode.get()
        label_text, label_color, button_state = "", COLOR_NORMAL, tk.DISABLED

        if mode == "title":
            label_text = f"Ký tự: {char_count} | Từ: {word_count}"
            if char_count == 0: pass
            elif TITLE_CHAR_LIMIT_GOOD_MIN <= char_count <= TITLE_CHAR_LIMIT_GOOD_MAX:
                label_color, button_state = COLOR_OK, tk.NORMAL
            elif char_count > TITLE_CHAR_LIMIT_MAX:
                label_color = COLOR_ERROR
            else:
                label_color = COLOR_WARN
        elif mode == "thumbnail":
            label_text = f"Ký tự: {char_count} | Từ: {word_count} | Dòng: {line_count}"
            if char_count > 0:
                label_color, button_state = COLOR_OK, tk.NORMAL

        self.counter_label.config(text=label_text, foreground=label_color)
        self.save_button.config(state=button_state)
    
    # --- HOTFIX [2025-06-18 09:40]: Thêm logic lưu trữ vào CSDL cho nút "Chốt & Lưu". Thay thế toàn bộ hàm này. ---
    def save_final_version(self):
        final_text = self.editor_text.get("1.0", tk.END).strip()
        if not final_text:
            messagebox.showwarning("Nội dung trống", "Không có nội dung để lưu.", parent=self.assistant_tab)
            return

        mode = self.assistant_mode.get()
        char_count = len(final_text)
        word_count = len(final_text.split())
        line_count = len(final_text.splitlines())
        
        success = False
        if mode == "title":
            success = self.db_manager.add_final_title(final_text, char_count, word_count)
        elif mode == "thumbnail":
            success = self.db_manager.add_final_thumbnail(final_text, char_count, word_count, line_count)

        if success:
            messagebox.showinfo("Thành công", f"Đã lưu phương án '{mode}' thành công!", parent=self.assistant_tab)
            self.editor_text.delete("1.0", tk.END)
            self.update_editor_metrics(None)
        else:
            messagebox.showerror("Thất bại", "Lỗi khi lưu vào cơ sở dữ liệu.", parent=self.assistant_tab)
    
    # --- HOTFIX [2025-06-23]: Nâng cấp tính năng Xem trước Thumbnail (Giai đoạn 1). Thay thế/thêm các hàm này. ---
    def update_editor_metrics(self, event):
        """Sửa lỗi đếm dòng và cập nhật các chỉ số."""
        content = self.editor_text.get("1.0", tk.END)
        # Đếm ký tự bao gồm cả ký tự xuống dòng nhưng trừ ký tự cuối cùng do ScrolledText tự thêm vào
        char_count = len(content) - 1 if len(content) > 0 else 0
        # Đếm từ
        word_count = len(content.strip().split()) if content.strip() else 0
        # Đếm số dòng có nội dung
        line_count = len([line for line in content.strip().splitlines() if line.strip()])

        mode = self.assistant_mode.get()
        label_text, label_color, button_state = "", COLOR_NORMAL, tk.DISABLED

        if mode == "title":
            # Logic cho title không đổi
            label_text = f"Ký tự: {char_count} | Từ: {word_count}"
            if char_count == 0: pass
            elif TITLE_CHAR_LIMIT_GOOD_MIN <= char_count <= TITLE_CHAR_LIMIT_GOOD_MAX:
                label_color, button_state = COLOR_OK, tk.NORMAL
            elif char_count > TITLE_CHAR_LIMIT_MAX:
                label_color = COLOR_ERROR
            else:
                label_color = COLOR_WARN
        elif mode == "thumbnail":
            # Cập nhật để hiển thị đúng số dòng
            label_text = f"Ký tự: {char_count} | Từ: {word_count} | Dòng: {line_count}"
            if char_count > 0:
                label_color, button_state = COLOR_OK, tk.NORMAL

        self.counter_label.config(text=label_text, foreground=label_color)
        self.save_button.config(state=button_state)

    def show_thumbnail_preview(self):
        if self.preview_window and self.preview_window.winfo_exists():
            self.preview_window.lift()
            return
        
        text_content = self.editor_text.get("1.0", tk.END).strip()
        if not text_content:
            messagebox.showwarning("Nội dung trống", "Không có nội dung để xem trước.", parent=self.assistant_tab)
            return

        self.preview_window = tk.Toplevel(self.root)
        self.preview_window.title("Xem trước Thumbnail")
        self.preview_window.geometry("854x580") # Chiều cao tăng để chứa thanh điều khiển
        self.preview_window.minsize(427, 320)

        # --- KHUNG ĐIỀU KHIỂN ---
        control_frame = ttk.Frame(self.preview_window, padding=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        ttk.Button(control_frame, text="Chọn ảnh nền...", command=self._select_background_image).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(control_frame, text="Độ mờ lớp phủ:").pack(side=tk.LEFT, padx=5)
        ttk.Scale(control_frame, from_=0, to=255, variable=self.preview_overlay_alpha, command=lambda e: self._redraw_thumbnail_canvas()).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        ttk.Button(control_frame, text="Xuất ảnh PNG...", command=self._export_thumbnail, style="Accent.TButton").pack(side=tk.RIGHT, padx=5)

        # --- CANVAS XEM TRƯỚC ---
        canvas_container = ttk.Frame(self.preview_window)
        canvas_container.pack(expand=True, fill="both")
        self.preview_canvas = tk.Canvas(canvas_container, bg="#1c1c1c", highlightthickness=0)
        self.preview_canvas.pack(expand=True, fill="both")

        self.preview_window.bind("<Configure>", self._on_preview_resize)
        self.preview_window.update_idletasks()
        self._redraw_thumbnail_canvas()

        self.preview_window.transient(self.root)
        self.preview_window.grab_set()
        self.root.wait_window(self.preview_window)
        
    def _on_preview_resize(self, event=None):
        # Đợi một chút để window ổn định kích thước rồi mới vẽ lại
        if hasattr(self, '_resize_job'):
            self.preview_window.after_cancel(self._resize_job)
        self._resize_job = self.preview_window.after(300, self._redraw_thumbnail_canvas)

        
    def _select_background_image(self):
        file_path = filedialog.askopenfilename(title="Chọn ảnh nền", filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if file_path:
            self.preview_bg_path = file_path
            self._redraw_thumbnail_canvas()
    
    def _redraw_thumbnail_canvas(self):
        if not (self.preview_window and self.preview_window.winfo_exists()): return
        canvas = self.preview_canvas
        canvas.delete("all")
        
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        if canvas_width < 10 or canvas_height < 10: return

        # 1. Tạo ảnh nền
        try:
            if self.preview_bg_path:
                bg_image = Image.open(self.preview_bg_path).convert("RGBA")
            else: # Tạo background mặc định nếu không có ảnh
                bg_image = Image.new('RGBA', (1280, 720), (80, 80, 80, 255))
        except Exception as e:
            canvas.create_text(10, 10, text=f"Lỗi ảnh: {e}", fill="red", anchor=tk.NW)
            return

        # 2. Resize và crop ảnh nền để vừa khít canvas 16:9
        bg_image = ImageOps.fit(bg_image, (canvas_width, canvas_height), Image.Resampling.LANCZOS)
        
        # 3. Thêm lớp phủ tối
        alpha = self.preview_overlay_alpha.get()
        if alpha > 0:
            overlay = Image.new('RGBA', bg_image.size, (0, 0, 0, alpha))
            bg_image = Image.alpha_composite(bg_image, overlay)
        
        self.preview_bg_photo = ImageTk.PhotoImage(bg_image)
        canvas.create_image(0, 0, anchor=tk.NW, image=self.preview_bg_photo)

        # 4. Vẽ Text
        text_content = self.editor_text.get("1.0", tk.END).strip()
        font_size = int(canvas_width / 16) # Cỡ chữ co giãn
        try:
            font_tuple = ("Impact", font_size, "normal")
            # Dùng Pillow để tính toán kích thước text chính xác
            pillow_font = ImageFont.truetype("impact.ttf", font_size)
        except IOError:
            font_tuple = ("Arial Black", font_size, "bold")
            pillow_font = ImageFont.truetype("arialbd.ttf", font_size)

        temp_draw = ImageDraw.Draw(Image.new("RGB", (1,1)))
        # Sử dụng textbbox để lấy kích thước chính xác của khối text nhiều dòng
        text_box = temp_draw.multiline_textbbox((0,0), text_content, font=pillow_font, align="center")
        text_width = text_box[2] - text_box[0]
        text_height = text_box[3] - text_box[1]

        # Căn giữa toàn bộ khối text
        x = canvas_width / 2
        y = (canvas_height - text_height) / 2

        outline_color = "black"
        offset = max(2, int(font_size / 25)) # Viền dày hơn một chút
        
        # Vẽ viền
        canvas.create_text(x, y, text=text_content, font=font_tuple, fill=outline_color, justify=tk.CENTER, anchor=tk.N, width=canvas_width * 0.9)
        # Vẽ text chính
        canvas.create_text(x, y, text=text_content, font=font_tuple, fill="white", justify=tk.CENTER, anchor=tk.N, width=canvas_width * 0.9)
    
    def _export_thumbnail(self):
        try:
            bg_image = None
            # 1. Tạo lại ảnh nền và lớp phủ bằng Pillow
            if self.preview_bg_path:
                bg_image = Image.open(self.preview_bg_path).convert("RGBA")
            else:
                bg_image = Image.new('RGBA', (1280, 720), (80, 80, 80, 255))

            bg_image = ImageOps.fit(bg_image, (1280, 720), Image.Resampling.LANCZOS)
            alpha = self.preview_overlay_alpha.get()
            if alpha > 0:
                overlay = Image.new('RGBA', bg_image.size, (0, 0, 0, alpha))
                bg_image = Image.alpha_composite(bg_image, overlay)

            # 2. Chuẩn bị để vẽ text
            draw = ImageDraw.Draw(bg_image)
            text_content = self.editor_text.get("1.0", tk.END).strip()
            font_size = int(1280 / 16) # Cỡ chữ cho file export chất lượng cao
            try:
                font = ImageFont.truetype("impact.ttf", font_size)
            except IOError:
                font = ImageFont.truetype("arialbd.ttf", font_size)

            # 3. Tính toán vị trí và vẽ
            text_bbox = draw.multiline_textbbox((0,0), text_content, font=font, align="center")
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            x = (1280 - text_width) / 2
            y = (720 - text_height) / 2
            
            outline_color = "black"
            main_color = "white"
            offset = max(3, int(font_size / 25))

            # Vẽ viền
            for dx in range(-offset, offset+1, offset):
                for dy in range(-offset, offset+1, offset):
                    if dx != 0 or dy != 0:
                        draw.multiline_text((x+dx, y+dy), text_content, font=font, fill=outline_color, align="center")
            # Vẽ text chính
            draw.multiline_text((x, y), text_content, font=font, fill=main_color, align="center")

            # 4. Mở dialog và lưu file
            file_path = filedialog.asksaveasfilename(title="Xuất ảnh Thumbnail", defaultextension=".png", filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg")])
            if file_path:
                bg_image.convert("RGB").save(file_path, quality=95)
                messagebox.showinfo("Thành công", f"Đã xuất ảnh thumbnail thành công tại:\n{file_path}", parent=self.preview_window)
                self.log_message(f"Đã xuất thumbnail: {file_path}")

        except Exception as e:
            messagebox.showerror("Lỗi xuất ảnh", f"Đã có lỗi xảy ra: {e}", parent=self.preview_window)
                
    # --- Các hàm của các tab khác (giữ nguyên, không tóm tắt) ---
    def _set_window_icon(self):
        try:
            if sys.platform.startswith('win'):
                icon_path = get_resource_path("icons/app_icon.ico")
                if os.path.exists(icon_path): self.root.iconbitmap(icon_path)
            else:
                icon_path_png = get_resource_path("icons/app_icon.png")
                if os.path.exists(icon_path_png):
                    photo = tk.PhotoImage(file=icon_path_png)
                    self.root.iconphoto(False, photo)
        except Exception as e:
            self.log_message(f"Error setting window icon: {e}")

    # --- KHÔI PHỤC CÁC HÀM ---
    def create_main_tab_widgets(self):
        frame = self.main_tab
        frame.rowconfigure(0, weight=3); frame.rowconfigure(1, weight=0); frame.rowconfigure(2, weight=0); 
        frame.rowconfigure(3, weight=0); frame.rowconfigure(4, weight=0); frame.rowconfigure(5, weight=3)
        frame.columnconfigure(0, weight=1)

        input_text_frame = ttk.LabelFrame(frame, text="Input Text", padding="10")
        input_text_frame.grid(row=0, column=0, sticky="ewns", padx=5, pady=5)
        input_text_frame.rowconfigure(0, weight=1); input_text_frame.columnconfigure(0, weight=1)
        self.main_text_input = scrolledtext.ScrolledText(input_text_frame, wrap=tk.WORD, height=10)
        self.main_text_input.grid(row=0, column=0, sticky="nsew")
        self.main_text_input.bind("<KeyRelease>", self.update_word_count)
        
        count_frame = ttk.Frame(input_text_frame)
        count_frame.grid(row=1, column=0, sticky="ew", pady=(5,0), padx=5)
        self.main_word_count_label = ttk.Label(count_frame, text="Ký tự: 0 | Từ: 0 | Dự kiến chunks: 0")
        self.main_word_count_label.pack(side="left")
        self.import_button = ttk.Button(count_frame, text="Import từ File...", command=self.import_text_from_file)
        self.import_button.pack(side="right")

        reading_style_frame = ttk.LabelFrame(frame, text="Reading Style Prompt (Select or Type Custom)", padding="10")
        reading_style_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.reading_style_combobox = ttk.Combobox(reading_style_frame, textvariable=self.reading_style_prompt_var, values=PREDEFINED_READING_STYLES, height=10)
        self.reading_style_combobox.pack(fill="x", expand=True, padx=5, pady=5)

        settings_container_frame = ttk.Frame(frame)
        settings_container_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        settings_container_frame.columnconfigure(0, weight=1); settings_container_frame.columnconfigure(1, weight=1)

        gen_settings_frame = ttk.LabelFrame(settings_container_frame, text="Generation Settings", padding="10")
        gen_settings_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        gen_settings_frame.columnconfigure(1, weight=1)
        
        ttk.Label(gen_settings_frame, text="Select Voice:").grid(row=0, column=0, sticky="w", pady=2)
        self.voice_dropdown = ttk.Combobox(gen_settings_frame, textvariable=self.selected_voice_display, values=self.voice_display_list, state="readonly")
        self.voice_dropdown.grid(row=0, column=1, columnspan=2, sticky="ew", pady=2)
        self.voice_dropdown.bind('<<ComboboxSelected>>', self.on_voice_selected)

        ttk.Label(gen_settings_frame, text="Temperature:").grid(row=1, column=0, sticky="w", pady=2)
        self.temp_scale = ttk.Scale(gen_settings_frame, from_=MIN_TEMPERATURE, to=MAX_TEMPERATURE, variable=self.temperature_var, orient=tk.HORIZONTAL, command=lambda v: self.temp_scale_val_label.config(text=f"{float(v):.2f}"))
        self.temp_scale.grid(row=1, column=1, sticky="ew", pady=2)
        self.temp_scale_val_label = ttk.Label(gen_settings_frame, text=f"{self.temperature_var.get():.2f}", width=4)
        self.temp_scale_val_label.grid(row=1, column=2, sticky="w", padx=(5,0))
        
        ttk.Label(gen_settings_frame, text="Top P:").grid(row=2, column=0, sticky="w", pady=2)
        self.top_p_scale = ttk.Scale(gen_settings_frame, from_=MIN_TOP_P, to=MAX_TOP_P, variable=self.top_p_var, orient=tk.HORIZONTAL, command=lambda v: self.top_p_scale_val_label.config(text=f"{float(v):.2f}"))
        self.top_p_scale.grid(row=2, column=1, sticky="ew", pady=2)
        self.top_p_scale_val_label = ttk.Label(gen_settings_frame, text=f"{self.top_p_var.get():.2f}", width=4)
        self.top_p_scale_val_label.grid(row=2, column=2, sticky="w", padx=(5,0))
        
        ttk.Label(gen_settings_frame, text="Ghi chú: Giữ Temp ở mức 1.0 để có kết quả ổn định nhất.", style="secondary.TLabel").grid(row=3, column=1, columnspan=2, padx=5, pady=(5, 0), sticky="w")
        
        output_settings_frame = ttk.LabelFrame(settings_container_frame, text="Output File Settings", padding="10")
        output_settings_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        output_settings_frame.columnconfigure(1, weight=1)
        
        ttk.Label(output_settings_frame, text="Output Directory:").grid(row=0, column=0, sticky="w", pady=2)
        self.output_dir_entry = ttk.Entry(output_settings_frame, textvariable=self.output_dir_var)
        self.output_dir_entry.grid(row=0, column=1, sticky="ew", pady=2)
        ttk.Button(output_settings_frame, text="Browse...", command=self.browse_main_output_directory).grid(row=0, column=2, padx=(5,0))

        ttk.Label(output_settings_frame, text="Story/Base Name:").grid(row=1, column=0, sticky="w", pady=2)
        self.story_name_entry = ttk.Entry(output_settings_frame, textvariable=self.story_name_var)
        self.story_name_entry.grid(row=1, column=1, columnspan=2, sticky="ew", pady=2)
        
        action_buttons_frame = ttk.Frame(frame, padding="5")
        action_buttons_frame.grid(row=3, column=0, pady=(10,0), sticky="ew", padx=5)
        self.generate_button = ttk.Button(action_buttons_frame, text="Generate Voice", command=self.start_tts_thread, style="Accent.TButton")
        self.generate_button.pack(side="left", padx=5)
        self.open_folder_button = ttk.Button(action_buttons_frame, text="Open Output Folder", command=self.open_last_output_folder, state="disabled")
        self.open_folder_button.pack(side="left", padx=5)

        progress_frame = ttk.LabelFrame(frame, text="Progress", padding="10")
        progress_frame.grid(row=4, column=0, sticky="ewns", padx=5, pady=5)
        progress_frame.columnconfigure(1, weight=1) 
        overall_progress_subframe = ttk.Frame(progress_frame)
        overall_progress_subframe.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        overall_progress_subframe.columnconfigure(1, weight=1)
        ttk.Label(overall_progress_subframe, text="Overall:", width=10).grid(row=0, column=0, sticky="w")
        self.progress_bar_total = ttk.Progressbar(overall_progress_subframe, orient="horizontal", mode="determinate", style="thin.Horizontal.TProgressbar")
        self.progress_bar_total.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.total_time_label = ttk.Label(overall_progress_subframe, text="Tổng thời gian: 00:00", style="secondary.TLabel")
        self.total_time_label.grid(row=0, column=2, sticky="e")

        self.thread_status_labels = []
        for i in range(NUM_API_KEYS):
            ttk.Label(progress_frame, text=f"API Key {i+1}:", width=10).grid(row=i+1, column=0, sticky="w", pady=1)
            status_label = ttk.Label(progress_frame, text="Idle", foreground=COLOR_NORMAL, anchor="w")
            status_label.grid(row=i+1, column=1, sticky="ew", pady=1, padx=5)
            self.thread_status_labels.append(status_label)
        
        log_frame = ttk.LabelFrame(frame, text="Log", padding="10")
        log_frame.grid(row=5, column=0, sticky="ewns", padx=5, pady=5)
        log_frame.rowconfigure(0, weight=1); log_frame.columnconfigure(0, weight=1)
        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=8, state='disabled')
        self.log_area.grid(row=0, column=0, sticky="nsew", padx=(5,0), pady=5)
        self.clear_log_button = ttk.Button(log_frame, text="Clear Log", command=self.clear_log_area, width=10)
        self.clear_log_button.grid(row=0, column=1, sticky="ne", padx=(2,5), pady=5)

    def on_voice_selected(self, event):
        selected_index = event.widget.current()
        if 0 <= selected_index < len(self.voice_name_list):
            voice_name = self.voice_name_list[selected_index]
            self.selected_voice_name.set(voice_name)

    def update_voice_display(self, voice_name_to_set):
        try:
            if voice_name_to_set in self.voice_name_list:
                idx = self.voice_name_list.index(voice_name_to_set)
                display_text = self.voice_display_list[idx]
                self.selected_voice_display.set(display_text)
            else: 
                if self.voice_display_list:
                    self.selected_voice_display.set(self.voice_display_list[0])
                    self.selected_voice_name.set(self.voice_name_list[0])
        except (ValueError, IndexError):
            if self.voice_display_list:
                self.selected_voice_display.set(self.voice_display_list[0])
                if self.voice_name_list:
                    self.selected_voice_name.set(self.voice_name_list[0])
    def import_text_from_file(self):
        """Mở dialog để chọn file .txt hoặc .docx và nạp nội dung."""
        file_path = filedialog.askopenfilename(
            title="Chọn file văn bản",
            filetypes=[("Word Document", "*.docx"), ("Text File", "*.txt"), ("All files", "*.*")]
        )
        if not file_path:
            return

        content = ""
        try:
            if file_path.lower().endswith(".txt"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif file_path.lower().endswith(".docx"):
                if docx is None:
                    messagebox.showerror("Thiếu thư viện", "Vui lòng cài đặt thư viện 'python-docx' để đọc file .docx.\nChạy lệnh: pip install python-docx")
                    return
                doc = docx.Document(file_path)
                content = "\n".join([para.text for para in doc.paragraphs])
            else:
                messagebox.showwarning("Định dạng không hỗ trợ", "Chỉ hỗ trợ file .txt và .docx.")
                return

            self.main_text_input.delete("1.0", tk.END)
            self.main_text_input.insert("1.0", content)
            self.update_word_count(None) # Cập nhật lại bộ đếm
            self.log_message(f"Đã import thành công nội dung từ: {os.path.basename(file_path)}")

        except Exception as e:
            messagebox.showerror("Lỗi đọc file", f"Đã có lỗi xảy ra khi đọc file:\n{e}")
            self.log_message(f"Lỗi import file: {e}")
            
    def create_settings_tab_widgets(self):
        frame = self.settings_tab
        api_keys_frame = ttk.LabelFrame(frame, text="API Key Management", padding="10")
        api_keys_frame.grid(row=0, column=0, padx=5, pady=10, sticky="ew")
        self.api_key_entries = [] 
        self.api_label_entries = []
        for i in range(NUM_API_KEYS):
            ttk.Label(api_keys_frame, text=f"Label API Key {i+1}:").grid(row=i*2, column=0, padx=5, pady=(10,2), sticky="w")
            label_entry = ttk.Entry(api_keys_frame, textvariable=self.api_label_vars[i], width=40)
            label_entry.grid(row=i*2, column=1, columnspan=2, padx=5, pady=(10,2), sticky="ew")
            self.api_label_entries.append(label_entry)
            ttk.Label(api_keys_frame, text=f"API Key {i+1}:").grid(row=i*2+1, column=0, padx=5, pady=2, sticky="w")
            key_entry = ttk.Entry(api_keys_frame, textvariable=self.api_key_vars[i], width=50, show="*")
            key_entry.grid(row=i*2+1, column=1, columnspan=2, padx=5, pady=2, sticky="ew")
            self.api_key_entries.append(key_entry)
        api_keys_frame.columnconfigure(1, weight=1)

        general_settings_frame = ttk.LabelFrame(frame, text="General Settings", padding="10")
        general_settings_frame.grid(row=1, column=0, padx=5, pady=10, sticky="ew")
        general_settings_frame.columnconfigure(1, weight=1)
        
        ttk.Label(general_settings_frame, text="Default Voice:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.settings_voice_dropdown = ttk.Combobox(general_settings_frame, textvariable=self.selected_voice_display, values=self.voice_display_list, state='readonly', width=40)
        self.settings_voice_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.settings_voice_dropdown.bind('<<ComboboxSelected>>', self.on_voice_selected)
        
        # --- MỚI: Thêm ô tùy chỉnh Chunk Size ---
        ttk.Label(general_settings_frame, text="Số từ tối đa mỗi chunk:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.chunk_size_entry = ttk.Entry(general_settings_frame, textvariable=self.words_per_chunk_var, width=10)
        self.chunk_size_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(general_settings_frame, text="Default Save Directory:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.settings_save_dir_entry = ttk.Entry(general_settings_frame, textvariable=self.output_dir_var, width=40)
        self.settings_save_dir_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(general_settings_frame, text="Browse...", command=self.browse_main_output_directory).grid(row=2, column=2, padx=5, pady=5)
        
        self.save_settings_button = ttk.Button(frame, text="Save All Settings", command=self.save_app_settings, style="Accent.TButton")
        self.save_settings_button.grid(row=2, column=0, padx=5, pady=15)
        ttk.Label(frame, text="Note: Settings are saved automatically on exit.").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        frame.columnconfigure(0, weight=1)
            
    def browse_main_output_directory(self):
        directory = filedialog.askdirectory(initialdir=self.output_dir_var.get(), title="Select Output Directory", parent=self.root)
        if directory: self.output_dir_var.set(directory); self.log_message(f"Output directory set to: {directory}")

    def clear_log_area(self):
        if hasattr(self, 'log_area') and self.log_area.winfo_exists():
            self.log_area.config(state="normal"); self.log_area.delete("1.0", tk.END); self.log_area.config(state="disabled")

    def open_last_output_folder(self):
        if self.last_saved_output_dir and os.path.isdir(self.last_saved_output_dir):
            try:
                if platform.system() == "Windows": os.startfile(self.last_saved_output_dir)
                elif platform.system() == "Darwin": subprocess.call(["open", self.last_saved_output_dir])
                else: subprocess.call(["xdg-open", self.last_saved_output_dir])
            except Exception as e: self.log_message(f"Error opening folder: {e}"); messagebox.showerror("Error", f"Could not open folder: {self.last_saved_output_dir}\n{e}", parent=self.root)
        else: self.log_message("No output folder recorded or folder does not exist.");

    def update_word_count(self, event=None):
        content = self.main_text_input.get("1.0", tk.END).strip()
        char_count = len(content)
        word_count = len(content.split()) if content else 0
        # Ước tính số chunks, giả định 1000 từ mỗi chunk
        est_chunks = (word_count + 999) // 1000 if word_count > 0 else 0
        
        self.main_word_count_label.config(text=f"Ký tự: {char_count} | Từ: {word_count} | Dự kiến chunks: {est_chunks}")

     # --- Sửa hàm log_message ---
    def log_message(self, message: str):
        # Giờ đây, hàm này chỉ cần gọi logging, hệ thống sẽ tự lo phần còn lại
        logging.info(message)

    def update_overall_progress(self, value: int):
        if hasattr(self, 'progress_bar_total') and self.progress_bar_total.winfo_exists():
            def _update():
                if self.progress_bar_total.winfo_exists(): self.progress_bar_total["value"] = value
            self.root.after_idle(_update)

    # --- THAY ĐỔI: Hàm update_thread_progress để nhận màu sắc ---
    def update_thread_progress(self, thread_index: int, status_message: str, status_color: str):
        if thread_index < len(self.thread_status_labels) and self.thread_status_labels[thread_index].winfo_exists():
            def _update_lbl():
                if self.thread_status_labels[thread_index].winfo_exists():
                    self.thread_status_labels[thread_index].config(text=status_message, foreground=status_color)
            self.root.after_idle(_update_lbl)
            
    def save_app_settings(self):
        current_settings = {
            "default_voice": self.selected_voice_name.get(),
            "temperature": self.temperature_var.get(),
            "top_p": self.top_p_var.get(),
            "save_dir": self.output_dir_var.get(),
            "max_words_per_part": self.words_per_chunk_var.get() # MỚI
        }
        for i in range(NUM_API_KEYS):
            current_settings[f"api_key_{i+1}"] = self.api_key_vars[i].get()
            current_settings[f"label_{i+1}"] = self.api_label_vars[i].get()
        if save_settings(current_settings):
            self.settings = current_settings; self.log_message("Settings saved successfully.")
            messagebox.showinfo("Settings", "Settings saved successfully!", parent=self.root)
        else:
            self.log_message("Failed to save settings."); messagebox.showerror("Error", "Failed to save settings.", parent=self.root)

    # --- HOTFIX [2025-06-18]: Sửa lỗi AttributeError do gọi sai tên biến text input. Thay thế toàn bộ hàm này. ---
    def start_tts_thread(self):
        # Sửa lại self.text_input thành self.main_text_input
        text_to_convert = self.main_text_input.get("1.0", tk.END).strip()
        if not text_to_convert:
            messagebox.showerror("Input Error", "Please enter text.", parent=self.root)
            return
        
        active_keys_info_list = []
        for i in range(NUM_API_KEYS):
            key_val = self.api_key_vars[i].get().strip()
            if key_val:
                active_keys_info_list.append({
                    "key": key_val, 
                    "label": self.api_label_vars[i].get().strip() or f"API Key {i+1}"
                })
        if not active_keys_info_list:
            messagebox.showerror("API Key Error", f"Please set at least one API Key in Settings.", parent=self.root)
            self.notebook.select(self.settings_tab)
            return
        self.log_message(f"Found {len(active_keys_info_list)} active API Key(s).")

        voice_to_use = self.selected_voice_name.get()
        if not voice_to_use:
            messagebox.showerror("Voice Error", "Please select a voice.", parent=self.root)
            return

        output_dir = self.output_dir_var.get().strip()
        story_base_name = self.story_name_var.get().strip()
        if not output_dir or not os.path.isdir(output_dir):
            messagebox.showerror("Output Error", "Invalid output directory.", parent=self.root)
            return
        if not story_base_name:
            messagebox.showerror("Output Error", "Please enter a Story/Base Name.", parent=self.root)
            return
        
        reading_style_prompt_text = self.reading_style_prompt_var.get().strip()

        selected_voice_for_filename = voice_to_use.replace("-", "")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_story_name = "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in story_base_name).rstrip()
        safe_voice_name = "".join(c if c.isalnum() else '' for c in selected_voice_for_filename)
        output_filename_only = f"{safe_voice_name}_{safe_story_name}_{timestamp}"
        output_file_path_base = os.path.normpath(os.path.join(output_dir, output_filename_only))
        
        self.log_message(f"Output base name: {output_filename_only}")

        self.generate_button.config(state="disabled", text="Generating...")
        if hasattr(self, 'open_folder_button'): self.open_folder_button.config(state="disabled")
        self.root.config(cursor="watch")
        
        thread = threading.Thread(
            target=self._tts_task_wrapper,
            args=(
                text_to_convert, voice_to_use, output_file_path_base,
                self.temperature_var.get(), self.top_p_var.get(),
                reading_style_prompt_text
            ),
            daemon=True
        )
        thread.start()

    # --- HOTFIX [2025-06-18]: Cung cấp phiên bản đầy đủ và chính xác của hàm _tts_task_wrapper. Thay thế toàn bộ hàm này. ---
    def _tts_task_wrapper(self, text_to_convert, voice, output_file_path_base, temp, top_p, reading_style_prompt):
        task_start_time = time.time()

        # Reset các hiển thị trên UI trước khi bắt đầu
        def _setup_ui_for_run():
            if hasattr(self, 'total_time_label') and self.total_time_label.winfo_exists():
                self.total_time_label.config(text="Tổng thời gian: 00:00")
            
            active_keys_count = sum(1 for var in self.api_key_vars if var.get().strip())
            for i in range(NUM_API_KEYS):
                if i < active_keys_count:
                    self.update_thread_progress(i, "Sẵn sàng...", COLOR_NORMAL)
                else:
                    self.update_thread_progress(i, "Không sử dụng", "gray")

        self.root.after_idle(_setup_ui_for_run)
        
        sanitized_temp = round(temp, 2)
        sanitized_top_p = round(top_p, 2)
        
        self.last_saved_output_dir = None
        try:
            active_keys_info_for_logic = [] 
            for i in range(NUM_API_KEYS):
                key_val = self.api_key_vars[i].get().strip()
                if key_val:
                    active_keys_info_for_logic.append({
                        "key": key_val, 
                        "label": self.api_label_vars[i].get().strip() or f"API Key {i+1}"
                    })
            if not active_keys_info_for_logic:
                self.log_message("Lỗi: Không có API Key nào được cấu hình.")
                # Phải gọi finalize để bật lại nút bấm
                # Dùng return sẽ không chạy vào finally, nên ta sẽ để nó chạy qua
                raise ValueError("No active API keys configured.")

            thread_specific_callbacks = []
            for i in range(len(active_keys_info_for_logic)):
                def create_callback(thread_idx_captured):
                    def _update_ui_for_thread(status_msg, status_color):
                        self.update_thread_progress(thread_idx_captured, status_msg, status_color)
                    return _update_ui_for_thread
                thread_specific_callbacks.append(create_callback(i))
            
            max_words = self.words_per_chunk_var.get()
            token_fallback = int(self.settings.get("max_tokens_fallback", 4800)) 
            retries = int(self.settings.get("max_retries_per_part", 1)) 
            timeout = int(self.settings.get("part_timeout", 600))
            
            success, final_file_path = generate_tts_audio_multithreaded( 
                active_api_keys_info=active_keys_info_for_logic, 
                text_to_speak=text_to_convert, 
                voice_name=voice, 
                output_file_path_base=output_file_path_base, 
                log_callback_ui=self.log_message, 
                progress_callback_ui_total=self.update_overall_progress,
                progress_callbacks_ui_thread=thread_specific_callbacks,
                reading_style_prompt=reading_style_prompt, 
                temp_setting=sanitized_temp,
                top_p_setting=sanitized_top_p,
                max_words_per_part=max_words,
                max_tokens_fallback=token_fallback,
                max_retries_per_part=retries,
                part_timeout=timeout
            )
            
            if success and final_file_path:
                self.log_message(f"TTS task completed successfully. Final file: {final_file_path}")
                self.last_saved_output_dir = os.path.dirname(final_file_path)
            else:
                self.log_message("TTS task failed or did not complete.")

        except Exception as e:
            logging.error(f"Error in TTS task wrapper: {e}", exc_info=True)
            self.log_message(f"Đã xảy ra lỗi: {e}")
        finally: 
            def _finalize_ui(): 
                duration = time.time() - task_start_time
                minutes, seconds = divmod(duration, 60)
                time_str = f"Tổng thời gian: {int(minutes):02d}:{int(seconds):02d}"

                if hasattr(self, 'root') and self.root.winfo_exists():
                    if hasattr(self, 'generate_button'):
                        self.generate_button.config(state="normal", text="Generate Voice")
                    self.root.config(cursor="")
                    if self.last_saved_output_dir and hasattr(self, 'open_folder_button'):
                        self.open_folder_button.config(state="normal")
                    if hasattr(self, 'total_time_label'):
                        self.total_time_label.config(text=time_str)
                    
                    for i in range(NUM_API_KEYS): 
                        if i < len(self.thread_status_labels) and self.thread_status_labels[i].winfo_exists():
                                self.update_thread_progress(i, "Idle", COLOR_NORMAL)
            
            if hasattr(self, 'root') and self.root.winfo_exists():
                self.root.after_idle(_finalize_ui)
```

---

## Phần 3: Quy ước Làm việc & Cấu trúc Phản hồi của AI

### 3.1. Quy ước về Cung cấp Code
* **Thay đổi Lớn (Thêm tính năng, tái cấu trúc):** AI sẽ cung cấp **toàn bộ nội dung file** với một số phiên bản mới rõ ràng.
* **Sửa lỗi Nhỏ (Hotfix):** AI sẽ chỉ cung cấp **đầy đủ phần thân của (các) hàm cần sửa đổi**, kèm theo comment `# --- HOTFIX...`.
* **Quy tắc Vàng:** AI **không bao giờ được tóm tắt code** bằng `...` hoặc `pass`. Mọi hàm hoặc class được cung cấp phải đầy đủ.

### 3.2. Quy ước về Giao tiếp & Trí nhớ
* **Xác nhận & Phân tích:** AI phải luôn xác nhận đã hiểu rõ yêu cầu, phân tích các rủi ro hoặc đề xuất của người dùng, và thống nhất kế hoạch chi tiết **trước khi** cung cấp code.
* **Rà soát & Đồng bộ:** Trước mỗi phản hồi chứa code, AI phải tự rà soát lại các file liên quan để đảm bảo tính nhất quán (ví dụ: một hàm được gọi phải tồn tại, các tham số truyền đi phải khớp).
* **Ghi nhớ Lộ trình:** AI phải luôn bám sát vào lộ trình đã được thống nhất, không "quên" các tính năng đã làm hoặc đi chệch hướng. Khi được hỏi về bước tiếp theo, phải trả lời dựa trên lộ trình này.

---

## Phần 4: Lộ trình Phát triển Tiếp theo (Công việc dang dở)

* **4.1. Nhiệm vụ ưu tiên:** Hoàn thành **Yêu cầu 4.1 - Nâng cấp toàn diện tính năng "Xem trước Thumbnail"**.

* **4.2. Trạng thái hiện tại:** Giao diện cơ bản đã được xây dựng bằng `Tkinter Canvas` với các nút điều khiển.

* **4.3. Checklist công việc cần làm cho Nhiệm vụ 4.1:**
    * `[ ]` **Sửa lỗi Font & Bố cục:** Khắc phục triệt để lỗi hiển thị font tiếng Việt, tràn lề, và căn chỉnh sai.
    * `[ ]` **Sửa lỗi Tỷ lệ 16:9:** Hoàn thiện logic co giãn cửa sổ để loại bỏ hoàn toàn viền xám.
    * `[ ]` **Hoàn thiện Bảng điều khiển:** Lập trình logic cho các widget đã tạo (chọn Font, Cỡ chữ).
    * `[ ]` **Thêm Tùy chỉnh Nâng cao:** Xây dựng logic tô màu cho từng dòng và hiệu ứng viền chữ/đổ bóng.
    * `[ ]` **Hoàn thiện chức năng Xuất ảnh:** Đảm bảo file ảnh xuất ra phản ánh đúng tất cả các tùy chỉnh.

* **4.4. Backlog - Ý tưởng tương lai:**
    * **Yêu cầu #5 - Cải tiến:** Thêm tính năng chống trùng lặp và đặt tên file thông minh cho tab "Soạn Truyện Dài".
    * **Yêu cầu #6:** Xây dựng module tải phụ đề YouTube.
    * **Yêu cầu #7:** Nghiên cứu giải pháp tự động hóa nâng cao (tương tác màn hình).