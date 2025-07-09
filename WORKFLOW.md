# QUY TRÌNH LÀM VIỆC DỰ ÁN (Project Workflow)
# Version: 2.3
# Last Updated: 2025-07-05

## 1. Checklist Khởi đầu (Bắt buộc trước mỗi nhiệm vụ mới)
Trước khi bắt đầu bất kỳ công việc nào, người thực hiện (cả bạn và AI) phải xác nhận đã hoàn thành các mục sau:
- [ ] Đã đồng bộ với trạng thái mới nhất của nhánh `main` (`git pull origin main`).
- [ ] Đã đọc và hiểu rõ các quy tắc trong file `WORKFLOW.md` này.
- [ ] **Đã đọc và hiểu các giới hạn và quyết định trong file `TECHNICAL_NOTES.md` để tránh lặp lại sai lầm cũ.**

## 2. Triết lý Chung
* **Nguồn sự thật duy nhất (Single Source of Truth):** Nhánh `main` trên repository GitHub là nền tảng ổn định và mới nhất. Mọi công việc phải bắt đầu từ đây.
* **Làm việc trên nhánh (Branching):** Không bao giờ làm việc trực tiếp trên `main`. Mọi thay đổi, dù là tính năng, sửa lỗi hay cập nhật tài liệu, đều phải được thực hiện trên các nhánh riêng biệt.
* **Hợp nhất qua Pull Request (Merge via PR):** Mọi thay đổi chỉ được đưa vào `main` thông qua một quy trình Pull Request có xem xét (review).
* **AI là Cộng tác viên:** Gemini AI được xem như một lập trình viên cộng tác cao cấp, có trách nhiệm tuân thủ nghiêm ngặt toàn bộ quy trình được định nghĩa trong tài liệu này.

### **2.1. Ghi phiên bản Tài liệu (MỚI)**
* Đối với các file tài liệu quy trình và kế hoạch cốt lõi (`WORKFLOW.md`, `ROADMAP.md`, `TECHNICAL_NOTES.md`), mỗi lần có sự thay đổi quan trọng, người chỉnh sửa có trách nhiệm cập nhật số phiên bản và ngày tháng ở đầu file để tiện theo dõi.
* Đối với các file mã nguồn (`.py`), không cần thêm thông tin này vì Git đã quản lý phiên bản.

## 3. Quy trình làm việc với Git & Môi trường
### 3.1. Đặt tên nhánh
* **Tính năng mới:** `feature/<ten-tinh-nang-ngan-gon>`
* **Sửa lỗi:** `fix/<ten-loi>`
* **Cập nhật tài liệu:** `docs/<noi-dung-cap-nhat>`
* **Tái cấu trúc code:** `refactor/<pham-vi-tai-cau-truc>`

### 3.2. Quy ước Commit Message
* Sử dụng quy ước **Conventional Commits** (`<type>(<scope>): <subject>`) để làm rõ lịch sử dự án.
* **Ví dụ:** `feat(thumbnail): Add per-line font size`, `fix(pydub): Resolve environment issue`, `docs(workflow): Overhaul collaboration process`.

### 3.3. Quy trình Pull Request (PR) & Hợp nhất
1.  **Tạo PR:** Sau khi hoàn thành công việc trên một nhánh, sử dụng extension **GitHub Pull Request** trong VS Code để tạo một Pull Request mới, với `base` là `main`.
2.  **Review:** Mở PR trên giao diện web của GitHub để xem xét lại toàn bộ các thay đổi.
3.  **Hợp nhất (Merge):** Sau khi PR được phê duyệt, nhấn nút "Merge Pull Request".
4.  **Dọn dẹp (Cleanup):** Ngay sau khi hợp nhất thành công, nhấn nút "Delete branch" để xóa nhánh đã làm việc, giữ cho repository luôn gọn gàng.

### 3.4. Quản lý Thư viện (`requirements.txt`)
* Khi cần thêm/thay đổi thư viện, quy trình chuẩn là:
    1.  Kích hoạt môi trường ảo (`venv`).
    2.  Chạy `pip install <tên-thư-viện>`.
    3.  Sau khi kiểm thử và đảm bảo chương trình hoạt động ổn định, chạy lệnh sau để cập nhật `requirements.txt`:
        ```bash
        pip freeze > requirements.txt
        ```
    4.  Sắp xếp lại file theo thứ tự A-Z (tùy chọn nhưng khuyến khích).

### 3.5. Quy trình Phát hành (Release)
Khi chuẩn bị cho một bản phát hành mới, quy trình sau phải được tuân thủ:
1.  **Kiểm tra Phiên bản:** Mở file `CHANGELOG.md` và xác định số phiên bản cuối cùng đã được phát hành.
2.  **Quyết định Phiên bản mới:** Dựa trên các thay đổi đã được hợp nhất vào `main`, quyết định số phiên bản tiếp theo (ví dụ: `1.0.1` -> `1.0.2` cho sửa lỗi, `1.0.1` -> `1.1.0` cho tính năng mới).
3.  **Tạo nhánh Release:** Tạo một nhánh mới với tên theo phiên bản, ví dụ: `release/v1.0.2`.
4.  **Cập nhật Tài liệu:** Trên nhánh này, cập nhật `CHANGELOG.md` và `README.md` với số phiên bản mới.
5.  **Hợp nhất:** Tạo Pull Request để hợp nhất nhánh release vào `main`.

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
* **Ngoại lệ "Hotfix":** AI chỉ được phép cung cấp một đoạn code nhỏ ("hotfix") khi và chỉ khi đã hỏi và được người dùng cho phép một cách tường minh. (Ví dụ câu hỏi của AI: `Thay đổi này chỉ ảnh hưởng đến hàm X. Bạn có cho phép tôi chỉ cung cấp 'hotfix' cho hàm này không?`)

### 4.4. Bước 3: Cấu trúc Phản hồi Chuẩn của AI
* **Quy tắc:** Mọi phản hồi cung cấp "Kế hoạch" hoặc "Gói Cập Nhật" đều phải tuân thủ cấu trúc sau để đảm bảo sự rõ ràng và có tính hành động.
    1.  **Phần 1: Phân tích & Kế hoạch:** Trình bày phân tích và/hoặc kế hoạch thực thi chi tiết.
    2.  **Phần 2: Gói Cập Nhật Mục Tiêu (Nếu có):** Cung cấp mã nguồn hoặc nội dung cập nhật.
    3.  **Phần 3: Hướng dẫn Hành động Tiếp theo dành cho bạn:** Chỉ rõ từng bước bạn cần làm tiếp theo (ví dụ: "Bây giờ, bạn hãy tạo nhánh mới...", "Bạn hãy áp dụng code này và chạy kiểm thử...", "Bạn hãy xem xét kế hoạch này và cho tôi biết bạn có phê duyệt không?").

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

Bối cảnh Quan trọng: [Liệt kê thông tin nền mà AI cần biết. Ví dụ: "Chúng ta sẽ tiếp tục làm việc trên nhánh X", "Lưu ý rằng file Y vừa được thay đổi".]

Kết quả Mong muốn: [Mô tả sản phẩm cuối cùng trông như thế nào hoặc hoạt động ra sao.]

### Template B: Khi Báo cáo Lỗi sau khi Chạy Test
Tình trạng: [Chạy test thất bại / Gặp lỗi]

Mô tả Lỗi: [Mô tả ngắn gọn những gì bạn quan sát được.]

Log/Traceback:
(Dán toàn bộ log lỗi vào đây)

Hành động Đã thử (Nếu có): [Liệt kê những gì bạn đã thử để khắc phục.]