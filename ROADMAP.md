# Lộ trình Phát triển (Roadmap)
# version: 4.0
# last-updated: 2025-07-17
# description: Bổ sung tính năng tích hợp Google Drive vào Giai đoạn 2.

Tài liệu này mô tả tầm nhìn và kế hoạch phát triển cho các phiên bản tiếp theo của Gemini Creative Suite.

## Tầm nhìn Dự án
Trở thành một bộ công cụ "tất cả trong một" (all-in-one), mạnh mẽ, và dễ sử dụng nhất cho các nhà sáng tạo nội dung truyện kể trên YouTube, giúp tự động hóa tối đa các công việc lặp đi lặp lại và kết nối các khâu rời rạc trong quá trình sáng tạo, từ kho ý tưởng trên cloud đến sản phẩm cuối cùng.

---

## Giai đoạn 1: Hoàn thiện & Ổn định (Đang thực hiện)

### 1.1. Tối ưu Giao diện (UI/UX)
* **Vấn đề:** Giao diện của tất cả các tab hiện tại được thiết kế ở mức cơ bản.
* **Yêu cầu:** Đây là một mục tiêu dài hạn, cần liên tục nghiên cứu và đưa ra các đề xuất cải tiến về bố cục, cách sắp xếp các nút bấm và luồng tương tác để tối ưu trải nghiệm người dùng.

---

## Giai đoạn 2: Tích hợp & Quản lý Nâng cao (Tiếp theo)

### 2.1. Tích hợp Google Drive & Quản lý theo "Nhóm Dự án" (MỚI)
* **Vấn đề:** Việc đưa truyện từ kho nội dung vào ứng dụng vẫn là thủ công. Cần một cơ chế quản lý các dự án theo từng kênh/mục đích riêng.
* **Yêu cầu:**
    * [ ] Xây dựng tính năng cho phép quản lý và đồng bộ hóa các "Nhóm Dự án" từ các thư mục Google Drive.
    * [ ] Mỗi "Folder ID" sẽ tương ứng với một "Nhóm Dự án".
    * [ ] Chương trình sẽ đọc các file Google Docs trong thư mục, tự động tạo dự án với Tên file là Tiêu đề và nội dung file là Nội dung Truyện.

### 2.2. Tích hợp Thư viện với Text-to-Speech
* **Vấn đề:** Hiện tại có 2 cách đưa văn bản vào TTS (dán trực tiếp, import file .txt). Cần có cách thứ 3 để lấy trực tiếp từ các dự án đã có.
* **Yêu cầu:**
    * [ ] Trong tab "Thư viện", thêm nút "Gửi sang TTS".
    * [ ] Khi nhấn nút, nội dung "Story" của dự án được chọn sẽ được tự động điền vào ô "Input Text" của tab "Text-to-Speech", đồng thời chuyển người dùng sang tab đó.

---

## Giai đoạn 3: Module Mở rộng (Tương lai)

### 3.1. Module Phụ đề
* **Yêu cầu:**
    * [ ] Xây dựng tính năng tải phụ đề từ một video YouTube.
    * [ ] Xây dựng tính năng tạo file phụ đề (`.srt`) từ kịch bản và file audio đã tạo.

---

## ✅ Thành tựu đã Đạt được (Key Milestones Achieved)

* **Hỗ trợ Đa ngôn ngữ TTS (Hoàn thành trong v1.2.0):** Hoàn thiện tính năng lựa chọn ngôn ngữ (Tiếng Việt, Tiếng Anh) và tự động cập nhật các "Reading Style Prompt" tương ứng trong tab Text-to-Speech.
* **Quản lý Dự án & Thư viện (Hoàn thành trong v1.1.0):** Xây dựng thành công hệ thống "Thư viện" dựa trên mô hình "Dự án", cho phép người dùng tạo, quản lý và chỉnh sửa các thành phần (Truyện, Tiêu đề, Thumbnail) một cách có tổ chức và liền mạch.