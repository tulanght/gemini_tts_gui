# Lộ trình Phát triển (Roadmap)
# version: 2.0
# last-updated: 2025-07-16
# description: Tái cấu trúc lại toàn bộ lộ trình, tích hợp các mục tiêu mới và chia thành các giai đoạn phát triển rõ ràng.

Tài liệu này mô tả tầm nhìn và kế hoạch phát triển cho các phiên bản tiếp theo của Gemini Creative Suite.

## Tầm nhìn Dự án
Trở thành một bộ công cụ "tất cả trong một" (all-in-one), mạnh mẽ, và dễ sử dụng nhất cho các nhà sáng tạo nội dung truyện kể trên YouTube, giúp tự động hóa tối đa các công việc lặp đi lặp lại và kết nối các khâu rời rạc trong quá trình sáng tạo.

---

## Giai đoạn 1: Hoàn thiện & Ổn định (Mục tiêu gần)

### 1.1. Cải tiến "Text-to-Speech" - Hỗ trợ Đa ngôn ngữ
* **Vấn đề:** Các "Reading Style Prompt" hiện tại được viết cứng cho tiếng Việt.
* **Yêu cầu:**
    * [ ] Nghiên cứu và thêm một menu lựa chọn ngôn ngữ (tối thiểu là Tiếng Việt và Tiếng Anh).
    * [ ] Dựa trên ngôn ngữ được chọn, chương trình sẽ sử dụng một bộ "Reading Style Prompt" phù hợp, giúp Gemini TTS tạo ra giọng đọc tự nhiên hơn.

---

## Giai đoạn 2: Tối ưu & Nâng cao (Mục tiêu dài hạn)

### 2.1. Tối ưu Giao diện (UI/UX)
* **Vấn đề:** Giao diện của tất cả các tab hiện tại được thiết kế ở mức cơ bản.
* **Yêu cầu:** Đây là một mục tiêu dài hạn, cần liên tục nghiên cứu và đưa ra các đề xuất cải tiến về bố cục, cách sắp xếp các nút bấm và luồng tương tác để tối ưu trải nghiệm người dùng.

### 2.2. Module Phụ đề
* **Yêu cầu:**
    * [ ] Xây dựng tính năng tải phụ đề từ một video YouTube.
    * [ ] Xây dựng tính năng tạo file phụ đề (`.srt`) từ kịch bản và file audio đã tạo.

---

## ✅ Thành tựu đã Đạt được (Key Milestones Achieved)

* **Quản lý Dự án & Thư viện (Hoàn thành trong v1.0.x):** Xây dựng thành công hệ thống "Thư viện" dựa trên mô hình "Dự án", cho phép người dùng tạo, quản lý và chỉnh sửa các thành phần (Truyện, Tiêu đề, Thumbnail) một cách có tổ chức và liền mạch.