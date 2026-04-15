import sys
sys.path.append('../Common')
import CommonBinanceDWH
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import talib
import plotly.graph_objects as go

# Load dữ liệu
symbol = 'ETHUSDT'
from_date = '2025-05-01'
to_date = '2025-06-21'
interval = '1d'

data = CommonBinanceDWH.CommonBinanceDWH.loaddataBinance_FromTo_Split(symbol, from_date, to_date, interval)

print("=== THÔNG TIN DỮ LIỆU ===")
print("Shape của data:", data.shape)
print("Columns:", data.columns.tolist())
print("Dữ liệu đầu:", data.head())
print("Dữ liệu cuối:", data.tail())

# Kiểm tra dữ liệu Close
print("\n=== KIỂM TRA DỮ LIỆU CLOSE ===")
print("Số lượng NaN trong Close:", data['Close'].isna().sum())
print("Giá trị min của Close:", data['Close'].min())
print("Giá trị max của Close:", data['Close'].max())
print("Giá trị cuối cùng của Close:", data['Close'].iloc[-1])

# Tính MA5
data['MA5'] = talib.SMA(data['Close'], timeperiod=5)
print("\n=== KIỂM TRA MA5 ===")
print("Số lượng NaN trong MA5:", data['MA5'].isna().sum())
print("Giá trị cuối cùng của MA5:", data['MA5'].iloc[-1])

# Loại bỏ NaN
data_clean = data.dropna(subset=['MA5'])
print("\n=== SAU KHI LOẠI BỎ NAN ===")
print("Shape của data_clean:", data_clean.shape)

# Thử nghiệm với các tham số ARIMA khác nhau
print("\n=== THỬ NGHIỆM ARIMA ===")

# Thử 1: ARIMA với Close
try:
    model1 = ARIMA(data_clean['Close'], order=(1, 1, 1))
    model_fit1 = model1.fit()
    predictions1 = model_fit1.forecast(steps=10)
    print("ARIMA(1,1,1) với Close - Predictions:", predictions1.values)
    print("AIC:", model_fit1.aic)
except Exception as e:
    print("Lỗi ARIMA(1,1,1) với Close:", e)

# Thử 2: ARIMA với MA5
try:
    model2 = ARIMA(data_clean['MA5'], order=(1, 1, 1))
    model_fit2 = model2.fit()
    predictions2 = model_fit2.forecast(steps=10)
    print("ARIMA(1,1,1) với MA5 - Predictions:", predictions2.values)
    print("AIC:", model_fit2.aic)
except Exception as e:
    print("Lỗi ARIMA(1,1,1) với MA5:", e)

# Thử 3: ARIMA với differencing thủ công
try:
    data_clean['Close_diff'] = data_clean['Close'].diff().dropna()
    model3 = ARIMA(data_clean['Close_diff'], order=(1, 0, 1))
    model_fit3 = model3.fit()
    predictions3 = model_fit3.forecast(steps=10)
    print("ARIMA(1,0,1) với Close_diff - Predictions:", predictions3.values)
    print("AIC:", model_fit3.aic)
except Exception as e:
    print("Lỗi ARIMA(1,0,1) với Close_diff:", e)

# Thử 4: ARIMA với tham số khác
try:
    model4 = ARIMA(data_clean['Close'], order=(2, 1, 2))
    model_fit4 = model4.fit()
    predictions4 = model_fit4.forecast(steps=10)
    print("ARIMA(2,1,2) với Close - Predictions:", predictions4.values)
    print("AIC:", model_fit4.aic)
except Exception as e:
    print("Lỗi ARIMA(2,1,2) với Close:", e)

# Vẽ biểu đồ với dự đoán tốt nhất
print("\n=== VẼ BIỂU ĐỒ ===")
try:
    # Sử dụng model tốt nhất (thường là model1)
    model_fit = model_fit1
    predictions = predictions1
    
    # Tạo dãy ngày cho dự đoán
    pred_dates = pd.date_range(start=data_clean.index[-1], periods=11, freq='D')[1:]
    
    # Vẽ biểu đồ
    fig = go.Figure()
    
    # Dữ liệu gốc
    fig.add_trace(go.Scatter(
        x=data_clean.index, 
        y=data_clean['Close'], 
        mode='lines', 
        name='Giá Đóng Cửa Gốc'
    ))
    
    # Dự đoán
    fig.add_trace(go.Scatter(
        x=pred_dates, 
        y=predictions, 
        mode='lines+markers', 
        name='Dự Đoán',
        line=dict(color='red')
    ))
    
    fig.update_layout(
        title='Dự Đoán Giá Cả Sử Dụng Mô Hình ARIMA',
        xaxis_title='Thời Gian',
        yaxis_title='Giá Đóng Cửa',
        hovermode='x unified'
    )
    
    fig.show()
    print("Biểu đồ đã được hiển thị!")
    
except Exception as e:
    print("Lỗi khi vẽ biểu đồ:", e)
