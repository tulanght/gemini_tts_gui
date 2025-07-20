# Lộ trình Phát triển (Roadmap)
# version: 6.0
# last-updated: 2025-07-21
# description: Cập nhật chính xác các thành tựu đã hoàn thành vào v1.3.0 và định hướng lại các giai đoạn phát triển tương lai.

## Tầm nhìn Dự án
Trở thành một bộ công cụ "tất cả trong một" (all-in-one), mạnh mẽ và dễ sử dụng cho các nhà sáng tạo nội dung, kết nối liền mạch kho ý tưởng trên cloud đến sản phẩm cuối cùng.

---

## Giai đoạn 2: Tối ưu Luồng làm việc & Mở rộng (Tiếp theo)

### 2.1. Tích hợp Thư viện với Text-to-Speech
* **Vấn đề:** Chưa có cách nhanh chóng để đưa một kịch bản đã hoàn thiện từ Thư viện sang module TTS.
* **Yêu cầu:**
    * [ ] Trong tab "Thư viện", thêm nút "Gửi sang TTS" để nhanh chóng chuyển nội dung "Story" của một dự án sang tab Text-to-Speech.

### 2.2. Cải tiến Trải nghiệm Người dùng (UI/UX)
* **Vấn đề:** Giao diện của một số thành phần có thể được cải tiến để trực quan hơn.
* **Yêu cầu:** Đây là một mục tiêu liên tục. Ví dụ: tự động làm sạch tiền tố ("001 - ") khỏi tiêu đề khi đồng bộ từ Google Drive.

### 2.3. Module Phụ đề
* **Vấn đề:** Chưa có công cụ hỗ trợ tạo phụ đề cho video.
* **Yêu cầu:**
    * [ ] Xây dựng tính năng tạo file phụ đề (`.srt`) từ kịch bản và file audio đã tạo.

---

## ✅ Thành tựu đã Đạt được (Key Milestones Achieved)

* **Tích hợp Google Drive & Quản lý Trạng thái (Hoàn thành trong v1.3.0):**
    - Xây dựng hệ thống "Nhóm Dự án" trong Settings, cho phép quản lý các nguồn nội dung (Local/Google Drive).
    - Triển khai thành công luồng xác thực OAuth 2.0 an toàn để kết nối với Google API.
    - Xây dựng tính năng "Đồng bộ Thông minh" từ Google Drive, hỗ trợ các chế độ "Chỉ thêm mới" và "Làm mới toàn bộ" để tối ưu hiệu năng.
    - Hoàn thiện hệ thống "Trạng thái Dự án" (Chưa làm, Đang làm dở, Đã làm) với cơ chế Menu Chuột phải và phản hồi trực quan bằng màu sắc trong Thư viện.
    - Xây dựng cơ chế "Di chuyển Cơ sở dữ liệu" (Migration) tự động để đảm bảo tính tương thích ngược cho các phiên bản CSDL cũ.

* **Hỗ trợ Đa ngôn ngữ TTS (Hoàn thành trong v1.2.0):**
    - Hoàn thiện tính năng lựa chọn ngôn ngữ (Tiếng Việt, Tiếng Anh) và tự động cập nhật các "Reading Style Prompt" tương ứng trong tab Text-to-Speech.

* **Hệ thống Quản lý Dự án & Thư viện (Hoàn thành trong v1.1.0):**
    - Xây dựng thành công hệ thống "Thư viện" dựa trên mô hình "Dự án", cho phép người dùng tạo, quản lý và chỉnh sửa các thành phần (Truyện, Tiêu đề, Thumbnail) một cách có tổ chức.
    - Tích hợp khái niệm "Dự án đang hoạt động" với thanh trạng thái trực quan, kết nối liền mạch các tab "Soạn Truyện", "Trợ lý Biên tập" và "Thư viện".

* **Công cụ Tự động hóa Phiên bản (Hoàn thành trong v1.0.0):**
    - Xây dựng kịch bản `scripts/release.py` để tự động hóa việc nâng cấp và đồng bộ số phiên bản trên toàn bộ dự án.