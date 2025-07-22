# QUY TRÌNH LÀM VIỆC DỰ ÁN (Project Workflow)
# version: 6.1
# last-updated: 2025-07-22
# description: Cải tổ toàn diện quy trình cộng tác với AI. Bổ sung "Quy tắc Phân loại Nhiệm vụ" để quyết định luồng làm việc linh hoạt (1 giai đoạn hoặc 2 giai đoạn). Cập nhật lại checklist khởi đầu.

## 1. Nguồn Lực Tham Chiếu
Trước khi bắt đầu bất kỳ nhiệm vụ nào, các tài liệu sau phải luôn được coi là nguồn thông tin cốt lõi và đáng tin cậy:
* **`WORKFLOW.md` (File này):** "Hiến pháp" về mọi quy trình làm việc.
* **`ROADMAP.md`:** Lộ trình phát triển và các mục tiêu của dự án.
* **`TECHNICAL_NOTES.md`:** Các quyết định kiến trúc và bài học kỹ thuật quan trọng.
* **`CHANGELOG.md`:** Lịch sử các thay đổi đã được phát hành để nắm được bối cảnh gần nhất.

## 2. Triết lý Chung
* **Nguồn sự thật duy nhất:** Nhánh `main` là nền tảng ổn định.
* **Làm việc trên nhánh (BẮT BUỘC):** Mọi thay đổi đều phải được thực hiện trên nhánh riêng.
    * *Ghi chú:* Gemini AI có trách nhiệm chủ động đề xuất tạo nhánh mới ở đầu mỗi nhiệm vụ tính năng lớn.
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
2.  **Nhập Phiên bản mới:** Cung cấp số hiệu phiên bản mới tuân theo quy tắc tại mục `3.6.1`.
3.  **Điền Changelog:** Người dùng mở `CHANGELOG.md` và điền chi tiết thay đổi.
4.  **Commit & Hợp nhất:** Tiến hành commit và tạo Pull Request.

#### 3.6.1. Quy tắc Đặt tên Phiên bản (Semantic Versioning)
* **Mục đích:** Để đảm bảo số hiệu phiên bản có ý nghĩa và phản ánh đúng bản chất của các thay đổi. Dự án tuân thủ tiêu chuẩn **Semantic Versioning (SemVer)** với cấu trúc `MAJOR.MINOR.PATCH`.
* **Quy tắc tăng số:**
    * **`PATCH` (ví dụ: 1.4.0 -> 1.4.1):** Chỉ tăng khi thực hiện các bản **sửa lỗi tương thích ngược** (backward-compatible bug fixes). Ví dụ: Sửa lỗi chính tả, vá một lỗi crash nhỏ.
    * **`MINOR` (ví dụ: 1.4.1 -> 1.5.0):** Chỉ tăng khi **thêm một tính năng mới** nhưng vẫn **tương thích ngược**. Ví dụ: Thêm một nút mới, một chức năng mới không làm hỏng chức năng cũ.
    * **`MAJOR` (ví dụ: 1.5.0 -> 2.0.0):** Chỉ tăng khi thực hiện các **thay đổi không tương thích ngược** (breaking changes). Ví dụ: Thay đổi lớn về kiến trúc, xóa bỏ tính năng, thay đổi CSDL khiến phiên bản cũ không dùng được.

### 3.7. Quy trình Cập nhật Roadmap
* Khi một giai đoạn lớn được hoàn thành, mục đó sẽ được xóa bỏ khỏi kế hoạch và một dòng tóm tắt thành tựu sẽ được thêm vào cuối file.

## 4. Quy trình Cộng tác với Gemini AI (BẮT BUỘC)

### 4.1. Quy tắc Vàng: Phân loại Nhiệm vụ trước khi Hành động
Đây là quy tắc cốt lõi, quyết định luồng làm việc sẽ diễn ra theo 1 hay 2 giai đoạn. Gemini AI phải tự đưa ra phán đoán dựa trên các tiêu chí sau:

#### A. KHI NÀO PHẢN HỒI GỘP TRONG 1 LẦN (Cho các thay đổi nhỏ & rõ ràng)
AI sẽ sử dụng một phản hồi duy nhất (bao gồm Phân tích ngắn gọn, Mã nguồn và lệnh Git) khi nhiệm vụ đáp ứng **TẤT CẢ** các tiêu chí sau:
1.  **Mục tiêu Cụ thể:** Yêu cầu không có sự mơ hồ (ví dụ: "đổi độ rộng cột X thành Y").
2.  **Rủi ro Thấp:** Thay đổi chỉ ảnh hưởng đến một file và ít khả năng gây lỗi phụ trợ.
3.  **Không có Logic Mới Phức tạp:** Không tạo hàm/lớp mới, chỉ sửa đổi các giá trị hoặc các thành phần đơn giản.

#### B. KHI NÀO PHẢI CHIA LÀM 2 GIAI ĐOẠN (Phân tích -> Thực thi)
AI **BẮT BUỘC** phải chia nhiệm vụ thành 2 giai đoạn (Giai đoạn 1: Phân tích & Xin phê duyệt; Giai đoạn 2: Thực thi) khi nhiệm vụ có **BẤT KỲ** đặc điểm nào sau đây:
1.  **Yêu cầu mang tính Ý tưởng/Chiến lược:** Yêu cầu mô tả một vấn đề lớn chưa có giải pháp kỹ thuật rõ ràng (ví dụ: "cải thiện giao diện tab X", "làm cho tính năng Y thông minh hơn").
2.  **Ảnh hưởng đến Nhiều File/Toàn bộ Ứng dụng:** Thay đổi có tác động đến nhiều module hoặc toàn bộ kiến trúc (ví dụ: áp dụng theme mới, thay đổi CSDL).
3.  **Yêu cầu tạo Logic Mới Phức tạp:** Cần viết các hàm, lớp, hoặc thuật toán mới.
4.  **Có Rủi ro tiềm ẩn:** Khi giải pháp có thể gây ra các tác dụng phụ không mong muốn.

### 4.2. Giai đoạn 1: Phân tích & Kế hoạch (Đối với thay đổi lớn)
* **Kích hoạt:** Khi nhiệm vụ được phân loại là "thay đổi lớn".
* **Hành động:** AI trình bày một phản hồi chi tiết bao gồm:
    * Tiếp nhận & Kiểm tra File (nếu cần, yêu cầu người dùng cung cấp).
    * Kiểm tra Trạng thái Phiên bản.
    * Phân tích sâu về yêu cầu, các hướng tiếp cận, ưu nhược điểm.
    * Đề xuất một kế hoạch thực thi cụ thể.
    * Kết thúc bằng việc **xin phê duyệt** kế hoạch từ người dùng.

### 4.3. Giai đoạn 2: Thực thi (Sau khi kế hoạch được phê duyệt)
* **Kích hoạt:** Sau khi người dùng trả lời "OK" cho kế hoạch ở Giai đoạn 1.
* **Hành động:** AI trình bày một phản hồi đầy đủ theo cấu trúc 4 phần:
    1.  `Phần 1: Phân tích & Kế hoạch` (Tóm tắt lại kế hoạch đã được duyệt).
    2.  `Phần 2: Gói Cập Nhật Mục Tiêu` (Cung cấp mã nguồn).
    3.  `Phần 3: Hướng dẫn Hành động & Lệnh Git`:
        * **Luôn bắt đầu** bằng lệnh `git checkout -b` để tạo nhánh mới.
        * Cung cấp các bước cài đặt, kiểm thử.
        * Cung cấp các lệnh `git add` và `git commit` để hoàn tất.
        * Nhắc nhở người dùng tại Pull Request và merge vào `main` nếu đạt được kết quả kỳ vọng ở phần 4.
    4.  `Phần 4: Kết quả Kỳ vọng & Cảnh báo`.

### 4.4. Cơ chế "Reset"
* Khi AI vi phạm quy tắc, người dùng sẽ sử dụng từ khóa `CHECK-WORKFLOW` để yêu cầu AI dừng lại và rà soát lại quy trình trong file này.

## 5. Phụ lục: Template Yêu cầu dành cho Người dùng
* (Phần này giữ nguyên không thay đổi)