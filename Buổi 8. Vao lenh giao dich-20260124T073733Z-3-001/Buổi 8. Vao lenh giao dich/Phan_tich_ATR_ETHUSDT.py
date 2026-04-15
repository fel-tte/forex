import pandas as pd
import ccxt
import talib
import numpy as np
from datetime import datetime, timedelta

def loaddataBinance_FromTo(symbol, from_date, to_date, timeframe):
    # Khởi tạo kết nối đến sàn Binance
    exchange = ccxt.binance()
    
    # Định dạng ngày tháng
    since = exchange.parse8601(from_date + 'T00:00:00Z')
    end = exchange.parse8601(to_date + 'T00:00:00Z')
    
    # Lấy dữ liệu thị trường từ sàn Binance
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=1000)
    
    # Chuyển dữ liệu thành DataFrame
    data = pd.DataFrame(ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    data['Timestamp'] = pd.to_datetime(data['Timestamp'], unit='ms')         
    data = data.rename(columns={'Timestamp': 'Datetime'})
    
    return data

# Lấy dữ liệu ETHUSDT
symbol = 'ETHUSDT'
from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')  # Lấy 7 ngày gần đây
to_date = (datetime.now() + timedelta(days=0)).strftime('%Y-%m-%d')
timeframe = '1m'

print("Đang tải dữ liệu ETHUSDT...")
data = loaddataBinance_FromTo(symbol, from_date, to_date, timeframe)

# Tính toán ATR
atr_period = 14
atr_threshold = 40
data['ATR'] = talib.ATR(data['High'], data['Low'], data['Close'], timeperiod=atr_period)

print("=== PHÂN TÍCH ATR CHO ETHUSDT ===")
print(f"Thống kê ATR của {symbol}:")
print(f"ATR trung bình: {data['ATR'].mean():.2f}")
print(f"ATR tối thiểu: {data['ATR'].min():.2f}")
print(f"ATR tối đa: {data['ATR'].max():.2f}")
print(f"ATR median: {data['ATR'].median():.2f}")
print(f"ATR std: {data['ATR'].std():.2f}")

print(f"\n=== ĐÁNH GIÁ ATR_THRESHOLD = {atr_threshold} ===")
print(f"Số điểm dữ liệu có ATR <= {atr_threshold}: {len(data[data['ATR'] <= atr_threshold])}")
print(f"Số điểm dữ liệu có ATR > {atr_threshold}: {len(data[data['ATR'] > atr_threshold])}")
print(f"Tỷ lệ ATR <= {atr_threshold}: {len(data[data['ATR'] <= atr_threshold])/len(data)*100:.2f}%")
print(f"Tỷ lệ ATR > {atr_threshold}: {len(data[data['ATR'] > atr_threshold])/len(data)*100:.2f}%")

# Phân tích percentiles
percentiles = [10, 25, 50, 75, 90, 95, 99]
print(f"\n=== PHÂN VỊ ATR ===")
for p in percentiles:
    value = data['ATR'].quantile(p/100)
    print(f"Percentile {p}%: {value:.2f}")

# Đề xuất ngưỡng ATR phù hợp
print(f"\n=== ĐỀ XUẤT ATR_THRESHOLD ===")
print(f"Để có 80% tín hiệu mua: ATR threshold ≈ {data['ATR'].quantile(0.8):.2f}")
print(f"Để có 90% tín hiệu mua: ATR threshold ≈ {data['ATR'].quantile(0.9):.2f}")
print(f"Để có 95% tín hiệu mua: ATR threshold ≈ {data['ATR'].quantile(0.95):.2f}")

# So sánh với giá hiện tại
current_price = data['Close'].iloc[-1]
atr_percentage = (data['ATR'].mean() / current_price) * 100
print(f"\n=== TỶ LỆ ATR SO VỚI GIÁ ===")
print(f"Giá hiện tại ETHUSDT: ${current_price:.2f}")
print(f"ATR trung bình: ${data['ATR'].mean():.2f}")
print(f"ATR trung bình (% giá): {atr_percentage:.2f}%")
print(f"ATR threshold {atr_threshold} (% giá): {(atr_threshold/current_price)*100:.2f}%")

# Đánh giá
print(f"\n=== KẾT LUẬN ===")
if atr_threshold > data['ATR'].quantile(0.95):
    print(f"❌ ATR threshold = {atr_threshold} QUÁ CAO!")
    print(f"   - Chỉ {len(data[data['ATR'] > atr_threshold])/len(data)*100:.1f}% dữ liệu vượt ngưỡng này")
    print(f"   - Hầu hết thời gian sẽ có tín hiệu mua, ít tín hiệu bán")
elif atr_threshold < data['ATR'].quantile(0.25):
    print(f"❌ ATR threshold = {atr_threshold} QUÁ THẤP!")
    print(f"   - {len(data[data['ATR'] <= atr_threshold])/len(data)*100:.1f}% dữ liệu dưới ngưỡng này")
    print(f"   - Hầu hết thời gian sẽ có tín hiệu bán, ít tín hiệu mua")
else:
    print(f"✅ ATR threshold = {atr_threshold} CÓ VẺ PHÙ HỢP")
    print(f"   - Cân bằng giữa tín hiệu mua và bán")
    print(f"   - Nằm trong khoảng hợp lý của phân phối ATR")

# Đề xuất cải thiện
suggested_threshold = data['ATR'].quantile(0.8)
print(f"\n=== ĐỀ XUẤT CẢI THIỆN ===")
print(f"Đề xuất ATR threshold: {suggested_threshold:.2f}")
print(f"Lý do: Đảm bảo 80% thời gian có tín hiệu mua, 20% thời gian có tín hiệu bán")
print(f"Điều này sẽ tạo ra chiến lược cân bằng hơn")

# Phân tích thêm về volatility của ETHUSDT
print(f"\n=== PHÂN TÍCH VOLATILITY ETHUSDT ===")
print(f"ETHUSDT thường có volatility cao hơn các asset khác")
print(f"Trong thị trường crypto, ATR thường dao động từ 0.5% đến 5% giá")
print(f"Với ETHUSDT hiện tại:")
print(f"  - ATR trung bình: {atr_percentage:.2f}% giá")
print(f"  - ATR threshold {atr_threshold} tương đương: {(atr_threshold/current_price)*100:.2f}% giá")

# So sánh với các ngưỡng thông dụng
print(f"\n=== SO SÁNH VỚI NGƯỠNG THÔNG DỤNG ===")
print(f"Ngưỡng thấp (0.5% giá): {(current_price * 0.005):.2f}")
print(f"Ngưỡng trung bình (1% giá): {(current_price * 0.01):.2f}")
print(f"Ngưỡng cao (2% giá): {(current_price * 0.02):.2f}")
print(f"Ngưỡng rất cao (5% giá): {(current_price * 0.05):.2f}")

if (atr_threshold/current_price)*100 > 5:
    print(f"⚠️  ATR threshold = {atr_threshold} tương đương {(atr_threshold/current_price)*100:.2f}% giá - RẤT CAO!")
    print(f"   - Chỉ phù hợp cho thị trường cực kỳ biến động")
elif (atr_threshold/current_price)*100 > 2:
    print(f"⚠️  ATR threshold = {atr_threshold} tương đương {(atr_threshold/current_price)*100:.2f}% giá - CAO!")
    print(f"   - Phù hợp cho thị trường biến động mạnh")
elif (atr_threshold/current_price)*100 > 1:
    print(f"✅ ATR threshold = {atr_threshold} tương đương {(atr_threshold/current_price)*100:.2f}% giá - PHÙ HỢP!")
    print(f"   - Mức biến động trung bình cho crypto")
else:
    print(f"✅ ATR threshold = {atr_threshold} tương đương {(atr_threshold/current_price)*100:.2f}% giá - THẤP!")
    print(f"   - Phù hợp cho thị trường ít biến động") 