# QUY TRÌNH LÀM VIỆC DỰ ÁN (Project Workflow)
# version: 10.0
# last-updated: 2025-07-24
# description: Phiên bản cuối cùng. Tinh chỉnh quy trình cộng tác với AI thành một luồng làm việc linh hoạt, thực tế và an toàn, thừa nhận các giới hạn về ngữ cảnh.

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
    * **Ví dụ:** `# hotfix - 2025-07-24 - Sửa lỗi chia cho zero`

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

### 4.1. Quy tắc "Làm mới Ngữ cảnh"
* Trước mỗi lần cung cấp mã nguồn, AI phải nêu rõ phiên bản file đang được sử dụng làm cơ sở.
* **Ví dụ:** "Phân tích và mã nguồn dưới đây được dựa trên file `[tên-file]` phiên bản `[số-phiên-bản]`."
* Điều này hoạt động như một lời nhắc để người dùng cung cấp phiên bản mới hơn nếu cần, đảm bảo AI không làm việc trên thông tin cũ.

### 4.2. Luồng làm việc cho Thay đổi Lớn / Phức tạp
* **Áp dụng khi:** Yêu cầu mang tính ý tưởng, chiến lược, hoặc ảnh hưởng đến nhiều file.
* **Quy trình:** Giữ nguyên quy trình 2 giai đoạn an toàn:
    1.  **Giai đoạn 1 - Phân tích & Xin Phê duyệt:** AI trình bày kế hoạch chi tiết và chờ người dùng đồng ý.
    2.  **Giai đoạn 2 - Thực thi & Phát hành:** Sau khi được phê duyệt, AI cung cấp mã nguồn, hướng dẫn kiểm thử, và sau khi người dùng xác nhận OK, AI sẽ cung cấp các bước để hoàn tất phát hành.

### 4.3. Luồng làm việc cho Thay đổi Nhỏ / Sửa lỗi (Tối giản)
* **Áp dụng khi:** Sửa một lỗi cụ thể, tinh chỉnh giao diện, hoặc các thay đổi nhỏ khác trong một file.
* **Quy trình:**
    1.  **Phản hồi #1 - Cung cấp Giải pháp:** AI cung cấp một phản hồi bao gồm:
        * Tạo nhánh làm việc mới (`git checkout -b ...`).
        * Cung cấp mã nguồn `hotfix`.
        * Kết thúc bằng một câu hỏi xác nhận duy nhất: "Bạn vui lòng áp dụng và kiểm tra. Nó đã hoạt động đúng như kỳ vọng chưa?"
    2.  **Phản hồi #2 - Hoàn tất (Chỉ sau khi người dùng xác nhận OK):**
        * AI cung cấp các bước còn lại: `git commit` cho tính năng, và toàn bộ quy trình phát hành (chạy `release.py`, cập nhật `CHANGELOG.md`, commit `release`).

### 4.4. Cơ chế "Reset"
* Khi AI vi phạm quy tắc, người dùng sẽ sử dụng từ khóa `CHECK-WORKFLOW` để yêu cầu AI dừng lại và rà soát lại quy trình trong file này.