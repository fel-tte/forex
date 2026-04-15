# Danh sách phần mềm cần cài đặt cho buổi học Python cơ bản

## 1. Python
- **Phiên bản khuyên dùng:** Python 3.11.x (hoặc 3.10.x, 3.9.x đều được)
- **Trang tải:** https://www.python.org/downloads/
- **Hướng dẫn cài đặt:**
  1. Truy cập trang web https://www.python.org/downloads/
  2. Tải phiên bản Python 3.11.x (hoặc 3.10.x, 3.9.x) cho hệ điều hành của bạn (Windows, macOS, Linux)
  3. Mở file cài đặt và chọn "Add Python to PATH" trong quá trình cài đặt
  4. Hoàn tất quá trình cài đặt

## 2. Jupyter Notebook hoặc VS Code
- **Jupyter Notebook:** Để chạy các file `.ipynb` (notebook).
  - Cài qua lệnh: `pip install notebook`
  - Mở Command Prompt (Windows) hoặc Terminal (macOS/Linux) và gõ lệnh: `pip install notebook`
  - Sau khi cài đặt, gõ lệnh `jupyter notebook` để khởi động Jupyter Notebook
- **Visual Studio Code:** Để lập trình Python, hỗ trợ cả notebook và file `.py`.
  - Trang tải: https://code.visualstudio.com/
  - Tải và cài đặt VS Code
  - Mở VS Code, vào phần Extensions (biểu tượng hình vuông ở thanh bên trái) và cài đặt các extension:
    - Python (Microsoft)
    - Jupyter (Microsoft)

## 3. Các thư viện Python cơ bản (cài qua pip)
- **numpy:** Thư viện tính toán số học
- **pandas:** Thư viện xử lý dữ liệu dạng bảng
- **matplotlib:** Thư viện vẽ biểu đồ
- **yfinance:** Thư viện lấy dữ liệu tài chính
- **metatrader5:** Thư viện giao tiếp với phần mềm MT5 (dùng cho buổi sau)
- **scikit-learn:** Thư viện phân tích dữ liệu và học máy
- **sqlalchemy, pyodbc:** Thư viện làm việc với cơ sở dữ liệu (dùng cho buổi sau)

**Cài đặt nhanh các thư viện cơ bản:**
```sh
pip install numpy pandas matplotlib yfinance scikit-learn
```

## 4. (Tùy chọn) MetaTrader 5
- Nếu bạn học phần giao tiếp với phần mềm giao dịch, cần cài MetaTrader 5: https://www.metatrader5.com/
- **Hướng dẫn cài đặt:**
  1. Truy cập trang web https://www.metatrader5.com/
  2. Tải phiên bản MetaTrader 5 cho hệ điều hành của bạn
  3. Cài đặt và đăng ký tài khoản demo để thực hành

---

**Tóm lại:**  
- Cài Python 3.x  
- Cài Jupyter Notebook hoặc VS Code  
- Cài các thư viện Python cơ bản bằng pip  
- (Tùy chọn) Cài MetaTrader 5 nếu học về giao dịch tự động 