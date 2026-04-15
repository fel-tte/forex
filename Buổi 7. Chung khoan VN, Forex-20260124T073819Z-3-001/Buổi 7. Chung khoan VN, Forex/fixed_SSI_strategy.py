import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import talib 

# Import hàm loaddataSSI từ file notebook
def loaddataSSI(symbol, from_date, to_date):
    # Import các module cần thiết
    from ssi_fc_data import fc_md_client, model
    from datetime import datetime
    import pandas as pd
    import json
    import configDataSSI

    # Sử dụng datetime để phân tích chuỗi ngày tháng
    from_date_new = datetime.strptime(from_date, '%Y-%m-%d')
    to_date_new = datetime.strptime(to_date, '%Y-%m-%d')

    # Định dạng lại ngày tháng sang định dạng 'dd/mm/yyyy'
    from_date_new = from_date_new.strftime('%d/%m/%Y')
    to_date_new = to_date_new.strftime('%d/%m/%Y')

    client = fc_md_client.MarketDataClient(configDataSSI)

    req = model.daily_ohlc(symbol, from_date_new, to_date_new)

    data_dict = client.daily_ohlc(configDataSSI, req)

    data_list = data_dict['data']

    data = pd.DataFrame(data_list)

    data = data.rename(columns={'TradingDate': 'Datetime'})       

    data = pd.DataFrame(data, columns=['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume'])

    return data

# ##############################################Step 0: Các tham số để lấy dữ liệu###############################
symbol = 'VCB'
from_date = (datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d')
to_date = (datetime.now() + timedelta(days=0)).strftime('%Y-%m-%d')

# ##############################################Step 1: Lấy dữ liệu##############################################
data = loaddataSSI(symbol, from_date, to_date)
# Thiết lập 'Datetime' làm chỉ mục của DataFrame
data.set_index('Datetime', inplace=True)
data['Close'] = pd.to_numeric(data['Close'])

# ##############################################Step 2: Chiến lược##############################################  
# Tính toán SMA và độ lệch chuẩn cho giá đóng cửa bằng TA-Lib
window1 = 6
window2 = 10
data['SMA6'] = talib.SMA(data['Close'], timeperiod=window1)
data['SMA10'] = talib.SMA(data['Close'], timeperiod=window2)

# Tạo cột tín hiệu mua và bán
data['Buy_Signal'] = (data['SMA6'] >= data['SMA10'])
data['Sell_Signal'] = (data['SMA6'] <= data['SMA10'])

# Tạo cột giá cho tín hiệu mua/bán (sử dụng giá Close thực tế)
data['Buy_Price'] = np.where(data['Buy_Signal'], data['Close'], np.nan)
data['Sell_Price'] = np.where(data['Sell_Signal'], data['Close'], np.nan)

print("Dữ liệu sau khi xử lý:")
print(data[['Close', 'SMA6', 'SMA10', 'Buy_Signal', 'Sell_Signal', 'Buy_Price', 'Sell_Price']])

# ##############################################Step 3: Ve bieu do##############################################  
# Ve bieu do
fig = go.Figure()
fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close'))
fig.add_trace(go.Scatter(x=data.index, y=data['SMA6'], mode='lines', name='SMA6'))
fig.add_trace(go.Scatter(x=data.index, y=data['SMA10'], mode='lines', name='SMA10'))
fig.add_trace(go.Scatter(x=data.index, y=data['Buy_Price'], mode='markers', name='Buy Signal', marker=dict(symbol='triangle-up', size=10, color='green')))
fig.add_trace(go.Scatter(x=data.index, y=data['Sell_Price'], mode='markers', name='Sell Signal', marker=dict(symbol='triangle-down', size=10, color='red')))

# Cập nhật layout
fig.update_layout(
    title=f'Chiến lược SMA cho {symbol}',
    xaxis_title='Ngày',
    yaxis_title='Giá',
    showlegend=True
)

fig.show() 