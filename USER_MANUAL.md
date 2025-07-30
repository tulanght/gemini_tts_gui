# Hướng dẫn Sử dụng Gemini Creative Suite
# Phiên bản 1.0 (Tương ứng với phiên bản ứng dụng v1.13.0)
# Last Updated: 2025-07-24

Chào mừng bạn đến với Gemini Creative Suite! Đây là tài liệu hướng dẫn chi tiết giúp bạn làm chủ toàn bộ các tính năng mạnh mẽ của bộ công cụ này.

## 1. Giới thiệu
Gemini Creative Suite là một bộ công cụ "tất cả trong một" (all-in-one) được xây dựng để hỗ trợ toàn diện cho các nhà sáng tạo nội dung, đặc biệt trong lĩnh vực sản xuất video truyện kể (voice-over). Mục tiêu của ứng dụng là tối ưu và tự động hóa các công đoạn trong quy trình sáng tạo, từ việc quản lý ý tưởng, soạn thảo, tạo giọng đọc AI, cho đến việc chuẩn bị các thành phần media như tiêu đề và thumbnail.

## 2. Cài đặt & Khởi động

### 2.1. Dành cho Người dùng cuối (Bản đóng gói .exe)
1.  Sau khi tải về, bạn sẽ có một file duy nhất: `Gemini Creative Suite.exe`.
2.  Bạn có thể sao chép file này đến bất kỳ vị trí nào trên máy tính Windows của bạn.
3.  Nhấp đúp vào file `Gemini Creative Suite.exe` để khởi động ứng dụng. Không cần cài đặt thêm bất kỳ phần mềm nào khác.

### 2.2. Dành cho Lập trình viên
Để chạy dự án từ mã nguồn, bạn cần chuẩn bị môi trường theo các bước sau:

**Yêu cầu:**
* Python 3.9+
* `ffmpeg`: Cần được cài đặt và thêm vào biến môi trường PATH của hệ thống.

**Các bước thực hiện:**
1.  **Tạo Môi trường ảo:** Mở terminal trong thư mục gốc của dự án và chạy lệnh:
    ```bash
    python -m venv venv
    ```
2.  **Kích hoạt Môi trường ảo:**
    ```bash
    .\venv\Scripts\activate
    ```
    *(Sau khi kích hoạt, bạn sẽ thấy `(venv)` ở đầu dòng lệnh.)*

3.  **Cài đặt các Thư viện:** Chạy lệnh sau để cài đặt tất cả các gói phụ thuộc cần thiết:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Chạy Ứng dụng:** Cuối cùng, chạy lệnh:
    ```bash
    python run.py
    ```

## 3. Tổng quan Giao diện
Giao diện chính của ứng dụng được chia thành 3 khu vực chính:

![Mô tả giao diện](URL_HINH_ANH_GIAO_DIEN_TONG_QUAN) *(Chúng ta sẽ thêm hình ảnh sau)*

1.  **Khu vực các Tab (Notebook):** Đây là khu vực làm việc chính, nơi chứa toàn bộ các tính năng của ứng dụng, được sắp xếp vào các tab riêng biệt (Text-to-Speech, Thư viện, Trợ lý Biên tập, v.v.).
2.  **Khu vực Nhật ký Hoạt động (Log):** Nằm ở phía dưới, khu vực này hiển thị các thông báo trạng thái, tiến trình, hoặc các lỗi xảy ra trong quá trình bạn sử dụng ứng dụng.
3.  **Thanh Trạng thái (Status Bar):** Nằm ở dưới cùng, thanh này hiển thị thông tin về "Dự án đang hoạt động" hiện tại, giúp bạn luôn biết mình đang làm việc với dự án nào.

---
*(Nội dung các mục tiếp theo sẽ được chúng ta xây dựng ở các bước sau.)*