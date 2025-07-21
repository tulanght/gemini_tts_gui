# Lộ trình Phát triển (Roadmap)
# version: 6.1
# last-updated: 2025-07-21
# description: Ghi nhận hoàn thành tính năng "Tích hợp Thư viện với TTS".

## Tầm nhìn Dự án
Trở thành một bộ công cụ "tất cả trong một" (all-in-one), mạnh mẽ và dễ sử dụng cho các nhà sáng tạo nội dung, kết nối liền mạch kho ý tưởng trên cloud đến sản phẩm cuối cùng.

---

## Giai đoạn 2: Tối ưu Luồng làm việc & Mở rộng (Tiếp theo)

### 2.1. Cải tiến Trải nghiệm Người dùng (UI/UX)
* **Vấn đề:** Giao diện của một số thành phần có thể được cải tiến để trực quan hơn.
* **Yêu cầu:** Đây là một mục tiêu liên tục. Ví dụ: tự động làm sạch tiền tố ("001 - ") khỏi tiêu đề khi đồng bộ từ Google Drive.

### 2.2. Module Phụ đề
* **Vấn đề:** Chưa có công cụ hỗ trợ tạo phụ đề cho video.
* **Yêu cầu:**
    * [ ] Xây dựng tính năng tạo file phụ đề (`.srt`) từ kịch bản và file audio đã tạo.

---

## ✅ Thành tựu đã Đạt được (Key Milestones Achieved)

* **Tích hợp Thư viện với TTS (Hoàn thành trong v1.4.0):**
    - Thêm nút "Gửi sang TTS" trong Thư viện để nhanh chóng chuyển nội dung "Story" của một dự án sang tab Text-to-Speech, tối ưu hóa luồng làm việc.

* **Tích hợp Google Drive & Quản lý Trạng thái (Hoàn thành trong v1.3.0):**
    - Xây dựng hệ thống "Nhóm Dự án" trong Settings, cho phép quản lý các nguồn nội dung (Local/Google Drive).
    - Triển khai thành công luồng xác thực OAuth 2.0 an toàn để kết nối với Google API.
    - Xây dựng tính năng "Đồng bộ Thông minh" từ Google Drive, hỗ trợ các chế độ "Chỉ thêm mới" và "Làm mới toàn bộ".
    - Hoàn thiện hệ thống "Trạng thái Dự án" (Chưa làm, Đang làm dở, Đã làm) với cơ chế Menu Chuột phải và phản hồi trực quan bằng màu sắc.
    - Xây dựng cơ chế "Di chuyển Cơ sở dữ liệu" (Migration) tự động để đảm bảo tính tương thích ngược.

* **Hỗ trợ Đa ngôn ngữ TTS (Hoàn thành trong v1.2.0):**
    - Hoàn thiện tính năng lựa chọn ngôn ngữ và "Reading Style Prompt" tương ứng trong tab Text-to-Speech.

* **Hệ thống Quản lý Dự án & Thư viện (Hoàn thành trong v1.1.0):**
    - Xây dựng hệ thống "Thư viện" dựa trên mô hình "Dự án", cho phép quản lý các thành phần (Truyện, Tiêu đề, Thumbnail).
    - Tích hợp khái niệm "Dự án đang hoạt động" với thanh trạng thái trực quan.

* **Công cụ Tự động hóa Phiên bản (Hoàn thành trong v1.0.0):**
    - Xây dựng kịch bản `scripts/release.py` để tự động hóa việc nâng cấp phiên bản.