# Lộ trình Phát triển (Roadmap)
# version: 8.0
# last-updated: 2025-07-24
# description: Ghi nhận hoàn thành Giai đoạn 2 & 3. Xác định Giai đoạn 4 là chặng tiếp theo.

## Tầm nhìn Dự án
Trở thành một bộ công cụ "tất cả trong một" (all-in-one), mạnh mẽ và dễ sử dụng cho các nhà sáng tạo nội dung, kết nối liền mạch kho ý tưởng trên cloud đến sản phẩm cuối cùng.

---
## Giai đoạn 4: Hoàn thiện & Mở rộng Chuyên sâu (Tiếp theo)
Mục tiêu: Bổ sung các tính năng tiện ích, hoàn thiện tài liệu và xây dựng chiến lược phát hành để đưa dự án đến trạng thái hoàn chỉnh.

* **[ ] Xây dựng Tab "Tiện ích":** Tạo một tab mới để chứa các công cụ nhỏ, độc lập trong tương lai (ví dụ: Tải phụ đề YouTube, các công cụ xử lý văn bản khác...), giúp ứng dụng gọn gàng và dễ mở rộng.
* **[ ] Khởi tạo & Viết Tài liệu Hướng dẫn (`USER_MANUAL.md`):** Bắt đầu viết tài liệu hướng dẫn sử dụng chi tiết cho toàn bộ các tính năng của ứng dụng và cập nhật liên tục.
* **[ ] Xây dựng Chiến lược Đóng gói & Phát hành (`.exe`):** Thường xuyên tạo các bản build `.exe` sau mỗi phiên bản MINOR ổn định để có thể sử dụng trên nhiều máy tính.

---
## ✅ Thành tựu đã Đạt được (Key Milestones Achieved)

* **Hoàn thiện Trải nghiệm Soạn thảo (Hoàn thành trong v1.13.0):**
    - Xây dựng tính năng "Chèn Hook" với luồng làm việc thông minh, có cảnh báo để tránh trùng lặp.
* **Xây dựng Công cụ Find & Replace (Hoàn thành trong v1.12.0):**
    - Tích hợp công cụ "Tìm & Thay thế" mạnh mẽ vào trình soạn thảo, hỗ trợ bộ đếm, highlight, và các tùy chọn tìm kiếm nâng cao.
* **Hoàn thiện Logic Trợ lý Biên tập (Hoàn thành trong v1.11.0):**
    - Bổ sung logic tự động nhận dạng và bóc tách các lựa chọn "Hook", hoàn thiện luồng làm việc cho cả ba loại nội dung.
* **Hoàn tất Tái cấu trúc & Tinh chỉnh UI (Hoàn thành trong v1.10.1):**
    - Hoàn tất quá trình tái cấu trúc toàn bộ ứng dụng thành các module tab riêng biệt, giúp mã nguồn trong sạch và dễ bảo trì.
    - Tinh chỉnh và sửa lỗi giao diện cho các tab "Soạn Truyện Dài", "Trợ lý Biên tập", "Cài đặt" và bố cục chính của ứng dụng.
* **Cải tiến Theme Giao diện (Hoàn thành trong v1.6.0):**
    - Tích hợp thư viện `sv-ttk` để áp dụng theme hiện đại cho toàn bộ ứng dụng.
* **Cải tiến UI/UX Thư viện (Hoàn thành trong v1.5.0):**
    - Tự động làm sạch tiền tố số khỏi Tên dự án và Tiêu đề khi hiển thị.
* **Tích hợp Thư viện với TTS (Hoàn thành trong v1.4.0):**
    - Thêm nút "Gửi sang TTS" trong Thư viện để tối ưu hóa luồng làm việc.
* **Tích hợp Google Drive & Quản lý Trạng thái (Hoàn thành trong v1.3.0):**
    - Xây dựng hệ thống "Nhóm Dự án", luồng xác thực OAuth 2.0, và tính năng đồng bộ.
    - Hoàn thiện hệ thống "Trạng thái Dự án" với màu sắc trực quan.
* **Hỗ trợ Đa ngôn ngữ TTS (Hoàn thành trong v1.2.0):**
    - Hoàn thiện tính năng lựa chọn ngôn ngữ và "Reading Style Prompt".
* **Hệ thống Quản lý Dự án & Thư viện (Hoàn thành trong v1.1.0):**
    - Xây dựng hệ thống "Thư viện" và khái niệm "Dự án đang hoạt động".
* **Công cụ Tự động hóa Phiên bản (Hoàn thành trong v1.0.0):**
    - Xây dựng kịch bản `scripts/release.py` để tự động hóa việc nâng cấp phiên bản.