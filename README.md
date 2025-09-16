# Gemini Creative Suite v1.21.0


**[Xem Lịch sử Thay đổi (Changelog)](CHANGELOG.md) | [Xem Lộ trình Phát triển (Roadmap)](ROADMAP.md) | [Xem Quy trình Làm việc (Workflow)](WORKFLOW.md) | [Ghi chú Kỹ thuật](TECHNICAL_NOTES.md)**

---

Một bộ công cụ desktop mạnh mẽ được xây dựng bằng Python và Tkinter, sử dụng sức mạnh của Google Gemini API để hỗ trợ toàn diện cho quy trình sáng tạo nội dung YouTube, đặc biệt cho thể loại truyện kể.

![Giao diện ứng dụng](https://i.imgur.com/image_5edff8.png)

## Hướng dẫn Sử dụng (Bản đóng gói)

1.  Sau khi quá trình đóng gói hoàn tất, tìm đến thư mục `dist`.
2.  Chạy file **`Gemini Creative Suite.exe`** để bắt đầu sử dụng ứng dụng.
3.  Không cần cài đặt Python hay bất kỳ thư viện nào khác.

---

## Chức năng Cốt lõi

Dự án được chia thành 3 module chính, hoạt động trên các tab riêng biệt:

* **🎙️ Text-to-Speech:** Chuyển đổi kịch bản dài thành file audio `.wav` chất lượng cao, hỗ trợ đa luồng và tự động ghép nối.
* **✍️ Trợ lý Biên tập:** Bóc tách các lựa chọn kịch bản từ Gemini, cung cấp trình soạn thảo với cảnh báo độ dài và cửa sổ xem trước thumbnail chuyên nghiệp.
* **📖 Soạn Truyện Dài:** Cung cấp bảng điều khiển nổi tiện lợi để soạn truyện dài, tự động hóa việc sao chép và tạo prompt tiếp nối.

---

## Cấu trúc Dự án

Dưới đây là cấu trúc các file quan trọng trong thư mục `src/` để giúp các lập trình viên dễ dàng nắm bắt:

src/gemini_tts_app/
│
├── main_app.py         # File chính, quản lý giao diện (Tkinter), các tab và luồng sự kiện.
├── tts_logic.py        # Xử lý logic cho module Text-to-Speech (gọi API, xử lý audio).
├── thumbnail_preview.py# Quản lý cửa sổ xem trước và thiết kế thumbnail.
├── database.py         # Xử lý logic cho module Trợ lý Biên tập (bóc tách text, CSDL SQLite).
├── long_form_composer.py# Logic cho module Soạn Truyện Dài (theo dõi clipboard, lọc nội dung).
├── settings_manager.py # Quản lý việc đọc/ghi các cài đặt của người dùng (API keys, themes...).
├── logger_setup.py     # Thiết lập hệ thống ghi log cho ứng dụng.
├── utils.py            # Chứa các hàm tiện ích dùng chung, ví dụ: get_resource_path.
└── constants.py        # Chứa các hằng số của ứng dụng (mã màu, giá trị mặc định...).

---

## Hướng dẫn Cài đặt (Dành cho Lập trình viên)

* **Yêu cầu Hệ thống:**
    * Python 3.9+
    * `ffmpeg`: Cần được cài đặt và thêm vào biến môi trường PATH.
* **Các bước:**
    1.  Clone repository: `git clone [URL]`
    2.  Tạo môi trường ảo: `python -m venv venv` và kích hoạt nó.
    3.  Cài đặt thư viện: `pip install -r requirements.txt`
    4.  Chạy ứng dụng: `python run.py`
    5.  Vào tab "Settings" để thêm API key và lưu lại.



