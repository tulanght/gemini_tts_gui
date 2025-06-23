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