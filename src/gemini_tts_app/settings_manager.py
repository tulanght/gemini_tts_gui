# file-path: src/gemini_tts_app/settings_manager.py
# version: 4.4
# last-updated: 2025-07-18
# description: Hỗ trợ "Loại Nhóm" (Local/Google Drive) và cải tiến logic.

import configparser
import os
import json
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

def get_default_settings():
    """Tạo và trả về một từ điển cài đặt mặc định hoàn chỉnh."""
    defaults = {
        "default_voice": DEFAULT_VOICE_CONST,
        "temperature": DEFAULT_TEMPERATURE_CONST,
        "top_p": DEFAULT_TOP_P_CONST,
        "save_dir": os.path.expanduser("~"),
        "max_words_per_part": 1000,
        "project_groups": [] # Luôn có khóa này
    }
    for i in range(1, NUM_API_KEYS + 1):
        defaults[f"api_key_{i}"] = ""
        defaults[f"label_{i}"] = f"API Key {i}"
    return defaults

def _ensure_config_dir_exists():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR, exist_ok=True)
    return True

def save_settings(settings_dict: dict):
    """Lưu cài đặt một cách an toàn vào file .ini."""
    if not _ensure_config_dir_exists(): return False

    config = configparser.ConfigParser()

    # Luôn tạo đủ các section để đảm bảo cấu trúc file
    config["GEMINI_TTS_GENERAL"] = {}
    config["GEMINI_TTS_API_KEYS"] = {}
    config["PROJECT_GROUPS"] = {}

    # Phân loại và lưu từng giá trị
    project_groups_data = settings_dict.get('project_groups', [])
    config.set('PROJECT_GROUPS', 'groups', json.dumps(project_groups_data, indent=4))

    for key, value in settings_dict.items():
        if key.startswith("api_key_") or key.startswith("label_"):
            config.set("GEMINI_TTS_API_KEYS", key, str(value))
        elif key != 'project_groups':
            config.set("GEMINI_TTS_GENERAL", key, str(value))

    try:
        with open(CONFIG_FILE, "w", encoding='utf-8') as configfile:
            config.write(configfile)
        return True
    except IOError as e:
        print(f"Lỗi khi ghi file cấu hình: {e}")
        return False

def load_settings() -> dict:
    """Tải cài đặt một cách an toàn, không làm mất dữ liệu."""
    # BƯỚC 1: LUÔN BẮT ĐẦU VỚI MỘT BỘ ĐẦY ĐỦ CÁC KHÓA MẶC ĐỊNH
    loaded_settings = get_default_settings()

    if not os.path.exists(CONFIG_FILE):
        save_settings(loaded_settings)
        return loaded_settings

    config = configparser.ConfigParser()
    try:
        config.read(CONFIG_FILE, encoding='utf-8')
    except Exception as e:
        print(f"Lỗi đọc file cấu hình, sử dụng mặc định: {e}")
        return loaded_settings

    # BƯỚC 2: GHI ĐÈ CÁC GIÁ TRỊ MẶC ĐỊNH BẰNG CÁC GIÁ TRỊ ĐÃ LƯU (NẾU CÓ)
    # Tải cài đặt chung
    if "GEMINI_TTS_GENERAL" in config:
        for key in loaded_settings:
            if key in config["GEMINI_TTS_GENERAL"]:
                # Chuyển đổi kiểu dữ liệu phù hợp
                default_value = get_default_settings().get(key)
                if isinstance(default_value, int):
                     loaded_settings[key] = config.getint("GEMINI_TTS_GENERAL", key, fallback=default_value)
                elif isinstance(default_value, float):
                    loaded_settings[key] = config.getfloat("GEMINI_TTS_GENERAL", key, fallback=default_value)
                else:
                    loaded_settings[key] = config.get("GEMINI_TTS_GENERAL", key, fallback=str(default_value))

    # Tải các khóa API
    if "GEMINI_TTS_API_KEYS" in config:
        for key in loaded_settings:
            if key in config["GEMINI_TTS_API_KEYS"]:
                loaded_settings[key] = config.get("GEMINI_TTS_API_KEYS", key)

    # Tải các nhóm dự án
    if "PROJECT_GROUPS" in config:
        groups_json = config.get("PROJECT_GROUPS", 'groups', fallback='[]')
        try:
            loaded_settings['project_groups'] = json.loads(groups_json)
        except json.JSONDecodeError:
            loaded_settings['project_groups'] = []

    return loaded_settings

# --- LOGIC QUẢN LÝ NHÓM DỰ ÁN (CẬP NHẬT) ---
def load_project_groups() -> list:
    """Tải danh sách các nhóm dự án từ file config."""
    settings = load_settings()
    return settings.get('project_groups', [])

def save_project_groups(groups_list: list):
    """Lưu toàn bộ danh sách các nhóm dự án vào file config."""
    settings = load_settings()
    settings['project_groups'] = groups_list
    return save_settings(settings)

def add_project_group(new_group: dict):
    """Thêm một nhóm dự án mới và lưu lại."""
    groups = load_project_groups()
    if any(g['name'] == new_group['name'] for g in groups):
        raise ValueError(f"Tên nhóm dự án '{new_group['name']}' đã tồn tại.")

    groups.append(new_group)
    return save_project_groups(groups)

def update_project_group(original_name: str, new_data: dict):
    """Cập nhật một nhóm dự án đã có."""
    groups = load_project_groups()

    if new_data['name'] != original_name and any(g['name'] == new_data['name'] for g in groups):
         raise ValueError(f"Tên nhóm dự án '{new_data['name']}' đã tồn tại.")

    updated = False
    for group in groups:
        if group['name'] == original_name:
            group.update(new_data)
            updated = True
            break

    if updated:
        return save_project_groups(groups)
    return False

def delete_project_group(name_to_delete: str):
    """Xóa một nhóm dự án khỏi danh sách và lưu lại."""
    groups = load_project_groups()
    original_count = len(groups)
    groups = [g for g in groups if g['name'] != name_to_delete]

    if len(groups) < original_count:
        return save_project_groups(groups)
    return False