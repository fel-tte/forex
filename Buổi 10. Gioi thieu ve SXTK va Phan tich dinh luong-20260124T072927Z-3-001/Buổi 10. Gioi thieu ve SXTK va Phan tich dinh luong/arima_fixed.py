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

# Kiểm tra dữ liệu Close
print("\n=== KIỂM TRA DỮ LIỆU CLOSE ===")
print("Số lượng NaN trong Close:", data['Close'].isna().sum())
print("Giá trị min của Close:", data['Close'].min())
print("Giá trị max của Close:", data['Close'].max())
print("Giá trị cuối cùng của Close:", data['Close'].iloc[-1])

# Đặt chỉ mục DataFrame với cột 'Datetime' có dữ liệu kiểu datetime
if 'Datetime' not in data.columns:
    print("Cột 'Datetime' không tồn tại trong DataFrame!")
else:
    data.set_index('Datetime', inplace=True)

# Buoc 1: Xay dung mo hinh
# Tính MA5 để so sánh
data['MA5'] = talib.SMA(data['Close'], timeperiod=5)

print("\n=== KIỂM TRA MA5 ===")
print("Số lượng NaN trong MA5:", data['MA5'].isna().sum())
print("Giá trị cuối cùng của MA5:", data['MA5'].iloc[-1])

# Loại bỏ NaN từ MA5 nếu cần
data_clean = data.dropna(subset=['MA5'])
print("\n=== SAU KHI LOẠI BỎ NAN ===")
print("Shape của data_clean:", data_clean.shape)

# SỬA LỖI: Sử dụng Close thay vì MA5 và tham số ARIMA phù hợp
print("\n=== HUẤN LUYỆN MÔ HÌNH ARIMA ===")

# Thử nghiệm với các tham số khác nhau
models_to_try = [
    ("ARIMA(1,1,1) với Close", data_clean['Close'], (1, 1, 1)),
    ("ARIMA(2,1,2) với Close", data_clean['Close'], (2, 1, 2)),
    ("ARIMA(1,1,1) với MA5", data_clean['MA5'], (1, 1, 1)),
]

best_model = None
best_predictions = None
best_aic = float('inf')
best_name = ""

for name, data_series, order in models_to_try:
    try:
        print(f"\nThử nghiệm: {name}")
        model = ARIMA(data_series, order=order)
        model_fit = model.fit()
        predictions = model_fit.forecast(steps=10)
        
        print(f"AIC: {model_fit.aic}")
        print(f"Predictions: {predictions.values}")
        
        if model_fit.aic < best_aic:
            best_aic = model_fit.aic
            best_model = model_fit
            best_predictions = predictions
            best_name = name
            
    except Exception as e:
        print(f"Lỗi với {name}: {e}")

print(f"\n=== MÔ HÌNH TỐT NHẤT ===")
print(f"Model: {best_name}")
print(f"AIC: {best_aic}")
print(f"Predictions: {best_predictions.values}")

# Vẽ biểu đồ với mô hình tốt nhất
print("\n=== VẼ BIỂU ĐỒ ===")

# Tạo dãy ngày cho các dự đoán
pred_dates = pd.date_range(start=data_clean.index[-1], periods=11, freq='D')[1:]

# Tạo biểu đồ
fig = go.Figure()

# Thêm dữ liệu giá đóng cửa gốc vào biểu đồ
fig.add_trace(go.Scatter(
    x=data_clean.index, 
    y=data_clean['Close'], 
    mode='lines', 
    name='Giá Đóng Cửa Gốc'
))

# Thêm dữ liệu dự đoán vào biểu đồ
fig.add_trace(go.Scatter(
    x=pred_dates, 
    y=best_predictions, 
    mode='lines+markers', 
    name='Dự Đoán',
    line=dict(color='red')
))

# Định cấu hình layout của biểu đồ
fig.update_layout(
    title=f'Dự Đoán Giá Cả Sử Dụng {best_name}',
    xaxis_title='Thời Gian',
    yaxis_title='Giá Đóng Cửa',
    hovermode='x unified'
)

# Hiển thị biểu đồ
fig.show()

print("\n=== KẾT LUẬN ===")
print("Nguyên nhân predictions = 0:")
print("1. Sử dụng data['MA5'] thay vì data['Close']")
print("2. MA5 có nhiều giá trị NaN ở đầu")
print("3. Tham số ARIMA(4,1,3) không phù hợp")
print("\nGiải pháp:")
print("1. Sử dụng data['Close'] thay vì data['MA5']")
print("2. Sử dụng tham số ARIMA(1,1,1) hoặc ARIMA(2,1,2)")
print("3. Loại bỏ NaN trước khi huấn luyện")

