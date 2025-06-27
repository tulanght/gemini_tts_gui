# QUY TRÌNH LÀM VIỆC DỰ ÁN (Project Workflow)
# Version: 1.2
# Last Updated: 2025-06-27

## 1. Triết lý Chung
* Dự án tuân thủ quy trình Git-flow đơn giản, lấy `main` làm nhánh chính.
* Mọi thay đổi đều được thực hiện trên các nhánh tính năng (`feature/`), nhánh sửa lỗi (`fix/`), hoặc nhánh tài liệu (`docs/`) trước khi hợp nhất vào `main`.
* Sử dụng Gemini AI như một lập trình viên Python cộng tác cao cấp, tuân thủ chặt chẽ các quy tắc được định nghĩa trong tài liệu này.
* **Nguồn sự thật duy nhất (Single Source of Truth):** Nhánh `main` trên repository GitHub.

## 2. Quy trình làm việc với Git
### 2.1. Đặt tên nhánh
* **Tính năng mới:** `feature/<ten-tinh-nang-ngan-gon>`
* **Sửa lỗi:** `fix/<ten-loi-ngan-gon>`
* **Cập nhật tài liệu:** `docs/<noi-dung-cap-nhat>`
* **Tái cấu trúc code:** `refactor/<pham-vi-tai-cau-truc>`

### 2.2. Quy ước Commit Message
* Sử dụng quy ước **Conventional Commits** để tự động hóa và làm rõ lịch sử dự án.
* **Cấu trúc cơ bản:** `<type>(<scope>): <subject>`

<details>
<summary>Nhấn vào đây để xem giải thích và các ví dụ chi tiết</summary>

* **`<type>`:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`.
* **`<scope>` (không bắt buộc):** Phạm vi của thay đổi (ví dụ: `ui`, `tts`, `thumbnail`, `workflow`).
* **`<subject>`:** Mô tả ngắn gọn về thay đổi, viết ở thì hiện tại.

**Ví dụ thực tế:**
* `feat(thumbnail): Add per-line font size customization`
* `fix(tts): Handle empty input gracefully`
* `docs(workflow): Add detailed examples using <details> tag`
* `refactor(utils): Simplify file reading function`
* `style(main_app): Format code according to PEP8`
* `chore: Update .gitignore to exclude .tmp files`

</details>

### 2.3. Pull Requests (PR)
* Mỗi nhánh sau khi hoàn thành sẽ được mở Pull Request vào nhánh `main`.
* PR cần có mô tả rõ ràng về những gì đã thay đổi và tại sao.

## 3. Quy trình Cộng tác với Gemini AI
### 3.1. Vai trò và Nhiệm vụ của AI
* AI đóng vai trò là một **lập trình viên Python cộng tác cao cấp**.
* Mọi phân tích và đề xuất của AI phải dựa trên phiên bản code mới nhất trên nhánh `main`.

### 3.2. Quy tắc Vàng (Bắt buộc tuân thủ)
1.  **Phân tích Trước, Code Sau:** AI phải trình bày "Kế hoạch Thực thi" và "Tự Phản biện". Kế hoạch phải được phê duyệt trước khi viết code.
2.  **Cung cấp Code có Mục tiêu:** AI chỉ cung cấp các đoạn code cần thay đổi, sử dụng `(...)` để biểu thị phần code không đổi.
3.  **Ghi chú và Phiên bản:** Mã nguồn AI cung cấp phải có Docstring, Comment và ghi chú phiên bản/timestamp.

### 3.3. Cấu trúc Phản hồi Chuẩn của AI
* Mọi gói cập nhật code phải tuân theo cấu trúc 5 phần: Bối cảnh -> Gói Cập Nhật -> Giải thích -> Hướng dẫn Tích hợp -> Kết quả Kỳ vọng.

<details>
<summary>Nhấn vào đây để xem ví dụ chi tiết về một phản hồi chuẩn</summary>

#### **Phần 1: Bối cảnh và Phân tích**
(Ví dụ: "Mục tiêu của gói cập nhật này là khắc phục lỗi X, dựa trên Kế hoạch Y đã được phê duyệt. Vấn đề hiện tại là hàm Z không xử lý đúng trường hợp ABC...")

#### **Phần 2: Gói Cập Nhật Mục Tiêu**
```python
# /path/to/file.py
# Version: 2.1
# Last Updated: 2025-06-28
# (...)
def updated_function():
    # Code thay đổi ở đây
    return True
````

#### **Phần 3: Giải thích Chi tiết Mã nguồn**

(Ví dụ: "Hàm `updated_function` đã được sửa để xử lý trường hợp ngoại lệ Z bằng cách thêm khối try-except. Logic mới này đảm bảo ứng dụng không bị crash và ghi lại lỗi vào log...")

#### **Phần 4: Hướng dẫn Tích hợp**

1.  **Tạo nhánh mới:** `git checkout -b feature/ten-tinh-nang`
2.  **Áp dụng thay đổi:** Mở file `path/to/file.py` và thay thế toàn bộ hàm `updated_function` cũ bằng phiên bản mới được cung cấp.
3.  **Commit:** `git commit -m "feat(module): Update function to handle Z"`

#### **Phần 5: Kết quả Kỳ vọng và Bước tiếp theo**

(Ví dụ: "Sau khi áp dụng, lỗi X sẽ được khắc phục. Ứng dụng sẽ hoạt động ổn định hơn. Bước tiếp theo là bạn hãy thực hiện review code trên Pull Request. Sau khi được phê duyệt, chúng ta sẽ lên kế hoạch cho tính năng tiếp theo.")

\</details\>

## 4\. Quy trình Cải tiến Liên tục (Continuous Improvement)

### 4.1. Triết lý

  * **"Tài liệu sống":** Quy trình làm việc này là một tài liệu sống, được thiết kế để phát triển cùng với dự án.
  * **Chào đón đề xuất:** Mọi đề xuất nhằm cải thiện hiệu suất, sự rõ ràng và chất lượng công việc đều được khuyến khích.
  * **Nguyên tắc "Hướng đạo sinh":** "Luôn để lại khu cắm trại sạch sẽ hơn lúc bạn đến." Nếu phát hiện điểm bất hợp lý, hãy chủ động đề xuất cải tiến.

### 4.2. Các bước đề xuất một thay đổi

1.  **Nêu vấn đề (The "Why"):** Bên đề xuất (người dùng hoặc AI) cần trình bày rõ ràng vấn đề hoặc cơ hội.
2.  **Đưa ra giải pháp (The "What"):** Đề xuất một giải pháp cụ thể.
3.  **Thảo luận và Phê duyệt (The "How"):** Thống nhất và phê duyệt giải pháp.
4.  **Thực thi và Cập nhật (The "Implementation"):** Tạo nhánh mới, cập nhật tài liệu và hợp nhất vào `main`.

<!-- end list -->

