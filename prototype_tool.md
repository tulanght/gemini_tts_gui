# Project Brief: Công cụ "Trợ Lý Sáng Tạo Radio Gia Đình"

**Ngày tạo:** 14/06/2025
**Phiên bản:** 1.0

---

## 1. Tóm Tắt & Mục Tiêu Dự Án

### 1.1. Tóm Tắt
Đây là dự án xây dựng một ứng dụng máy tính (desktop app) bằng Python với giao diện đồ họa (GUI) sử dụng thư viện Tkinter. Ứng dụng này có tên là "Trợ Lý Sáng Tạo Radio Gia Đình", đóng vai trò là công cụ hỗ trợ cho người dùng trong quá trình biên tập và chốt phương án cuối cùng cho Tiêu đề và Text Thumbnail của các video YouTube.

### 1.2. Vấn đề cần giải quyết
Hiện tại, người dùng phải làm việc với các lựa chọn nội dung (tiêu đề, text thumbnail) do AI (Gemini) tạo ra. Quá trình này đòi hỏi các bước thủ công, lặp đi lặp lại và dễ sai sót như:
-   Đếm số ký tự/từ của nhiều lựa chọn để đảm bảo tuân thủ quy định của YouTube.
-   Kiểm tra các quy luật về độ dài (ví dụ: vùng vàng 90-100 ký tự).
-   Khó quản lý, so sánh và lưu trữ các phương án đã chốt.

### 1.3. Mục tiêu của công cụ
-   **Tự động hóa** việc bóc tách và phân tích các lựa chọn do AI cung cấp.
-   **Trực quan hóa** số liệu (ký tự, từ) và đưa ra cảnh báo theo thời gian thực.
-   **Tạo ra một môi trường soạn thảo** hiệu quả, giúp người dùng dễ dàng chỉnh sửa và ra quyết định cuối cùng.
-   **Lưu trữ** các phương án đã được chốt một cách có hệ thống để dễ dàng tra cứu về sau.

---

## 2. Mô Tả Chức Năng Chi Tiết (Functional Description)

### 2.1. Chức năng Cốt lõi
-   **Nhập liệu & Bóc tách (Input & Parsing):** Cho phép người dùng dán toàn bộ đoạn văn bản phản hồi từ Gemini. Chương trình phải có khả năng tự động nhận diện và bóc tách các lựa chọn riêng biệt.
-   **Đếm & Hiển thị (Counting & Display):** Đếm chính xác số ký tự (bao gồm dấu cách) và số từ của mỗi lựa chọn.
-   **Soạn thảo & Giám sát (Editing & Live-monitoring):** Cung cấp một không gian để người dùng chỉnh sửa phương án đã chọn. Trong quá trình soạn thảo, chương trình phải liên tục đếm lại và cập nhật số liệu.
-   **Cảnh báo bằng màu sắc (Color-coded Alerts):** Thay đổi màu sắc của bộ đếm để cảnh báo người dùng khi họ vi phạm các quy luật về độ dài.
-   **Lưu trữ (Storage):** Lưu phương án cuối cùng vào một file cơ sở dữ liệu đơn giản (SQLite) hoặc file văn bản (CSV/TXT).

### 2.2. Luồng Hoạt Động của Người Dùng (User Workflow)
1.  Người dùng chạy prompt tạo tiêu đề/thumbnail trên giao diện Gemini.
2.  Người dùng bôi đen và sao chép (copy) toàn bộ văn bản phản hồi của Gemini.
3.  Người dùng chuyển sang ứng dụng "Trợ Lý Sáng Tạo", dán (paste) văn bản vào **Vùng Nhập Liệu**.
4.  Người dùng nhấn nút **"Bóc Tách & Phân Tích"**.
5.  Các lựa chọn được bóc tách sẽ hiện ra trong **Danh Sách Lựa Chọn**.
6.  Người dùng nhấp vào một lựa chọn trong danh sách. Lựa chọn đó sẽ tự động được điền vào **Vùng Soạn Thảo**.
7.  Người dùng chỉnh sửa nội dung trong Vùng Soạn Thảo. **Bộ Đếm & Cảnh Báo** sẽ cập nhật theo thời gian thực.
8.  Khi nội dung đã tối ưu (ví dụ: bộ đếm có màu xanh lá), người dùng nhấn nút **"Chốt & Lưu"**.
9.  Chương trình lưu dữ liệu và hiển thị thông báo thành công.

---

## 3. Thiết Kế Giao Diện Người Dùng (GUI) - Prototype

Ứng dụng sẽ sử dụng `tkinter.ttk.Notebook` để tạo giao diện theo các Tab.

### 3.1. Bố cục Tổng thể
-   Một cửa sổ chính có tiêu đề "Trợ Lý Sáng Tạo Radio Gia Đình".
-   Bên trong có 2 Tab chính: **"Xử Lý Tiêu Đề"** và **"Xử Lý Thumbnail"**.

### 3.2. Chi tiết Tab "Xử Lý Tiêu Đề"
Giao diện được chia thành các khu vực chính:

-   **Khu vực Nhập liệu (Bên trái):**
    -   `Label(text="Dán phản hồi của Gemini vào đây:")`
    -   `scrolledtext.ScrolledText(id="input_text_title")`: Một ô văn bản lớn, có thanh cuộn, để dán nội dung.
    -   `Button(id="parse_button_title", text="Bóc Tách & Phân Tích")`: Nút để thực thi việc bóc tách.

-   **Khu vực Lựa chọn & Soạn thảo (Bên phải):**
    -   `Label(text="Các lựa chọn đã bóc tách:")`
    -   `Listbox(id="options_list_title")`: Danh sách hiển thị các lựa chọn. Khi một mục được chọn, sự kiện `<<ListboxSelect>>` sẽ được kích hoạt.
    -   `Label(text="Soạn thảo tiêu đề cuối cùng:")`
    -   `Entry(id="editor_entry_title")`: Ô văn bản một dòng để chỉnh sửa tiêu đề. Nội dung trong ô này sẽ được theo dõi sự kiện `<KeyRelease>`.
    -   `Label(id="counter_label_title", text="Số ký tự: 0 | Số từ: 0")`: Bộ đếm, có khả năng thay đổi màu sắc.
    -   `Button(id="save_button_title", text="Chốt Tiêu Đề Này", state=tk.DISABLED)`: Nút lưu, ban đầu bị vô hiệu hóa.

### 3.3. Chi tiết Tab "Xử Lý Thumbnail"
-   Thiết kế tương tự Tab Tiêu đề.
-   Điểm khác biệt: **Vùng Soạn Thảo Cuối Cùng** sẽ là một `scrolledtext.ScrolledText` (giống vùng nhập liệu) thay vì `Entry` để có thể soạn thảo nhiều dòng.
-   **Bộ Đếm & Cảnh Báo** sẽ hiển thị thêm thông tin: "Số dòng: Z", và có thể có logic cảnh báo riêng cho số từ/dòng.

---

## 4. Yêu Cầu Kỹ Thuật & Khung Sườn Mã

### 4.1. Ngôn ngữ & Thư viện
-   **Ngôn ngữ:** Python 3.x
-   **Thư viện:**
    -   `tkinter` (và `tkinter.ttk`, `tkinter.scrolledtext`): Thư viện chuẩn để xây dựng GUI.
    -   `re`: Thư viện chuẩn cho Regular Expressions, dùng cho chức năng bóc tách cốt lõi.
    -   `sqlite3`: Thư viện chuẩn để tạo và quản lý cơ sở dữ liệu lưu trữ.
    -   `pyperclip` (Tùy chọn, nâng cao): Giúp tạo nút "Dán Nhanh" để tự động lấy nội dung từ clipboard, tăng trải nghiệm người dùng.

### 4.2. Khung Sườn Mã Python (Gợi ý)
```python
# main.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import re
import sqlite3

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Trợ Lý Sáng Tạo Radio Gia Đình")
        # ... khởi tạo các thành phần giao diện ...
        
        # Kết nối CSDL
        self.conn = sqlite3.connect("database.db")
        self.create_table()

    def create_table(self):
        # Tạo bảng 'titles' và 'thumbnails' nếu chưa tồn tại
        pass

    # --- CÁC HÀM XỬ LÝ CHO TAB TIÊU ĐỀ ---
    def parse_titles(self):
        # Lấy text từ input_text_title
        # Dùng regex để tìm các lựa chọn
        # Xóa listbox cũ và điền các lựa chọn mới vào
        pass

    def on_title_selected(self, event):
        # Lấy tiêu đề từ listbox và đưa vào editor_entry_title
        pass

    def update_title_counter(self, event):
        # Lấy text từ editor_entry_title
        # Đếm ký tự, đếm từ
        # Cập nhật label bộ đếm và màu sắc (logic đỏ/xanh)
        # Bật/tắt nút save_button_title
        pass
        
    def save_final_title(self):
        # Lấy text từ editor_entry_title
        # Lưu vào CSDL SQLite
        # Hiển thị messagebox xác nhận
        pass

    # --- CÁC HÀM TƯƠNG TỰ CHO TAB THUMBNAIL ---
    # ...

if __name__ == "__main__":
    app = App()
    app.mainloop()
```
---

#### **KHỐI 2 (Từ mục 4.3 đến hết)**
```markdown
### 4.3. Logic Xử Lý Chính (Gợi ý cụ thể)
-   **Logic Bóc tách (Parsing):** Sử dụng `re.findall()`. Một pattern gợi ý rất hiệu quả để bóc tách các lựa chọn từ phản hồi của Gemini là:
    `\*\*LỰA CHỌN \d+.*?\*\*([\s\S]*?)(?=\*\*LỰA CHỌN|\Z)`
    Pattern này sẽ tìm tất cả các khối văn bản nằm giữa các tiêu đề "LỰA CHỌN X" do Gemini tạo ra.

-   **Logic Đếm & Cảnh báo:** Trong hàm `update_title_counter`, sau khi lấy được số ký tự `char_count`:
    ```python
    if 90 <= char_count <= 100:
        self.counter_label_title.config(foreground="green")
        self.save_button_title.config(state=tk.NORMAL)
    else:
        self.counter_label_title.config(foreground="red")
        self.save_button_title.config(state=tk.DISABLED)
    ```

---

## 5. Phân Tích Rủi Ro & Giải Pháp Đề Xuất

### 5.1. Rủi ro về Tự động hóa Giao diện (Ví dụ: dùng OpenCV)
-   **Rủi ro:** Việc cố gắng tự động hóa việc đọc và sao chép văn bản trực tiếp từ cửa sổ trình duyệt Gemini là cực kỳ rủi ro và không bền vững. Giao diện web thay đổi liên tục, chỉ cần một thay đổi nhỏ về font chữ, màu sắc, hoặc cấu trúc HTML là sẽ làm hỏng toàn bộ chức năng.
-   **Giải pháp đề xuất (TỐT NHẤT):** Giữ nguyên luồng làm việc **Copy & Paste thủ công**. Đây là giải pháp đơn giản nhất, đáng tin cậy 100% và không phụ thuộc vào bất kỳ thay đổi nào từ phía giao diện của Gemini. Sự ổn định quan trọng hơn sự tự động hóa tuyệt đối trong trường hợp này.

### 5.2. Rủi ro về Thay đổi Định dạng Output của Gemini
-   **Rủi ro:** Gemini có thể thay đổi cách trình bày các lựa chọn (ví dụ: không dùng `**LỰA CHỌN X**` nữa mà dùng `- Lựa chọn 1:`).
-   **Giải pháp:** Đây là một rủi ro có thể chấp nhận được. Việc cập nhật lại pattern Regular Expression trong mã nguồn là một thao tác tương đối đơn giản và nhanh chóng.

---

## 6. Hướng Dẫn cho AI Lập Trình

Gửi Gemini (phiên bản lập trình),

Nhiệm vụ của bạn là hiện thực hóa ứng dụng Python Tkinter được mô tả trong tài liệu này. Hãy đọc kỹ từng phần để hiểu rõ mục tiêu, chức năng, và các yêu cầu kỹ thuật.

**Những điểm cần đặc biệt lưu ý:**
1.  **Cấu trúc giao diện:** Tuân thủ bố cục các Tab và các widget đã được mô tả, sử dụng các `id` (tên biến) gợi ý để mã nguồn dễ hiểu.
2.  **Logic bóc tách:** Áp dụng phương pháp Regular Expression đã được gợi ý để xử lý văn bản đầu vào.
3.  **Tính năng tương tác:** Đảm bảo hàm `update_title_counter` được liên kết với sự kiện `<KeyRelease>` của vùng soạn thảo để tạo ra trải nghiệm theo thời gian thực.
4.  **Luồng hoạt động:** Ưu tiên luồng Copy & Paste thủ công, không cố gắng tích hợp các giải pháp tự động hóa giao diện phức tạp và không ổn định.
5.  **Mã hóa:** Toàn bộ file và xử lý chuỗi phải sử dụng `UTF-8`.