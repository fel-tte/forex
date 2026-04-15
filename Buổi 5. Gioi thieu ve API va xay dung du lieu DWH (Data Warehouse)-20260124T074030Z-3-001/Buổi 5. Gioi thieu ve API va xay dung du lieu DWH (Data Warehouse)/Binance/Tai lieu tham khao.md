# Hướng dẫn sử dụng Binance API

## 1. Cài đặt thư viện
```bash
pip install ccxt
```

## 2. Tài liệu tham khảo chính thức
1. **CCXT Documentation**
   - Link: https://docs.ccxt.com/
   - Đây là thư viện chính để kết nối với Binance và nhiều sàn khác
   - Có hướng dẫn chi tiết về cách sử dụng API

2. **Binance API Documentation**
   - Link: https://binance-docs.github.io/apidocs/
   - Tài liệu chính thức từ Binance
   - Bao gồm tất cả các endpoints và parameters

## 3. Cách sử dụng cơ bản
```python
import ccxt

# Khởi tạo kết nối với Binance
exchange = ccxt.binance({
    # Không cần API Key và Secret nếu chỉ lấy dữ liệu public
})

# Lấy thông tin thị trường
markets = exchange.load_markets()

# Lấy giá hiện tại
ticker = exchange.fetch_ticker('BTC/USDT')

# Lấy lịch sử giá
ohlcv = exchange.fetch_ohlcv('BTC/USDT', '1d')
```

## 4. Các loại dữ liệu có thể lấy
1. **Dữ liệu thị trường**
   - Giá hiện tại
   - Khối lượng giao dịch
   - Order book
   - Lịch sử giao dịch

2. **Dữ liệu lịch sử**
   - OHLCV (Open, High, Low, Close, Volume)
   - Các khung thời gian: 1m, 5m, 15m, 1h, 4h, 1d, 1w, 1M

3. **Thông tin tài khoản** (cần API Key)
   - Số dư
   - Lịch sử giao dịch
   - Orders

## 5. Các nguồn học tập
1. **GitHub Repositories**
   - CCXT: https://github.com/ccxt/ccxt
   - Binance API: https://github.com/binance/binance-spot-api-docs

2. **Ví dụ và Tutorials**
   - CCXT Examples: https://github.com/ccxt/ccxt/tree/master/examples
   - Binance API Examples: https://github.com/binance/binance-api-postman

3. **Cộng đồng**
   - Stack Overflow: https://stackoverflow.com/questions/tagged/binance-api
   - Reddit: r/binance
   - Telegram Groups

## 6. Lưu ý quan trọng
1. **Rate Limits**
   - Binance có giới hạn số lượng request
   - Cần xử lý rate limit để tránh bị block

2. **Bảo mật**
   - Không chia sẻ API Key và Secret
   - Nên tạo API Key với quyền hạn chế
   - Sử dụng IP whitelist nếu có thể

3. **Xử lý lỗi**
   - Luôn có try-catch khi gọi API
   - Xử lý các trường hợp mất kết nối
   - Kiểm tra dữ liệu trước khi sử dụng

## 7. Ví dụ code đầy đủ
```python
import ccxt
import pandas as pd
from datetime import datetime

def get_binance_data(symbol, timeframe='1d', limit=100):
    """
    Lấy dữ liệu từ Binance
    
    Parameters:
    symbol (str): Cặp giao dịch (ví dụ: 'BTC/USDT')
    timeframe (str): Khung thời gian ('1m', '5m', '1h', '1d', etc.)
    limit (int): Số lượng nến cần lấy
    
    Returns:
    pandas.DataFrame: DataFrame chứa dữ liệu OHLCV
    """
    try:
        # Khởi tạo exchange
        exchange = ccxt.binance()
        
        # Lấy dữ liệu OHLCV
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        
        # Chuyển đổi thành DataFrame
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # Chuyển đổi timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        return df
        
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        return None

# Sử dụng
if __name__ == "__main__":
    # Lấy dữ liệu BTC/USDT
    df = get_binance_data('BTC/USDT', timeframe='1d', limit=30)
    
    if df is not None:
        print("\nDữ liệu BTC/USDT:")
        print(df.head())
        
        # Lưu vào file CSV
        df.to_csv('BTC_USDT_data.csv')
        print("\nĐã lưu dữ liệu vào file BTC_USDT_data.csv")
```

## 8. Tài liệu bổ sung
1. **Sách và Khóa học**
   - "Mastering Python for Finance" - James Ma Weiming
   - "Python for Finance" - Yves Hilpisch
   - Udemy: "Python for Financial Analysis and Algorithmic Trading"

2. **Blogs và Articles**
   - Binance Blog: https://www.binance.com/en/blog
   - Medium: Tìm kiếm "Binance API Python"
   - Towards Data Science: Các bài viết về crypto trading

3. **Tools và Libraries**
   - TA-Lib: Phân tích kỹ thuật
   - Pandas: Xử lý dữ liệu
   - NumPy: Tính toán số học
   - Matplotlib/Plotly: Vẽ biểu đồ 