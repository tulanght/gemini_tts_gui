# Lộ trình Phát triển (Roadmap)
# version: 7.0
# last-updated: 2025-07-22
# description: Sắp xếp lại toàn bộ lộ trình, hủy bỏ Module Phụ đề và ưu tiên các tính năng cải thiện UI/UX, trải nghiệm soạn thảo.

## Tầm nhìn Dự án
Trở thành một bộ công cụ "tất cả trong một" (all-in-one), mạnh mẽ và dễ sử dụng cho các nhà sáng tạo nội dung, kết nối liền mạch kho ý tưởng trên cloud đến sản phẩm cuối cùng.

---
## Giai đoạn 2: Nền tảng UI/UX & Các Cải tiến Nhanh (Tiếp theo)
Mục tiêu: Nhanh chóng nâng cao chất lượng trải nghiệm người dùng và xây dựng các nền tảng cần thiết cho các tính năng lớn hơn.

* **[ ] Cải thiện Theme Giao diện:** Nghiên cứu và áp dụng một theme `ttk` hiện đại (ví dụ: `sv-ttk`) để thay thế giao diện xám-trắng mặc định, đồng thời cho phép người dùng lựa chọn theme trong Cài đặt.
* **[ ] Tối ưu Cột trong Thư viện:** Điều chỉnh lại độ rộng các cột trong tab Thư viện, ưu tiên không gian hiển thị cho cột "Nội dung Truyện".
* **[ ] Tái thiết kế Tab Trợ lý Biên tập:** Phân tích và thiết kế lại giao diện của tab này để trở nên trực quan, logic và dễ sử dụng hơn (Cần hình ảnh để phân tích chi tiết).
* **[ ] Khởi tạo Tài liệu Hướng dẫn:** Bắt đầu viết file `USER_MANUAL.md`, ghi lại hướng dẫn sử dụng cho các tính năng đã có và cập nhật liên tục khi có tính năng mới.

---
## Giai đoạn 3: Nâng cấp Trải nghiệm Soạn thảo
Mục tiêu: Bổ sung các công cụ mạnh mẽ giúp tăng tốc và tối ưu hóa quy trình xử lý, tái sử dụng nội dung.

* **[ ] Xây dựng Tính năng Find & Replace:** Tích hợp công cụ Tìm kiếm & Thay thế vào cửa sổ chỉnh sửa truyện, hỗ trợ các tùy chọn quan trọng như "Toàn bộ từ" (Match whole word) và "Phân biệt chữ hoa/thường" để thay thế nội dung (tên kênh, tên nhân vật) một cách an toàn và chính xác.
* **[ ] Xây dựng Tính năng Chèn Hook:** Tích hợp công cụ xử lý văn bản (paste-and-parse) để người dùng có thể dán các gợi ý hook từ Gemini, sau đó lọc, chọn và chèn hook phù hợp vào đầu truyện một cách nhanh chóng.

---
## Giai đoạn 4: Mở rộng Kiến trúc & Chiến lược
Mục tiêu: Đặt nền móng cho sự phát triển trong tương lai và xác định các chiến lược dài hạn.

* **[ ] Xây dựng Tab "Tiện ích":** Tạo một tab mới để chứa các công cụ nhỏ, độc lập trong tương lai (ví dụ: Tải phụ đề YouTube, các công cụ xử lý văn bản khác...), giúp ứng dụng gọn gàng và dễ mở rộng.
* **[ ] Xây dựng Chiến lược Đóng gói & Phát hành:** Thường xuyên tạo các bản build `.exe` sau mỗi phiên bản MINOR ổn định để có thể sử dụng trên nhiều máy tính.

---
## Các Tính năng Tạm hoãn / Hủy bỏ
* **Module Phụ đề:** Tính năng xây dựng một module chuyên dụng để tạo file `.srt` đã được **tạm hoãn vô thời hạn** để tập trung nguồn lực vào các tính năng có mức độ ưu tiên cao hơn. Nó có thể được xem xét lại dưới dạng một tiện ích nhỏ trong Tab "Tiện ích" trong tương lai.

---
## ✅ Thành tựu đã Đạt được (Key Milestones Achieved)

* **Cải tiến UI/UX Thư viện (Hoàn thành trong v1.5.0):**
    * Tự động làm sạch tiền tố số khỏi Tên dự án và Tiêu đề khi hiển thị để giao diện gọn gàng, dễ đọc hơn.
    * Tái cấu trúc các hàm xử lý sự kiện để đảm bảo tính toàn vẹn dữ liệu khi tương tác.

* **Tích hợp Thư viện với TTS (Hoàn thành trong v1.4.0):**
    * Thêm nút "Gửi sang TTS" trong Thư viện để nhanh chóng chuyển nội dung "Story" của một dự án sang tab Text-to-Speech, tối ưu hóa luồng làm việc.

* **Tích hợp Google Drive & Quản lý Trạng thái (Hoàn thành trong v1.3.0):**
    * Xây dựng hệ thống "Nhóm Dự án" trong Settings, cho phép quản lý các nguồn nội dung (Local/Google Drive).
    * Triển khai thành công luồng xác thực OAuth 2.0 an toàn để kết nối với Google API.
    * Xây dựng tính năng "Đồng bộ Thông minh" từ Google Drive, hỗ trợ các chế độ "Chỉ thêm mới" và "Làm mới toàn bộ".
    * Hoàn thiện hệ thống "Trạng thái Dự án" (Chưa làm, Đang làm dở, Đã làm) với cơ chế Menu Chuột phải và phản hồi trực quan bằng màu sắc.
    * Xây dựng cơ chế "Di chuyển Cơ sở dữ liệu" (Migration) tự động để đảm bảo tính tương thích ngược.

* **Hỗ trợ Đa ngôn ngữ TTS (Hoàn thành trong v1.2.0):**
    * Hoàn thiện tính năng lựa chọn ngôn ngữ và "Reading Style Prompt" tương ứng trong tab Text-to-Speech.

* **Hệ thống Quản lý Dự án & Thư viện (Hoàn thành trong v1.1.0):**
    * Xây dựng hệ thống "Thư viện" dựa trên mô hình "Dự án", cho phép quản lý các thành phần (Truyện, Tiêu đề, Thumbnail).
    * Tích hợp khái niệm "Dự án đang hoạt động" với thanh trạng thái trực quan.

* **Công cụ Tự động hóa Phiên bản (Hoàn thành trong v1.0.0):**
    * Xây dựng kịch bản `scripts/release.py` để tự động hóa việc nâng cấp phiên bản.