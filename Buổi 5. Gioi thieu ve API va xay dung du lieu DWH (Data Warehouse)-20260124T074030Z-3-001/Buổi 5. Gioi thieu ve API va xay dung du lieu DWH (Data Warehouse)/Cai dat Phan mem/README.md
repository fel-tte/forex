# Danh sách phần mềm cần cài đặt cho buổi học thứ năm

## 1. Python
- Phiên bản khuyến nghị: 3.11.x, 3.10.x hoặc 3.9.x
- Link tải: https://www.python.org/downloads/
- Hướng dẫn cài đặt:
  - Tải file cài đặt phù hợp với hệ điều hành
  - Chạy file cài đặt
  - Đánh dấu vào ô "Add Python to PATH" trong quá trình cài đặt
  - Hoàn tất quá trình cài đặt

## 2. Jupyter Notebook hoặc VS Code
### Jupyter Notebook
- Cài đặt thông qua pip:
```sh
pip install notebook
```
- Khởi động Jupyter Notebook:
```sh
jupyter notebook
```

### Visual Studio Code
- Link tải: https://code.visualstudio.com/
- Cài đặt các extension cần thiết:
  - Python
  - Jupyter
  - Python Extension Pack

## 3. Các thư viện Python cơ bản
Cài đặt các thư viện cần thiết thông qua pip:
```sh
pip install numpy pandas matplotlib yfinance metatrader5 scikit-learn sqlalchemy pyodbc xlsxwriter requests beautifulsoup4
```

## 4. Công cụ phát triển API
### Postman (Tùy chọn)
- Link tải: https://www.postman.com/downloads/
- Cài đặt nếu bạn muốn test API

## 5. SQL Server và SQL Server Management Studio (SSMS)
#### SQL Server
- Link tải: https://www.microsoft.com/en-us/sql-server/sql-server-downloads
- Chọn phiên bản "Developer" (miễn phí cho mục đích học tập)
- Hướng dẫn cài đặt:
  - Tải file cài đặt SQL Server
  - Chạy file cài đặt
  - Chọn "Basic" installation type
  - Chọn thư mục cài đặt
  - Nhấn "Install" và đợi quá trình cài đặt hoàn tất
  - Ghi nhớ mật khẩu SA (System Administrator) được tạo trong quá trình cài đặt

#### SQL Server Management Studio (SSMS)
- Link tải: https://learn.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms
- Cài đặt để quản lý cơ sở dữ liệu SQL Server
- Hướng dẫn kết nối:
  - Mở SSMS
  - Server name: localhost hoặc .\SQLEXPRESS
  - Authentication: SQL Server Authentication
  - Login: sa
  - Password: (mật khẩu đã tạo khi cài đặt SQL Server)

## 6. Redis
### Redis Server
- Link tải: https://github.com/tporadowski/redis/releases
- Cài đặt Redis server cho Windows

### Redis Desktop Manager (Client)
- Link tải: https://redis-desktop-manager.en.lo4d.com/download
- Cài đặt công cụ quản lý Redis để dễ dàng thao tác với dữ liệu

## 7. MetaTrader 5 (Tùy chọn)
- Link tải: https://www.metatrader5.com/
- Cài đặt nếu bạn muốn học về phần mềm giao dịch

## Tóm tắt các bước cài đặt
1. Cài đặt Python 3.x
2. Cài đặt Jupyter Notebook hoặc VS Code
3. Cài đặt các thư viện Python cơ bản bằng pip
4. (Tùy chọn) Cài đặt Postman để test API
5. Cài đặt SQL Server và SQL Server Management Studio
6. Cài đặt Redis
7. (Tùy chọn) Cài đặt MetaTrader 5 nếu muốn học về phần mềm giao dịch 