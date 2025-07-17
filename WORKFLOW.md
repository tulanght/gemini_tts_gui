# QUY TRÌNH LÀM VIỆC DỰ ÁN (Project Workflow)
# version: 3.0
# last-updated: 2025-07-17
# description: Tái cấu trúc, hợp nhất các quy tắc versioning và tích hợp release script.

## 1. Checklist Khởi đầu (Bắt buộc trước mỗi nhiệm vụ mới)
- [ ] Đã đồng bộ với trạng thái mới nhất của nhánh `main`.
- [ ] Đã đọc và hiểu rõ các quy tắc trong file `WORKFLOW.md` này.
- [ ] **Đã đọc và hiểu các giới hạn trong file `TECHNICAL_NOTES.md`**

## 2. Triết lý Chung
* **Nguồn sự thật duy nhất:** Nhánh `main` là nền tảng ổn định.
* **Làm việc trên nhánh:** Mọi thay đổi đều phải được thực hiện trên nhánh riêng.
* **Hợp nhất qua Pull Request:** Mọi thay đổi chỉ được đưa vào `main` qua PR.
* **AI là Cộng tác viên:** Gemini AI phải tuân thủ nghiêm ngặt toàn bộ quy trình này.

## 3. Quy trình làm việc với Git & Môi trường

### 3.1. Đặt tên nhánh
* **Tính năng mới:** `feature/<ten-tinh-nang-ngan-gon>`
* **Sửa lỗi:** `fix/<ten-loi>`
* **Tài liệu/Quy trình:** `docs/<noi-dung-cap-nhat>`
* **Tái cấu trúc:** `refactor/<pham-vi-tai-cau-truc>`

### 3.2. Quy ước Commit Message
* Sử dụng **Conventional Commits** (`<type>(<scope>): <subject>`).

### 3.3. Quy trình Pull Request (PR) & Hợp nhất
1.  **Tạo PR:** Tạo PR với `base` là `main`.
2.  **Review:** Xem xét lại các thay đổi.
3.  **Hợp nhất (Merge):** Hợp nhất PR vào `main`.
4.  **Dọn dẹp (Cleanup):** Xóa nhánh đã làm việc.

### 3.4. Quản lý Thư viện (`requirements.txt`)
* Khi thay đổi thư viện, sau khi kiểm thử ổn định, chạy `pip freeze > requirements.txt` để cập nhật.

### 3.5. Quy tắc Versioning File & Hotfix (HỢP NHẤT)
* **Mục đích:** Để theo dõi chính xác các phiên bản của từng file, tránh nhầm lẫn.
* **Quy tắc cho File:** Mọi file mã nguồn `.py` và tài liệu `.md` quan trọng khi được chỉnh sửa lớn phải có một khối bình luận ở đầu file theo định dạng:
    ```python
    # file-path: [đường dẫn]
    # version: [số phiên bản, ví dụ: 2.1]
    # last-updated: [YYYY-MM-DD]
    # description: [Mô tả thay đổi]
    ```
* **Quy tắc cho Hotfix hàm:** Khi cung cấp một bản vá lỗi nhỏ cho một hàm, AI phải thêm khối bình luận sau ngay trên hàm đó:
    ```python
    # hotfix-version: [file_version].[hotfix_count].[a,b,c] (ví dụ: v2.1.a)
    # hotfix-date: [YYYY-MM-DD HH:MM:SS]
    # hotfix-reason: [Lý do sửa đổi]
    ```

### 3.6. Quy trình Hoàn tất Tính năng & Phát hành (CẬP NHẬT)
* **Quy tắc:** Khi một nhánh `feature/...` được xác nhận là đã hoàn thành về mặt code, quy trình sau là **bắt buộc** trước khi tạo Pull Request.
1.  **Chạy Kịch bản Nâng cấp:** Người dùng thực thi lệnh `python scripts/release.py`.
2.  **Nhập Phiên bản mới:** Cung cấp số hiệu phiên bản mới (ví dụ: `1.2.0` -> `1.3.0`). Kịch bản sẽ tự động cập nhật `constants.py`, `README.md`, và `CHANGELOG.md`.
3.  **Điền Changelog:** Người dùng mở file `CHANGELOG.md` và điền chi tiết các thay đổi vào template đã được tạo sẵn.
4.  **Commit & Hợp nhất:** Sau khi hoàn tất các bước trên, tiến hành commit và tạo Pull Request.

### 3.7. Quy trình Cập nhật Roadmap
* Khi một giai đoạn lớn được hoàn thành, mục đó sẽ được xóa bỏ khỏi kế hoạch và một dòng tóm tắt thành tựu sẽ được thêm vào cuối file.

## 4. Quy trình Cộng tác với Gemini AI (BẮT BUỘC)

### 4.1. Bước 0: Xác nhận Nhiệm vụ (Khóa an toàn)
* **Quy tắc:** Sau mỗi yêu cầu mới từ người dùng, phản hồi **đầu tiên và duy nhất** của AI bắt buộc phải là:
    > "Đã nhận nhiệm vụ. Đã hoàn thành 'Checklist Khởi đầu'. Đang phân tích theo `WORKFLOW.md`."
* **Mục đích:** Buộc AI phải "nạp" lại toàn bộ quy trình và báo hiệu cho người dùng rằng quy trình đã bắt đầu đúng hướng.

### 4.2. Bước 1: Kế hoạch Thực thi
* **Quy tắc:** Trước khi cung cấp bất kỳ mã nguồn nào, AI phải trình bày một **"Kế hoạch Thực thi"** chi tiết.
* **Nội dung kế hoạch:** Phải bao gồm phần **"Phân tích"** và **"Tự Phản biện"** (phân tích rủi ro, lựa chọn thay thế, lý do chọn giải pháp).
* **Phê duyệt:** Kế hoạch phải được người dùng phê duyệt một cách tường minh (ví dụ: `Phê duyệt kế hoạch.`).

### 4.3. Bước 2: Cung cấp Gói Cập Nhật Mục Tiêu
* **Quy tắc về Nội dung:** Mặc định, mọi gói cập nhật mã nguồn phải là **toàn bộ nội dung của file** bị ảnh hưởng.
* **Ngoại lệ "Hotfix":** AI chỉ được phép cung cấp một đoạn code nhỏ ("hotfix") khi và chỉ khi đã hỏi và được người dùng cho phép một cách tường minh.

### 4.4. Bước 3: Cấu trúc Phản hồi Chuẩn của AI
* **Quy tắc:** Mọi phản hồi cung cấp "Kế hoạch" hoặc "Gói Cập Nhật" đều phải tuân thủ cấu trúc 4 phần sau để đảm bảo sự rõ ràng và có tính hành động.
    1.  **Phần 1: Phân tích & Kế hoạch:** Trình bày phân tích và/hoặc kế hoạch thực thi chi tiết.
    2.  **Phần 2: Gói Cập Nhật Mục Tiêu (Nếu có):** Cung cấp mã nguồn hoặc nội dung cập nhật.
    3.  **Phần 3: Hướng dẫn Hành động Tiếp theo dành cho bạn:** Chỉ rõ từng bước bạn cần làm tiếp theo.
    4.  **Phần 4: Kết quả Kỳ vọng & Cảnh báo:** Mô tả kết quả người dùng nên mong đợi sau khi thực hiện, và các rủi ro hoặc cảnh báo cần lưu ý.

### 4.5. Bước 4: Hướng dẫn Tích hợp và Kiểm thử
* Phần "Hướng dẫn" của AI phải bao gồm các bước kiểm thử cụ thể.
* Phải có ghi chú rõ ràng, yêu cầu người dùng **chỉ `git add` và `git commit` sau khi đã xác nhận code chạy đúng yêu cầu**.

### 4.6. Cơ chế "Reset"
* Khi AI vi phạm bất kỳ quy tắc nào ở trên, người dùng sẽ sử dụng từ khóa **`CHECK-WORKFLOW`** để yêu cầu AI dừng lại, rà soát và tự sửa lỗi.

## 5. Phụ lục: Template Yêu cầu dành cho Người dùng
*Để tối ưu hóa sự tương tác, hãy sử dụng các template này khi đưa ra yêu cầu.*

### Template A: Khi Yêu cầu Nhiệm vụ Mới / Sửa lỗi
Nhiệm vụ: [Tên nhiệm vụ ngắn gọn]

Mô tả: [Mô tả chi tiết những gì cần làm.]

Bối cảnh Quan trọng: [Liệt kê thông tin nền mà AI cần biết.]

Kết quả Mong muốn: [Mô tả sản phẩm cuối cùng trông như thế nào hoặc hoạt động ra sao.]

### Template B: Khi Báo cáo Lỗi sau khi Chạy Test
Tình trạng: [Chạy test thất bại / Gặp lỗi]

Mô tả Lỗi: [Mô tả ngắn gọn những gì bạn quan sát được.]

Log/Traceback:
(Dán toàn bộ log lỗi vào đây)

Hành động Đã thử (Nếu có): [Liệt kê những gì bạn đã thử để khắc phục.]