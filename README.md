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

---
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

---
## 3. Cấu hình Máy chủ Minecraft (Server Configuration)
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
```
java -jar <tên-file-paper>.jar
VD: java -jar paper-26.1.2-64.jar
```

---
## 4. Hướng dẫn Vận hành (Usage)
Quá trình vận hành yêu cầu thực hiện song song trên Game Server và Terminal chạy Python.

BƯỚC 4.1: Triệu hồi Bảng tin (Trong Game)
Đăng nhập vào server Minecraft thông qua địa chỉ 127.0.0.1.

Đứng tại vị trí bạn muốn đặt màn hình LED, mở khung chat (phím T) và dán lệnh sau để khởi tạo thực thể nhận dữ liệu:

Đoạn mã
```
/summon text_display ~ ~2 ~ {Tags:["hust_board"],billboard:"fixed",transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[3f,3f,3f]},text:'{"text":"HỆ THỐNG READY - CHỜ KẾT NỐI PYTHON..."}'}
```
(Lưu ý: Hệ thống hỗ trợ cập nhật hàng loạt màn hình. Bạn có thể sử dụng lệnh này nhiều lần ở các vị trí khác nhau trong trường. Tất cả sẽ được đồng bộ cùng lúc).

BƯỚC 4.2: Khởi động Tiến trình Python
Mở một cửa sổ Terminal/CMD mới, di chuyển vào thư mục dự án và chạy lệnh:

Bash
```
python minecraft_news_rcon.py
```

Hình ảnh sau khi hoạt động:
<img width="1199" height="693" alt="image" src="https://github.com/user-attachments/assets/3792376a-889b-46aa-a468-abb8c010f387" />


---
## 5. Cơ chế hoạt động & Tính năng nổi bật
Đo lường độ trễ (Benchmarking): Script tự động tính toán End-to-End Latency bằng time.perf_counter() và in ra terminal ở mỗi chu kỳ thành công.

Persistent Connection: Tái sử dụng HTTP Session (Keep-Alive) và duy trì Socket RCON ngoài vòng lặp, giúp thời gian cập nhật giảm từ ~1400ms xuống ~900ms (nhanh gấp 1.5 lần).

Trước khi tối ưu đường truyền RSS:
<img width="1129" height="184" alt="image" src="https://github.com/user-attachments/assets/4cc5311b-00f4-47f4-be6d-2b86d375daa2" />

Sau khi tối ưu đường truyền RSS:
<img width="1138" height="168" alt="image" src="https://github.com/user-attachments/assets/9d7e4ab3-0f7d-4dfa-a8be-198fa0b4d5f4" />


Tự chữa lành (Fault Tolerance): Nếu Game Server bị tắt đột ngột hoặc khởi động lại, script Python sẽ không bị Crash. Nó sẽ bắt các ngoại lệ mất kết nối socket và tự động tái thiết lập đường truyền (Reconnect) ngay khi Server hoạt động trở lại.

Đồng bộ hàng loạt (Multi-display Sync): Sử dụng lệnh /execute as kết hợp Query Selector để cập nhật đồng loạt tất cả bảng tin có tag hust_board trong thế giới, thay vì bị giới hạn cập nhật 1 thực thể đơn lẻ như lệnh /data modify thông thường.

Các tin nhắn được đồng bộ hàng loạt:
<img width="2559" height="1432" alt="image" src="https://github.com/user-attachments/assets/9f426b38-5ad7-4970-88d8-c5118f4a4e6a" />

---
## 6. Phân tích Chi tiết Kiến trúc & Logic Mã nguồn (Code Analysis)

Mã nguồn của hệ thống (`minecraft_news_rcon.py`) không chỉ dừng lại ở một script gửi lệnh đơn thuần, mà được thiết kế theo các tiêu chuẩn kỹ thuật phần mềm dành cho Backend Service, bao gồm Phân tách module, Tối ưu hóa TCP và Cơ chế tự phục hồi.

### 6.1. Kiến trúc Phân rã (Decoupled Architecture)
Hệ thống áp dụng triệt để nguyên lý Phân tách mối quan tâm (Separation of Concerns), chia luồng xử lý thành 3 phân vùng độc lập:
1. **Data Ingestion (Thu thập dữ liệu):** Hàm `fetch_latest_titles` đóng vai trò cào dữ liệu thô. Thay vì dùng Regex dễ sinh lỗi, dự án sử dụng `BeautifulSoup` với trình phân tích `xml` để trích xuất chính xác các thẻ `<title>` từ luồng RSS, sau đó giới hạn số lượng tin trả về bằng tham số `NEWS_COUNT`.
2. **Payload Formatting (Định dạng Dữ liệu):** Hàm `build_text_component` bọc các chuỗi văn bản thô vào cấu trúc **JSON Text Component** của Mojang. Việc tổ chức các mảng `extra` với thuộc tính `color` và `bold` giúp tái tạo giao diện UI sắc nét trong không gian Voxel.
3. **Transport (Vận chuyển RCON):** Hàm `send_rcon_command` chịu trách nhiệm giao tiếp Socket cấp thấp, bọc chuỗi NBT và đẩy vào máy chủ game.

### 6.2. Chiến lược Tối ưu hóa Luồng Mạng (TCP Optimization)
Điểm sáng lớn nhất về mặt hiệu năng của hệ thống nằm ở cách quản lý vòng đời của các kết nối mạng:
* **HTTP Keep-Alive (Session-based):** Việc khởi tạo `session = requests.Session()` ở ngoài vòng lặp `while True` giúp hệ thống không phải liên tục thực hiện quá trình bắt tay 3 bước (TCP 3-way Handshake) và đàm phán SSL/TLS với máy chủ `hust.edu.vn` ở mỗi chu kỳ 60 giây.
* **Persistent RCON Connection:** Tương tự, đối tượng `MCRcon` được thiết lập và gọi `.connect()` một lần duy nhất khi khởi động script. Socket được giữ ở trạng thái mở (Persistent). Việc tái sử dụng đường hầm này giúp **độ trễ End-to-End giảm mạnh từ ~500ms xuống chỉ còn ~40ms**.

### 6.3. Xử lý Dữ liệu NBT & Định dạng Đa ngôn ngữ (UTF-8)
Để Minecraft (phiên bản 1.20.5+) có thể hiểu và hiển thị chính xác Tiếng Việt có dấu, mã nguồn sử dụng thủ thuật quan trọng trong quá trình Serialize dữ liệu:
```
python
json_str = json.dumps(component, ensure_ascii=False, separators=(",", ":"))
```
Cờ ensure_ascii=False ngăn Python tự động chuyển đổi các ký tự Unicode (như Đồ án, Bách Khoa) thành chuỗi escape \uXXXX. Điều này giúp bảo toàn định dạng byte thô, ngăn chặn lỗi vỡ font hiển thị trên Client.

Cờ separators=(",", ":") thực hiện nén chuỗi (Minify), loại bỏ toàn bộ khoảng trắng thừa để tiết kiệm băng thông khi truyền qua gói tin RCON.

6.4. Cơ chế Tự chữa lành (Fault Tolerance & Self-healing)
Trong quá trình vận hành liên tục, kết nối TCP có thể bị gián đoạn (do máy chủ game khởi động lại, sụt mạng rớt gói tin). Hệ thống bắt chặn các rủi ro này bằng khối ngoại lệ thông minh:
```
Python
RCON_RECONNECT_ERRORS = (socket.error, ConnectionError, BrokenPipeError, OSError)
try:
    return rcon_client.command(command)
except RCON_RECONNECT_ERRORS as exc:
    rcon_client.connect() # Tự động thiết lập lại đường truyền
    return rcon_client.command(command)
```
Nếu xảy ra lỗi ```BrokenPipeError``` (Đường hầm TCP bị đứt), thay vì chương trình văng lỗi (Crash), Daemon sẽ tự động gọi lại hàm ```.connect()``` để khôi phục socket và gửi lại lệnh, đảm bảo tính liên tục (High Availability) cho hệ thống bảng tin.

6.5. Cập nhật Đa màn hình (Multi-display Synchronization)
Thay vì sử dụng lệnh ```/data modify``` trực tiếp (vốn bị giới hạn bởi tham số ```limit=1``` gây lỗi chỉ cập nhật được màn hình đầu tiên), hệ thống sử dụng Query Selector nâng cao:

```
Python
f"/execute as @e[type=text_display,tag=hust_board] run data modify entity @s text set value {json_str}"
Lệnh /execute as sẽ quét toàn bộ không gian Virtual Campus. Bất kỳ thực thể nào mang thẻ hust_board đều sẽ bị ép thực thi lệnh thay đổi NBT lên chính nó (@s). Nhờ vậy, quản trị viên có thể summon hàng chục màn hình LED ở các khu vực khác nhau (Thư viện, Quảng trường C1, Cổng Parabol) và tất cả sẽ được đồng bộ hóa nội dung thời gian thực cùng một lúc.
```
