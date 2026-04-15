import sys
sys.path.append('../Common')
import CommonBinanceDWH
import pandas as pd 
from statsmodels.tsa.arima.model import ARIMA
import talib
import plotly.graph_objects as go
import numpy as np

# Load dữ liệu
symbol = 'ETHUSDT'
from_date = '2025-05-01'
to_date = '2025-06-21'
interval = '1d'

data = CommonBinanceDWH.CommonBinanceDWH.loaddataBinance_FromTo_Split(symbol, from_date, to_date, interval)

print("=== THÔNG TIN DỮ LIỆU ===")
print("Shape của data:", data.shape)
print("Columns:", data.columns.tolist())

# Đặt chỉ mục DataFrame với cột 'Datetime'
if 'Datetime' in data.columns:
    data.set_index('Datetime', inplace=True)

# Tính toán tất cả các chỉ báo
print("\n=== TÍNH TOÁN CÁC CHỈ BÁO ===")

# 1. Moving Averages
data['MA5'] = talib.SMA(data['Close'], timeperiod=5)
data['MA10'] = talib.SMA(data['Close'], timeperiod=10)
data['MA20'] = talib.SMA(data['Close'], timeperiod=20)

# 2. Differencing
data['Close_diff'] = data['Close'].diff()
data['Close_diff2'] = data['Close'].diff().diff()  # Second difference

# 3. Returns
data['Returns'] = data['Close'].pct_change()
data['Log_Returns'] = np.log(data['Close'] / data['Close'].shift(1))

# 4. Price changes
data['Price_Change'] = data['Close'] - data['Close'].shift(1)

# 5. RSI
data['RSI'] = talib.RSI(data['Close'], timeperiod=14)

# 6. MACD
data['MACD'], data['MACD_Signal'], data['MACD_Hist'] = talib.MACD(data['Close'])

# 7. Bollinger Bands
data['BB_Upper'], data['BB_Middle'], data['BB_Lower'] = talib.BBANDS(data['Close'])

# 8. Stochastic
data['Stoch_K'], data['Stoch_D'] = talib.STOCH(data['High'], data['Low'], data['Close'])

# Loại bỏ NaN
data_clean = data.dropna()

print(f"Shape sau khi loại bỏ NaN: {data_clean.shape}")
print(f"Số lượng NaN trong từng cột:")
for col in data_clean.columns:
    nan_count = data_clean[col].isna().sum()
    if nan_count > 0:
        print(f"  {col}: {nan_count}")

# Danh sách tất cả các biến để test
variables_to_test = [
    ('Close', 'Giá đóng cửa gốc'),
    ('MA5', 'Moving Average 5'),
    ('MA10', 'Moving Average 10'),
    ('MA20', 'Moving Average 20'),
    ('Close_diff', 'Chênh lệch giá đóng cửa (lần 1)'),
    ('Close_diff2', 'Chênh lệch giá đóng cửa (lần 2)'),
    ('Returns', 'Tỷ suất sinh lợi'),
    ('Log_Returns', 'Tỷ suất sinh lợi logarit'),
    ('Price_Change', 'Thay đổi giá'),
    ('RSI', 'RSI'),
    ('MACD', 'MACD'),
    ('BB_Middle', 'Bollinger Bands Middle'),
    ('Stoch_K', 'Stochastic %K'),
]

# Tham số ARIMA để test
arima_orders = [
    (1, 1, 1),
    (2, 1, 2),
    (1, 0, 1),
    (2, 0, 2),
    (0, 1, 1),
    (1, 1, 0),
]

print("\n=== KẾT QUẢ TEST TẤT CẢ CÁC BIẾN ===")

results = []

for var_name, var_desc in variables_to_test:
    print(f"\n--- TESTING: {var_desc} ({var_name}) ---")
    
    # Kiểm tra dữ liệu
    var_data = data_clean[var_name]
    print(f"  Số lượng NaN: {var_data.isna().sum()}")
    print(f"  Giá trị min: {var_data.min():.6f}")
    print(f"  Giá trị max: {var_data.max():.6f}")
    print(f"  Giá trị cuối: {var_data.iloc[-1]:.6f}")
    
    # Test với các tham số ARIMA khác nhau
    for p, d, q in arima_orders:
        try:
            model = ARIMA(var_data, order=(p, d, q))
            model_fit = model.fit()
            predictions = model_fit.forecast(steps=5)
            
            # Kiểm tra xem predictions có toàn 0 không
            is_all_zero = np.allclose(predictions.values, 0, atol=1e-10)
            is_all_same = np.allclose(predictions.values, predictions.values[0], atol=1e-10)
            
            result = {
                'variable': var_name,
                'description': var_desc,
                'order': (p, d, q),
                'aic': model_fit.aic,
                'predictions': predictions.values,
                'is_all_zero': is_all_zero,
                'is_all_same': is_all_same,
                'prediction_range': predictions.max() - predictions.min(),
                'success': True
            }
            
            results.append(result)
            
            status = "✅" if not is_all_zero and not is_all_same else "❌"
            print(f"  {status} ARIMA{p,d,q}: AIC={model_fit.aic:.2f}, Predictions={predictions.values[:3]}...")
            
        except Exception as e:
            print(f"  ❌ ARIMA{p,d,q}: Lỗi - {str(e)[:50]}...")
            results.append({
                'variable': var_name,
                'description': var_desc,
                'order': (p, d, q),
                'error': str(e),
                'success': False
            })

# Tóm tắt kết quả
print("\n" + "="*80)
print("TÓM TẮT KẾT QUẢ")
print("="*80)

# Nhóm theo biến
for var_name, var_desc in variables_to_test:
    var_results = [r for r in results if r['variable'] == var_name and r['success']]
    
    if var_results:
        print(f"\n📊 {var_desc} ({var_name}):")
        
        # Tìm mô hình tốt nhất (AIC thấp nhất)
        best_result = min(var_results, key=lambda x: x['aic'])
        print(f"  🏆 Mô hình tốt nhất: ARIMA{best_result['order']} (AIC: {best_result['aic']:.2f})")
        
        # Kiểm tra chất lượng predictions
        if best_result['is_all_zero']:
            print(f"  ❌ VẤN ĐỀ: Predictions toàn 0!")
        elif best_result['is_all_same']:
            print(f"  ⚠️  VẤN ĐỀ: Predictions giống nhau!")
        else:
            print(f"  ✅ TỐT: Predictions có ý nghĩa (range: {best_result['prediction_range']:.6f})")
            print(f"     Predictions: {best_result['predictions'][:3]}...")
    else:
        print(f"\n❌ {var_desc} ({var_name}): Không có mô hình nào thành công")

# Tìm top 5 mô hình tốt nhất
print("\n" + "="*80)
print("TOP 5 MÔ HÌNH TỐT NHẤT (AIC THẤP NHẤT)")
print("="*80)

successful_results = [r for r in results if r['success']]
if successful_results:
    top_5 = sorted(successful_results, key=lambda x: x['aic'])[:5]
    
    for i, result in enumerate(top_5, 1):
        status = "✅" if not result['is_all_zero'] and not result['is_all_same'] else "❌"
        print(f"{i}. {status} {result['description']} - ARIMA{result['order']}")
        print(f"   AIC: {result['aic']:.2f}")
        print(f"   Predictions: {result['predictions'][:3]}...")
        print()

# Vẽ biểu đồ với mô hình tốt nhất
print("\n=== VẼ BIỂU ĐỒ MÔ HÌNH TỐT NHẤT ===")

if successful_results:
    # Chọn mô hình tốt nhất không có vấn đề
    good_results = [r for r in successful_results if not r['is_all_zero'] and not r['is_all_same']]
    
    if good_results:
        best_result = min(good_results, key=lambda x: x['aic'])
        
        print(f"Sử dụng mô hình: {best_result['description']} - ARIMA{best_result['order']}")
        
        # Tạo biểu đồ
        fig = go.Figure()
        
        # Dữ liệu gốc
        var_data = data_clean[best_result['variable']]
        fig.add_trace(go.Scatter(
            x=var_data.index, 
            y=var_data.values, 
            mode='lines', 
            name=f'{best_result["description"]} (Gốc)'
        ))
        
        # Dự đoán
        pred_dates = pd.date_range(start=var_data.index[-1], periods=6, freq='D')[1:]
        fig.add_trace(go.Scatter(
            x=pred_dates, 
            y=best_result['predictions'], 
            mode='lines+markers', 
            name='Dự Đoán',
            line=dict(color='red')
        ))
        
        fig.update_layout(
            title=f'Dự Đoán {best_result["description"]} - ARIMA{best_result["order"]}',
            xaxis_title='Thời Gian',
            yaxis_title=best_result['description'],
            hovermode='x unified'
        )
        
        fig.show()
        print("✅ Biểu đồ đã được hiển thị!")
    else:
        print("❌ Không có mô hình nào cho predictions có ý nghĩa!")
else:
    print("❌ Không có mô hình nào thành công!")

print("\n" + "="*80)
print("KẾT LUẬN")
print("="*80)
print("1. Close, MA5, MA10, MA20: Thường cho kết quả tốt")
print("2. Close_diff, Returns, Log_Returns: Có thể cho kết quả tốt với d=0")
print("3. RSI, MACD, Stochastic: Có thể khó dự đoán do tính chất dao động")
print("4. Tham số ARIMA(1,1,1) và ARIMA(2,1,2) thường hoạt động tốt")
print("5. Luôn kiểm tra predictions có ý nghĩa hay không!")

