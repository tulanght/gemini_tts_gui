# Lịch sử thay đổi (Changelog)

Tất cả các thay đổi đáng chú ý của dự án sẽ được ghi lại tại đây.
Dự án này tuân theo [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2025-06-28

Đây là phiên bản ổn định đầu tiên, hoàn thiện các tính năng cốt lõi và khắc phục các vấn đề nghiêm trọng về môi trường và logic.

### Đã thêm (Added)
-   **Logic Cỡ chữ Nâng cao:** Triển khai cơ chế "cờ trạng thái" (`is_edited`) trong `thumbnail_preview.py` để "khóa" cỡ chữ của các dòng đã được chỉnh sửa thủ công, tránh bị "Cỡ chữ chung" ghi đè.
-   **Phụ thuộc Bắt buộc:** Thêm `fontTools` và `audioop-lts` vào `requirements.txt` để giải quyết các lỗi cốt lõi.
-   **Đóng gói Sản phẩm:** Thêm quy trình và hỗ trợ đóng gói ứng dụng thành file `.exe` bằng PyInstaller.
-   **Tài liệu Dự án:** Tạo mới các file `WORKFLOW.md` và `TECHNICAL_NOTES.md` để chuẩn hóa quy trình làm việc và ghi lại các quyết định kỹ thuật quan trọng.

### Đã thay đổi (Changed)
-   **Tái cấu trúc Kiến trúc Font (Rất quan trọng):** Viết lại hoàn toàn logic xử lý font trong `thumbnail_preview.py`. Dự án đã **từ bỏ hoàn toàn** việc hỗ trợ **Variable Fonts** do lỗi tương thích môi trường không thể khắc phục. Giờ đây, chương trình chỉ quét và làm việc với các **font tĩnh** (mỗi kiểu chữ là một file `.ttf` riêng biệt).
-   **Tái cấu trúc Logic "Cỡ chữ chung":** Đơn giản hóa hành vi của `Spinbox` Cỡ chữ chung, có hiệu lực ngay khi người dùng thay đổi giá trị, loại bỏ nút "Áp dụng" không cần thiết.

### Đã sửa (Fixed)
-   **Sửa lỗi Căn giữa Nghiêm trọng:** Khắc phục triệt để lỗi căn chỉnh của khối văn bản trong thumbnail. Khối text giờ đây luôn được căn giữa hoàn hảo theo cả chiều dọc và chiều ngang.
-   **Sửa lỗi Kiểu chữ (Font Weight):** Chức năng chọn Kiểu chữ (Bold, Normal...) từ `Combobox` chung giờ đây hoạt động chính xác và đáng tin cậy.
-   **Sửa lỗi Môi trường `pydub`:** Khắc phục hoàn toàn lỗi `ModuleNotFoundError: No module named 'pyaudioop'` khi khởi chạy ứng dụng.
-   **Sửa lỗi Đóng gói:** Khắc phục lỗi `FileNotFoundError` khi build file `.exe` do thiếu file icon.

### Đã xóa (Removed)
-   Loại bỏ hoàn toàn các widget và logic không được yêu cầu liên quan đến việc chọn kiểu chữ cho từng dòng, quay về đúng yêu cầu gốc là một kiểu chữ thống nhất.

---

## [0.8.0] - (Ngày tháng cũ)
-   ... (Các thay đổi cũ)

## [0.8.0] - 2025-06-27
### Đã thay đổi (Changed)
- **Tài liệu:** Hợp nhất các file hướng dẫn thành một file `WORKFLOW.md` duy nhất, đồng thời tạo mới `CHANGELOG.md` và `ROADMAP.md` để làm rõ quy trình.
- **Thumbnail Preview:** Tái cấu trúc (refactor) module để chuẩn bị cho việc hỗ trợ tùy chỉnh thuộc tính (cỡ chữ, font weight) cho từng dòng văn bản riêng biệt.

### Đã thêm (Added)
- **Workflow:** Bổ sung quy trình cải tiến liên tục vào `WORKFLOW.md`.