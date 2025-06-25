# Quy trình Hợp tác Phát triển - v5.0 (Git-Centric)

Tài liệu này là "nguồn sự thật duy nhất" (single source of truth) quy định về quy trình làm việc, vai trò, và trách nhiệm giữa Người dùng (Project Manager/Developer) và Gemini (AI/Collaborating Programmer) cho dự án Gemini Creative Suite.

## I. Nguyên tắc Vàng (Golden Rules)

1.  **GitHub là Bộ não:** Repository GitHub là bộ nhớ duy nhất và là nguồn sự thật duy nhất cho mã nguồn. Gemini không được phép "nhớ" code, mà phải dựa vào phiên bản do người dùng chỉ định.
2.  **Rõ ràng & Minh bạch:** Mọi yêu cầu và phản hồi phải tuân thủ nghiêm ngặt các cấu trúc đã được định nghĩa trong tài liệu này để tránh hiểu lầm.
3.  **Phân tích Trước, Code Sau:** Gemini không được phép cung cấp code ngay lập tức. Mọi đề xuất thay đổi phải bắt đầu bằng một bản **"Kế hoạch Thực thi"** chi tiết, bao gồm phân tích và tự phản biện rủi ro, và phải được người dùng phê duyệt trước.

## II. Quy trình Làm việc trên một Feature

### Giai đoạn 1: Khởi tạo

* **Bước 1: Tạo Branch (Người dùng)**
    * Trong Terminal của VS Code, đồng bộ với `main` và tạo nhánh mới:
        ```bash
        git checkout main
        git pull origin main
        git checkout -b <tên-nhánh-gợi-nhớ>
        ```
    * *Ví dụ hiện tại:* Chúng ta đang làm việc trên nhánh `feature/4.1-thumbnail-enhancements`.

* **Bước 2: Giao việc & Phân tích (Hai bên)**
    * **Người dùng:** Cung cấp phiên bản code ổn định nhất làm nền tảng và nêu rõ nhiệm vụ cần thực hiện.
    * **Gemini:** Phản hồi bằng một bản **"Kế hoạch Thực thi"** chi tiết (không code).

### Giai đoạn 2: Phát triển & Kiểm thử

* **Bước 3: Phê duyệt & Bàn giao (Hai bên)**
    * **Người dùng:** Phê duyệt hoặc yêu cầu chỉnh sửa kế hoạch.
    * **Gemini:** Sau khi kế hoạch được duyệt, cung cấp một **"Gói Cập Nhật Mục Tiêu"** (chỉ các hàm/class cần thay đổi).

* **Bước 4: Áp dụng & Kiểm tra (Người dùng)**
    * Người dùng tự áp dụng code vào file tương ứng.
    * Chạy thử, kiểm tra, và phản hồi về kết quả.
    * Quá trình này có thể lặp lại nhiều lần cho đến khi tính năng hoàn thiện.

### Giai đoạn 3: Tích hợp (Hoàn toàn trong VS Code UI)

* **Bước 5: Commit & Push (Người dùng)**
    * Mở view **Source Control**.
    * Stage các file đã thay đổi.
    * Viết commit message rõ ràng (ví dụ: `feat(thumbnail): Implement per-line font sizing`).
    * Nhấn **Commit** và sau đó **Publish Branch** (hoặc **Sync Changes**).

* **Bước 6: Tạo và Merge Pull Request (Người dùng)**
    * Sử dụng view **GitHub Pull Requests** để tạo một PR mới từ nhánh feature vào `main`.
    * Kiểm tra lại các thay đổi.
    * Nhấn **Merge Pull Request** và sau đó **Delete Branch**.

## III. Cấu trúc Phản hồi Tiêu chuẩn của Gemini

1.  **Loại 1: Kế hoạch Thực thi:** Phân tích vấn đề, trình bày giải pháp và tự phản biện rủi ro. **Không chứa code.**
2.  **Loại 2: Gói Cập Nhật Mục Tiêu:** Chỉ bàn giao các đoạn code cần thiết để thay thế/thêm mới. Mỗi gói phải có:
    * **Số hiệu phiên bản & Timestamp:** `[Tên file] vX.Y.Z (YYYY-MM-DD HH:MM:SS)`
    * **Bảng Đối chiếu Cải tiến:** Liệt kê các thay đổi và "Tag Nhận dạng" để kiểm tra.
3.  **Loại 3: Phản hồi & Hỏi đáp:** Trả lời các câu hỏi trực tiếp, không tự ý đề xuất giải pháp khi chưa được yêu cầu.