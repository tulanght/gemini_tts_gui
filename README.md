# Gemini Creative Suite v0.8.0

**[Xem Lịch sử Thay đổi (Changelog)](CHANGELOG.md) | [Xem Lộ trình Phát triển (Roadmap)](ROADMAP.md) | [Xem Quy trình Làm việc (Workflow)](WORKFLOW.md)**

---

Một bộ công cụ desktop mạnh mẽ được xây dựng bằng Python và Tkinter, sử dụng sức mạnh của Google Gemini API để hỗ trợ toàn diện cho quy trình sáng tạo nội dung YouTube, đặc biệt cho thể loại truyện kể.

![Giao diện ứng dụng](https://i.imgur.com/image_5edff8.png)

## 核心功能 (Core Modules)

Dự án được chia thành 3 module chính, hoạt động trên các tab riêng biệt:

### 1. 🎙️ **Text-to-Speech (Chuyển văn bản thành giọng nói)**
- Generate âm thanh chất lượng cao, xử lý đa luồng, tự động chia nhỏ văn bản và ghép nối thông minh.

### 2. ✍️ **Trợ Lý Biên Tập (Editing Assistant)**
- Bóc tách tiêu đề/kịch bản, soạn thảo với cảnh báo độ dài, và xem trước thumbnail chuyên nghiệp.

### 3. 📖 **Soạn Truyện Dài (Long-form Story Composer)**
- Bảng điều khiển nổi, tự động hóa qua clipboard, bộ lọc thông minh và lưu trữ bản thảo.

## Cấu trúc Dự án (Project Structure)
```
/
├── run.py                  # Điểm khởi chạy chính của ứng dụng
├── requirements.txt        # Danh sách các thư viện phụ thuộc
├── resources/              # Chứa các tài nguyên tĩnh như fonts, icons
│   ├── fonts/
│   └── voices.json
└── src/
└── gemini_tts_app/
├── init.py
├── main_app.py         # File chính, quản lý giao diện và các tab
├── tts_logic.py        # Xử lý logic cho module Text-to-Speech
├── thumbnail_preview.py# Quản lý cửa sổ xem trước thumbnail
├── long_form_composer.py# Logic cho module Soạn Truyện Dài
├── utils.py            # Các hàm tiện ích dùng chung
└── constants.py        # Chứa các hằng số của ứng dụng
```

## Yêu cầu Hệ thống
* Python 3.9+
* `ffmpeg`: Cần được cài đặt và thêm vào biến môi trường PATH.
* Một hoặc nhiều Google Gemini API Key.

## Hướng dẫn Cài đặt & Chạy
1.  **Clone repository:** `git clone [URL]`
2.  **Tạo môi trường ảo:** `python -m venv venv` và kích hoạt nó.
3.  **Cài đặt thư viện:** `pip install -r requirements.txt`
4.  **Chạy ứng dụng:** `python run.py`
5.  **Cấu hình:** Vào tab "Settings" để thêm API key và lưu lại.

