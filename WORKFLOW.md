# QUY TRÌNH LÀM VIỆC DỰ ÁN (Project Workflow)
# version: 9.0
# last-updated: 2025-07-22
# description: Phiên bản cuối cùng. Hoàn thiện quy tắc cung cấp mã nguồn, phân biệt rõ ràng giữa hotfix cho hàm và cập nhật header cho file.

## 1. Nguồn Lực Tham Chiếu
Trước khi bắt đầu bất kỳ nhiệm vụ nào, các tài liệu sau phải luôn được coi là nguồn thông tin cốt lõi và đáng tin cậy:
* **`WORKFLOW.md` (File này):** "Hiến pháp" về mọi quy trình làm việc.
* **`ROADMAP.md`:** Lộ trình phát triển và các mục tiêu của dự án.
* **`TECHNICAL_NOTES.md`:** Các quyết định kiến trúc và bài học kỹ thuật quan trọng.
* **`CHANGELOG.md`:** Lịch sử các thay đổi đã được phát hành để nắm được bối cảnh gần nhất.

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
* Sử dụng **Conventional Commits** (`<type>(<scope>): <subject>`). Có hai loại commit chính:
    * **Commit tính năng:** `feat`, `fix`, `refactor`, etc. (Ví dụ: `feat(ui): add new button`).
    * **Commit phát hành:** Luôn là `release: version X.Y.Z`.

### 3.3. Quy trình Pull Request (PR) & Hợp nhất
1.  **Tạo PR:** Tạo PR với `base` là `main`.
2.  **Review:** Xem xét lại các thay đổi.
3.  **Hợp nhất (Merge):** Hợp nhất PR vào `main`.
4.  **Dọn dẹp (Cleanup):** Xóa nhánh đã làm việc.

### 3.4. Quản lý Thư viện (`requirements.txt`)
* Khi thay đổi thư viện, sau khi kiểm thử ổn định, chạy `pip freeze > requirements.txt` để cập nhật.

### 3.5. Quy ước Cung cấp Mã nguồn & Định dạng
Đây là quy tắc duy nhất và quan trọng nhất về cách AI cung cấp và định dạng mã nguồn.

#### 3.5.1. Quy ước Header cho File
* **Mục đích:** Ghi nhận các thay đổi lớn về cấu trúc hoặc chức năng cốt lõi của một file.
* **Áp dụng khi nào:** Header của file (`# version`, `# description`) **chỉ được cập nhật** khi có thay đổi tương đương với một phiên bản `MINOR` hoặc `MAJOR` của ứng dụng (ví dụ: thêm một loạt tính năng mới vào file).
* **KHÔNG ÁP DỤNG** cho các thay đổi nhỏ, sửa lỗi (hotfix).
* **Định dạng:**
    ```python
    # file-path: [đường dẫn]
    # version: [số phiên bản, ví dụ: 2.1]
    # last-updated: [YYYY-MM-DD]
    # description: [Mô tả thay đổi]
    ```

#### 3.5.2. Quy tắc Cung cấp Hotfix (Sửa đổi hàm hiện có)
* **Áp dụng khi nào:** Khi sửa lỗi hoặc thay đổi nhỏ **bên trong một hoặc nhiều hàm đã tồn tại**.
* **Cách cung cấp:** AI chỉ cung cấp khối mã nguồn của (các) hàm được thay đổi.
* **Định dạng bắt buộc:** Phía trên mỗi hàm được sửa đổi, AI phải đặt một bình luận theo định dạng sau để tạo "nhật ký thay đổi nội bộ":
    ```python
    # hotfix - YYYY-MM-DD - [Mô tả ngắn gọn về thay đổi]
    ```
    * **Ví dụ:** `# hotfix - 2025-07-22 - Sửa lỗi chia cho zero`

#### 3.5.3. Quy tắc Cung cấp Toàn bộ File
* **Áp dụng khi nào:**
    * Thêm **bất kỳ hàm mới hoặc lớp (class) mới nào**.
    * Thực hiện tái cấu trúc lớn (refactor) ảnh hưởng đến cấu trúc tổng thể của file.
    * Chỉnh sửa các file tài liệu (`.md`) hoặc các file mã nguồn ngắn.
    * Người dùng yêu cầu một cách tường minh.
* **Cách cung cấp:** AI **bắt buộc** phải cung cấp lại **toàn bộ nội dung của file**.

### 3.6. Quy trình Chuẩn bị Phát hành
* **Quy tắc:** Đây là các bước **chuẩn bị** trước khi tạo commit `release`.
1.  **Chạy Kịch bản Nâng cấp:** Người dùng thực thi lệnh `python scripts/release.py`.
2.  **Nhập Phiên bản mới:** Cung cấp số hiệu phiên bản mới tuân theo quy tắc tại mục `3.6.1`.
3.  **Điền Changelog:** Người dùng mở `CHANGELOG.md` và điền chi tiết thay đổi.

#### 3.6.1. Quy tắc Đặt tên Phiên bản (Semantic Versioning)
* Dự án tuân thủ tiêu chuẩn **Semantic Versioning (SemVer)** với cấu trúc `MAJOR.MINOR.PATCH`.
* **`PATCH`:** Cho các bản sửa lỗi nhỏ, tương thích ngược.
* **`MINOR`:** Khi thêm một tính năng mới nhưng vẫn tương thích ngược.
* **`MAJOR`:** Khi có các thay đổi không tương thích ngược (breaking changes).

## 4. Quy trình Cộng tác với Gemini AI (BẮT BUỘC)

### 4.0. Cấu trúc Phản hồi Chuẩn
Mọi phản hồi chính (khi cung cấp kế hoạch hoặc mã nguồn) phải tuân thủ cấu trúc 4 phần sau:
1.  `Phần 1: Phân tích & Kế hoạch`
2.  `Phần 2: Gói Cập Nhật Mục Tiêu`
3.  `Phần 3: Hướng dẫn Hành động & Lệnh Git`
4.  `Phần 4: Kết quả Kỳ vọng & Cảnh báo`

### 4.1. Bước 1: Khởi động & Phân loại (Phản hồi đầu tiên)
Sau mỗi yêu cầu mới, phản hồi đầu tiên của AI phải bao gồm:
1.  **Tiếp nhận & Kiểm tra File:** Xác nhận nhiệm vụ và trạng thái truy cập các file nguồn liên quan. Nếu không truy cập được, AI sẽ dừng lại và yêu cầu người dùng cung cấp.
2.  **Kiểm tra Trạng thái Phiên bản:** Đưa ra phiên bản hiện tại và phiên bản đề xuất.
3.  **Phân loại Công khai:** AI phải tuyên bố rõ ràng: **"Đây là một thay đổi nhỏ"** hoặc **"Đây là một thay đổi lớn/phức tạp"**.
    * Nếu là **thay đổi nhỏ**, AI sẽ tiếp tục trình bày **Bước 3** trong cùng một phản hồi.
    * Nếu là **thay đổi lớn**, AI sẽ trình bày **Bước 2** và dừng lại chờ phê duyệt.

### 4.2. Bước 2: Phân tích & Kế hoạch Chi tiết (Chỉ dành cho thay đổi lớn)
* **Kích hoạt:** Khi nhiệm vụ được phân loại là "thay đổi lớn".
* **Hành động:** AI trình bày một bản phân tích sâu về yêu cầu, các phương án, và kế hoạch thực thi chi tiết. Kết thúc bằng việc **xin phê duyệt** kế hoạch từ người dùng.

### 4.3. Bước 3: Thực thi (Phản hồi chính)
* **Kích hoạt:** Ngay lập tức (đối với thay đổi nhỏ) hoặc sau khi kế hoạch được phê duyệt (đối với thay đổi lớn).
* **Hành động:** AI trình bày một phản hồi đầy đủ theo **Cấu trúc 4 Phần**, trong đó:
    * `Phần 2` sẽ chứa mã nguồn (tuân thủ **Mục 3.5**).
    * `Phần 3` **luôn bắt đầu** bằng lệnh `git checkout -b` để tạo nhánh mới. Sau đó là các hướng dẫn cài đặt, kiểm thử và cuối cùng là lệnh `git commit` cho **tính năng** (ví dụ: `git commit -m "feat: add new button"`).

### 4.4. Bước 4: Hoàn tất & Phát hành
* **Kích hoạt:** Sau khi người dùng xác nhận tính năng ở Bước 3 đã hoạt động đúng như kỳ vọng.
* **Hành động:** Phản hồi tiếp theo của AI **chỉ tập trung** vào việc hướng dẫn người dùng hoàn tất quy trình phát hành (theo mục 3.6):
    1.  Hướng dẫn chạy `python scripts/release.py`.
    2.  Cung cấp nội dung để cập nhật vào `CHANGELOG.md`.
    3.  Cung cấp lệnh `git commit` cho việc **phát hành** (`git commit -m "release: version X.Y.Z"`).
    4.  Nhắc nhở về việc **Tạo Pull Request**, **Hợp nhất (Merge)**, và **Xóa nhánh**.

### 4.5. Cơ chế "Reset"
* Khi AI vi phạm quy tắc, người dùng sẽ sử dụng từ khóa `CHECK-WORKFLOW` để yêu cầu AI dừng lại và rà soát lại quy trình trong file này.