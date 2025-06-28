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