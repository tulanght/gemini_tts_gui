# file-path: src/gemini_tts_app/settings_manager.py
# version: 4.0
# last-updated: 2025-07-17
# description: Nâng cấp để hỗ trợ lưu/tải danh sách Nhóm Dự án (Google Drive) bằng JSON.

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

DEFAULT_SETTINGS = {
    "default_voice": DEFAULT_VOICE_CONST,
    "temperature": DEFAULT_TEMPERATURE_CONST,
    "top_p": DEFAULT_TOP_P_CONST,
    "save_dir": os.path.expanduser("~"),
    "max_words_per_part": 1000
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
    # Tách riêng project_groups nếu có
    project_groups_data = settings_dict.pop('project_groups', [])

    for key, value in settings_dict.items():
        if key.startswith("api_key_") or key.startswith("label_"):
            api_key_settings[key] = str(value)
        else:
            general_settings[key] = str(value)

    config["GEMINI_TTS_GENERAL"] = general_settings
    config["GEMINI_TTS_API_KEYS"] = api_key_settings
    # Lưu project_groups vào một section riêng
    config["PROJECT_GROUPS"] = {'groups': json.dumps(project_groups_data)}

    try:
        with open(CONFIG_FILE, "w", encoding='utf-8') as configfile:
            config.write(configfile)
        return True
    except IOError as e:
        print(f"Error writing to config file: {e}")
        return False

def load_settings() -> dict:
    if not os.path.exists(CONFIG_FILE):
        # Thêm khóa rỗng cho project_groups vào settings mặc định
        DEFAULT_SETTINGS['project_groups'] = []
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

    config = configparser.ConfigParser()
    try:
        config.read(CONFIG_FILE, encoding='utf-8')
    except Exception as e:
        print(f"Error reading config, using defaults: {e}")
        DEFAULT_SETTINGS['project_groups'] = []
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

    loaded_settings = {}
    # Tải các cài đặt chung
    general_section = "GEMINI_TTS_GENERAL"
    if general_section in config:
        for key, default_value in DEFAULT_SETTINGS.items():
            if not (key.startswith("api_key_") or key.startswith("label_") or key == 'project_groups'):
                if isinstance(default_value, int):
                    loaded_settings[key] = config.getint(general_section, key, fallback=default_value)
                elif isinstance(default_value, float):
                    loaded_settings[key] = config.getfloat(general_section, key, fallback=default_value)
                else:
                    loaded_settings[key] = config.get(general_section, key, fallback=str(default_value))

    # Tải các cài đặt API Key
    api_section = "GEMINI_TTS_API_KEYS"
    if api_section in config:
        for i in range(1, NUM_API_KEYS + 1):
            loaded_settings[f"api_key_{i}"] = config.get(api_section, f"api_key_{i}", fallback="")
            loaded_settings[f"label_{i}"] = config.get(api_section, f"label_{i}", fallback=f"API Key {i}")

    # Tải danh sách Nhóm Dự án
    loaded_settings['project_groups'] = load_project_groups(config)

    return loaded_settings

def load_project_groups(config_parser=None) -> list:
    """Tải danh sách các nhóm dự án từ file config."""
    if config_parser is None:
        config_parser = configparser.ConfigParser()
        if os.path.exists(CONFIG_FILE):
            config_parser.read(CONFIG_FILE, encoding='utf-8')
        else:
            return []

    groups_section = "PROJECT_GROUPS"
    if groups_section in config_parser:
        groups_json = config_parser.get(groups_section, 'groups', fallback='[]')
        try:
            return json.loads(groups_json)
        except json.JSONDecodeError:
            return []
    return []

def save_project_groups(groups_list: list):
    """Lưu danh sách các nhóm dự án vào file config."""
    if not _ensure_config_dir_exists(): return False

    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE, encoding='utf-8')

    groups_section = "PROJECT_GROUPS"
    if groups_section not in config:
        config.add_section(groups_section)

    config.set(groups_section, 'groups', json.dumps(groups_list, indent=4))

    try:
        with open(CONFIG_FILE, "w", encoding='utf-8') as configfile:
            config.write(configfile)
        return True
    except IOError as e:
        print(f"Error writing project groups to config file: {e}")
        return False