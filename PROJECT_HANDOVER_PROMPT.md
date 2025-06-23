# Prompt Chuẩn Bị Chi Tiết cho Dự Án Gemini TTS GUI (Phiên bản Ổn Định Hiện Tại)

## Phần 1: Giới thiệu chung và Mục tiêu Dự án

**Tiêu đề Dự án:** Ứng dụng GUI Desktop Text-to-Speech (TTS) sử dụng API Gemini của Google.

**Mục tiêu chính:**
Xây dựng một ứng dụng Python có giao diện người dùng đồ họa (GUI) bằng Tkinter, cho phép người dùng:
1.  Nhập một đoạn văn bản dài (đã thử nghiệm thành công với ~4500 từ / ~19000 ký tự, chia thành 5 parts).
2.  **(Đã hoạt động)** Chọn giọng nói từ danh sách 30 giọng được hỗ trợ bởi model Gemini TTS (danh sách này người dùng đã có và sẽ cung cấp trong `constants.py`).
3.  **(Đã hoạt động)** Chương trình tự động chia văn bản dài thành các phần nhỏ hơn (chunks) dựa trên số từ (ví dụ: 1000 từ/part), có kiểm tra token fallback (ví dụ: 4800 token) để đảm bảo an toàn cho API.
4.  **(Đã hoạt động)** Sử dụng tối đa 3 API key của Google AI Studio để thực hiện các yêu cầu generate audio cho các chunks song song (đa luồng). Mỗi thread worker sẽ quản lý một API key và xử lý các chunks từ một hàng đợi chung.
5.  **(Đã hoạt động)** Lưu các file audio của từng phần dưới dạng file WAV tạm thời. Header WAV được thêm vào nếu dữ liệu trả về từ API là PCM thô.
6.  **(Đã hoạt động)** Sau khi tất cả các phần đã được generate thành công, tự động ghép các file WAV tạm thành một file WAV hoàn chỉnh duy nhất.
7.  Giao diện quản lý API keys, cài đặt output, và theo dõi tiến trình (đã có cơ bản và hoạt động).

**Model Gemini đang sử dụng:** `models/gemini-2.5-pro-preview-tts`.
* Thông tin chi tiết model: Người dùng đã cung cấp hình ảnh `image_732f32.png` cho thấy model này có "Input token limit: 8,000" và "Capabilities -> Audio generation: Supported".
* Danh sách model hỗ trợ: Người dùng đã cung cấp hình ảnh `image_570b36.png` cho thấy model này hỗ trợ "Single speaker" và "Multispeaker".

**Thư viện Python chính:** `google-generativeai` (phiên bản người dùng đang có là `0.8.5`).
**Thư viện phụ trợ:**
* `pydub` (để ghép audio, yêu cầu `ffmpeg` đã được cài đặt trên hệ thống của người dùng).
* `appdirs` (để quản lý thư mục settings).
* `audioop-lts` (người dùng đã cài đặt để giải quyết vấn đề module `audioop` bị thiếu trên Python 3.13 khi `pydub` cần).

**Nguồn gốc ý tưởng và "Get code" ban đầu:**
Người dùng bắt đầu ý tưởng từ Google AI Studio, mục "Generate speech". Khi nhấn "Get code", một panel được hiển thị (tham khảo hình ảnh `image_748f51.png` người dùng đã cung cấp). Panel này gợi ý sử dụng thư viện `google-genai` và cung cấp một cấu trúc code ban đầu (bao gồm `from google.genai import types`, `types.GenerateContentConfig`, `response_modalities=["AUDIO"]`, và `speech_config` lồng nhau). Danh sách 30 giọng nói (như Zephyr, Puck, Algieba, v.v. - xem hình ảnh `Screenshot 2025-05-25 171307.png`) cũng đến từ giao diện AI Studio và đã được người dùng xác nhận là hoạt động với model `models/gemini-2.5-pro-preview-tts` khi truyền đúng cấu trúc config.

## Phần 2: Trạng thái Code Hoạt Động Tốt Nhất Hiện Tại (Nền tảng để phát triển tiếp)

Phiên bản code hiện tại (tương đương logic của `tts_logic_v35_exact_stable_wav_no_poison` và `main_app_v9_true_rollback_no_style` như đã thảo luận trong các phản hồi trước của AI) đã **hoạt động thành công** và tạo ra file WAV hoàn chỉnh cho cả văn bản ngắn và văn bản dài được chia thành nhiều part, sử dụng đa luồng.

### 2.1. Cấu trúc Thư mục Dự án:

gemini_tts_gui/
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
├── pyproject.toml  # (Hoặc setup.py nếu có)
├── run.py          # Script chính để khởi chạy ứng dụng
|
├── src/
│   └── gemini_tts_app/       # Tên package của ứng dụng
│       ├── __init__.py
│       ├── __main__.py       # Cho phép chạy bằng `python -m gemini_tts_app`
│       │
│       ├── main_app.py       # Lớp GUI chính (TTSApp)
│       ├── tts_logic.py      # Logic xử lý TTS với API Gemini
│       ├── settings_manager.py # Quản lý đọc/ghi cài đặt
│       ├── constants.py      # Hằng số ứng dụng
│       ├── utils.py          # Hàm tiện ích
│       │
│       └── ui/               # (Tùy chọn, nếu có các widget UI tùy chỉnh)
│           ├── __init__.py
│           └── custom_widgets.py 
│
├── resources/
│   └── icons/
│       ├── app_icon.ico
│       └── app_icon.png
│
├── tests/
│   ├── __init__.py
│   └── # ... (các file test) ...
│
└── venv/                   # Thư mục môi trường ảo Python (nằm trong .gitignore)


### 2.2. Tổng quan chức năng các file chính (trong phiên bản ổn định):

* **`constants.py`**: Định nghĩa các hằng số như danh sách giọng nói (`GEMINI_TTS_VOICES` với 30 giọng đã được API xác nhận), số lượng API key (`NUM_API_KEYS=3`), `DEFAULT_TEMPERATURE=1.0`.
* **`utils.py`**: Chứa hàm `get_resource_path()`.
* **`settings_manager.py`**: Quản lý lưu/tải 3 cặp API key/label, thư mục lưu mặc định, temperature vào `settings.ini`.
* **`main_app.py`**: Xây dựng giao diện Tkinter chính.
    * Tab "Text-to-Speech": Ô nhập text, chọn giọng, thanh trượt temperature (mặc định và đang dùng `1.0`), chọn thư mục output, nhập tên file cơ sở. **Không có UI cho "Reading Style Prompt" ở phiên bản ổn định này.**
    * Tab "Settings": Quản lý 3 cặp API key/label.
    * Tiến trình đa luồng: 3 thanh progress bar và label trạng thái cho từng luồng, 1 thanh progress tổng.
    * Nút "Clear Log", "Open Output Folder".
* **`tts_logic.py`**: Chứa logic cốt lõi:
    * Hàm chính `generate_tts_audio_multithreaded`: Điều phối đa luồng, chia text bằng `split_text_into_chunks`. Sử dụng `queue.Queue` cho job. **KHÔNG sử dụng `POISON_PILL`**; worker thread thoát dựa trên timeout của `job_queue.get()` và `daemon=True`, kết hợp với một bộ đếm số lần `queue.Empty` liên tiếp để chủ động thoát worker.
    * Hàm `_process_text_chunk_worker`: Logic cho mỗi thread. Sử dụng `gemini_api_config_lock` khi gọi `genai.configure()` và tạo `GenerativeModel`.
    * Hàm `_generate_audio_for_single_chunk`:
        * Model: `models/gemini-2.5-pro-preview-tts`.
        * `contents` là dictionary: `[{"role": "user", "parts": [{"text": text_for_api}]}]`.
        * `generation_config` là dictionary `ai_studio_config_dict` có cấu trúc:
            ```python
            ai_studio_config_dict = {
                "temperature": 1.0, 
                "response_modalities": ["AUDIO"], 
                "speech_config": {
                    "voice_config": {
                        "prebuilt_voice_config": {"voice_name": "TÊN_GIỌNG_ĐÃ_CHỌN_TỪ_UI"}
                    }
                }
                # KHÔNG có "response_mime_type" trong dict này.
            }
            ```
        * Lời gọi API: `model_instance.generate_content(..., stream=True)`.
        * Dữ liệu audio: Lấy từ `part.inline_data.data`.
        * Header WAV: Được thêm nếu `inline_data` là PCM thô (giả định 24kHz, 16-bit, mono nếu `part.mime_type` không rõ ràng). Các file part tạm là WAV.
    * Các hàm tiện ích khác (`split_text_into_chunks` chia theo từ, có kiểm tra token fallback).

### 2.3. Log thành công tiêu biểu của phiên bản này:
* **Văn bản ngắn (~200 ký tự, 1 part, ví dụ output `Achird_476_...wav`):**
    * Chia thành 1 chunk.
    * Thread 1 xử lý thành công Part 1/1 (khoảng 15 giây).
    * Các thread khác thoát đúng cách.
    * Ghép file WAV thành công. Tổng thời gian ~20 giây. File audio nghe được, thời lượng hợp lý.
* **Văn bản dài (~19000 ký tự, ~4480 từ, chia 5 parts, ví dụ output `Alnilam_4480chars_...wav`):**
    * Chia thành 5 chunks.
    * Cả 3 worker thread xử lý các part song song.
    * Tất cả 5 part được generate WAV thành công (thời gian mỗi part ~140s-200s).
    * Các thread thoát đúng cách.
    * Ghép 5 file WAV part thành công. Tổng thời gian ~340-380 giây. File audio nghe được, thời lượng hợp lý.
    * **Ghi chú của người dùng về phiên bản này:** "vẫn còn lỗi lộn xộn reading style lúc cao lúc thấp, lúc bị echo vọng." (Điều này xảy ra NGAY CẢ KHI KHÔNG CÓ "Reading Style Prompt" tường minh, chỉ dùng text gốc và `temperature=1.0`).

### 2.4. Mã code các file chính (Người dùng sẽ cung cấp phiên bản ổn định nhất của họ sau khi nhận được prompt này):

* **`constants.py`:**
    ```python
    # src/gemini_tts_app/constants.py
    APP_NAME = "Gemini TTS GUI"
    APP_VERSION = "0.1.0" # Đồng bộ với pyproject.toml
    APP_AUTHOR = "Cuong Tran" # Dùng cho appdirs

    # --- API Key Settings ---
    NUM_API_KEYS = 3 # Số lượng API key người dùng có thể cấu hình

    DEFAULT_VOICE = "Algieba"
    # Cần kiểm tra tên voice chính xác từ tài liệu Google Gemini TTS
    # Danh sách này nên được cập nhật dựa trên tài liệu API mới nhất
    GEMINI_TTS_VOICES = [
        "Enceladus",
        "Zephyr",
        "Puck",
        "Charon",
        "Kore",
        "Fenrir",
        "Leda",
        "Orus",
        "Aoede",
        "Callirhoe",
        "Autonoe",
        "Iapetus",
        "Umbriel",
        "Algieba",
        "Despina",
        "Erinome",
        "Algenib",
        "Rasalgethi",
        "Laomedeia",
        "Achernar",
        "Alnilam",
        "Schedar",
        "Gacrux",
        "Pulcherrima",
        "Achird",
        "Zubenelgenubi",
        "Vindemiatrix",
        "Sadachbia",
        "Sadaltager",
        "Sulafar"
    ]
    # Hoặc lấy từ models API nếu có
    # MODEL_NAME = "gemini-1.5-flash-tts-001" # Ví dụ tên model, không phải tên voice

    DEFAULT_TEMPERATURE = 1.0
    MIN_TEMPERATURE = 0.0
    MAX_TEMPERATURE = 2.0 # Kiểm tra giới hạn thực tế của API
    ```

* **`utils.py`:**
    ```python
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
    ```

* **`settings_manager.py`:**
    ```python
    # src/gemini_tts_app/settings_manager.py
    # Phiên bản: settings_manager_v2.1_multi_api_with_constant

    import configparser
    import os
    from appdirs import user_config_dir
    ## Import hằng số từ constants.py
    from .constants import APP_NAME as APP_NAME_CONST, \
                        APP_AUTHOR as APP_AUTHOR_CONST, \
                        DEFAULT_VOICE as DEFAULT_VOICE_CONST, \
                        DEFAULT_TEMPERATURE as DEFAULT_TEMPERATURE_CONST, \
                        NUM_API_KEYS # <--- IMPORT HẰNG SỐ NÀY

    CONFIG_DIR = user_config_dir(APP_NAME_CONST, APP_AUTHOR_CONST)
    CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.ini")
    # NUM_API_KEYS đã được import từ constants

    DEFAULT_SETTINGS = {
        "default_voice": DEFAULT_VOICE_CONST,
        "temperature": DEFAULT_TEMPERATURE_CONST,
        "save_dir": os.path.expanduser("~")
    }
    # Thêm mục mặc định cho API keys và labels dựa trên NUM_API_KEYS
    for i in range(1, NUM_API_KEYS + 1):
        DEFAULT_SETTINGS[f"api_key_{i}"] = ""
        DEFAULT_SETTINGS[f"label_{i}"] = f"API Key {i}" # Label mặc định


    def _ensure_config_dir_exists():
        if not os.path.exists(CONFIG_DIR):
            try:
                os.makedirs(CONFIG_DIR, exist_ok=True)
            except OSError as e:
                print(f"Error creating config directory {CONFIG_DIR}: {e}")
                return False
        return True

    def save_settings(settings_dict: dict): # settings_dict giờ sẽ chứa các api_key_X và label_X
        if not _ensure_config_dir_exists():
            return False
                
        config = configparser.ConfigParser()
        
        # Lưu các cài đặt chung
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
            print(f"Error writing to config file {CONFIG_FILE}: {e}")
            return False

    def load_settings() -> dict:
        # ... (hàm này giữ nguyên logic, nó đã dùng DEFAULT_SETTINGS để biết các key cần load) ...
        # Đảm bảo DEFAULT_SETTINGS đã được cập nhật với đúng số lượng key và label
        current_default_settings = DEFAULT_SETTINGS.copy()
        # Cập nhật lại DEFAULT_SETTINGS một lần nữa phòng trường hợp constants.py thay đổi NUM_API_KEYS
        # sau khi module này được import lần đầu.
        # Cách tốt hơn là DEFAULT_SETTINGS được xây dựng hoàn toàn dựa trên NUM_API_KEYS mỗi lần.
        # Tuy nhiên, cách hiện tại vẫn sẽ hoạt động nếu NUM_API_KEYS không thay đổi trong một phiên chạy.
        # Để chắc chắn, chúng ta có thể xây dựng lại phần API keys của default settings ở đây.
        
        # Xây dựng lại phần default cho API keys để đảm bảo nhất quán với NUM_API_KEYS
        # (Mặc dù DEFAULT_SETTINGS ở trên đã làm điều này, lặp lại ở đây để chắc chắn hơn nếu load_settings được gọi nhiều lần
        # và NUM_API_KEYS có thể thay đổi - điều này không xảy ra trong thực tế của chúng ta nhưng tốt cho sự rõ ràng)
        api_related_defaults = {}
        for i in range(1, NUM_API_KEYS + 1):
            api_related_defaults[f"api_key_{i}"] = ""
            api_related_defaults[f"label_{i}"] = f"API Key {i}"
        
        # Ghi đè hoặc thêm các default này vào current_default_settings
        current_default_settings.update(api_related_defaults)


        if not _ensure_config_dir_exists() or not os.path.exists(CONFIG_FILE):
            save_settings(current_default_settings) 
            return current_default_settings


        config = configparser.ConfigParser()
        try:
            config.read(CONFIG_FILE, encoding='utf-8')
        except Exception as e:
            print(f"Error reading config file {CONFIG_FILE}, using defaults: {e}")
            save_settings(current_default_settings)
            return current_default_settings

        loaded_settings = {}
        # Load General Settings
        if "GEMINI_TTS_GENERAL" in config:
            for key in current_default_settings: # Duyệt qua các key trong default đã cập nhật
                if not (key.startswith("api_key_") or key.startswith("label_")):
                    default_value = current_default_settings[key]
                    if isinstance(default_value, float):
                        loaded_settings[key] = config.getfloat("GEMINI_TTS_GENERAL", key, fallback=default_value)
                    elif isinstance(default_value, int):
                        loaded_settings[key] = config.getint("GEMINI_TTS_GENERAL", key, fallback=default_value)
                    else:
                        loaded_settings[key] = config.get("GEMINI_TTS_GENERAL", key, fallback=str(default_value))
        else:
            for key, default_value in current_default_settings.items():
                if not (key.startswith("api_key_") or key.startswith("label_")):
                    loaded_settings[key] = default_value

        # Load API Key Settings
        if "GEMINI_TTS_API_KEYS" in config:
            for i in range(1, NUM_API_KEYS + 1): # Sử dụng NUM_API_KEYS đã import
                loaded_settings[f"api_key_{i}"] = config.get("GEMINI_TTS_API_KEYS", f"api_key_{i}", fallback=current_default_settings.get(f"api_key_{i}",""))
                loaded_settings[f"label_{i}"] = config.get("GEMINI_TTS_API_KEYS", f"label_{i}", fallback=current_default_settings.get(f"label_{i}",f"API Key {i}"))
        else:
            for i in range(1, NUM_API_KEYS + 1):
                loaded_settings[f"api_key_{i}"] = current_default_settings.get(f"api_key_{i}","")
                loaded_settings[f"label_{i}"] = current_default_settings.get(f"label_{i}",f"API Key {i}")
                
        # Đảm bảo tất cả các default keys đều có mặt nếu file config cũ hơn
        for key, default_value in current_default_settings.items():
            if key not in loaded_settings:
                loaded_settings[key] = default_value
                
        return loaded_settings
    ```

* **`main_app.py` (phiên bản `main_app_v9_true_rollback_no_style` - Không có UI cho Reading Style):**
    ```python
    # src/gemini_tts_app/main_app.py
    # Phiên bản: main_app_v9_true_rollback_no_style

    import tkinter as tk
    from tkinter import ttk, scrolledtext, filedialog, messagebox
    import threading
    import os
    import sys
    import platform
    import subprocess
    import datetime
    # import json # Không cần nếu không load voices.json
    import traceback

    from .tts_logic import generate_tts_audio_multithreaded # Đảm bảo đây là tts_logic_v35...
    from .settings_manager import save_settings, load_settings, NUM_API_KEYS
    from .constants import GEMINI_TTS_VOICES, DEFAULT_VOICE, MIN_TEMPERATURE, MAX_TEMPERATURE, \
                        APP_NAME, APP_VERSION
    from .utils import get_resource_path

    class TTSApp:
        def __init__(self, root):
            self.root = root
            self.root.title(f"{APP_NAME} v{APP_VERSION}")
            # Điều chỉnh geometry lại vì đã bỏ style prompt frame
            self.root.geometry("700x800") 

            self.settings = load_settings()
            
            self.api_key_vars = []
            self.api_label_vars = []
            for i in range(NUM_API_KEYS):
                key_var = tk.StringVar(value=self.settings.get(f"api_key_{i+1}", ""))
                label_var = tk.StringVar(value=self.settings.get(f"label_{i+1}", f"API Key {i+1}"))
                self.api_key_vars.append(key_var)
                self.api_label_vars.append(label_var)

            self.selected_voice = tk.StringVar(value=self.settings.get("default_voice", DEFAULT_VOICE))
            self.temperature_var = tk.DoubleVar(value=self.settings.get("temperature", 1.0)) # Default 1.0
            self.output_dir_var = tk.StringVar(value=self.settings.get("save_dir", os.path.expanduser("~")))
            self.story_name_var = tk.StringVar(value="MyStory")
            
            # KHÔNG CÓ self.reading_style_prompt_var
            
            self.last_saved_output_dir = None
            self.thread_status_labels = []
            self.thread_progress_bars = []
            # self.num_parts_total_for_progress = 0 # Có thể không cần nữa nếu progress tổng dựa vào callback
            # self.num_parts_completed_for_progress = 0 
            # self.progress_lock = threading.Lock() 

            self._set_window_icon()
            self.notebook = ttk.Notebook(root)
            self.main_tab = ttk.Frame(self.notebook, padding="10")
            self.notebook.add(self.main_tab, text="Text-to-Speech")
            self.create_main_tab_widgets()
            self.settings_tab = ttk.Frame(self.notebook, padding="10")
            self.notebook.add(self.settings_tab, text="Settings")
            self.create_settings_tab_widgets()
            self.notebook.pack(expand=True, fill="both", padx=5, pady=5)
            self.update_word_count()

        def _set_window_icon(self):
            try:
                if sys.platform.startswith('win'):
                    icon_path = get_resource_path("icons/app_icon.ico")
                    if os.path.exists(icon_path): self.root.iconbitmap(icon_path)
                    else: self.log_message(f"Warning: Icon file not found at {icon_path}")
                else:
                    icon_path_png = get_resource_path("icons/app_icon.png")
                    if os.path.exists(icon_path_png):
                        photo = tk.PhotoImage(file=icon_path_png)
                        self.root.iconphoto(False, photo)
                    else: self.log_message(f"Warning: Icon file not found at {icon_path_png}")
            except Exception as e:
                self.log_message(f"Error setting window icon: {e}")

        def create_main_tab_widgets(self):
            frame = self.main_tab

            # --- Input Text Area --- (row 0)
            input_text_frame = ttk.LabelFrame(frame, text="Input Text", padding="10")
            input_text_frame.grid(row=0, column=0, sticky="ewns") # columnspan=1 nếu chỉ có 1 cột
            self.text_input = scrolledtext.ScrolledText(input_text_frame, wrap=tk.WORD, height=10)
            self.text_input.pack(expand=True, fill="both", padx=5, pady=5)
            self.text_input.bind("<KeyRelease>", self.update_word_count)
            self.word_count_label = ttk.Label(input_text_frame, text="Word count: 0")
            self.word_count_label.pack(side="left", pady=(0,5), padx=5)

            # --- Controls Frame (Generation Settings - row 1) ---
            controls_frame = ttk.LabelFrame(frame, text="Generation Settings", padding="10")
            controls_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
            ttk.Label(controls_frame, text="Select Voice:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.voice_dropdown = ttk.Combobox(controls_frame, textvariable=self.selected_voice, values=GEMINI_TTS_VOICES, state="readonly", width=30)
            self.voice_dropdown.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
            if self.selected_voice.get() not in GEMINI_TTS_VOICES and GEMINI_TTS_VOICES: self.selected_voice.set(GEMINI_TTS_VOICES[0])
            elif not GEMINI_TTS_VOICES: self.selected_voice.set("N/A")
            ttk.Label(controls_frame, text="Temperature:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
            self.temp_scale_val_label = ttk.Label(controls_frame, text=f"{self.temperature_var.get():.2f}", width=4, anchor="w")
            self.temp_scale_val_label.grid(row=1, column=2, padx=(0,5), pady=5, sticky="w")
            self.temp_scale = ttk.Scale(controls_frame, from_=MIN_TEMPERATURE, to=MAX_TEMPERATURE, variable=self.temperature_var, orient=tk.HORIZONTAL, command=lambda val: self.temp_scale_val_label.config(text=f"{float(val):.2f}"))
            self.temp_scale.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
            self.temperature_var.set(self.settings.get("temperature", 1.0)) # Default temp 1.0
            self.temp_scale_val_label.config(text=f"{self.temperature_var.get():.2f}")
            controls_frame.columnconfigure(1, weight=1)

            # --- Output File Settings Frame (row 2) ---
            output_settings_frame = ttk.LabelFrame(frame, text="Output File Settings", padding="10")
            output_settings_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
            ttk.Label(output_settings_frame, text="Output Directory:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.output_dir_entry = ttk.Entry(output_settings_frame, textvariable=self.output_dir_var, width=45)
            self.output_dir_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            self.browse_output_dir_button = ttk.Button(output_settings_frame, text="Browse...", command=self.browse_main_output_directory)
            self.browse_output_dir_button.grid(row=0, column=2, padx=5, pady=5)
            ttk.Label(output_settings_frame, text="Story/Base Name:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
            self.story_name_entry = ttk.Entry(output_settings_frame, textvariable=self.story_name_var, width=45)
            self.story_name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
            output_settings_frame.columnconfigure(1, weight=1)

            # --- Action Frame (row 3) ---
            action_buttons_frame = ttk.Frame(frame, padding="5")
            action_buttons_frame.grid(row=3, column=0, pady=(10,0), sticky="ew")
            self.generate_button = ttk.Button(action_buttons_frame, text="Generate Voice", command=self.start_tts_thread, style="Accent.TButton")
            self.generate_button.pack(side="left", padx=5)
            self.open_folder_button = ttk.Button(action_buttons_frame, text="Open Output Folder", command=self.open_last_output_folder, state="disabled")
            self.open_folder_button.pack(side="left", padx=5)

            # --- Progress Bars Frame (row 4) ---
            progress_frame = ttk.LabelFrame(frame, text="Progress", padding="10")
            progress_frame.grid(row=4, column=0, pady=10, sticky="ewns")
            overall_progress_subframe = ttk.Frame(progress_frame); overall_progress_subframe.pack(fill="x", expand=True, pady=(0,10))
            ttk.Label(overall_progress_subframe, text="Overall:").pack(side="left", padx=5)
            self.progress_bar_total = ttk.Progressbar(overall_progress_subframe, orient="horizontal", length=200, mode="determinate")
            self.progress_bar_total.pack(side="left", fill="x", expand=True, padx=5)
            self.thread_progress_bars = []; self.thread_status_labels = []
            for i in range(NUM_API_KEYS):
                thread_subframe = ttk.Frame(progress_frame); thread_subframe.pack(fill="x", expand=True, pady=2)
                api_label_for_thread = ttk.Label(thread_subframe, text=f"Thread {i+1} (Idle):", width=25, anchor="w") # Đã sửa width
                api_label_for_thread.pack(side="left", padx=5); self.thread_status_labels.append(api_label_for_thread)
                pb_thread = ttk.Progressbar(thread_subframe, orient="horizontal", length=150, mode="determinate")
                pb_thread.pack(side="left", fill="x", expand=True, padx=5); self.thread_progress_bars.append(pb_thread)
            progress_frame.columnconfigure(0, weight=1)

            # --- Log Area --- (row 5)
            log_frame = ttk.LabelFrame(frame, text="Log", padding="10")
            log_frame.grid(row=5, column=0, padx=5, pady=5, sticky="ewns")
            log_frame.rowconfigure(0, weight=1); log_frame.columnconfigure(0, weight=1)
            self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=8)
            self.log_area.grid(row=0, column=0, sticky="nsew", padx=(5,0), pady=5)
            self.clear_log_button = ttk.Button(log_frame, text="Clear Log", command=self.clear_log_area, width=10)
            self.clear_log_button.grid(row=0, column=1, sticky="ne", padx=(2,5), pady=5)
            
            # Row configure cho frame chính của tab
            frame.rowconfigure(0, weight=2) # Input text
            frame.rowconfigure(1, weight=0) # Generation Settings
            frame.rowconfigure(2, weight=0) # Output Settings
            frame.rowconfigure(3, weight=0) # Action Buttons
            frame.rowconfigure(4, weight=1) # Progress Bars
            frame.rowconfigure(5, weight=2) # Log Area
            frame.columnconfigure(0, weight=1)


        def create_settings_tab_widgets(self): # ... (giữ nguyên như main_app_v4.2) ...
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
            ttk.Label(general_settings_frame, text="Default Save Directory:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.settings_save_dir_entry = ttk.Entry(general_settings_frame, textvariable=self.output_dir_var, width=40)
            self.settings_save_dir_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            self.settings_browse_save_dir_button = ttk.Button(general_settings_frame, text="Browse...", command=self.browse_main_output_directory)
            self.settings_browse_save_dir_button.grid(row=0, column=2, padx=5, pady=5)
            general_settings_frame.columnconfigure(1, weight=1)

            self.save_settings_button = ttk.Button(frame, text="Save All Settings", command=self.save_app_settings, style="Accent.TButton")
            self.save_settings_button.grid(row=2, column=0, padx=5, pady=15)
            ttk.Label(frame, text="Note: API keys and settings are stored locally.").grid(row=3, column=0, padx=5, pady=5, sticky="w")
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
                    self.log_message(f"Opened folder: {self.last_saved_output_dir}")
                except Exception as e: self.log_message(f"Error opening folder: {e}"); messagebox.showerror("Error", f"Could not open folder: {self.last_saved_output_dir}\n{e}", parent=self.root)
            else: self.log_message("No output folder recorded or folder does not exist."); messagebox.showwarning("Info", "No output folder to open.", parent=self.root)

        def update_word_count(self, event=None):
            try:
                if self.root.winfo_exists() and hasattr(self, 'text_input') and self.text_input.winfo_exists():
                    content = self.text_input.get("1.0", tk.END).strip()
                    word_count = len(content.split()) if content else 0
                    self.word_count_label.config(text=f"Word count: {word_count}")
            except tk.TclError: pass

        def log_message(self, message: str):
            if not hasattr(self, 'log_area') or not self.log_area.winfo_exists(): print(f"LOG (UI not ready): {message}"); return
            def _log():
                if self.log_area.winfo_exists(): self.log_area.config(state="normal"); self.log_area.insert(tk.END, message + "\n"); self.log_area.see(tk.END); self.log_area.config(state="disabled")
            self.root.after_idle(_log)

        def update_overall_progress(self, value: int): # Đổi tên từ update_progress
            # print(f"DEBUG_UI: Overall Progress = {value}%")
            if hasattr(self, 'progress_bar_total') and self.progress_bar_total.winfo_exists():
                def _update():
                    if self.progress_bar_total.winfo_exists():
                        self.progress_bar_total["value"] = value
                self.root.after_idle(_update)

        def update_thread_progress(self, thread_index: int, percentage: int, status_message: str): # MỚI
            # print(f"DEBUG_UI: Thread {thread_index+1} Progress = {percentage}%, Status = {status_message}")
            if thread_index < len(self.thread_progress_bars) and \
            hasattr(self.thread_progress_bars[thread_index], 'winfo_exists') and \
            self.thread_progress_bars[thread_index].winfo_exists():
                def _update_pb():
                    if self.thread_progress_bars[thread_index].winfo_exists():
                        self.thread_progress_bars[thread_index]["value"] = percentage
                self.root.after_idle(_update_pb)

            if thread_index < len(self.thread_status_labels) and \
            hasattr(self.thread_status_labels[thread_index], 'winfo_exists') and \
            self.thread_status_labels[thread_index].winfo_exists():
                # Lấy label API key tương ứng
                api_label_text = "Unknown API"
                if thread_index < len(self.api_label_vars):
                    api_label_text = self.api_label_vars[thread_index].get() or f"API Key {thread_index+1}"

                def _update_lbl():
                    if self.thread_status_labels[thread_index].winfo_exists():
                        # Giữ lại label API, chỉ cập nhật status message và %
                        self.thread_status_labels[thread_index].config(text=f"{api_label_text[:15]}: {status_message} ({percentage}%)")
                self.root.after_idle(_update_lbl)


        def save_app_settings(self): # ... (giữ nguyên như main_app_v4.2) ...
            current_settings = {"default_voice": self.selected_voice.get(), "temperature": self.temperature_var.get(), "save_dir": self.output_dir_var.get()}
            for i in range(NUM_API_KEYS):
                current_settings[f"api_key_{i+1}"] = self.api_key_vars[i].get()
                current_settings[f"label_{i+1}"] = self.api_label_vars[i].get()
            if save_settings(current_settings):
                self.settings = current_settings; self.log_message("Settings saved successfully.")
                messagebox.showinfo("Settings", "Settings saved successfully!", parent=self.root)
            else:
                self.log_message("Failed to save settings."); messagebox.showerror("Error", "Failed to save settings.", parent=self.root)

        def start_tts_thread(self):
            text_to_convert = self.text_input.get("1.0", tk.END).strip()
            if not text_to_convert: messagebox.showerror("Input Error", "Please enter text.", parent=self.root); return
            
            active_keys_info_list = []
            for i in range(NUM_API_KEYS):
                key_val = self.api_key_vars[i].get().strip()
                if key_val: active_keys_info_list.append({"key": key_val, "label": self.api_label_vars[i].get().strip() or f"API Key {i+1}", "active_model_name": "models/gemini-2.5-pro-preview-tts"})
            if not active_keys_info_list: messagebox.showerror("API Key Error", f"Please set at least one API Key in Settings.", parent=self.root); self.notebook.select(self.settings_tab); return
            self.log_message(f"Found {len(active_keys_info_list)} active API Key(s).")

            output_dir = self.output_dir_var.get().strip(); story_base_name = self.story_name_var.get().strip()
            if not output_dir or not os.path.isdir(output_dir): messagebox.showerror("Output Error", "Invalid output directory.", parent=self.root); self.output_dir_entry.focus(); return
            if not story_base_name: messagebox.showerror("Output Error", "Please enter a Story/Base Name.", parent=self.root); self.story_name_entry.focus(); return
            
            selected_voice_for_filename = self.selected_voice.get().replace("-", "")
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_story_name = "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in story_base_name).rstrip()
            safe_voice_name = "".join(c if c.isalnum() else '' for c in selected_voice_for_filename)
            output_filename_only = f"{safe_voice_name}_{safe_story_name}_{timestamp}"
            output_file_path_base = os.path.normpath(os.path.join(output_dir, output_filename_only))
            
            self.log_message(f"Output base name: {output_filename_only}")
            # KHÔNG CÓ LOG CHO reading_style
            self.generate_button.config(state="disabled", text="Generating...")
            if hasattr(self, 'open_folder_button'): self.open_folder_button.config(state="disabled")
            self.root.config(cursor="watch")
            self.update_overall_progress(0)
            for i in range(NUM_API_KEYS):
                # api_label_for_ui = self.api_label_vars[i].get().strip() or f"API Key {i+1}" # Không cần thiết ở đây nữa
                if i < len(active_keys_info_list): 
                    self.update_thread_progress(i, 0, "Ready")
                    self.thread_status_labels[i].config(text=f"{active_keys_info_list[i]['label'][:15]}: Ready")
                else: 
                    self.update_thread_progress(i, 0, "Idle")
                    self.thread_status_labels[i].config(text=f"Thread {i+1} (Idle):")

            thread = threading.Thread(
                target=self._tts_task_wrapper,
                args=(
                    text_to_convert, 
                    self.selected_voice.get(), 
                    output_file_path_base, 
                    self.temperature_var.get() # temp_setting từ UI, đảm bảo là 1.0
                ),
                daemon=True
            )
            thread.start()

        # _tts_task_wrapper KHÔNG CÒN NHẬN reading_style
        def _tts_task_wrapper(self, text_to_convert, voice, output_file_base, temp):
            self.last_saved_output_dir = None
            try:
                active_keys_info_for_logic = []
                for i in range(NUM_API_KEYS):
                    key_val = self.api_key_vars[i].get().strip()
                    if key_val: active_keys_info_for_logic.append({"key": key_val, "label": self.api_label_vars[i].get().strip() or f"API Key {i+1}", "active_model_name": "models/gemini-2.5-pro-preview-tts"})
                
                if not active_keys_info_for_logic: 
                    self.log_message("No active API keys for the TTS task (wrapper).")
                    # ... (finalize UI error như cũ) ...
                    return

                thread_specific_callbacks = []
                if not hasattr(self, 'thread_progress_bars'): self.thread_progress_bars = []
                if not hasattr(self, 'thread_status_labels'): self.thread_status_labels = []
                for i in range(len(active_keys_info_for_logic)):
                    def create_callback(thread_idx_captured):
                        def _update_ui_for_thread(percentage, status_msg):
                            self.update_thread_progress(thread_idx_captured, percentage, status_msg)
                        return _update_ui_for_thread
                    thread_specific_callbacks.append(create_callback(i))
                while len(thread_specific_callbacks) < len(active_keys_info_for_logic):
                    thread_specific_callbacks.append(lambda ti, p, msg: None)

                # Lấy các giá trị từ settings hoặc dùng default
                temp = self.temperature_var.get() # Lấy temperature từ UI
                max_words = self.settings.get("max_words_per_part", 1000) 
                token_fallback = self.settings.get("max_tokens_fallback", 4800) 
                retries = self.settings.get("max_retries_per_part", 1) 
                timeout = self.settings.get("part_timeout", 360) 
                
                success, final_file_path = generate_tts_audio_multithreaded( 
                    active_keys_info_for_logic,
                    text_to_convert,
                    # "", # reading_style_prompt đã bị bỏ khỏi định nghĩa hàm generate_tts_audio_multithreaded trong v35
                    voice, 
                    output_file_base, 
                    self.log_message, 
                    self.update_overall_progress,
                    thread_specific_callbacks,
                    # BẮT ĐẦU TRUYỀN DƯỚI DẠNG KEYWORD ARGUMENTS TỪ ĐÂY
                    temp_setting=temp, # Sử dụng tên tham số rõ ràng
                    max_words_per_part=int(max_words),
                    max_tokens_fallback=int(token_fallback),
                    max_retries_per_part=int(retries),
                    part_timeout=int(timeout)
                )
                
                if success and final_file_path:
                    self.log_message(f"TTS task completed successfully. Final file: {final_file_path}")
                    self.last_saved_output_dir = os.path.dirname(final_file_path)
                elif success:
                    self.log_message("TTS task reported success but no final file path was returned.")
                else:
                    self.log_message("TTS task failed or did not complete.")
            except Exception as e:
                self.log_message(f"Unhandled error in TTS task wrapper: {e}")
                self.log_message(traceback.format_exc()) 
            finally: # ... (giữ nguyên finalize_ui)
                def _finalize_ui(): 
                    if hasattr(self, 'generate_button') and self.generate_button.winfo_exists(): self.generate_button.config(state="normal", text="Generate Voice")
                    if hasattr(self, 'root') and self.root.winfo_exists(): self.root.config(cursor="")
                    if self.last_saved_output_dir and hasattr(self, 'open_folder_button') and self.open_folder_button.winfo_exists(): self.open_folder_button.config(state="normal")
                    for i in range(NUM_API_KEYS): 
                        if hasattr(self, 'thread_status_labels') and i < len(self.thread_status_labels) and self.thread_status_labels[i].winfo_exists(): self.thread_status_labels[i].config(text=f"Thread {i+1} (Idle):")
                        if hasattr(self, 'thread_progress_bars') and i < len(self.thread_progress_bars) and self.thread_progress_bars[i].winfo_exists(): self.thread_progress_bars[i]["value"] = 0
                if hasattr(self, 'root') and self.root.winfo_exists(): self.root.after_idle(_finalize_ui)
    ```

* **`tts_logic.py` (phiên bản `tts_logic_v35_exact_stable_wav_no_poison` - Không POISON_PILL, dùng config dictionary, output WAV, temperature=1.0):**
    ```python
    # src/gemini_tts_app/tts_logic.py
    # Phiên bản: tts_logic_v35_exact_stable_wav_no_poison

    import mimetypes
    import os
    import struct
    import traceback
    import json
    import base64
    import time
    import queue 
    import threading

    import google.generativeai as genai
    from google.generativeai import types
    from google.api_core import exceptions as core_exceptions
    from pydub import AudioSegment

    gemini_api_config_lock = threading.Lock()
    # KHÔNG CÓ POISON_PILL Ở ĐÂY

    # --- Các hàm tiện ích (GIỮ NGUYÊN) ---
    # --- (Dán lại đầy đủ các hàm tiện ích từ phiên bản v34) ---
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
        if log_callback: log_callback(f"Attempting to add WAV header. Assumed original format (for params): '{assumed_pcm_mime_type}'. Data size: {len(audio_data)}")
        parameters = parse_audio_mime_type(assumed_pcm_mime_type)
        bits_per_sample = parameters.get("bits_per_sample", 16); sample_rate = parameters.get("rate", 24000)
        num_channels = 1; data_size = len(audio_data);
        if data_size == 0:
            if log_callback: log_callback("Cannot convert empty audio data to WAV.")
            return None
        bytes_per_sample = bits_per_sample // 8
        block_align = num_channels * bytes_per_sample; byte_rate = sample_rate * block_align
        riff_chunk_data_size = 4 + (8 + 16) + (8 + data_size)
        header = struct.pack("<4sI4s4sIHHIIHH4sI", b"RIFF", riff_chunk_data_size, b"WAVE", b"fmt ", 16, 1, num_channels, sample_rate, byte_rate, block_align, bits_per_sample, b"data", data_size)
        if log_callback: log_callback(f"WAV header generated (sample_rate={sample_rate}, bits_per_sample={bits_per_sample}). Header size: {len(header)}")
        return header + audio_data
    def count_tokens_for_model(model_instance: genai.GenerativeModel, text_or_content, log_callback=None) -> int | None:
        try:
            token_count_obj = model_instance.count_tokens(text_or_content)
            if hasattr(token_count_obj, 'total_tokens'): return token_count_obj.total_tokens
            else:
                if log_callback: log_callback(f"Unexpected response type from count_tokens: {type(token_count_obj)}")
                return None
        except Exception as e:
            if log_callback: log_callback(f"Error counting tokens for: '{str(text_or_content)[:50]}...': {e}")
            return None
    def count_words(text: str) -> int:
        if not text: return 0
        return len(text.split())
    def split_text_into_chunks(model_instance: genai.GenerativeModel, full_text: str, max_words_per_chunk: int, max_tokens_fallback: int, log_callback=None) -> list[str]:
        if log_callback: log_callback(f"Splitting text (length: {len(full_text)} chars, ~{count_words(full_text)} words) into chunks of max ~{max_words_per_chunk} words, fallback max ~{max_tokens_fallback} tokens.")
        chunks = []; current_char_offset = 0
        while current_char_offset < len(full_text):
            words_in_remaining_text = full_text[current_char_offset:].split()
            current_chunk_words = words_in_remaining_text[:max_words_per_chunk]
            candidate_chunk_text = " ".join(current_chunk_words)
            end_char_offset_candidate = current_char_offset + len(candidate_chunk_text) 
            if current_chunk_words:
                temp_search_offset = current_char_offset
                for i, word in enumerate(current_chunk_words):
                    found_pos = full_text.find(word, temp_search_offset)
                    if found_pos != -1: temp_search_offset = found_pos + len(word)
                    else: temp_search_offset = current_char_offset + len(" ".join(current_chunk_words[:i+1])); break 
                end_char_offset_candidate = temp_search_offset
            text_for_token_check = full_text[current_char_offset : end_char_offset_candidate]
            num_tokens = count_tokens_for_model(model_instance, text_for_token_check, log_callback)
            while (num_tokens is None or num_tokens > max_tokens_fallback) and len(current_chunk_words) > 1:
                current_chunk_words = current_chunk_words[:-10] 
                if not current_chunk_words: break 
                current_chunk_text_candidate = " ".join(current_chunk_words)
                temp_search_offset = current_char_offset
                for i, word in enumerate(current_chunk_words):
                    found_pos = full_text.find(word, temp_search_offset)
                    if found_pos != -1: temp_search_offset = found_pos + len(word)
                    else: temp_search_offset = current_char_offset + len(" ".join(current_chunk_words[:i+1])); break
                end_char_offset_candidate = temp_search_offset
                text_for_token_check = full_text[current_char_offset : end_char_offset_candidate]
                num_tokens = count_tokens_for_model(model_instance, text_for_token_check, log_callback)
            final_text_segment = full_text[current_char_offset : end_char_offset_candidate]
            actual_end_char_offset = end_char_offset_candidate
            if end_char_offset_candidate < len(full_text):
                best_split_pos = -1; pos = final_text_segment.rfind("\n\n")
                if pos != -1: best_split_pos = pos + 2
                else:
                    pos = final_text_segment.rfind("\n")
                    if pos != -1: best_split_pos = pos + 1
                    else:
                        for punc in ['.', '!', '?']:
                            pos = final_text_segment.rfind(punc)
                            if pos > best_split_pos : best_split_pos = pos + 1
                if best_split_pos != -1 and best_split_pos > len(final_text_segment) * 0.5 : 
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
    def merge_audio_files(audio_file_paths: list[str], output_merged_path: str, output_format: str = "wav", log_callback=None) -> bool:
        if not audio_file_paths:
            if log_callback: log_callback("No audio files to merge.")
            return False
        actual_files_to_merge = [f for f in audio_file_paths if f and os.path.exists(os.path.normpath(f))]
        if not actual_files_to_merge:
            if log_callback: log_callback("No valid audio part files found to merge after checking existence.")
            return False
        norm_output_merged_path = os.path.normpath(output_merged_path)
        if log_callback: log_callback(f"Merging {len(actual_files_to_merge)} audio files into {norm_output_merged_path} (as {output_format}).") # output_format sẽ là "wav"
        try:
            combined_audio = AudioSegment.empty()
            for i, file_path in enumerate(actual_files_to_merge):
                try:
                    segment = AudioSegment.from_file(file_path) 
                    combined_audio += segment
                except Exception as e_segment:
                    if log_callback: log_callback(f"Error loading audio segment {os.path.basename(file_path)}: {e_segment}. Skipping this segment.")
            if len(combined_audio) == 0: 
                if log_callback: log_callback("No valid audio segments were successfully combined.")
                return False
            output_dir_final = os.path.dirname(norm_output_merged_path)
            if not os.path.exists(output_dir_final): os.makedirs(output_dir_final, exist_ok=True)
            
            combined_audio.export(norm_output_merged_path, format="wav") # LUÔN EXPORT WAV
            if log_callback: log_callback(f"Successfully merged audio to (WAV): {norm_output_merged_path}")
            return True
        except Exception as e:
            if log_callback: log_callback(f"Error merging audio files: {e}\n{traceback.format_exc()}")
            return False
    # --- Kết thúc các hàm tiện ích ---

    # --- Hàm _generate_audio_for_single_chunk (phiên bản v25.1_base_logic - đã hoạt động tốt) ---
    def _generate_audio_for_single_chunk(
        model_instance: genai.GenerativeModel,
        text_chunk: str,
        # reading_style_prompt BỊ LOẠI BỎ
        voice_name: str,
        part_filename_base: str, 
        part_num: int,
        total_parts: int,
        temp_setting: float, # Sẽ là 1.0
        max_retries: int,
        part_timeout: int,
        log_callback_main, 
        progress_callback_part
        ) -> tuple[str | None, float]: 

        part_start_time = time.time()
        text_for_api = text_chunk # Không còn reading_style_prompt
        
        log_callback_main(f"Part {part_num}/{total_parts}, Attempt 1/{max_retries + 1}: Requesting STREAMING audio for text (len: {len(text_for_api)}), Voice: '{voice_name}', Temp: {temp_setting}")
        progress_callback_part(0, "Requesting") 
        
        tts_contents_as_dict = [{"role": "user", "parts": [{"text": text_for_api}]}]
        
        ai_studio_config_dict = {
            "temperature": temp_setting, 
            "response_modalities": ["AUDIO"], 
            "speech_config": {
                "voice_config": {
                    "prebuilt_voice_config": {"voice_name": voice_name}
                }
            }
        }
        request_options_for_part = types.RequestOptions(timeout=part_timeout) 

        for attempt in range(max_retries + 1):
            try:
                if attempt > 0: 
                    log_callback_main(f"Part {part_num}, Attempt {attempt + 1}/{max_retries + 1}: Requesting audio stream...")
                    progress_callback_part(0, f"Retrying ({attempt+1})")
                
                response_stream = model_instance.generate_content(
                    contents=tts_contents_as_dict,
                    generation_config=ai_studio_config_dict,
                    stream=True,
                    request_options=request_options_for_part
                )
                progress_callback_part(10, "Processing stream")

                all_audio_data_part = bytearray()
                final_mime_type_part = "audio/wav" 
                first_audio_processed_part = False
                stream_chunk_count = 0
                
                for chunk_idx, chunk in enumerate(response_stream): 
                    stream_chunk_count += 1
                    # ... (log progress stream như cũ) ...

                    if hasattr(chunk, 'parts') and chunk.parts:
                        for i_part_obj, part_obj in enumerate(chunk.parts):
                            part_mime_attr = getattr(part_obj, 'mime_type', None)
                            current_part_audio_data = None
                            if hasattr(part_obj, 'inline_data') and part_obj.inline_data and hasattr(part_obj.inline_data, 'data'):
                                data_from_inline = part_obj.inline_data.data
                                if isinstance(data_from_inline, str):
                                    try: data_from_inline = base64.b64decode(data_from_inline)
                                    except Exception: continue
                                if isinstance(data_from_inline, bytes): current_part_audio_data = data_from_inline
                            
                            if current_part_audio_data:
                                all_audio_data_part.extend(current_part_audio_data)
                                if not first_audio_processed_part:
                                    if part_mime_attr and part_mime_attr != 'N/A' and part_mime_attr.startswith("audio/"):
                                        final_mime_type_part = part_mime_attr 
                                    first_audio_processed_part = True
                
                if not all_audio_data_part: 
                    log_callback_main(f"Error: No audio data collected for Part {part_num}, Attempt {attempt + 1} after {stream_chunk_count} stream chunks.")
                    if 'chunk' in locals() and chunk and hasattr(chunk, 'prompt_feedback') and chunk.prompt_feedback: log_callback_main(f"  Prompt feedback from last chunk: {chunk.prompt_feedback}")
                    raise genai.types.generation_types.StopCandidateException("No audio data in stream for part")

                progress_callback_part(85, "Finalizing audio")
                data_buffer_to_save_part = bytes(all_audio_data_part)
                
                part_file_full_path_norm = os.path.normpath(f"{part_filename_base}.wav") # Luôn là .wav

                is_already_wav_part = data_buffer_to_save_part.startswith(b'RIFF') and data_buffer_to_save_part[8:12] == b'WAVE'
                if not is_already_wav_part:
                    assumed_pcm_format_part = "audio/L16;rate=24000" if final_mime_type_part.lower() == "audio/wav" else final_mime_type_part
                    converted_buffer_part = convert_to_wav(data_buffer_to_save_part, assumed_pcm_format_part, log_callback_main)
                    if converted_buffer_part: data_buffer_to_save_part = converted_buffer_part
                    else: log_callback_main(f"Warning: Failed to add WAV header for Part {part_num}.")
                
                if save_binary_file(part_file_full_path_norm, data_buffer_to_save_part, log_callback_main):
                    part_time_taken = time.time() - part_start_time
                    log_callback_main(f"Part {part_num}/{total_parts} (Attempt {attempt+1}) saved: {os.path.basename(part_file_full_path_norm)} (MIME: {final_mime_type_part}, took {part_time_taken:.2f}s)")
                    progress_callback_part(100, "Done")
                    return part_file_full_path_norm, part_time_taken
                else: 
                    log_callback_main(f"Error: Failed to save audio for Part {part_num}, Attempt {attempt + 1}.")
            
            except (core_exceptions.InternalServerError, core_exceptions.ServiceUnavailable, core_exceptions.ResourceExhausted, core_exceptions.DeadlineExceeded, genai.types.generation_types.StopCandidateException) as e_retryable: 
                log_callback_main(f"Part {part_num}, Attempt {attempt + 1} FAILED with retryable error: {e_retryable.__class__.__name__}: {str(e_retryable)[:200]}")
                if attempt < max_retries:
                    wait_time = 1.0 * (2**attempt); log_callback_main(f"Retrying Part {part_num} in {wait_time:.1f}s..."); progress_callback_part(0, f"Retrying in {wait_time:.1f}s"); time.sleep(wait_time)
                else:
                    log_callback_main(f"Part {part_num} FAILED after {max_retries + 1} attempts due to {e_retryable.__class__.__name__}."); progress_callback_part(0, "Failed (retries exc.)"); part_time_taken = time.time() - part_start_time; return None, part_time_taken
            except Exception as e_part_gen: 
                log_callback_main(f"Part {part_num} FAILED with NON-retryable error on attempt {attempt + 1}: {e_part_gen.__class__.__name__}: {e_part_gen}"); log_callback_main(traceback.format_exc()); progress_callback_part(0, "Error (non-retryable)"); part_time_taken = time.time() - part_start_time; return None, part_time_taken
        part_time_taken = time.time() - part_start_time; log_callback_main(f"Part {part_num} could not be generated after all attempts (took {part_time_taken:.2f}s)."); # ... (như cũ)
        return None, part_time_taken

    # --- HÀM WORKER CHO THREAD (phiên bản v24_base - KHÔNG POISON_PILL, timeout exit) ---
    def _process_text_chunk_worker(
        api_key_info: dict, job_queue: queue.Queue, results_list: list, 
        thread_id: int, 
        # reading_style_prompt BỊ LOẠI BỎ
        voice_name: str, temp_audio_dir: str, 
        base_filename_no_ext: str, total_chunks: int, temp_setting: float,
        max_retries_per_part: int, part_timeout: int,
        log_callback_ui, progress_callback_ui_thread,
        part_times_list: list, api_key_config_lock: threading.Lock 
        ):
        model_instance_for_thread = None
        worker_label = f"[Thread-{thread_id+1} ({api_key_info.get('label','Key')[:15]})]" 
        try:
            with api_key_config_lock: # Quan trọng cho thread safety
                genai.configure(api_key=api_key_info["key"])
                model_instance_for_thread = genai.GenerativeModel(model_name=api_key_info["active_model_name"])
            log_callback_ui(f"{worker_label} Worker ready. Model: '{model_instance_for_thread.model_name}'")
        except Exception as e_model_init:
            log_callback_ui(f"{worker_label} FATAL: Error initializing model: {e_model_init}")
            return 

        consecutive_empty_gets = 0
        MAX_CONSECUTIVE_EMPTY_TIMEOUTS = 5 # Worker sẽ thoát sau bao nhiêu lần timeout liên tiếp

        while True: 
            part_index = -1 
            try:
                part_index, text_chunk = job_queue.get(block=True, timeout=1.0) # Timeout 1 giây
                consecutive_empty_gets = 0 # Reset counter nếu nhận được job

                # log_callback_ui(f"{worker_label} Picked up Part {part_index + 1}/{total_chunks}.") # Bớt log
                def _part_progress_update_for_worker(percentage, status_message):
                    progress_callback_ui_thread(percentage, status_message)

                part_filename_base_for_chunk = os.path.normpath(os.path.join(temp_audio_dir, f"{base_filename_no_ext}_part_{part_index + 1:03d}"))
                
                file_path, time_taken = _generate_audio_for_single_chunk(
                    model_instance_for_thread, text_chunk, 
                    # "" CHO reading_style_prompt VÌ ĐÃ BỎ
                    voice_name,
                    part_filename_base_for_chunk, part_index + 1, total_chunks,
                    temp_setting, max_retries_per_part, part_timeout,
                    log_callback_ui, _part_progress_update_for_worker
                )
                results_list[part_index] = file_path 
                part_times_list[part_index] = time_taken
                
                job_queue.task_done() # QUAN TRỌNG
                
                if file_path: log_callback_ui(f"{worker_label} Part {part_index + 1} result: SUCCESS (took {time_taken:.2f}s).")
                else: log_callback_ui(f"{worker_label} Part {part_index + 1} result: FAILED (took {time_taken:.2f}s).")
            
            except queue.Empty: 
                consecutive_empty_gets += 1
                # log_callback_ui(f"{worker_label} Job queue empty on timeout ({consecutive_empty_gets}/{MAX_CONSECUTIVE_EMPTY_TIMEOUTS}).")
                if consecutive_empty_gets >= MAX_CONSECUTIVE_EMPTY_TIMEOUTS:
                    log_callback_ui(f"{worker_label} Job queue confirmed empty by multiple timeouts. Worker exiting.")
                    break # Thoát vòng lặp while True
                # Nếu chưa đủ số lần timeout liên tiếp, tiếp tục vòng lặp để thử get() lại
                continue 
            except Exception as e_worker_loop: 
                log_callback_ui(f"{worker_label} CRITICAL Error in worker's main loop for Part {part_index + 1 if part_index != -1 else 'Unknown'}: {e_worker_loop}")
                log_callback_ui(traceback.format_exc())
                if part_index != -1: 
                    results_list[part_index] = None 
                    part_times_list[part_index] = -1.0
                try: # Vẫn cố gắng task_done nếu đã get được item trước khi lỗi
                    if not isinstance(e_worker_loop, queue.Empty) and part_index != -1 :
                        job_queue.task_done() 
                        log_callback_ui(f"{worker_label} Called task_done() after critical error for Part {part_index + 1}.")
                except ValueError: 
                    log_callback_ui(f"{worker_label} Error calling task_done() after exception.")
                break # Thoát vòng lặp nếu có lỗi nghiêm trọng khác
                
        log_callback_ui(f"{worker_label} Worker loop finished.")


    # --- Hàm generate_tts_audio ĐIỀU PHỐI CHÍNH (phiên bản v35.1 - KHÔNG POISON_PILL, output WAV) ---
    def generate_tts_audio_multithreaded(
                        active_api_keys_info: list[dict], 
                        text_to_speak: str, 
                        # reading_style_prompt BỊ LOẠI BỎ
                        voice_name: str,
                        output_file_path_base: str, 
                        log_callback_ui, 
                        progress_callback_ui_total, progress_callbacks_ui_thread: list,
                        temp_setting: float = 1.0, # Mặc định temperature là 1.0
                        max_words_per_part: int = 1000, 
                        max_tokens_fallback: int = 4800, 
                        max_retries_per_part: int = 1, # Giữ lại 1 retry
                        part_timeout: int = 360 # 6 phút
                        ):
        total_start_time = time.time()
        log_callback_ui(f"--- generate_tts_audio_multithreaded_v35.1_exact_stable_wav called ---")
        log_callback_ui(f"Output will be WAV. NO POISON PILL. Temp: {temp_setting}")
        
        # ... (Phần đầu hàm giữ nguyên như v33.1: kiểm tra, tạo temp_dir, configure key đầu tiên, tạo model_for_splitting, chia text) ...
        if not active_api_keys_info: log_callback_ui("No active API Keys provided."); progress_callback_ui_total(0); return False, None
        if not text_to_speak.strip(): log_callback_ui("Input text is empty."); progress_callback_ui_total(0); return False, None
        progress_callback_ui_total(2); norm_output_file_path_base = os.path.normpath(output_file_path_base)
        output_dir = os.path.dirname(norm_output_file_path_base); base_filename_no_ext = os.path.basename(norm_output_file_path_base)
        temp_audio_dir = os.path.normpath(os.path.join(output_dir, f"{base_filename_no_ext}_parts_temp"))
        try:
            if not os.path.exists(temp_audio_dir): os.makedirs(temp_audio_dir); log_callback_ui(f"Created temp dir: {temp_audio_dir}")
        except Exception as e_mkdir: log_callback_ui(f"Error creating temp dir {temp_audio_dir}: {e_mkdir}"); progress_callback_ui_total(0); return False, None
        initial_api_key_info = active_api_keys_info[0]; model_for_splitting = None; # api_key_config_lock đã khai báo global
        try:
            with gemini_api_config_lock: 
                genai.configure(api_key=initial_api_key_info["key"])
                model_for_splitting = genai.GenerativeModel(model_name=initial_api_key_info["active_model_name"])
            log_callback_ui(f"Primary model for splitting text (API: '{initial_api_key_info['label']}') created.")
        except Exception as e_init_model:
            log_callback_ui(f"Error initializing model for text splitting: {e_init_model}"); progress_callback_ui_total(0); return False, None
        progress_callback_ui_total(5); log_callback_ui("Splitting text by words (with token fallback)...")
        text_chunks = split_text_into_chunks(model_for_splitting, text_to_speak, max_words_per_part, max_tokens_fallback, log_callback_ui)
        if not text_chunks: log_callback_ui("Text could not be split."); progress_callback_ui_total(0); return False, None
        total_chunks = len(text_chunks); log_callback_ui(f"Text split into {total_chunks} chunk(s). Adding to job queue..."); progress_callback_ui_total(10)
        
        job_queue = queue.Queue()
        for i, chunk_text in enumerate(text_chunks): 
            job_queue.put((i, chunk_text))
        
        # KHÔNG THÊM POISON_PILL VÀO QUEUE
        log_callback_ui(f"All {total_chunks} jobs added to queue. Initial queue size: {job_queue.qsize()}. NO POISON PILLS.")
        
        results_list = [None] * total_chunks; part_times_list = [-1.0] * total_chunks; threads = []
        num_worker_threads = len(active_api_keys_info)
        log_callback_ui(f"Initializing {num_worker_threads} worker threads...")
        for i in range(num_worker_threads):
            api_key_info_for_thread = active_api_keys_info[i]
            if "active_model_name" not in api_key_info_for_thread: api_key_info_for_thread["active_model_name"] = "models/gemini-2.5-pro-preview-tts" 
            thread_progress_callback = progress_callbacks_ui_thread[i] if i < len(progress_callbacks_ui_thread) else lambda pct,stat_msg: None
            worker_thread = threading.Thread(
                target=_process_text_chunk_worker, 
                args=(
                    api_key_info_for_thread, job_queue, results_list, i, 
                    # Bỏ reading_style_prompt khỏi args
                    voice_name, temp_audio_dir, base_filename_no_ext, total_chunks, 
                    temp_setting, max_retries_per_part, part_timeout, 
                    log_callback_ui, thread_progress_callback, 
                    part_times_list, gemini_api_config_lock
                ), 
                daemon=True # Worker threads là daemon
            )
            threads.append(worker_thread); worker_thread.start()
            log_callback_ui(f"Thread {i+1} (API: '{api_key_info_for_thread['label']}') has been started.")
        
        log_callback_ui("All worker threads started. Waiting for job queue to be processed (job_queue.join())...")
        job_queue.join() # Chờ cho đến khi tất cả các item trong queue được get và task_done
        log_callback_ui("Job queue processing complete. Waiting for threads to fully terminate (thread.join())..."); 
        for t_idx, t in enumerate(threads):
            t.join(timeout=part_timeout + 10) # Cho thread một chút thời gian để thoát sau khi queue rỗng
            if t.is_alive(): log_callback_ui(f"Warning: Thread {t_idx+1} is still alive after join timeout.")
        log_callback_ui("All worker threads should be terminated now.")

        # ... (Phần còn lại của hàm: log thời gian, merge WAV, cleanup giữ nguyên như v33.1, chỉ đảm bảo output là WAV) ...
        for idx, p_time in enumerate(part_times_list): 
            if p_time >= 0: log_callback_ui(f"  Part {idx+1} processing time: {p_time:.2f}s")
            else: log_callback_ui(f"  Part {idx+1} did not complete or time not recorded.")
        actual_generated_files_ordered = [results_list[i] for i in range(total_chunks) if results_list[i] and os.path.exists(os.path.normpath(results_list[i]))]
        if len(actual_generated_files_ordered) != total_chunks:
            failed_parts_indices = [i+1 for i, path in enumerate(results_list) if not path or not os.path.exists(os.path.normpath(path) if path else "")]
            log_callback_ui(f"Error: {len(failed_parts_indices)} part(s) failed or missing: {failed_parts_indices}. Generated: {len(actual_generated_files_ordered)}/{total_chunks}. Cannot merge.")
            progress_callback_ui_total(0); return False, None 
        progress_callback_ui_total(90); log_callback_ui("All parts generated successfully. Starting merge process (WAV)...")
        
        final_output_filename_with_ext = os.path.normpath(f"{norm_output_file_path_base}.wav") # Luôn là .wav
        
        if merge_audio_files(actual_generated_files_ordered, final_output_filename_with_ext, "wav", log_callback_ui):
            total_time_taken = time.time() - total_start_time
            log_callback_ui(f"Successfully merged all parts into WAV: {final_output_filename_with_ext} (Total time: {total_time_taken:.2f}s)")
            progress_callback_ui_total(100)
            try: 
                for part_file in actual_generated_files_ordered: os.remove(os.path.normpath(part_file))
                os.rmdir(temp_audio_dir)
                log_callback_ui("Temporary files cleaned up.")
            except Exception as e_cleanup: log_callback_ui(f"Warning: Could not clean up temp files: {e_cleanup}")
            return True, final_output_filename_with_ext
        else:
            log_callback_ui("Error: Failed to merge audio parts."); progress_callback_ui_total(0); return False, None
    ```

## Phần 3: Hướng dẫn Chạy Dự án và Yêu cầu Cụ Thể

### 3.1. Hướng dẫn Chạy Dự án (Người dùng sẽ đảm bảo môi trường sẵn sàng):
1.  Mở Terminal hoặc PowerShell.
2.  Di chuyển đến thư mục gốc của dự án: `cd path/to/gemini_tts_gui`
3.  Kích hoạt môi trường ảo: `.\venv\Scripts\activate` (Windows) hoặc `source venv/bin/activate` (macOS/Linux).
4.  Đảm bảo các thư viện trong `requirements.txt` đã được cài (`google-generativeai==0.8.5`, `pydub`, `appdirs`, và `audioop-lts` do người dùng dùng Python 3.13).
5.  Chạy ứng dụng: `python run.py`

### 3.2. Yêu cầu về Cấu trúc Phản hồi của AI (QUAN TRỌNG):
Khi bạn (Gemini) cung cấp các thay đổi về code hoặc phiên bản code mới, vui lòng tuân theo cấu trúc sau để đảm bảo sự rõ ràng và dễ theo dõi:

1.  **Phân tích Yêu cầu/Log Lỗi (NẾU CÓ):**
    * Phân tích chi tiết yêu cầu của người dùng hoặc log lỗi được cung cấp.
    * Đưa ra các nhận định, giả thuyết về nguyên nhân.
    * Đề xuất hướng giải quyết tổng quan.

2.  **Tên Phiên Bản Rõ Ràng (CHO CODE MỚI):**
    * **Toàn bộ file:** Nếu có nhiều thay đổi trong một file, hãy đặt tên phiên bản cho toàn bộ file ở đầu khối code, ví dụ:
        * `# src/gemini_tts_app/tts_logic.py`
        * `# Phiên bản: tts_logic_v[SốPhiênBảnChính]_[MôTảNgắnGọn]`
    * **Hàm cụ thể:** Nếu chỉ sửa đổi một hoặc vài hàm trong một file lớn, hãy đặt tên phiên bản cho từng hàm đó, ví dụ:
        * `# --- Hàm generate_tts_audio_multithreaded (phiên bản generate_tts_audio_multithreaded_v[Số].[SốPhụ]_[MôTảNgắnGọn]) ---`

3.  **Cung cấp Code (CHO CODE MỚI):**
    * **Luôn ưu tiên cung cấp TOÀN BỘ NỘI DUNG FILE đã cập nhật** (cho các file chính như `tts_logic.py`, `main_app.py` khi có thay đổi). Điều này giúp người dùng copy và paste một lần, thay thế hoàn toàn file cũ, tránh lỗi do copy thiếu hoặc sai vị trí. Chỉ khi file thực sự quá lớn và thay đổi rất nhỏ mới cân nhắc chỉ cung cấp đoạn code.
    * Sử dụng khối code Markdown (```python ... ```) rõ ràng.

4.  **Giải thích Thay đổi (CHO CODE MỚI):**
    * Liệt kê rõ ràng những thay đổi chính đã được thực hiện trong phiên bản code đó so với phiên bản trước.
    * Giải thích lý do cho những thay đổi đó.

5.  **Hướng dẫn Hành động cho Người dùng (SAU KHI CUNG CẤP CODE MỚI):**
    * Chỉ rõ người dùng cần làm gì:
        * "COPY & PASTE toàn bộ nội dung code mới cho file `[tên_file]` ở trên."
        * "Cập nhật các dòng sau trong hàm `[tên_hàm]` của file `[tên_file]` (nếu chỉ cung cấp đoạn sửa)."
        * "Chạy lại ứng dụng."
        * "Thử nghiệm với [kịch_bản_cụ_thể]."
        * "Quan sát log và cung cấp lại [thông_tin_cụ_thể]."
    * Nếu có các thay đổi liên quan đến nhiều file, hướng dẫn rõ ràng.

6.  **Kỳ vọng Kết quả (CHO CODE MỚI):**
    * Nêu rõ kết quả mong đợi sau khi áp dụng thay đổi (ví dụ: "Lỗi X sẽ không còn", "Tính năng Y sẽ hoạt động", "Log sẽ hiển thị Z", "File audio tạo ra sẽ có chất lượng Y").

### 3.3. Yêu cầu Cụ Thể cho Cuộc Trò Chuyện Mới (theo thứ tự ưu tiên):

**Sau khi AI mới đã đọc và hiểu toàn bộ thông tin trên (bao gồm code người dùng sẽ dán vào các placeholder ở Phần 2.5), yêu cầu đầu tiên là:**

1.  **Tích hợp "Reading Style Prompt":**
    * Người dùng đã xác nhận rằng việc thêm chỉ dẫn văn phong vào đầu prompt (ví dụ: "Hãy đọc đoạn sau với giọng thật vui vẻ: [nội dung text]") có tác dụng với model `models/gemini-2.5-pro-preview-tts`.
    * **Yêu cầu cụ thể cho AI:**
        * **Trong `main_app.py`:** Hướng dẫn người dùng (hoặc cung cấp code cập nhật) để thêm một ô `ttk.Entry` (một dòng là đủ) cho "Reading Style Prompt" (có thể đặt phía trên phần "Generation Settings"). Giá trị này có thể để trống.
        * Giá trị từ ô nhập này sẽ được lấy trong hàm `start_tts_thread` và truyền vào hàm `generate_tts_audio_multithreaded`.
        * **Trong `tts_logic.py`:**
            * Hàm `generate_tts_audio_multithreaded` sẽ nhận thêm tham số `reading_style_prompt: str`.
            * Tham số này sẽ được truyền xuống hàm `_process_text_chunk_worker`.
            * Hàm `_process_text_chunk_worker` sẽ truyền nó xuống hàm `_generate_audio_for_single_chunk`.
            * Bên trong `_generate_audio_for_single_chunk`, nếu `reading_style_prompt` có giá trị, nó sẽ được **ghép vào đầu mỗi `text_chunk`** để tạo thành `text_for_api` trước khi gửi đến API. Ví dụ cách ghép: `text_for_api = f"{reading_style_prompt.strip()}: {text_chunk}"`.
    * **Mục tiêu:** Cho phép người dùng điều khiển văn phong, tông giọng của audio output thông qua prompt, và kiểm tra xem điều này có cải thiện vấn đề "chất lượng âm thanh không đồng nhất/echo" hay không. Đồng thời, thử nghiệm đặt `temperature: 0.0` trong `ai_studio_config_dict` khi có "Reading Style Prompt" để xem có giúp giọng đọc ổn định hơn không.

2.  **(Sau khi Reading Style ổn định) Tùy chọn Output MP3:**
    * Thêm tùy chọn (ví dụ checkbox "Output as MP3") trên UI.
    * Nếu được chọn, sau khi file WAV cuối cùng được ghép thành công, convert nó sang MP3 bằng `pydub`.

3.  **(Sau này) Rà soát và tối ưu hóa `split_text_into_chunks`** cho mục tiêu 1000 từ/part, đảm bảo an toàn token.