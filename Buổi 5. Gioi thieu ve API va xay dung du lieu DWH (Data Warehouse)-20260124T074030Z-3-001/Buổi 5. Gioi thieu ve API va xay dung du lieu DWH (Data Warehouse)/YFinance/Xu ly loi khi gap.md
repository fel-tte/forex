# Xử lý lỗi YFRateLimitError trong yfinance

## Lỗi YFRateLimitError là gì?
YFRateLimitError là lỗi xảy ra khi bạn gửi quá nhiều request đến Yahoo Finance API trong một khoảng thời gian ngắn. Yahoo Finance có giới hạn về số lượng request để bảo vệ server của họ.

## Nguyên nhân
1. Gửi quá nhiều request trong thời gian ngắn
2. Tải dữ liệu cho nhiều mã chứng khoán cùng lúc
3. Tải dữ liệu với khoảng thời gian quá nhỏ (ví dụ: 1m, 5m)
4. Không có delay giữa các request

## Cách xử lý

### 1. Thêm delay giữa các request
```python
import yfinance as yf
import time

def get_stock_data_with_delay(ticker, start_date, end_date, interval='1d', delay=1):
    """
    Lấy dữ liệu với delay giữa các request
    
    Parameters:
    ticker (str): Mã cổ phiếu
    start_date (str): Ngày bắt đầu
    end_date (str): Ngày kết thúc
    interval (str): Khoảng thời gian
    delay (int): Thời gian delay giữa các request (giây)
    """
    try:
        data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
        time.sleep(delay)  # Delay giữa các request
        return data
    except Exception as e:
        print(f"Lỗi khi lấy dữ liệu cho {ticker}: {str(e)}")
        return None
```

### 2. Sử dụng try-except và retry
```python
import yfinance as yf
import time
from datetime import datetime, timedelta

def get_stock_data_with_retry(ticker, start_date, end_date, interval='1d', max_retries=3, delay=2):
    """
    Lấy dữ liệu với cơ chế retry khi gặp lỗi
    
    Parameters:
    ticker (str): Mã cổ phiếu
    start_date (str): Ngày bắt đầu
    end_date (str): Ngày kết thúc
    interval (str): Khoảng thời gian
    max_retries (int): Số lần thử lại tối đa
    delay (int): Thời gian delay giữa các lần thử (giây)
    """
    for attempt in range(max_retries):
        try:
            data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
            return data
        except Exception as e:
            if "YFRateLimitError" in str(e):
                print(f"Lần thử {attempt + 1}/{max_retries}: Gặp lỗi rate limit. Đợi {delay} giây...")
                time.sleep(delay)
                delay *= 2  # Tăng thời gian delay sau mỗi lần thử
            else:
                print(f"Lỗi khác: {str(e)}")
                return None
    return None
```

### 3. Chia nhỏ khoảng thời gian
```python
def get_stock_data_in_chunks(ticker, start_date, end_date, interval='1d', chunk_size=30):
    """
    Lấy dữ liệu bằng cách chia nhỏ khoảng thời gian
    
    Parameters:
    ticker (str): Mã cổ phiếu
    start_date (str): Ngày bắt đầu
    end_date (str): Ngày kết thúc
    interval (str): Khoảng thời gian
    chunk_size (int): Số ngày trong mỗi chunk
    """
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    all_data = []
    current_start = start
    
    while current_start < end:
        current_end = min(current_start + timedelta(days=chunk_size), end)
        
        try:
            chunk_data = yf.download(ticker, 
                                   start=current_start.strftime('%Y-%m-%d'),
                                   end=current_end.strftime('%Y-%m-%d'),
                                   interval=interval)
            all_data.append(chunk_data)
            time.sleep(1)  # Delay giữa các chunk
        except Exception as e:
            print(f"Lỗi khi lấy dữ liệu chunk {current_start} - {current_end}: {str(e)}")
        
        current_start = current_end
    
    return pd.concat(all_data) if all_data else None
```

## Các biện pháp phòng tránh

1. **Sử dụng khoảng thời gian lớn hơn**
   - Tránh sử dụng interval quá nhỏ (1m, 5m) nếu không cần thiết
   - Ưu tiên sử dụng interval 1d, 1wk, 1mo

2. **Lưu cache dữ liệu**
   - Lưu dữ liệu đã tải vào file CSV hoặc database
   - Chỉ tải dữ liệu mới khi cần thiết

3. **Sử dụng proxy hoặc VPN**
   - Thay đổi IP để tránh bị giới hạn
   - Sử dụng nhiều proxy khác nhau

4. **Tối ưu hóa request**
   - Gộp nhiều request thành một request lớn
   - Sử dụng batch processing
   - Tránh lặp lại các request không cần thiết

## Ví dụ sử dụng

```python
# Ví dụ 1: Lấy dữ liệu với delay
data = get_stock_data_with_delay('AAPL', '2024-01-01', '2024-03-15', delay=2)

# Ví dụ 2: Lấy dữ liệu với retry
data = get_stock_data_with_retry('AAPL', '2024-01-01', '2024-03-15', max_retries=3)

# Ví dụ 3: Lấy dữ liệu theo chunks
data = get_stock_data_in_chunks('AAPL', '2024-01-01', '2024-03-15', chunk_size=30)
```

## Lưu ý quan trọng
1. Luôn xử lý lỗi một cách graceful
2. Thêm logging để theo dõi các lỗi
3. Cân nhắc sử dụng các nguồn dữ liệu thay thế
4. Tuân thủ điều khoản sử dụng của Yahoo Finance
5. Không spam request để tránh bị block IP 