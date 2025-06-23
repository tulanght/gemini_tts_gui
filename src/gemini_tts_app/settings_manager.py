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