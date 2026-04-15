# Tài liệu tham khảo về yfinance

## 1. Tài liệu chính thức
- GitHub Repository: https://github.com/ranaroussi/yfinance
- Documentation: https://pypi.org/project/yfinance/

## 2. Hướng dẫn nhanh và ví dụ
- Quick Start Guide: https://pypi.org/project/yfinance/#quick-start
- Examples: https://github.com/ranaroussi/yfinance/tree/main/examples

## 3. API Reference
- Ticker Class: https://pypi.org/project/yfinance/#ticker
- Download Function: https://pypi.org/project/yfinance/#download

## 4. Bài viết hướng dẫn chi tiết
- Medium: https://medium.com/@ranaroussi/yfinance-python-tutorial-15d061a7f532
- Towards Data Science: https://towardsdatascience.com/how-to-get-stock-data-using-python-c0de1df17e75

## 5. Stack Overflow
- Có nhiều câu hỏi và trả lời hữu ích về yfinance
- Link: https://stackoverflow.com/questions/tagged/yfinance

## 6. Video hướng dẫn
- YouTube Tutorials: https://www.youtube.com/results?search_query=yfinance+python+tutorial

## 7. Blog chuyên về tài chính
- Quantopian: https://www.quantopian.com/
- Alpha Vantage: https://www.alphavantage.co/

## 8. Tài liệu Yahoo Finance API
- Yahoo Finance API Documentation: https://finance.yahoo.com/apis
- Yahoo Finance API Guide: https://developer.yahoo.com/finance/

## 9. Khóa học online
- Udemy: https://www.udemy.com/
- Coursera: https://www.coursera.org/
- DataCamp: https://www.datacamp.com/

## 10. Diễn đàn và cộng đồng
- Reddit r/algotrading
- GitHub Discussions
- Python Discord

## Cách tìm kiếm thông tin
Khi cần tìm hiểu về một hàm cụ thể hoặc cách sử dụng yfinance:
1. Đọc tài liệu chính thức trên GitHub
2. Tìm kiếm trên Stack Overflow
3. Xem các ví dụ trong repository
4. Tham khảo các bài viết trên Medium hoặc Towards Data Science

## Các hàm chính của yfinance

### 1. Lấy dữ liệu OHLC cơ bản
```python
import yfinance as yf

# Cách 1: Sử dụng yf.download()
data = yf.download(ticker, start="2024-01-01", end="2024-03-15", interval="1d")

# Cách 2: Sử dụng Ticker object
ticker = yf.Ticker("AAPL")
data = ticker.history(period="1y", interval="1d")
```

### 2. Các tham số quan trọng
- `period`: Khoảng thời gian
  - '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'
- `interval`: Khoảng thời gian giữa các điểm dữ liệu
  - '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'
- `start`: Ngày bắt đầu (format: 'YYYY-MM-DD')
- `end`: Ngày kết thúc (format: 'YYYY-MM-DD')

### 3. Các hàm bổ sung
```python
ticker = yf.Ticker("AAPL")

# Lấy thông tin cơ bản về công ty
info = ticker.info

# Lấy báo cáo tài chính
financials = ticker.financials

# Lấy danh sách cổ đông lớn
major_holders = ticker.major_holders

# Lấy danh sách tổ chức đầu tư
institutional_holders = ticker.institutional_holders

# Lấy thông tin về cổ tức và tách cổ phiếu
actions = ticker.actions
dividends = ticker.dividends
splits = ticker.splits
```

## Lưu ý quan trọng
1. Đối với cổ phiếu Việt Nam, cần thêm hậu tố `.VN` (ví dụ: 'VCB.VN')
2. Có giới hạn về số lượng request (rate limit), cần xử lý lỗi khi gặp "Too Many Requests"
3. Dữ liệu có thể bị trễ so với thời gian thực
4. Một số mã chứng khoán có thể không có sẵn trên Yahoo Finance 