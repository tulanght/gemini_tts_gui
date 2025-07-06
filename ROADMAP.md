# Lộ trình Phát triển (Roadmap)
# Phiên bản: 2.0
# Cập nhật lần cuối: 2025-07-06

Tài liệu này mô tả tầm nhìn và kế hoạch phát triển cho các phiên bản tiếp theo của Gemini Creative Suite.

## Tầm nhìn Dự án
Trở thành một bộ công cụ "tất cả trong một" (all-in-one), mạnh mẽ, và dễ sử dụng nhất cho các nhà sáng tạo nội dung truyện kể trên YouTube, giúp tự động hóa tối đa các công việc lặp đi lặp lại và kết nối các khâu rời rạc trong quá trình sáng tạo.

---

## Giai đoạn 1: Hoàn thiện & Ổn định (Mục tiêu gần)

### 1.1. Cải tiến "Trợ lý Biên tập" - Quản lý Dữ liệu
* **Vấn đề:** Nút "Chốt & Lưu" hiện tại không cho phép người dùng xem lại các tiêu đề hay kịch bản thumbnail đã lưu.
* **Yêu cầu:**
    * [ ] Xây dựng một giao diện (có thể là một cửa sổ con hoặc một tab mới) để người dùng có thể **xem lại, chỉnh sửa, hoặc xóa** các lựa chọn đã được lưu vào cơ sở dữ liệu.

### 1.2. Cải tiến "Text-to-Speech" - Hỗ trợ Đa ngôn ngữ
* **Vấn đề:** Các "Reading Style Prompt" hiện tại được viết cứng cho tiếng Việt.
* **Yêu cầu:**
    * [ ] Nghiên cứu và thêm một menu lựa chọn ngôn ngữ (tối thiểu là Tiếng Việt và Tiếng Anh).
    * [ ] Dựa trên ngôn ngữ được chọn, chương trình sẽ sử dụng một bộ "Reading Style Prompt" phù hợp, giúp Gemini TTS tạo ra giọng đọc tự nhiên hơn.

---

## Giai đoạn 2: Quản lý & Mở rộng (Mục tiêu trung hạn)

### 2.1. Tính năng "Quản lý Dự án" - Đồng bộ Nội dung
* **Vấn đề:** Các module (Soạn Truyện, Tiêu đề, Thumbnail) đang hoạt động độc lập, thiếu sự liên kết.
* **Yêu cầu:**
    * [ ] Xây dựng một hệ thống để liên kết một nội dung truyện dài với tiêu đề và kịch bản thumbnail tương ứng của nó.
    * [ ] Có thể cần một giao diện "Quản lý Dự án" mới, hiển thị danh sách các "dự án truyện", cho phép người dùng quản lý chúng một cách nhất quán.

## Giai đoạn 3: Tối ưu & Nâng cao (Mục tiêu dài hạn)

### 3.1. Tối ưu Giao diện (UI/UX)
* **Vấn đề:** Giao diện của tất cả các tab hiện tại được thiết kế ở mức cơ bản.
* **Yêu cầu:** Đây là một mục tiêu dài hạn, cần liên tục nghiên cứu và đưa ra các đề xuất cải tiến về bố cục, cách sắp xếp các nút bấm và luồng tương tác để tối ưu trải nghiệm người dùng.

### 3.2. Module Phụ đề
* **Kế hoạch cũ (chuyển sang giai đoạn này):**
    * [ ] Xây dựng tính năng tải phụ đề từ một video YouTube.
    * [ ] Xây dựng tính năng tạo file phụ đề (`.srt`) từ kịch bản và file audio đã tạo.

### 3.3. Tích hợp AI tạo ảnh
* **Ý tưởng:** Nghiên cứu tích hợp các model tạo ảnh (ví dụ: Midjourney, Stable Diffusion) để tạo ảnh nền cho thumbnail.