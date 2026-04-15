import pandas as pd
import plotly.graph_objects as go
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import talib

# ##############################################Step 0: Lấy dữ liệu mẫu##############################################
# Sử dụng yfinance để lấy dữ liệu mẫu (không cần API SSI)
symbol = 'AAPL'  # Apple stock
from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
to_date = datetime.now().strftime('%Y-%m-%d')

# Lấy dữ liệu
data = yf.download(symbol, start=from_date, end=to_date)
print("Dữ liệu gốc:")
print(data.head())

# ##############################################Step 1: Tính toán chỉ báo##############################################
# Tính toán SMA
window1 = 6
window2 = 10
data['SMA6'] = talib.SMA(data['Close'], timeperiod=window1)
data['SMA10'] = talib.SMA(data['Close'], timeperiod=window2)

# Tạo tín hiệu mua/bán
data['Buy_Signal'] = (data['SMA6'] >= data['SMA10'])
data['Sell_Signal'] = (data['SMA6'] <= data['SMA10'])

# Tạo cột giá cho tín hiệu mua/bán (QUAN TRỌNG: Sử dụng giá Close thực tế)
data['Buy_Price'] = np.where(data['Buy_Signal'], data['Close'], np.nan)
data['Sell_Price'] = np.where(data['Sell_Signal'], data['Close'], np.nan)

print("\nDữ liệu sau khi xử lý:")
print(data[['Close', 'SMA6', 'SMA10', 'Buy_Signal', 'Sell_Signal', 'Buy_Price', 'Sell_Price']].tail(10))

# ##############################################Step 2: Vẽ biểu đồ##############################################
fig = go.Figure()

# Thêm đường giá và SMA
fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close', line=dict(color='black')))
fig.add_trace(go.Scatter(x=data.index, y=data['SMA6'], mode='lines', name='SMA6', line=dict(color='blue')))
fig.add_trace(go.Scatter(x=data.index, y=data['SMA10'], mode='lines', name='SMA10', line=dict(color='orange')))

# Thêm tín hiệu mua (hình tam giác xanh hướng lên)
fig.add_trace(go.Scatter(
    x=data.index, 
    y=data['Buy_Price'], 
    mode='markers', 
    name='Buy Signal', 
    marker=dict(
        symbol='triangle-up', 
        size=12, 
        color='green',
        line=dict(color='darkgreen', width=1)
    )
))

# Thêm tín hiệu bán (hình tam giác đỏ hướng xuống)
fig.add_trace(go.Scatter(
    x=data.index, 
    y=data['Sell_Price'], 
    mode='markers', 
    name='Sell Signal', 
    marker=dict(
        symbol='triangle-down', 
        size=12, 
        color='red',
        line=dict(color='darkred', width=1)
    )
))

# Cập nhật layout
fig.update_layout(
    title=f'Chiến lược SMA cho {symbol}',
    xaxis_title='Ngày',
    yaxis_title='Giá ($)',
    showlegend=True,
    hovermode='x unified'
)

# Hiển thị biểu đồ
fig.show()

print("\nGiải thích:")
print("- Hình tam giác xanh hướng lên: Tín hiệu mua (SMA6 >= SMA10)")
print("- Hình tam giác đỏ hướng xuống: Tín hiệu bán (SMA6 <= SMA10)")
print("- Đường xanh: SMA6")
print("- Đường cam: SMA10")
print("- Đường đen: Giá đóng cửa") 