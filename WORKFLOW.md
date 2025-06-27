# QUY TRÌNH LÀM VIỆC DỰ ÁN (Project Workflow)
# Version: 1.0
# Last Updated: 2025-06-27

## 1. Triết lý Chung
* Dự án tuân thủ quy trình Git-flow đơn giản, lấy `main` làm nhánh chính.
* Mọi thay đổi đều được thực hiện trên các nhánh tính năng (`feature/`), nhánh sửa lỗi (`fix/`), hoặc nhánh tài liệu (`docs/`) trước khi hợp nhất vào `main`.
* Sử dụng Gemini AI như một lập trình viên Python cộng tác cao cấp, tuân thủ chặt chẽ các quy tắc được định nghĩa trong tài liệu này.
* **Nguồn sự thật duy nhất (Single Source of Truth):** Nhánh `main` trên repository GitHub.

## 2. Quy trình làm việc với Git
### 2.1. Đặt tên nhánh
* **Tính năng mới:** `feature/<ten-tinh-nang-ngan-gon>` (ví dụ: `feature/thumbnail-per-line-styling`)
* **Sửa lỗi:** `fix/<ten-loi-ngan-gon>` (ví dụ: `fix/font-weight-logic`)
* **Cập nhật tài liệu:** `docs/<noi-dung-cap-nhat>` (ví dụ: `docs/update-workflow-file`)
* **Tái cấu trúc code:** `refactor/<pham-vi-tai-cau-truc>` (ví dụ: `refactor/simplify-tts-logic`)

### 2.2. Quy ước Commit Message
* Sử dụng quy ước **Conventional Commits** để tự động hóa và làm rõ lịch sử dự án.
* **Cấu trúc:** `<type>(<scope>): <subject>`
* **Các `type` phổ biến:**
    * `feat`: Thêm một tính năng mới.
    * `fix`: Sửa một lỗi.
    * `docs`: Thay đổi liên quan đến tài liệu.
    * `style`: Thay đổi về định dạng code (dấu chấm phẩy, thụt lề...).
    * `refactor`: Tái cấu trúc code mà không sửa lỗi hay thêm tính năng.
    * `test`: Thêm hoặc sửa các bài test.
    * `chore`: Các công việc khác không ảnh hưởng đến mã nguồn (cập nhật build scripts, quản lý package...).
* **Ví dụ:** `feat(thumbnail): Refactor to support per-line styling`, `fix(ui): Correct button alignment`, `docs: Consolidate workflow and remove outdated prompts`.

### 2.3. Pull Requests (PR)
* Mỗi nhánh sau khi hoàn thành sẽ được mở Pull Request vào nhánh `main`.
* PR cần có mô tả rõ ràng về những gì đã thay đổi và tại sao.

## 3. Quy trình Cộng tác với Gemini AI
### 3.1. Vai trò và Nhiệm vụ của AI
* AI đóng vai trò là một **lập trình viên Python cộng tác cao cấp**.
* Mọi phân tích và đề xuất của AI phải dựa trên phiên bản code mới nhất trên nhánh `main` đã được cung cấp.

### 3.2. Quy tắc Vàng (Bắt buộc tuân thủ)
1.  **Phân tích Trước, Code Sau:** AI phải trình bày "Kế hoạch Thực thi" chi tiết và phần "Tự Phản biện". Kế hoạch phải được người dùng phê duyệt trước khi viết code.
2.  **Cung cấp Code có Mục tiêu:** AI chỉ được cung cấp các đoạn code của hàm hoặc class cần thay đổi, sử dụng `(...)` để biểu thị phần code không đổi.
3.  **Ghi chú và Phiên bản:** Mọi mã nguồn AI cung cấp phải có Docstring, Comment và ghi chú phiên bản/timestamp nếu có thay đổi lớn.

### 3.3. Cấu trúc Phản hồi Chuẩn của AI
* Mọi gói cập nhật code phải tuân theo cấu trúc 5 phần:
    1.  **Phần 1: Bối cảnh và Phân tích:** Giới thiệu mục tiêu, liên kết với kế hoạch đã duyệt.
    2.  **Phần 2: Gói Cập Nhật Mục Tiêu:** Cung cấp mã nguồn thay đổi.
    3.  **Phần 3: Giải thích Chi tiết Mã nguồn:** Giải thích lý do và logic của thay đổi.
    4.  **Phần 4: Hướng dẫn Tích hợp:** Các bước Git và thao tác trên file để áp dụng code.
    5.  **Phần 5: Kết quả Kỳ vọng và Bước tiếp theo:** Mô tả trạng thái dự án sau khi áp dụng và đề xuất bước kế tiếp.