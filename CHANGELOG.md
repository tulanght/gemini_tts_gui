# Lịch sử thay đổi (Changelog)

Tất cả các thay đổi đáng chú ý của dự án sẽ được ghi lại tại đây.
Dự án này tuân theo [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.21.0] - 2025-08-22

### ✨ Tính năng mới (Features)
- **Nâng cấp CSDL:** Bổ sung các cột mới (`summary_content`, `translated_content`, `rewritten_content`, `main_ideas_content`) vào bảng `downloaded_subtitles` để lưu trữ nội dung đã qua xử lý. Tích hợp cơ chế "di trú" (migration) để tự động cập nhật CSDL cho người dùng cũ.
- **Lưu Nội dung đã xử lý:** Thêm chức năng cho phép người dùng lưu các kết quả từ việc tạo prompt (Tóm tắt, Dịch, Viết lại...) vào CSDL.

### ♻️ Tái cấu trúc (Refactoring)
- **Tái cấu trúc giao diện Tab Tiện ích:** Thay đổi bố cục để có luồng làm việc tự nhiên hơn: 1. Tải phụ đề -> 2. Thư viện phụ đề -> 3. Xử lý nội dung.
- **Tối ưu hóa Thư viện Phụ đề:**
    - Sắp xếp và điều chỉnh lại độ rộng các cột để dễ nhìn hơn.
    - Thêm cột "Đã xử lý" (📝) để hiển thị trạng thái của các phụ đề, giúp người dùng nhận biết nhanh những mục đã được làm việc.


## [1.20.0] - 2025-08-22

### ✨ Tính năng mới (Features)
- **Tích hợp "Prompt Thông minh" vào Tab Tiện ích:**
    - Bổ sung khu vực "Xử lý Nội dung & Tạo Prompt" mới.
    - Tự động tải nội dung của phụ đề được chọn trong thư viện lên khu vực xử lý.
    - Cung cấp các nút bấm để tự động tạo prompt cho các tác vụ: Tóm tắt, Dịch sang Tiếng Việt, Viết lại thành lời dẫn, và Tìm ý chính.
    - Thêm chức năng "Sao chép Prompt" tiện lợi để sử dụng với Gemini Web hoặc các nền tảng AI khác.


## [1.19.0] - 2025-08-22

### ✨ Tính năng mới (Features)
- **Nâng cấp Thư viện Phụ đề:**
    - Bổ sung hệ thống **Hashtag** để phân loại và tổ chức các phụ đề đã tải về.
    - Tạo cửa sổ "Chi tiết Phụ đề" (truy cập bằng nhấp đúp) cho phép xem nội dung và thêm/sửa hashtag.
    - Thêm chức năng **Tìm kiếm/Lọc** theo hashtag.
    - Tự động **tô màu nền** cho các hàng trong thư viện dựa trên hashtag chính để dễ dàng nhận diện chủ đề.
    - Thêm chức năng **Xóa phụ đề** thông qua menu chuột phải, có hộp thoại xác nhận an toàn.

## [1.18.0] - 2025-08-21

### ✨ Tính năng mới (Features)
- **Thêm Tab "Tiện ích":** Bổ sung Tab "Tiện ích" mới, tạo nền tảng cho các công cụ trong tương lai.
- **Tiện ích Tải phụ đề YouTube:**
    - Cho phép tải về các phụ đề có sẵn (do người dùng tải lên) và phụ đề tự động gốc (do YouTube tạo).
    - Logic lọc thông minh để chỉ hiển thị các phụ đề thực sự tồn tại, tránh hiển thị hàng trăm bản dịch không cần thiết.
    - Tự động dọn dẹp nội dung phụ đề (xóa timestamp, ký tự đặc biệt, định dạng thừa) để cho ra file `.txt` sạch sẽ.
    - Tích hợp "Thư viện Phụ đề" để lưu trữ và quản lý các phụ đề đã tải về trong cơ sở dữ liệu.
- **Cải tiến Giao diện:** Thêm menu chuột phải (Cắt/Sao chép/Dán) vào ô nhập liệu URL để tăng tính tiện dụng.

### 🐛 Sửa lỗi (Bug Fixes)
- Sửa nhiều lỗi liên quan đến việc xử lý dữ liệu từ `yt-dlp` và các lỗi giao diện trong quá trình phát triển tính năng.


## [1.17.0] - 2025-08-18

### ✨ Tính năng mới (Features)
- **Thêm Tab "Tiện ích":** Bổ sung một tab mới vào giao diện chính. Đây là bộ khung ban đầu để chứa các công cụ nhỏ, độc lập trong các phiên bản tương lai, giúp giữ cho cấu trúc ứng dụng gọn gàng và dễ mở rộng.


## [1.16.1] - 2025-08-18

### ✨ Tính năng mới (Features)
- **Định dạng Capitalized Case:** Bổ sung nút "Aa" và logic tự động định dạng tiêu đề sang dạng "Capitalized Case" (Viết Hoa Chữ Cái Đầu) trong Tab Trợ lý Biên tập để đảm bảo tính nhất quán.

### 🐛 Sửa lỗi (Bug Fixes)
- **Logic Xác thực Tiêu đề:** Sửa lỗi logic hiển thị màu sắc và trạng thái nút "Lưu" không chính xác khi chọn các tiêu đề dài hơn 100 ký tự. Củng cố lại logic để ngăn chặn tuyệt đối việc lưu các tiêu đề không hợp lệ.


## [1.16.0] - 2025-08-17

### ✨ Tính năng mới (Features)
- **Cải tiến Luồng làm việc Tab Soạn Truyện Dài:**
    - Giao diện "Lưu vào Thư viện" được tái cấu trúc, loại bỏ combobox không cần thiết và thay bằng label hiển thị rõ "Dự án đang hoạt động".
    - Nút "Lưu truyện vào Dự án" chỉ được kích hoạt khi có một dự án đang hoạt động, ngăn ngừa lỗi logic.

### 🐛 Sửa lỗi (Bug Fixes)
- **Logic Lưu truyện An toàn:** Bổ sung các bước kiểm tra (nội dung rỗng, hỏi xác nhận trước khi ghi đè) để đảm bảo an toàn dữ liệu khi lưu bản thảo truyện.
- **Sửa lỗi `TypeError` và `AttributeError`** trong quá trình tái cấu trúc luồng làm việc giữa các tab.


## [1.15.0] - 2025-08-01

### ✨ Tính năng mới (Features)
- **Tái cấu trúc Luồng làm việc Thư viện:**
    - Bổ sung bộ lọc "Nhóm Dự án" vào Tab Thư viện, cho phép người dùng dễ dàng xem các dự án theo từng nhóm.
    - Khôi phục và cải tiến chức năng đồng bộ Google Drive, đưa các tùy chọn ("Chỉ thêm mới" / "Làm mới toàn bộ") vào một cửa sổ con riêng biệt.

### 🐛 Sửa lỗi (Bug Fixes)
- **Logic Trạng thái Ứng dụng:**
    - Triển khai cơ chế "khóa/mở khóa" cho các tab "Soạn Truyện Dài" và "Trợ lý Biên tập". Các tab này sẽ bị vô hiệu hóa cho đến khi một "Dự án đang hoạt động" được chọn, giúp ngăn ngừa các lỗi logic.
    - Sửa lỗi không tự động làm mới danh sách khi tạo một dự án mới trong một nhóm "Local".
- **Đồng bộ Google Drive:** Sửa lỗi logic nghiêm trọng, đảm bảo việc xác thực và kết nối với Google Drive luôn được thực hiện **trước khi** xóa dữ liệu cục bộ ở chế độ "Làm mới toàn bộ", giúp bảo vệ dữ liệu người dùng.


## [1.14.1] - 2025-07-31

### 🐛 Sửa lỗi (Bug Fixes)
- **Logic Trợ lý Biên tập:**
    - Khắc phục lỗi logic nhận dạng khiến input "Tiêu đề" bị xử lý nhầm thành "Hook".
    - Sửa lỗi logic tra cứu trong hàm `save_final_version` để đảm bảo có thể lưu Tiêu đề, Thumbnail, Hook vào dự án đang hoạt động.
    - Bổ sung logic kiểm tra độ dài tiêu đề (tối đa 100 ký tự) trước khi cho phép lưu để đảm bảo tuân thủ quy định của YouTube.


## [1.14.0] - 2025-07-30

### 📝 Tài liệu (Documentation)
- **Khởi tạo Tài liệu Hướng dẫn:** Tạo file `USER_MANUAL.md` và soạn thảo nội dung ban đầu cho các phần Giới thiệu, Cài đặt & Khởi động, và Tổng quan Giao diện.


## [1.13.0] - 2025-07-24

### ✨ Tính năng mới (Features)
- **Hoàn thiện Tính năng Chèn Hook:**
    - Tích hợp nút "Chèn vào đầu truyện" vào tab "Hook" của Trợ lý Biên tập.
    - Bổ sung logic cảnh báo thông minh, hỏi người dùng xác nhận trước khi chèn hook vào một dự án đã có sẵn nội dung truyện, giúp tránh sai sót.
    - Hoàn thiện luồng tương tác giữa các module tab để chèn hook và tự động chuyển đến tab "Soạn Truyện Dài".


## [1.12.0] - 2025-07-24

### ✨ Tính năng mới (Features)
- **Tích hợp Công cụ Tìm & Thay thế:**
    - Xây dựng module `find_replace_dialog.py` chuyên trách cho việc tìm kiếm và thay thế.
    - Tích hợp cửa sổ "Tìm & Thay thế" vào trình soạn thảo truyện trong tab Thư viện.
    - Hỗ trợ đầy đủ các chức năng: tìm kiếm, thay thế, thay thế tất cả, phân biệt chữ hoa/thường, và tìm kiếm toàn bộ từ.
    - Bổ sung bộ đếm kết quả và tự động tô sáng (highlight) kết quả tìm thấy để cải thiện trải nghiệm người dùng.
    - Thêm phím tắt `Ctrl+F` để mở nhanh công cụ.

## [1.11.0] - 2025-07-24

### ✨ Tính năng mới (Features)
- **Hoàn thiện Tab Trợ lý Biên tập:** Bổ sung logic tự động nhận dạng và bóc tách các lựa chọn "Hook" mở đầu từ văn bản đầu vào, hoàn thiện luồng làm việc cho cả ba loại nội dung (Tiêu đề, Thumbnail, Hook).

### 🐛 Sửa lỗi (Bug Fixes)
- **Logic bóc tách Hook:** Sửa lỗi logic trong hàm `_parse_hooks` để đảm bảo nội dung của các lựa chọn hook được trích xuất đầy đủ và chính xác.


## [1.10.1] - 2025-07-24

### 🐛 Sửa lỗi (Bug Fixes)
- **Giao diện Tab Cài đặt:** Sắp xếp lại bố cục khu vực API Key thành dạng hàng ngang nhỏ gọn để tối ưu không gian hiển thị.

## [1.10.0] - 2025-07-24

### ✨ Tính năng mới (Features)
- **Tái thiết kế Giao diện Tab Trợ lý Biên tập:** Điều chỉnh lại tỉ lệ kích thước giữa khung "Lựa chọn" và khung "Soạn thảo" thành 1:3, ưu tiên tối đa không gian cho việc biên tập nội dung.

### 🐛 Sửa lỗi (Bug Fixes)
- **Giao diện Trợ lý Biên tập:** Sử dụng tùy chọn `uniform` của trình quản lý layout `.grid()` để đảm bảo tỉ lệ 1:3 được hiển thị một cách chính xác và nhất quán.


## [1.9.1] - 2025-07-24

### 🐛 Sửa lỗi (Bug Fixes)
- **Giao diện Chính:** Sắp xếp lại thứ tự `pack()` của các widget chính trong `main_app.py` để khắc phục triệt để lỗi khu vực "Nhật ký Hoạt động" và "Thanh Trạng thái" bị che khuất.



## [1.9.0] - 2025-07-23

### ♻️ Tái cấu trúc (Refactoring)
- **Hoàn tất Tái cấu trúc Module hóa Toàn bộ Ứng dụng:**
    - Tách toàn bộ giao diện và logic của tab "Settings" từ `main_app.py` ra một module riêng (`settings_tab.py`).
    - Hoàn thiện việc tách các module cho các tab "Text-to-Speech", "Trợ lý Biên tập", và "Soạn Truyện Dài".
    - File `main_app.py` giờ đây đã cực kỳ gọn nhẹ, chỉ còn đóng vai trò điều phối chính, giúp tăng cường khả năng bảo trì và mở rộng của dự án.


## [1.8.0] - 2025-07-23

### ♻️ Tái cấu trúc (Refactoring)
- **Tách Module Tab Soạn Truyện Dài:** Tiếp tục tái cấu trúc kiến trúc, tách toàn bộ giao diện và logic của tab "Soạn Truyện Dài" từ `main_app.py` ra một module riêng (`long_form_composer_tab.py`).


## [1.7.0] - 2025-07-22

### ♻️ Tái cấu trúc (Refactoring)
- **Tách Module Tab Text-to-Speech:** Tái cấu trúc lớn, tách toàn bộ giao diện và logic của tab "Text-to-Speech" từ `main_app.py` ra một module riêng (`tts_tab.py`). Giúp `main_app.py` trở nên gọn nhẹ hơn và tuân thủ chặt chẽ nguyên tắc Tách bạch Trách nhiệm.
- **Tách Module Tab Trợ lý Biên tập:** Tái cấu trúc lớn, tách toàn bộ giao diện và logic của tab "Trợ lý Biên tập" từ `main_app.py` ra một module riêng (`editorial_assistant_tab.py`), đồng thời tái thiết kế giao diện bên trong với cấu trúc tab con (Tiêu đề, Thumbnail, Hook).


## [1.6.0] - 2025-07-22

### ✨ Tính năng mới (Features)
- **Tích hợp Theme Giao diện Hiện đại:** Tích hợp thư viện `sv-ttk` để áp dụng theme "light" cho toàn bộ ứng dụng, mang lại một diện mạo mới, đồng bộ và chuyên nghiệp hơn, thay thế cho theme `clam` mặc định.

## [1.5.0] - 2025-07-21

### ✨ Tính năng mới (Features)
- **Tự động làm sạch Tiêu đề trong Thư viện:** Tên dự án và tiêu đề trong tab Thư viện giờ đây sẽ được tự động làm sạch các tiền tố số (ví dụ: "001 - Tên" -> "Tên") để giao diện gọn gàng và dễ đọc hơn.

### ♻️ Tái cấu trúc (Refactoring)
- Tái cấu trúc các hàm xử lý sự kiện trong `library_tab.py` (`_set_active_project`, `_delete_selected_project`, `_edit_project_name`) để luôn truy vấn tên dự án gốc từ CSDL, đảm bảo tính toàn vẹn dữ liệu sau khi tên hiển thị đã được làm sạch.


## [1.4.0] - 2025-07-21

### ✨ Added (Tính năng mới)
- **Tích hợp Thư viện với Text-to-Speech:** Thêm nút "Gửi sang TTS" trong tab "Thư viện", cho phép người dùng nhanh chóng gửi nội dung "Story" của một dự án đã chọn sang tab "Text-to-Speech" để chuẩn bị tạo giọng nói, tối ưu hóa luồng làm việc.


## [1.3.0] - 2025-07-19

### ✨ Added (Tính năng mới)
- **Hệ thống Quản lý Dự án & Thư viện:**
    - Xây dựng tab "Thư viện" hoàn toàn mới, cho phép quản lý các dự án truyện một cách có tổ chức.
    - Cho phép Tạo, Xóa, và Sửa tên dự án.
    - Cho phép sửa đổi từng thành phần của dự án (Truyện, Tiêu đề, Thumbnail) một cách độc lập thông qua thao tác double-click.
- **Tích hợp "Dự án đang hoạt động":**
    - Thêm thanh trạng thái ở dưới cùng cửa sổ để hiển thị dự án đang được làm việc.
    - Thêm nút "Làm việc với Dự án này" trong Thư viện để kích hoạt một dự án, tự động tải nội dung truyện vào tab "Soạn Truyện Dài".
    - Kết nối các tab "Trợ lý Biên tập" và "Soạn Truyện Dài" để tự động lưu vào "Dự án đang hoạt động".
- **Phản hồi Trạng thái bằng Màu sắc:**
    - Thanh trạng thái tự động đổi màu (vàng/xanh) để phản ánh tiến độ hoàn thành của dự án đang hoạt động (đã đủ 3 thành phần hay chưa).
- **Hệ thống Trạng thái Dự án:**
    - Thêm cột "Trạng thái" vào Thư viện.
    - Cho phép thay đổi trạng thái (Chưa làm, Đang làm dở, Đã làm) của dự án thông qua menu chuột phải, với màu nền tương ứng.
- **Hỗ trợ Đa ngôn ngữ cho TTS:** Trong tab Text-to-Speech, người dùng giờ đây có thể chọn ngôn ngữ (Tiếng Việt/English) và danh sách "Reading Style Prompt" sẽ tự động cập nhật.

### ♻️ Changed (Thay đổi)
- Tái cấu trúc lại cơ sở dữ liệu (`database.py`) để chuyển từ mô hình lưu trữ riêng lẻ sang mô hình "Dự án" (một-một).
- Thay đổi logic lưu của các tab "Trợ lý Biên tập" và "Soạn Truyện Dài" để tương thích với hệ thống dự án mới.

### 🐛 Fixed (Sửa lỗi)
- Sửa nhiều lỗi liên quan đến `AttributeError` và `NameError` do bất đồng bộ mã nguồn.
- Sửa các lỗi layout `TclError` trong các tab Settings và Thư viện.
- Khắc phục lỗi logic nghiêm trọng gây mất dữ liệu API trong `settings_manager.py`.



## [1.2.0] - 2025-07-17

### ✨ Added (Tính năng mới)
- **Hỗ trợ Đa ngôn ngữ cho TTS:** Trong tab Text-to-Speech, người dùng giờ đây có thể chọn ngôn ngữ (Tiếng Việt/English). Danh sách các "Reading Style Prompt" sẽ tự động cập nhật để phù hợp với ngôn ngữ đã chọn.
---
## [1.1.0] - 2025-07-16

### ✨ Added (Tính năng mới)
- **Hệ thống Quản lý Dự án & Thư viện:**
    - Xây dựng tab "Thư viện" hoàn toàn mới, cho phép quản lý các dự án truyện một cách có tổ chức.
    - Cho phép Tạo, Xóa, và Sửa tên dự án.
    - Cho phép sửa đổi từng thành phần của dự án (Truyện, Tiêu đề, Thumbnail) một cách độc lập thông qua thao tác double-click.
- **Tích hợp "Dự án đang hoạt động":**
    - Thêm thanh trạng thái ở dưới cùng cửa sổ để hiển thị dự án đang được làm việc.
    - Thêm nút "Làm việc với Dự án này" trong Thư viện để kích hoạt một dự án, tự động tải nội dung truyện vào tab "Soạn Truyện Dài".
    - Kết nối các tab "Trợ lý Biên tập" và "Soạn Truyện Dài" để tự động lưu vào "Dự án đang hoạt động".
- **Phản hồi Trạng thái bằng Màu sắc:**
    - Thanh trạng thái tự động đổi màu (vàng/xanh) để phản ánh tiến độ hoàn thành của dự án đang hoạt động (đã đủ 3 thành phần hay chưa).

### ♻️ Changed (Thay đổi)
- Tái cấu trúc lại cơ sở dữ liệu (`database.py`) để chuyển từ mô hình lưu trữ riêng lẻ sang mô hình "Dự án" (một-một).
- Thay đổi logic lưu của các tab "Trợ lý Biên tập" và "Soạn Truyện Dài" để tương thích với hệ thống dự án mới.

---
## [1.0.4] - 2025-07-06

### Đã thêm (Added)
- **Công cụ Hỗ trợ Phát hành:** Tạo kịch bản `scripts/release.py` để tự động hóa hoàn toàn việc nâng cấp và đồng bộ số phiên bản trên toàn bộ dự án, bao gồm các file: `constants.py`, `main_app.py`, `README.md` và `CHANGELOG.md`.


## [1.0.3] - 2025-07-06

- **Test chức năng:** `scripts/release.py`
        
## [1.0.2] - 2025-07-04

### Đã sửa (Fixed)
-   **Logic Bóc tách Tiêu đề:** Cải tiến và sửa lỗi hàm `_parse_titles` trong `main_app.py` để trích xuất chính xác các lựa chọn tiêu đề từ định dạng phản hồi mới của Gemini.

## [1.0.1] - 2025-06-28

### Đã sửa (Fixed)
-   **Văn bản Đầu ra:** Tinh chỉnh lại các chuỗi văn bản trong `main_app.py` để đảm bảo tính nhất quán và chất lượng khi sử dụng làm prompt cho các tác vụ khác.


## [1.0.0] - 2025-06-28

Đây là phiên bản ổn định đầu tiên, hoàn thiện các tính năng cốt lõi và khắc phục các vấn đề nghiêm trọng về môi trường và logic.

### Đã thêm (Added)
-   **Logic Cỡ chữ Nâng cao:** Triển khai cơ chế "cờ trạng thái" (`is_edited`) trong `thumbnail_preview.py` để "khóa" cỡ chữ của các dòng đã được chỉnh sửa thủ công, tránh bị "Cỡ chữ chung" ghi đè.
-   **Phụ thuộc Bắt buộc:** Thêm `fontTools` và `audioop-lts` vào `requirements.txt` để giải quyết các lỗi cốt lõi.
-   **Đóng gói Sản phẩm:** Thêm quy trình và hỗ trợ đóng gói ứng dụng thành file `.exe` bằng PyInstaller.
-   **Tài liệu Dự án:** Tạo mới các file `WORKFLOW.md` và `TECHNICAL_NOTES.md` để chuẩn hóa quy trình làm việc và ghi lại các quyết định kỹ thuật quan trọng.

### Đã thay đổi (Changed)
-   **Tái cấu trúc Kiến trúc Font (Rất quan trọng):** Viết lại hoàn toàn logic xử lý font trong `thumbnail_preview.py`. Dự án đã **từ bỏ hoàn toàn** việc hỗ trợ **Variable Fonts** do lỗi tương thích môi trường không thể khắc phục. Giờ đây, chương trình chỉ quét và làm việc với các **font tĩnh** (mỗi kiểu chữ là một file `.ttf` riêng biệt).
-   **Tái cấu trúc Logic "Cỡ chữ chung":** Đơn giản hóa hành vi của `Spinbox` Cỡ chữ chung, có hiệu lực ngay khi người dùng thay đổi giá trị, loại bỏ nút "Áp dụng" không cần thiết.

### Đã sửa (Fixed)
-   **Sửa lỗi Căn giữa Nghiêm trọng:** Khắc phục triệt để lỗi căn chỉnh của khối văn bản trong thumbnail. Khối text giờ đây luôn được căn giữa hoàn hảo theo cả chiều dọc và chiều ngang.
-   **Sửa lỗi Kiểu chữ (Font Weight):** Chức năng chọn Kiểu chữ (Bold, Normal...) từ `Combobox` chung giờ đây hoạt động chính xác và đáng tin cậy.
-   **Sửa lỗi Môi trường `pydub`:** Khắc phục hoàn toàn lỗi `ModuleNotFoundError: No module named 'pyaudioop'` khi khởi chạy ứng dụng.
-   **Sửa lỗi Đóng gói:** Khắc phục lỗi `FileNotFoundError` khi build file `.exe` do thiếu file icon.

### Đã xóa (Removed)
-   Loại bỏ hoàn toàn các widget và logic không được yêu cầu liên quan đến việc chọn kiểu chữ cho từng dòng, quay về đúng yêu cầu gốc là một kiểu chữ thống nhất.

---

## [0.8.0] - (Ngày tháng cũ)
-   ... (Các thay đổi cũ)

## [0.8.0] - 2025-06-27
### Đã thay đổi (Changed)
- **Tài liệu:** Hợp nhất các file hướng dẫn thành một file `WORKFLOW.md` duy nhất, đồng thời tạo mới `CHANGELOG.md` và `ROADMAP.md` để làm rõ quy trình.
- **Thumbnail Preview:** Tái cấu trúc (refactor) module để chuẩn bị cho việc hỗ trợ tùy chỉnh thuộc tính (cỡ chữ, font weight) cho từng dòng văn bản riêng biệt.

### Đã thêm (Added)
- **Workflow:** Bổ sung quy trình cải tiến liên tục vào `WORKFLOW.md`.