# QUY TRÌNH LÀM VIỆC DỰ ÁN (Project Workflow)
# version: 4.2
# last-updated: 2025-07-21
# description: Bổ sung "Bước 0.5: Kiểm tra Trạng thái" để tăng độ tin cậy.

## 1. Checklist Khởi đầu (Bắt buộc trước mỗi nhiệm vụ mới)
- [ ] Đã đồng bộ với trạng thái mới nhất của nhánh `main`.
- [ ] Đã đọc và hiểu rõ các quy tắc trong file `WORKFLOW.md` này.
- [ ] **Đã đọc và hiểu các giới hạn trong file `TECHNICAL_NOTES.md`**

## 2. Triết lý Chung
* **Nguồn sự thật duy nhất:** Nhánh `main` là nền tảng ổn định.
* **Làm việc trên nhánh:** Mọi thay đổi đều phải được thực hiện trên nhánh riêng.
* **Hợp nhất qua Pull Request:** Mọi thay đổi chỉ được đưa vào `main` qua PR.
* **AI là Cộng tác viên:** Gemini AI phải tuân thủ nghiêm ngặt toàn bộ quy trình này.

### 2.1. Nguyên tắc Kiến trúc: Tách bạch Trách nhiệm
* **Mục đích:** Đảm bảo mã nguồn có tổ chức, dễ bảo trì và mở rộng.
* **Quy tắc:**
    * **Module Giao diện (View/Controller):** Các file như `main_app.py`, `library_tab.py` chịu trách nhiệm xây dựng, sắp xếp các widget và xử lý các sự kiện từ người dùng.
    * **Module Logic/Dữ liệu (Model):** Các file như `settings_manager.py`, `database.py` chịu trách nhiệm xử lý việc lưu, tải, và thao tác với dữ liệu. Các module này **không được** chứa mã nguồn liên quan đến giao diện (Tkinter).
    * **Luồng hoạt động:** Module Giao diện sẽ gọi các hàm từ Module Logic để thực thi nhiệm vụ.

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
* **Quy tắc cho File:** Mọi file mã nguồn `.py` và tài liệu `.md` quan trọng khi được chỉnh sửa lớn phải có khối bình luận ở đầu file theo định dạng:
    ```python
    # file-path: [đường dẫn]
    # version: [số phiên bản, ví dụ: 2.1]
    # last-updated: [YYYY-MM-DD]
    # description: [Mô tả thay đổi]
    ```
* **Quy tắc cho Hotfix hàm (CẬP NHẬT):** Khi cung cấp một bản vá lỗi nhỏ cho một hàm, AI phải thêm khối bình luận sau ngay trên hàm đó, với ngày giờ thực tế:
    ```python
    # hotfix v[phiên-bản-file].[số-thứ-tự] - YYYY-MM-DD - [Lý do sửa đổi ngắn gọn]
    ```
    * **Ví dụ:** `# hotfix v6.7.1 - 2025-07-19 - Sửa lỗi luồng và thuộc tính.`

### 3.6. Quy trình Hoàn tất Tính năng & Phát hành
* **Quy tắc:** Khi một nhánh `feature/...` được xác nhận là đã hoàn thành, quy trình sau là **bắt buộc** trước khi tạo PR.
1.  **Chạy Kịch bản Nâng cấp:** Người dùng thực thi lệnh `python scripts/release.py`.
2.  **Nhập Phiên bản mới:** Cung cấp số hiệu phiên bản mới.
3.  **Điền Changelog:** Người dùng mở `CHANGELOG.md` và điền chi tiết thay đổi.
4.  **Commit & Hợp nhất:** Tiến hành commit và tạo Pull Request.

### 3.7. Quy trình Cập nhật Roadmap
* Khi một giai đoạn lớn được hoàn thành, mục đó sẽ được xóa bỏ khỏi kế hoạch và một dòng tóm tắt thành tựu sẽ được thêm vào cuối file.

## 4. Quy trình Cộng tác với Gemini AI (BẮT BUỘC)

### 4.1. Bước 0: Xác nhận Nhiệm vụ (Khóa an toàn)
* **Quy tắc:** Sau mỗi yêu cầu mới từ người dùng, phản hồi **đầu tiên và duy nhất** của AI bắt buộc phải là:
    > "Đã nhận nhiệm vụ. Đã hoàn thành 'Checklist Khởi đầu'. Đang phân tích theo `WORKFLOW.md`."

### 4.2. Bước 0.5: Kiểm tra Trạng thái (MỚI)
* **Quy tắc:** Ngay sau "Bước 0", trước khi trình bày "Kế hoạch Thực thi", AI bắt buộc phải đưa ra một khối "Kiểm tra Trạng thái" để được người dùng xác nhận.
* **Mục đích:** Để đảm bảo AI và người dùng luôn đồng bộ về tiến độ và mục tiêu, tránh việc AI "nhớ nhầm" phiên bản.
* **Định dạng:**
    ```
    **KIỂM TRA TRẠNG THÁI:**
    * **Phiên bản Hoàn thành Gần nhất:** `vX.Y.Z` ([Tên tính năng chính]).
    * **Nhiệm-vụ Hiện tại:** [Tên nhiệm vụ đang thực hiện].
    * **Phiên bản Đề xuất sau khi Hoàn thành:** `vA.B.C`.

    *Vui lòng xác nhận ("OK") nếu các thông tin trên là chính xác.*
    ```

### 4.3. Bước 1: Kế hoạch Thực thi
* **Quy tắc:** Sau khi "Kiểm tra Trạng thái" được xác nhận, AI phải trình bày một **"Kế hoạch Thực thi"** chi tiết.
* **Nội dung:** Phải bao gồm **"Phân tích"** và **"Tự Phản biện"**.
* **Phê duyệt:** Kế hoạch phải được người dùng phê duyệt.

### 4.4. Bước 2: Cung cấp Gói Cập Nhật Mục Tiêu
* **Quy tắc:** Mặc định cung cấp **toàn bộ nội dung của file**.
* **Ngoại lệ "Hotfix":** Chỉ cung cấp một đoạn code nhỏ khi được người dùng cho phép.

### 4.5. Bước 3: Cấu trúc Phản hồi Chuẩn của AI
* **Quy tắc:** Mọi phản hồi chính phải tuân thủ cấu trúc 4 phần:
    1.  `Phần 1: Phân tích & Kế hoạch`
    2.  `Phần 2: Gói Cập Nhật Mục Tiêu (Nếu có)`
    3.  `Phần 3: Hướng dẫn Hành động Tiếp theo dành cho bạn`
    4.  `Phần 4: Kết quả Kỳ vọng & Cảnh báo`

### 4.6. Bước 4: Hướng dẫn Tích hợp và Kiểm thử
* Phần "Hướng dẫn" phải bao gồm các bước kiểm thử cụ thể và yêu cầu **commit sau khi đã xác nhận code chạy đúng**.

### 4.7. Cơ chế "Reset"
* Khi AI vi phạm quy tắc, người dùng sẽ sử dụng từ khóa **`CHECK-WORKFLOW v[số-phiên-bản]`** (ví dụ: `CHECK-WORKFLOW v4.1`) để yêu cầu AI dừng lại và rà soát đúng phiên bản.

## 5. Phụ lục: Template Yêu cầu dành cho Người dùng
* (Phần này giữ nguyên không thay đổi)