# Gemini Creative Suite v1.21.0

**[Xem Lịch sử Thay đổi (Changelog)](https://www.google.com/search?q=CHANGELO) | [Xem Lộ trình Phát triển (Roadmap)](https://www.google.com/search?q=ROADMAP.md) | [Xem Quy trình Làm việc (Workflow)](https://www.google.com/search?q=WORKFLOW.md) | [Ghi chú Kỹ thuật](https://www.google.com/search?q=TECHNICAL_NOTES.md)**

-----

Một bộ công cụ desktop mạnh mẽ được xây dựng bằng Python và Tkinter, sử dụng sức mạnh của Google Gemini API để hỗ trợ toàn diện cho quy trình sáng tạo nội dung YouTube, đặc biệt cho thể loại truyện kể.

[Hình ảnh]

## Luồng làm việc cốt lõi

Gemini Creative Suite (GCS) được thiết kế để tối ưu hóa toàn bộ quy trình sáng tạo của bạn thông qua một kiến trúc module hóa, trực quan:

1.  **⚙️ Cài đặt:** Thiết lập API Keys và quản lý các Nhóm Dự án (Lưu trữ cục bộ hoặc đồng bộ với Google Drive).
2.  **📖 Thư viện:** Trung tâm quản lý tất cả các dự án của bạn. Đồng bộ hóa ý tưởng từ Google Drive, tạo dự án mới, và kích hoạt "Dự án đang hoạt động" để bắt đầu làm việc.
3.  **📝 Soạn Truyện Dài:** Soạn thảo kịch bản với sự hỗ trợ của các công cụ tiện ích như tìm kiếm & thay thế.
4.  **✍️ Trợ lý Biên tập:** Tận dụng Gemini để tạo và bóc tách hàng loạt các lựa chọn Tiêu đề, Thumbnail, Hook. Soạn thảo và chốt phương án cuối cùng với các công cụ kiểm tra độ dài và định dạng thông minh.
5.  **🎙️ Text-to-Speech (TTS):** Chuyển đổi kịch bản đã hoàn thiện thành file audio `.wav` chất lượng cao, hỗ trợ đa luồng và tự động ghép nối.
6.  **🛠️ Tiện ích:** Nơi chứa các công cụ bổ sung mạnh mẽ, bắt đầu với **"Tải phụ đề YouTube"**, cho phép bạn lấy và lưu trữ nội dung từ bất kỳ video nào để làm nguồn tư liệu.

-----

## Cấu trúc Dự án (Đã cập nhật)

Dự án tuân thủ nghiêm ngặt nguyên tắc **Tách bạch Trách nhiệm**. Giao diện và Logic được tách biệt rõ ràng để dễ dàng bảo trì và mở rộng.

```
src/gemini_tts_app/
│
├── main_app.py                 # File điều phối chính, quản lý cửa sổ và các tab.
│
├── core/                       # Chứa các logic nghiệp vụ và xử lý dữ liệu nền
│   ├── database.py             # Quản lý toàn bộ CSDL SQLite (dự án, phụ đề, hashtags).
│   ├── google_api_handler.py   # Xử lý xác thực và tương tác với Google Drive API.
│   ├── logger_setup.py         # Thiết lập hệ thống ghi log.
│   ├── settings_manager.py     # Quản lý việc đọc/ghi file cài đặt của người dùng.
│   └── tts_logic.py            # Xử lý logic cho module Text-to-Speech (gọi API, xử lý audio).
│
├── modules/                    # Mỗi file là một tab hoặc một cửa sổ chức năng độc lập
│   ├── settings_tab.py         # Giao diện và sự kiện cho Tab Cài đặt.
│   ├── library_tab.py          # Giao diện và sự kiện cho Tab Thư viện.
│   ├── long_form_composer_tab.py # Giao diện và sự kiện cho Tab Soạn Truyện Dài.
│   ├── editorial_assistant_tab.py # Giao diện và sự kiện cho Tab Trợ lý Biên tập.
│   ├── tts_tab.py              # Giao diện và sự kiện cho Tab Text-to-Speech.
│   ├── utilities_tab.py        # Giao diện và sự kiện cho Tab Tiện ích.
│   ├── subtitle_details_window.py # Cửa sổ chi tiết để quản lý hashtag phụ đề.
│   └── find_replace_dialog.py  # Cửa sổ chức năng Tìm & Thay thế.
│
├── shared/                     # Chứa các thành phần được sử dụng ở nhiều nơi
│   ├── constants.py            # Chứa các hằng số của ứng dụng (mã màu, đường dẫn...).
│   ├── thumbnail_preview.py    # Quản lý cửa sổ xem trước và thiết kế thumbnail.
│   └── utils.py                # Chứa các hàm tiện ích dùng chung.
│
└── __init__.py
```

-----

## Hướng dẫn Cài đặt (Dành cho Lập trình viên)

  * **Yêu cầu Hệ thống:**
      * Python 3.9+
      * `ffmpeg`: Cần được cài đặt và thêm vào biến môi trường PATH của hệ thống.
  * **Các bước:**
    1.  Clone repository: `git clone [URL]`
    2.  Tạo môi trường ảo: `python -m venv venv` và kích hoạt nó.
    3.  Cài đặt các thư viện cần thiết: `pip install -r requirements.txt`
    4.  Chạy ứng dụng: `python run.py`
    5.  Lần đầu sử dụng, hãy vào tab **"⚙️ Cài đặt"** để thêm API key và thiết lập các thông số cần thiết.