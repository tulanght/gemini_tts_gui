# Quy trình Hợp tác Toàn diện v4.1

Tài liệu này là "nguồn sự thật duy nhất" (single source of truth) quy định về quy trình làm việc, vai trò, và trách nhiệm giữa Người dùng (Project Manager/Developer) và Gemini (AI/Collaborating Programmer) cho dự án Gemini Creative Suite.

## I. Tổng quan

1.  **Nền tảng:** Mọi công việc được thực hiện trong Visual Studio Code với các extension GitLens và GitHub Pull Requests.
2.  **Nguyên tắc:** Mỗi thay đổi (feature, bugfix) được thực hiện trên một `branch` riêng và được tích hợp vào `main` thông qua một `Pull Request`.
3.  **Kiểm tra chéo:** Gemini có trách nhiệm cung cấp các "Điểm Kiểm tra Chéo" trong mỗi "Gói Bàn Giao" để người dùng xác minh, giảm thiểu sai sót.

## II. Quy tắc tạo Issue linh hoạt

* **BẮT BUỘC TẠO ISSUE:** Đối với các nhiệm vụ đột xuất như báo lỗi (Bug) hoặc đề xuất ý tưởng mới không có trong lộ trình.
* **TÙY CHỌN (KHÔNG BẮT BUỘC):** Đối với các nhiệm vụ đã được định nghĩa sẵn trong lộ trình (file `PROJECT_HANDOVER_PROMPT_v2.md`).

## III. Quy trình chi tiết từ A-Z

### Giai đoạn 1: Chuẩn bị

* **Bước 1: Lấy code mới nhất và Tạo Branch**
    * **Hành động (Người dùng):** Mở **Terminal** trong VS Code, chạy các lệnh:
        ```bash
        git checkout main
        git pull origin main
        git checkout -b <tên-nhánh-gợi-nhớ>
        ```

* **Bước 2: Giao việc**
    * **Hành động (Người dùng):** Chat với Gemini, giao nhiệm vụ.
    * **Hành động (Gemini):** Phản hồi bằng **"Kế hoạch Thực thi"**.

### Giai đoạn 2: Phát triển

* **Bước 3: Bàn giao và Áp dụng**
    * **Hành động (Người dùng):** Phê duyệt kế hoạch, áp dụng code, và trả lời **"Điểm Kiểm tra Chéo"**.

### Giai đoạn 3: Tích hợp (Hoàn toàn trong VS Code UI)

* **Bước 4: Commit Code**
    * **Hành động (Người dùng):** Mở view **Source Control**, stage các file, dán `commit message` do Gemini cung cấp, và nhấn nút **"Commit"**.

* **Bước 5: Publish Branch**
    * **Hành động (Người dùng):** Trong view **Source Control**, nhấn nút **"Publish Branch"**.

* **Bước 6: Tạo Pull Request (PR)**
    * **Hành động (Người dùng):**
        1.  Sau khi "Publish", VS Code sẽ đề nghị tạo PR. Hoặc vào view **GitHub Pull Requests** và nhấn **"Create PR"**.
        2.  Trong tab "Create Pull Request" mới mở ra, kiểm tra lại thông tin và nhấn nút **"Create"** màu xanh dương.

* **Bước 7: Merge (Gộp) và Dọn dẹp PR**
    * **Hành động (Người dùng):**
        1.  Giao diện sẽ chuyển sang màn hình quản lý PR. Tại đây, bạn có thể rà soát lại các thay đổi trong mục "Files Changed".
        2.  Nhấn nút **"Merge Pull Request"** màu xanh lá cây.
        3.  Xác nhận việc Merge.
        4.  Nhấn nút **"Delete Branch"** xuất hiện sau đó để dọn dẹp.

## IV. Cấu trúc Phản hồi Tiêu chuẩn của Gemini

Gemini sẽ tuân thủ 3 dạng phản hồi chính:

1.  **Loại 1: Kế hoạch Thực thi:** Đề xuất hướng giải quyết cho một nhiệm vụ.
2.  **Loại 2: Gói Bàn Giao:** Bàn giao mã nguồn hoàn chỉnh, bao gồm 7 mục: Mô tả, Cung cấp Code, Giải thích, Hướng dẫn, Lệnh Commit, Điểm Kiểm tra Chéo, và Kết quả kỳ vọng.
3.  **Loại 3: Phản hồi & Hỏi đáp:** Thảo luận, tư vấn, và gỡ lỗi.