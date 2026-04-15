import ccxt
import time
from datetime import datetime

print("K13")
print("I Love You")

# Tạo kết nối với các sàn
binance = ccxt.binance()
coinbase = ccxt.coinbase()
mexc = ccxt.mexc()

# So sánh giá BTC mỗi 5 giây
while True:
    try:
        # Lấy thời gian hiện tại
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        
        print(f"\n=== [{time_str}] So sánh giá BTC ===")
        
        # Lấy giá từ Binance
        binance_ticker = binance.fetch_ticker('BTC/USDT')
        binance_price = binance_ticker['last']
        print(f"Binance:  ${binance_price:,.2f} USDT")
        
        # Lấy giá từ Coinbase
        coinbase_ticker = coinbase.fetch_ticker('BTC/USD')
        coinbase_price = coinbase_ticker['last']
        print(f"Coinbase: ${coinbase_price:,.2f} USD")
        
        # Lấy giá từ MEXC
        mexc_ticker = mexc.fetch_ticker('BTC/USDT')
        mexc_price = mexc_ticker['last']
        print(f"MEXC:     ${mexc_price:,.2f} USDT")
        
        # Tìm giá cao nhất và thấp nhất
        prices = [binance_price, mexc_price]
        max_price = max(prices)
        min_price = min(prices)
        spread = max_price - min_price
        
        print(f"Chênh lệch: ${spread:.2f} USDT")
        
        time.sleep(5)  # Chờ 5 giây
        
    except Exception as e:
        print(f"Lỗi: {e}")
        time.sleep(5)
