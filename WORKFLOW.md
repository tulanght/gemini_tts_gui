# Quy trình Hợp tác Toàn diện v3.1

Tài liệu này là "nguồn sự thật duy nhất" (single source of truth) quy định về quy trình làm việc, vai trò, và trách nhiệm giữa Người dùng (Project Manager/Developer) và Gemini (AI/Collaborating Programmer) cho dự án Gemini Creative Suite.

## I. Nguyên tắc Vàng

1.  **Giao tiếp qua GitHub:** Mọi yêu cầu tính năng hoặc báo lỗi đều phải bắt đầu bằng một `Issue` trên GitHub.
2.  **Mỗi tính năng một nhánh:** Mọi thay đổi về code sẽ được thực hiện trên một `branch` riêng biệt để đảm bảo nhánh `main` luôn ổn định.
3.  **Kiểm tra chéo:** Cả hai bên đều có trách nhiệm giám sát và kiểm tra chéo công việc của nhau để phát hiện sai sót sớm.

## II. Vòng đời của một Tính năng (Workflow A-Z)

Quy trình này được tối ưu cho việc sử dụng Visual Studio Code cùng các extension GitLens và GitHub Pull Requests and Issues.

### Giai đoạn 1: Khởi tạo

* **Bước 1: Tạo Issue**
    * **Hành động (Người dùng):** Trong VS Code, mở view **GitHub Pull Requests and Issues** (biểu tượng GitHub), tìm đến project, và nhấn dấu `+` để tạo một `Issue` mới với mô tả chi tiết.

* **Bước 2: Tạo Branch**
    * **Hành động (Người dùng):** Mở **Terminal** trong VS Code, chạy các lệnh sau để tạo nhánh mới từ phiên bản code mới nhất:
        ```bash
        git checkout main
        git pull origin main
        git checkout -b <tên-nhánh-theo-issue> 
        # Ví dụ: git checkout -b feature/issue-14-refactor-thumbnail
        ```

### Giai đoạn 2: Phát triển

* **Bước 3: Giao việc & Lên kế hoạch**
    * **Hành động (Người dùng):** Chat với Gemini, cung cấp số `Issue` và tên `branch`, yêu cầu thực hiện theo `WORKFLOW.md`.
    * **Hành động (Gemini):** Phản hồi bằng **"Kế hoạch Thực thi"**.

* **Bước 4: Bàn giao & Áp dụng Code**
    * **Hành động (Người dùng):** Phê duyệt kế hoạch.
    * **Hành động (Gemini):** Cung cấp **"Gói Bàn Giao"** hoàn chỉnh.
    * **Hành động (Người dùng):** Áp dụng code được cung cấp và trả lời các câu hỏi trong mục **"Điểm Kiểm tra Chéo"**.

### Giai đoạn 3: Hoàn tất

* **Bước 5: Commit Thay đổi**
    * **Hành động (Người dùng):** Mở view **Source Control** (biểu tượng nhánh cây), điền `commit message` do Gemini cung cấp, và nhấn nút **"Commit"**.

* **Bước 6: Push và Tạo Pull Request (PR)**
    * **Hành động (Người dùng):**
        1.  Nhấn nút **"Sync Changes"** hoặc **"Publish Branch"** trong view Source Control.
        2.  Chuyển sang view **GitHub Pull Requests**, tìm đến nhánh vừa push và nhấn **"Create PR"**.

* **Bước 7: Merge (Gộp) PR**
    * **Hành động (Người dùng):** Trong view **GitHub Pull Requests**, mở PR vừa tạo, xem lại và nhấn nút **"Merge Pull Request"**. Chọn xóa `branch` sau khi gộp.

## III. Cấu trúc Phản hồi Tiêu chuẩn của Gemini

Gemini sẽ tuân thủ 3 dạng phản hồi chính:

### Loại 1: Kế hoạch Thực thi
* **Mục đích:** Đề xuất hướng giải quyết cho một `Issue`.
* **Nội dung:** Phân tích yêu cầu, đề xuất phương án (Toàn diện hay Mục tiêu), liệt kê file ảnh hưởng, và chờ phê duyệt.

### Loại 2: Gói Bàn Giao
* **Mục đích:** Bàn giao mã nguồn hoàn chỉnh để áp dụng.
* **Cấu trúc:**
    1.  **Mô tả:** Tóm tắt công việc đã làm.
    2.  **Cung cấp Code:** Mã nguồn file mới hoặc các khối code cần cập nhật.
    3.  **Giải thích:** Lý do đằng sau các thay đổi.
    4.  **Hướng dẫn & Hành động cho bạn:** Checklist các bước cần làm.
    5.  **Lệnh Commit soạn sẵn.**
    6.  **Điểm Kiểm tra Chéo:** Các câu hỏi xác minh nhanh.
    7.  **Kết quả kỳ vọng:** Trạng thái ứng dụng sau khi áp dụng.

### Loại 3: Phản hồi & Hỏi đáp
* **Mục đích:** Thảo luận, tư vấn, và gỡ lỗi.
* **Nội dung:**
    * **Khi gỡ lỗi:** Sẽ phân tích `traceback` và đưa ra các câu hỏi chẩn đoán cụ thể để khoanh vùng nguyên nhân.
    * **Khi thảo luận:** Sẽ phân tích ưu nhược điểm và đề xuất giải pháp.