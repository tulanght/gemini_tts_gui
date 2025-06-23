# tests/test_settings_manager.py
import unittest
import os
from gemini_tts_app.settings_manager import save_settings, load_settings, CONFIG_FILE

class TestSettingsManager(unittest.TestCase):
    def setUp(self):
        # Backup existing config if it exists, then remove for test
        self.backup_config_file = CONFIG_FILE + ".bak"
        if os.path.exists(CONFIG_FILE):
            os.rename(CONFIG_FILE, self.backup_config_file)

    def tearDown(self):
        # Clean up: remove test config file, restore backup if exists
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)
        if os.path.exists(self.backup_config_file):
            os.rename(self.backup_config_file, CONFIG_FILE)

    def test_save_and_load_settings(self):
        test_settings = {
            "api_key": "test_key_123",
            "default_voice": "TestVoice",
            "temperature": 0.8,
            "save_dir": "/test/path"
        }
        save_settings(test_settings)
        loaded = load_settings()

        # So sánh từng key vì load_settings có thể thêm các key mặc định không có trong test_settings ban đầu
        self.assertEqual(loaded["api_key"], test_settings["api_key"])
        self.assertEqual(loaded["default_voice"], test_settings["default_voice"])
        self.assertEqual(loaded["temperature"], test_settings["temperature"])
        self.assertEqual(loaded["save_dir"], test_settings["save_dir"])

    def test_load_default_settings_if_no_file(self):
        if os.path.exists(CONFIG_FILE): # Đảm bảo file không tồn tại
            os.remove(CONFIG_FILE)

        from gemini_tts_app.settings_manager import DEFAULT_SETTINGS # Import lại để lấy giá trị mới nhất
        loaded = load_settings()
        self.assertEqual(loaded["api_key"], DEFAULT_SETTINGS["api_key"])
        self.assertEqual(loaded["temperature"], DEFAULT_SETTINGS["temperature"])


if __name__ == '__main__':
    unittest.main()