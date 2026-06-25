# GR1
TÌM HIỂU VỀ KHẢ NĂNG ĐỒNG BỘ DỮ LIỆU GIỮA THẾ GIỚI THẬT VÀ MINECRAFT JAVA EDITION (ỨNG DỤNG FETCH API VÀ TỐI ƯU HÓA LUỒNG DỮ LIỆU TCP/IP)



# Đồ Án 1: Hệ Thống Đồng Bộ Dữ Liệu HUST News Vào Minecraft 

Hệ thống phân phối dữ liệu đa phương tiện tự động (Data Pipeline) từ cổng thông tin Đại học Bách Khoa Hà Nội (RSS) vào không gian 3D của Minecraft Java Edition thông qua giao thức TCP RCON.

Dự án áp dụng kiến trúc phân rã (Decoupled Architecture) và tối ưu hóa đường truyền mạng bằng kết nối duy trì (Persistent Connection), giúp giảm thiểu độ trễ (Latency) xuống mức tối đa.

---

## 1. Yêu cầu môi trường (Prerequisites)

Để hệ thống hoạt động, máy chủ cần được cài đặt sẵn các môi trường sau:
* **Môi trường Game Server:**
  - Java Development Kit (JDK) 21 (Bắt buộc để chạy lõi Paper 1.20.5+).
  - Lõi máy chủ: PaperMC (Khuyên dùng bản 1.21.x).
  - Game Client: Minecraft Java Edition 1.21.x.
* **Môi trường Code (Python Daemon):**
  - Python 3.11 trở lên.

## 2. Hướng dẫn Cài đặt (Installation)

**Bước 1: Tải mã nguồn**
Clone repository này về máy của bạn:
```bash
git clone <đường-link-github-của-bạn>
cd <tên-thư-mục-dự-án>

```
Bước 2: Cài đặt thư viện Python
Mở Terminal/CMD tại thư mục dự án và chạy lệnh cài đặt các thư viện phụ thuộc:

Bash
```pip install requests beautifulsoup4 mcrcon lxml```
(Mẹo: Bạn có thể lưu lệnh này vào file requirements.txt và chạy pip install -r requirements.txt)

3. Cấu hình Máy chủ Minecraft (Server Configuration)
Tải file paper-1.21-xxx.jar từ trang chủ PaperMC và đặt vào thư mục gốc.

Chạy file .jar lần đầu tiên, sau đó mở file eula.txt và đổi eula=false thành eula=true.

Mở file server.properties và thiết lập các thông số RCON bắt buộc sau để cho phép Python giao tiếp với Game:

Properties
```
enable-rcon=true
rcon.port=25575
rcon.password=123456
```
Khởi động lại máy chủ bằng lệnh:

DOS
```java -jar <tên-file-paper>.jar```
4. Hướng dẫn Vận hành (Usage)
Quá trình vận hành yêu cầu thực hiện song song trên Game Server và Terminal chạy Python.

BƯỚC 4.1: Triệu hồi Bảng tin (Trong Game)
Đăng nhập vào server Minecraft thông qua địa chỉ 127.0.0.1.

Đứng tại vị trí bạn muốn đặt màn hình LED, mở khung chat (phím T) và dán lệnh sau để khởi tạo thực thể nhận dữ liệu:

Đoạn mã
```/summon text_display ~ ~2 ~ {Tags:["hust_board"],billboard:"fixed",transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[3f,3f,3f]},text:'{"text":"HỆ THỐNG READY - CHỜ KẾT NỐI PYTHON..."}'}```
(Lưu ý: Hệ thống hỗ trợ cập nhật hàng loạt màn hình. Bạn có thể sử dụng lệnh này nhiều lần ở các vị trí khác nhau trong trường. Tất cả sẽ được đồng bộ cùng lúc).

BƯỚC 4.2: Khởi động Tiến trình Python
Mở một cửa sổ Terminal/CMD mới, di chuyển vào thư mục dự án và chạy lệnh:

Bash
```python minecraft_news_rcon.py```
5. Cơ chế hoạt động & Tính năng nổi bật
Đo lường độ trễ (Benchmarking): Script tự động tính toán End-to-End Latency bằng time.perf_counter() và in ra terminal ở mỗi chu kỳ thành công.

Persistent Connection: Tái sử dụng HTTP Session (Keep-Alive) và duy trì Socket RCON ngoài vòng lặp, giúp thời gian cập nhật giảm từ ~1400ms xuống ~900ms (nhanh gấp 1.5 lần).

Tự chữa lành (Fault Tolerance): Nếu Game Server bị tắt đột ngột hoặc khởi động lại, script Python sẽ không bị Crash. Nó sẽ bắt các ngoại lệ mất kết nối socket và tự động tái thiết lập đường truyền (Reconnect) ngay khi Server hoạt động trở lại.

Đồng bộ hàng loạt (Multi-display Sync): Sử dụng lệnh /execute as kết hợp Query Selector để cập nhật đồng loạt tất cả bảng tin có tag hust_board trong thế giới, thay vì bị giới hạn cập nhật 1 thực thể đơn lẻ như lệnh /data modify thông thường.
