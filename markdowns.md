# **CÁC TÀI LIỆU CỐT LÕI (BẮT BUỘC ĐỌC)**

**1. QUY TRÌNH LÀM VIỆC (WORKFLOW.md):**
```markdown
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
```

**2. LỘ TRÌNH PHÁT TRIỂN (ROADMAP.md):**
```markdown
# Lộ trình Phát triển (Roadmap)
# version: 6.1
# last-updated: 2025-07-21
# description: Ghi nhận hoàn thành tính năng "Tích hợp Thư viện với TTS".

## Tầm nhìn Dự án
Trở thành một bộ công cụ "tất cả trong một" (all-in-one), mạnh mẽ và dễ sử dụng cho các nhà sáng tạo nội dung, kết nối liền mạch kho ý tưởng trên cloud đến sản phẩm cuối cùng.

---

## Giai đoạn 2: Tối ưu Luồng làm việc & Mở rộng (Tiếp theo)

### 2.1. Cải tiến Trải nghiệm Người dùng (UI/UX)
* **Vấn đề:** Giao diện của một số thành phần có thể được cải tiến để trực quan hơn.
* **Yêu cầu:** Đây là một mục tiêu liên tục. Ví dụ: tự động làm sạch tiền tố ("001 - ") khỏi tiêu đề khi đồng bộ từ Google Drive.

### 2.2. Module Phụ đề
* **Vấn đề:** Chưa có công cụ hỗ trợ tạo phụ đề cho video.
* **Yêu cầu:**
    * [ ] Xây dựng tính năng tạo file phụ đề (`.srt`) từ kịch bản và file audio đã tạo.

---

## ✅ Thành tựu đã Đạt được (Key Milestones Achieved)

* **Tích hợp Thư viện với TTS (Hoàn thành trong v1.4.0):**
    - Thêm nút "Gửi sang TTS" trong Thư viện để nhanh chóng chuyển nội dung "Story" của một dự án sang tab Text-to-Speech, tối ưu hóa luồng làm việc.

* **Tích hợp Google Drive & Quản lý Trạng thái (Hoàn thành trong v1.3.0):**
    - Xây dựng hệ thống "Nhóm Dự án" trong Settings, cho phép quản lý các nguồn nội dung (Local/Google Drive).
    - Triển khai thành công luồng xác thực OAuth 2.0 an toàn để kết nối với Google API.
    - Xây dựng tính năng "Đồng bộ Thông minh" từ Google Drive, hỗ trợ các chế độ "Chỉ thêm mới" và "Làm mới toàn bộ".
    - Hoàn thiện hệ thống "Trạng thái Dự án" (Chưa làm, Đang làm dở, Đã làm) với cơ chế Menu Chuột phải và phản hồi trực quan bằng màu sắc.
    - Xây dựng cơ chế "Di chuyển Cơ sở dữ liệu" (Migration) tự động để đảm bảo tính tương thích ngược.

* **Hỗ trợ Đa ngôn ngữ TTS (Hoàn thành trong v1.2.0):**
    - Hoàn thiện tính năng lựa chọn ngôn ngữ và "Reading Style Prompt" tương ứng trong tab Text-to-Speech.

* **Hệ thống Quản lý Dự án & Thư viện (Hoàn thành trong v1.1.0):**
    - Xây dựng hệ thống "Thư viện" dựa trên mô hình "Dự án", cho phép quản lý các thành phần (Truyện, Tiêu đề, Thumbnail).
    - Tích hợp khái niệm "Dự án đang hoạt động" với thanh trạng thái trực quan.

* **Công cụ Tự động hóa Phiên bản (Hoàn thành trong v1.0.0):**
    - Xây dựng kịch bản `scripts/release.py` để tự động hóa việc nâng cấp phiên bản.

```

**3. GHI CHÚ KỸ THUẬT (TECHNICAL_NOTES.md):**
```markdown
# Ghi chú Kỹ thuật & Quyết định Kiến trúc
# Last Updated: 2025-06-28

Tài liệu này ghi lại những vấn đề kỹ thuật hóc búa đã gặp phải trong quá trình phát triển và các quyết định cuối cùng đã được đưa ra để giải quyết chúng. Bất kỳ ai tham gia phát triển dự án này trong tương lai **BẮT BUỘC** phải đọc file này trước khi thực hiện bất kỳ thay đổi nào liên quan đến các module được đề cập.

---

### **1. Vấn đề Môi trường: Lỗi Tương thích `Pillow` & Variable Fonts**

* **Triệu chứng:** Khi cố gắng render các **Variable Fonts** (ví dụ: Oswald, Open Sans) bằng cách sử dụng tham số `variation` của thư viện Pillow, chương trình gây ra lỗi `TypeError: truetype() got an unexpected keyword argument 'variation'`.

* **Quá trình Điều tra (Các giải pháp đã thất bại):**
    * Nâng cấp phiên bản Pillow.
    * Cài đặt lại toàn bộ môi trường ảo (`venv`).
    * Xóa cache của `pip`.
    * Kiểm tra và xác nhận `Raqm` (complex text layout) đã được kích hoạt.
    * Chẩn đoán bằng `inspect` đã xác nhận hàm `truetype` trong môi trường đích không nhận tham số `variation`, bất kể phiên bản cài đặt là gì.

* **Kết luận & Quyết định Kiến trúc (Rất quan trọng):**
    * Vấn đề được xác định là một lỗi tương thích môi trường sâu, không thể giải quyết bằng các phương pháp thông thường.
    * **QUYẾT ĐỊNH:** Dự án sẽ **TỪ BỎ HOÀN TOÀN** việc hỗ trợ tính năng `variation` của Variable Fonts.
    * **HỆ QUẢ:** Hàm `_build_font_map` trong `thumbnail_preview.py` đã được viết lại để chủ động **bỏ qua tất cả các file font được nhận dạng là Variable Font**. Chương trình chỉ làm việc với các font tĩnh, nơi mỗi kiểu chữ (Bold, Normal...) là một file `.ttf` riêng biệt. Mọi nỗ lực "cải tiến" để hỗ trợ lại Variable Fonts trong tương lai rất có thể sẽ gặp lại đúng lỗi này.

---

### **2. Vấn đề Môi trường: Lỗi Import `pydub` trên Python 3.13+**

* **Triệu chứng:** Sau khi tạo lại môi trường ảo trên Python 3.13, chương trình crash ngay khi khởi động với lỗi `ModuleNotFoundError: No module named 'pyaudioop'`.

* **Nguyên nhân gốc:** Module `audioop` là một phần của thư viện chuẩn Python nhưng đã bị **xóa bỏ hoàn toàn** từ phiên bản 3.13. Thư viện `pydub` khi được import, nếu không tìm thấy backend `ffmpeg` ngay lập tức, sẽ cố gắng fallback về việc sử dụng `audioop` và gây ra lỗi.

* **Giải pháp & Quyết định Phụ thuộc:**
    * **QUYẾT ĐỊNH:** Thư viện `audioop-lts` phải được thêm vào `requirements.txt` như một phụ thuộc bắt buộc.
    * **HỆ QUẢ:** Thư viện này cung cấp một bản thay thế cho module `audioop` đã bị xóa, giải quyết được vấn đề import của `pydub`.

---

### **3. Quyết định Logic: Tương tác giữa "Cỡ chữ chung" và "Cỡ chữ từng dòng"**

* **Vấn đề:** Cần một cơ chế để các thay đổi "Cỡ chữ từng dòng" không bị "Cỡ chữ chung" ghi đè một cách không mong muốn.

* **Giải pháp & Quyết định Thiết kế:**
    * **QUYẾT ĐỊNH:** Logic được triển khai bằng cách sử dụng một **cờ trạng thái (`is_edited: False`)** trong cấu trúc dữ liệu của mỗi dòng text.
    * **HỆ QUẢ:**
        * Khi người dùng chỉnh sửa cỡ chữ của một dòng cụ thể lần đầu tiên, cờ `is_edited` của dòng đó sẽ được đặt thành `True`.
        * Hàm "Cỡ chữ chung" sẽ chỉ áp dụng cho những dòng có cờ `is_edited` là `False`. Điều này tạo ra hành vi "khóa" giá trị cho các dòng đã được tinh chỉnh thủ công.

---

### **4. Vấn đề Kiến trúc: Di chuyển Cơ sở dữ liệu (Database Migration)**

* **Bối cảnh:** Trong quá trình phát triển (nhánh `feature/project-status-system`), chúng ta đã cần thêm các cột mới (`source_group`, `status`) vào bảng `projects` đã tồn tại.
* **Vấn đề:** Lệnh `CREATE TABLE IF NOT EXISTS` trong `database.py` không tự động cập nhật cấu trúc của một bảng đã tồn tại. Điều này dẫn đến lỗi `IndexError` hoặc `no such column` khi mã nguồn mới cố gắng truy cập vào các cột chưa tồn tại trong file CSDL cũ của người dùng.
* **Giải pháp & Quyết định Thiết kế:**
    * **QUYẾT ĐỊNH:** Một hàm `_run_migrations` đã được thêm vào `database.py`. Hàm này được gọi mỗi khi ứng dụng khởi động.
    * **HỆ QUẢ:** Hàm này có trách nhiệm kiểm tra cấu trúc của các bảng hiện có (sử dụng `PRAGMA table_info`) và chạy các lệnh `ALTER TABLE ADD COLUMN` để thêm vào các cột còn thiếu. Bất kỳ thay đổi nào về cấu trúc CSDL trong tương lai đều **BẮT BUỘC** phải được xử lý thông qua cơ chế di chuyển này để đảm bảo tính tương thích ngược cho người dùng cũ.
```

**4. GIỚI THIỆU VỀ CHƯƠNG TRÌNH (README.md):**
# Gemini Creative Suite v1.4.0

**[Xem Lịch sử Thay đổi (Changelog)](CHANGELOG.md) | [Xem Lộ trình Phát triển (Roadmap)](ROADMAP.md) | [Xem Quy trình Làm việc (Workflow)](WORKFLOW.md) | [Ghi chú Kỹ thuật](TECHNICAL_NOTES.md)**

---

Một bộ công cụ desktop mạnh mẽ được xây dựng bằng Python và Tkinter, sử dụng sức mạnh của Google Gemini API để hỗ trợ toàn diện cho quy trình sáng tạo nội dung YouTube, đặc biệt cho thể loại truyện kể.

![Giao diện ứng dụng](https://i.imgur.com/image_5edff8.png)

## Hướng dẫn Sử dụng (Bản đóng gói)

1.  Sau khi quá trình đóng gói hoàn tất, tìm đến thư mục `dist`.
2.  Chạy file **`Gemini Creative Suite.exe`** để bắt đầu sử dụng ứng dụng.
3.  Không cần cài đặt Python hay bất kỳ thư viện nào khác.

---

## Chức năng Cốt lõi

Dự án được chia thành 3 module chính, hoạt động trên các tab riêng biệt:

* **🎙️ Text-to-Speech:** Chuyển đổi kịch bản dài thành file audio `.wav` chất lượng cao, hỗ trợ đa luồng và tự động ghép nối.
* **✍️ Trợ lý Biên tập:** Bóc tách các lựa chọn kịch bản từ Gemini, cung cấp trình soạn thảo với cảnh báo độ dài và cửa sổ xem trước thumbnail chuyên nghiệp.
* **📖 Soạn Truyện Dài:** Cung cấp bảng điều khiển nổi tiện lợi để soạn truyện dài, tự động hóa việc sao chép và tạo prompt tiếp nối.

---

## Cấu trúc Dự án

Dưới đây là cấu trúc các file quan trọng trong thư mục `src/` để giúp các lập trình viên dễ dàng nắm bắt (Thực ra đây chưa phải là bản cấu trúc đầy đủ):

src/gemini_tts_app/
│
├── main_app.py         # File chính, quản lý giao diện (Tkinter), các tab và luồng sự kiện.
├── tts_logic.py        # Xử lý logic cho module Text-to-Speech (gọi API, xử lý audio).
├── thumbnail_preview.py# Quản lý cửa sổ xem trước và thiết kế thumbnail.
├── database.py         # Xử lý logic cho module Trợ lý Biên tập (bóc tách text, CSDL SQLite).
├── long_form_composer.py# Logic cho module Soạn Truyện Dài (theo dõi clipboard, lọc nội dung).
├── settings_manager.py # Quản lý việc đọc/ghi các cài đặt của người dùng (API keys, themes...).
├── logger_setup.py     # Thiết lập hệ thống ghi log cho ứng dụng.
├── utils.py            # Chứa các hàm tiện ích dùng chung, ví dụ: get_resource_path.
└── constants.py        # Chứa các hằng số của ứng dụng (mã màu, giá trị mặc định...).

---

## Hướng dẫn Cài đặt (Dành cho Lập trình viên)

* **Yêu cầu Hệ thống:**
    * Python 3.9+
    * `ffmpeg`: Cần được cài đặt và thêm vào biến môi trường PATH.
* **Các bước:**
    1.  Clone repository: `git clone [URL]`
    2.  Tạo môi trường ảo: `python -m venv venv` và kích hoạt nó.
    3.  Cài đặt thư viện: `pip install -r requirements.txt`
    4.  Chạy ứng dụng: `python run.py`
    5.  Vào tab "Settings" để thêm API key và lưu lại.
