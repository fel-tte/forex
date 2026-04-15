# # Bài tập: Nhập vào 1 giá trị, nếu giá trị đó là "buy" thì in ra màn hình "Hãy mua đi"

# # Nhập giá trị từ người dùng
# gia_tri = input("Nhập vào một giá trị: ")

# # Kiểm tra nếu giá trị là "buy"
# if gia_tri == "buy":
#     print("Hãy mua đi")
# else:
#     print("Không phải lệnh buy")


##########################################################################

# # Lấy giá BTC 1 phút, nếu giá < 115000 thì Mua, ngược lại Bán
# # Enhance: Cho chạy 1 phút 1 lần

# import ccxt # pip install ccxt
# import time
# from datetime import datetime

# # Tạo kết nối với Binance
# binance = ccxt.binance()

# print("=== BOT TRADING BTC ===")
# print("Quy tắc: Giá < 115000 USDT = MUA, Giá >= 115000 USDT = BÁN")
# print("Chạy mỗi 1 phút...\n")

# # Chạy mỗi 1 phút
# while True:
#     try:
#         # Lấy thời gian hiện tại
#         now = datetime.now()
#         time_str = now.strftime("%H:%M:%S")
        
#         # Lấy giá BTC từ Binance
#         ticker = binance.fetch_ticker('BTC/USDT')
#         btc_price = ticker['last']
        
#         print(f"[{time_str}] Giá BTC: ${btc_price:,.2f} USDT")
        
#         # So sánh giá và đưa ra quyết định
#         if btc_price < 115000:
#             print("🎯 QUYẾT ĐỊNH: MUA BTC")
#             print("Lý do: Giá < 115,000 USDT")
#         else:
#             print("🎯 QUYẾT ĐỊNH: BÁN BTC")
#             print("Lý do: Giá >= 115,000 USDT")
        
#         print("-" * 50)
        
#         # Chờ 60 giây (1 phút)
#         time.sleep(60)
        
#     except Exception as e:
#         print(f"Lỗi: {e}")
#         time.sleep(60)

##########################################################################

# Lay gia BTC 1m cua 10 san Crypto lon
# - List: 10 san Crypto lon: API, tay
# - For: Lay gia BTC 1m cua tung san
# - In ra man hinh
import ccxt
import time
from datetime import datetime
listSan = ['binance', 'okx', 'bingx', 'huobi', 'gate', 'bitget', 'bitfinex', 'bitstamp', 'kraken', 'coinex', 'mexc']    

for san in listSan:
    try:
        # Tạo kết nối với từng sàn
        exchange = getattr(ccxt, san)()
        
        # Lấy giá BTC từ sàn đó
        ticker = exchange.fetch_ticker('BTC/USDT')
        price = ticker['last']
        
        print(f"{san.upper()}: ${price:,.2f} USDT")
        time.sleep(1)
        
    except Exception as e:
        print(f"{san.upper()}: Lỗi - {e}")
        time.sleep(1)







# - So sanh gia BTC 1m cua tung san
# - In ra man hinh
