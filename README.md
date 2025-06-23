# Gemini Creative Suite v0.8.0

Một bộ công cụ desktop mạnh mẽ được xây dựng bằng Python và Tkinter, sử dụng sức mạnh của Google Gemini API để hỗ trợ toàn diện cho quy trình sáng tạo nội dung YouTube, đặc biệt cho thể loại truyện kể.

![Giao diện ứng dụng](https://i.imgur.com/image_5edff8.png)

---

## 核心功能 (Core Modules)

Dự án được chia thành 3 module chính, hoạt động trên các tab riêng biệt:

### 1. 🎙️ **Text-to-Speech (Chuyển văn bản thành giọng nói)**
- **Generate Âm thanh Chất lượng cao:** Chuyển đổi các kịch bản truyện dài thành file audio `.wav` bằng model `gemini-2.5-pro-preview-tts`.
- **Xử lý Đa luồng:** Tận dụng tối đa 3 API Key để xử lý các đoạn văn bản song song, tăng tốc độ generate lên đáng kể.
- **Tự động Chia nhỏ Văn bản:** Tự động chia các kịch bản dài thành các chunk nhỏ hơn dựa trên số từ có thể tùy chỉnh, với cơ chế kiểm tra token fallback để đảm bảo an toàn cho API.
- **Tùy chỉnh Nâng cao:** Cho phép điều chỉnh các tham số `Temperature` và `Top P` để tinh chỉnh sắc thái và độ đa dạng của giọng đọc.
- **Ghép nối Thông minh:** Tự động ghép các file audio của từng phần lại với nhau, có thêm tùy chọn chèn một khoảng lặng ngắn giữa các đoạn để tạo nhịp nghỉ tự nhiên.
- **Import Tiện lợi:** Hỗ trợ import kịch bản trực tiếp từ file `.txt` và `.docx`.

### 2. ✍️ **Trợ Lý Biên Tập (Editing Assistant)**
- **Bóc tách Thông minh:** Tự động phân tích và bóc tách các lựa chọn Tiêu đề hoặc kịch bản Thumbnail từ nội dung do Gemini cung cấp, loại bỏ các chi tiết thừa.
- **Soạn thảo Thời gian thực:** Cung cấp một môi trường soạn thảo với bộ đếm ký tự, từ, và dòng hoạt động theo thời gian thực.
- **Cảnh báo Trực quan:** Sử dụng màu sắc (xanh, vàng, đỏ) để cảnh báo người dùng khi tiêu đề vi phạm các quy luật về độ dài của YouTube.
- **Xem trước Thumbnail Chuyên nghiệp:**
    - Mở một cửa sổ xem trước (preview) riêng biệt, luôn giữ đúng tỷ lệ 16:9.
    - Cho phép tùy chỉnh ảnh nền, font chữ, cỡ chữ, và lớp phủ tối (overlay) để có cái nhìn trực quan nhất.
    - Hỗ trợ xuất bản xem trước ra file ảnh `.png`.
- **Lưu trữ Cơ sở dữ liệu:** Lưu trữ các phương án đã "chốt" vào một file CSDL SQLite để dễ dàng tra cứu.

### 3. 📖 **Soạn Truyện Dài (Long-form Story Composer)**
- **Bảng điều khiển Nổi:** Cung cấp một panel điều khiển nhỏ gọn, luôn nổi trên các cửa sổ khác, giúp người dùng tương tác mà không cần rời khỏi trình duyệt đang viết truyện.
- **Tự động hóa qua Clipboard:** Chế độ "Theo dõi Clipboard" tự động bắt lấy nội dung truyện bạn vừa copy, nối vào bản thảo và tạo prompt tiếp nối.
- **Bộ lọc Thông minh:** Tự động bỏ qua các nội dung không hợp lệ (text quá ngắn, code,...) dựa trên các quy luật do người dùng định nghĩa (ví dụ: số từ phải trong một khoảng nhất định).
- **Lưu trữ Bản thảo:** Dễ dàng lưu toàn bộ câu chuyện đã được nối lại thành một file `.txt` duy nhất.

---

## Yêu cầu Hệ thống

* Python 3.9+
* `ffmpeg`: Cần được cài đặt trên hệ thống và thêm vào biến môi trường PATH. (Yêu cầu của thư viện `pydub`).
* Một hoặc nhiều Google Gemini API Key.

## Hướng dẫn Cài đặt & Chạy

1.  **Clone repository về máy:**
    ```bash
    git clone [URL-repository-cua-ban]
    cd gemini-creative-suite 
    ```

2.  **Tạo và kích hoạt môi trường ảo:**
    ```bash
    # Lệnh cho Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Lệnh cho macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Cài đặt các thư viện cần thiết:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Chạy ứng dụng:**
    ```bash
    python run.py
    ```

5.  **Cấu hình lần đầu:**
    * Mở ứng dụng, vào tab **"Settings"**.
    * Dán (các) API Key của bạn vào các ô tương ứng.
    * Thiết lập các thông số mặc định khác nếu muốn.
    * Nhấn **"Save All Settings"**.

---

## Lộ trình Phát triển Tiếp theo

-   Hoàn thiện các tùy chọn nâng cao cho tính năng "Xem trước Thumbnail" (tô màu từng dòng, hiệu ứng đổ bóng).
-   Xây dựng module tải phụ đề YouTube.
-   Nghiên cứu các giải pháp tự động hóa nâng cao hơn.