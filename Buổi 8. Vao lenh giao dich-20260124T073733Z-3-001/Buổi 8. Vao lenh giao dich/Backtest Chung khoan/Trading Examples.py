#!/usr/bin/env python3
"""
Trading Examples - Python Cơ Bản cho Trading
Khóa AI Bot Autotrade Nâng Cao
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import requests
import json
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log', encoding='utf-8'),  # Lưu vào file
        logging.StreamHandler()  # Hiển thị trên console
    ]
)
logger = logging.getLogger(__name__)

# =============================================================================
# 1. TẠO DỮ LIỆU MẪU
# =============================================================================

def loaddataSSI(symbol: str = "VNM", days: int = 100) -> pd.DataFrame:
    """Lấy dữ liệu thực từ SSI cho một mã chứng khoán"""
    
    # Import CommonSSI để lấy dữ liệu thực
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '../..', 'Common'))
    
    from CommonSSI import CommonSSI # Neu chi import => CommonSSI.CommonSSI.ham
    # from CommonMT5 import CommonMT5
    from datetime import datetime, timedelta
    
    # Tính toán ngày bắt đầu và kết thúc
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Format ngày tháng
    from_date = start_date.strftime('%Y-%m-%d')
    to_date = end_date.strftime('%Y-%m-%d')
    
    print(f"Đang lấy dữ liệu thực cho {symbol} từ {from_date} đến {to_date}")
    
    try:
        # Lấy dữ liệu thực từ SSI
        data = CommonSSI.loaddataSSI(symbol, from_date, to_date)
        
        # Thêm cột Symbol
        data['Symbol'] = symbol
        
        # Chuyển đổi các cột giá về float
        data['Open'] = pd.to_numeric(data['Open'], errors='coerce')
        data['High'] = pd.to_numeric(data['High'], errors='coerce')
        data['Low'] = pd.to_numeric(data['Low'], errors='coerce')
        data['Close'] = pd.to_numeric(data['Close'], errors='coerce')
        data['Volume'] = pd.to_numeric(data['Volume'], errors='coerce')
        
        # Chuyển đổi Datetime thành index
        data['Datetime'] = pd.to_datetime(data['Datetime'], dayfirst=True)
        data = data.set_index('Datetime')
        
        # Sắp xếp theo thời gian
        data = data.sort_index()
        
        print(f"Đã lấy thành công {len(data)} ngày dữ liệu cho {symbol}")
        
        return data
        
    except Exception as e:
        print(f"Lỗi khi lấy dữ liệu từ SSI: {e}")
        print("Sử dụng dữ liệu mẫu thay thế...")
        
        # Fallback về dữ liệu mẫu nếu có lỗi
        np.random.seed(42)
        
        # Tạo ngày tháng
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Tạo giá mẫu
        initial_price = 50.0
        prices = [initial_price]
        
        for i in range(1, len(dates)):
            # Tạo biến động giá ngẫu nhiên
            change = np.random.normal(0, 0.02)  # 2% biến động trung bình
            new_price = prices[-1] * (1 + change)
            prices.append(max(new_price, 1))  # Giá không được âm
        
        # Tạo DataFrame
        df = pd.DataFrame({
            'Symbol': symbol,
            'Open': prices,
            'High': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'Low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'Close': prices,
            'Volume': np.random.randint(1000000, 10000000, len(dates))
        }, index=dates)
        
        # Đảm bảo High >= Low và High >= Close >= Low
        df['High'] = df[['Open', 'High', 'Close']].max(axis=1)
        df['Low'] = df[['Open', 'Low', 'Close']].min(axis=1)
        
        print(f"Đã tạo dữ liệu mẫu cho {symbol}: {len(df)} ngày")
        return df

# =============================================================================
# 2. TÍNH TOÁN CHỈ BÁO KỸ THUẬT
# =============================================================================

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Tính toán các chỉ báo kỹ thuật sử dụng TA-Lib"""
    
    try:
        import talib
        
        # Chuyển đổi dữ liệu sang định dạng phù hợp với TA-Lib
        high = df['High'].values.astype(float)
        low = df['Low'].values.astype(float)
        close = df['Close'].values.astype(float)
        volume = df['Volume'].values.astype(float)
        
        # Returns
        df['Returns'] = df['Close'].pct_change()
        df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
        
        # Moving Averages - SMA
        df['SMA_5'] = talib.SMA(close, timeperiod=5)
        df['SMA_20'] = talib.SMA(close, timeperiod=20)
        df['SMA_50'] = talib.SMA(close, timeperiod=50)
        
        # Moving Averages - EMA
        df['EMA_12'] = talib.EMA(close, timeperiod=12)
        df['EMA_26'] = talib.EMA(close, timeperiod=26)
        df['EMA_50'] = talib.EMA(close, timeperiod=50)
        
        # MACD
        macd, macd_signal, macd_hist = talib.MACD(close, 
                                                  fastperiod=12, 
                                                  slowperiod=26, 
                                                  signalperiod=9)
        df['MACD'] = macd
        df['MACD_Signal'] = macd_signal
        df['MACD_Histogram'] = macd_hist
        
        # RSI
        df['RSI'] = talib.RSI(close, timeperiod=14)
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = talib.BBANDS(close, 
                                                     timeperiod=20, 
                                                     nbdevup=2, 
                                                     nbdevdn=2, 
                                                     matype=0)
        df['BB_Upper'] = bb_upper
        df['BB_Middle'] = bb_middle
        df['BB_Lower'] = bb_lower
        df['BB_Width'] = (bb_upper - bb_lower) / bb_middle
        
        # Stochastic
        slowk, slowd = talib.STOCH(high, low, close, 
                                   fastk_period=5, 
                                   slowk_period=3, 
                                   slowk_matype=0, 
                                   slowd_period=3, 
                                   slowd_matype=0)
        df['Stoch_K'] = slowk
        df['Stoch_D'] = slowd
        
        # Williams %R
        df['Williams_R'] = talib.WILLR(high, low, close, timeperiod=14)
        
        # Average True Range (ATR)
        df['ATR'] = talib.ATR(high, low, close, timeperiod=14)
        
        # Commodity Channel Index (CCI)
        df['CCI'] = talib.CCI(high, low, close, timeperiod=14)
        
        # Money Flow Index (MFI)
        df['MFI'] = talib.MFI(high, low, close, volume, timeperiod=14)
        
        # On Balance Volume (OBV)
        df['OBV'] = talib.OBV(close, volume)
        
        # Volume indicators
        df['Volume_SMA'] = talib.SMA(volume, timeperiod=20)
        df['Volume_Ratio'] = volume / df['Volume_SMA']
        
        # Volatility
        df['Volatility'] = df['Returns'].rolling(window=20).std()
        
        # Additional indicators
        # Parabolic SAR
        df['SAR'] = talib.SAR(high, low, acceleration=0.02, maximum=0.2)
        
        # Average Directional Index (ADX)
        df['ADX'] = talib.ADX(high, low, close, timeperiod=14)
        
        # Plus/Minus Directional Indicators
        df['PLUS_DI'] = talib.PLUS_DI(high, low, close, timeperiod=14)
        df['MINUS_DI'] = talib.MINUS_DI(high, low, close, timeperiod=14)
        
        # Aroon Oscillator
        aroon_down, aroon_up = talib.AROON(high, low, timeperiod=14)
        df['Aroon_Down'] = aroon_down
        df['Aroon_Up'] = aroon_up
        df['Aroon_Osc'] = talib.AROONOSC(high, low, timeperiod=14)
        
        # Momentum indicators
        df['ROC'] = talib.ROC(close, timeperiod=10)  # Rate of Change
        df['MOM'] = talib.MOM(close, timeperiod=10)  # Momentum
        
        # Price Rate of Change
        df['PROC'] = talib.ROCP(close, timeperiod=10)
        
        logger.info("Đã tính toán các chỉ báo kỹ thuật bằng TA-Lib") # Log ra man hinh
        
    except ImportError:
        logger.warning("TA-Lib không được cài đặt. Sử dụng phương pháp tính toán thủ công...")
        
        # Fallback về phương pháp cũ nếu không có TA-Lib
        # Returns
        df['Returns'] = df['Close'].pct_change()
        df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
        
        # Moving Averages
        df['SMA_5'] = df['Close'].rolling(window=5).mean()
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['EMA_26'] = df['Close'].ewm(span=26).mean()
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle']
        
        # Volume indicators
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
        
        # Volatility
        df['Volatility'] = df['Returns'].rolling(window=20).std()
        
        logger.info("Đã tính toán các chỉ báo kỹ thuật bằng phương pháp thủ công")
    
    return df

# =============================================================================
# 3. CHIẾN LƯỢC GIAO DỊCH
# =============================================================================

@dataclass
class TradingSignal:
    """Class đại diện cho tín hiệu giao dịch"""
    date: datetime
    symbol: str
    signal: str  # BUY, SELL, HOLD
    price: float
    confidence: float
    reason: str

def simple_ma_strategy(df: pd.DataFrame) -> pd.DataFrame:
    """Chiến lược giao dịch dựa trên Moving Average - Sử dụng vectorized operations"""
    
    # Tạo tín hiệu mua: SMA5 > SMA20
    df['Buy_Signal'] = (df['SMA_5'] > df['SMA_20']) # Dinh nghia chien luoc
    
    # Tạo tín hiệu bán: SMA5 < SMA20
    df['Sell_Signal'] = (df['SMA_5'] < df['SMA_20']) # Dinh nghia chien luoc
    
    # Tạo độ tin cậy
    df['Signal_Confidence'] = 0.7  # Độ tin cậy cố định cho MA strategy
    
    # Tạo lý do tín hiệu
    df['Signal_Reason'] = df.apply(
        lambda row: f"SMA5 ({row['SMA_5']:.0f}) > SMA20 ({row['SMA_20']:.0f})" if row['Buy_Signal']
        else f"SMA5 ({row['SMA_5']:.0f}) < SMA20 ({row['SMA_20']:.0f})" if row['Sell_Signal']
        else "SMA5 = SMA20", axis=1
    )
    
    return df

def rsi_strategy(df: pd.DataFrame, oversold: int = 30, overbought: int = 70) -> pd.DataFrame:
    """Chiến lược giao dịch dựa trên RSI - Sử dụng vectorized operations"""
    
    # Tạo tín hiệu mua: RSI < oversold
    df['Buy_Signal'] = (df['RSI'] < oversold)
    
    # Tạo tín hiệu bán: RSI > overbought
    df['Sell_Signal'] = (df['RSI'] > overbought)
    
    # Tạo độ tin cậy
    df['Signal_Confidence'] = df['RSI'].apply(
        lambda x: 0.8 if pd.notna(x) and (x < oversold or x > overbought) else 0.6
    )
    
    # Tạo lý do tín hiệu
    df['Signal_Reason'] = df['RSI'].apply(
        lambda x: f"RSI oversold ({x:.1f})" if pd.notna(x) and x < oversold
        else f"RSI overbought ({x:.1f})" if pd.notna(x) and x > overbought
        else f"RSI neutral ({x:.1f})" if pd.notna(x) else "RSI N/A"
    )
    
    return df

def macd_strategy(df: pd.DataFrame) -> pd.DataFrame:
    """Chiến lược giao dịch dựa trên MACD - Sử dụng vectorized operations"""
    
    # Tạo tín hiệu mua: MACD > Signal và MACD Histogram > 0
    df['Buy_Signal'] = (
        (df['MACD'] > df['MACD_Signal']) & 
        (df['MACD_Histogram'] > 0) &
        (df['MACD'].notna()) & 
        (df['MACD_Signal'].notna())
    )
    
    # Tạo tín hiệu bán: MACD < Signal và MACD Histogram < 0
    df['Sell_Signal'] = (
        (df['MACD'] < df['MACD_Signal']) & 
        (df['MACD_Histogram'] < 0) &
        (df['MACD'].notna()) & 
        (df['MACD_Signal'].notna())
    )
    
    # Tạo độ tin cậy
    df['Signal_Confidence'] = df.apply(
        lambda row: 0.75 if (row['Buy_Signal'] or row['Sell_Signal']) else 0.5, axis=1
    )
    
    # Tạo lý do tín hiệu
    df['Signal_Reason'] = df.apply(
        lambda row: f"MACD bullish ({row['MACD']:.2f} > {row['MACD_Signal']:.2f})" if row['Buy_Signal']
        else f"MACD bearish ({row['MACD']:.2f} < {row['MACD_Signal']:.2f})" if row['Sell_Signal']
        else "MACD neutral", axis=1
    )
    
    return df

def dataframe_to_signals(df: pd.DataFrame, symbol: str) -> List[TradingSignal]:
    """Chuyển đổi DataFrame với boolean signals thành danh sách TradingSignal"""
    signals = []
    
    for i in range(len(df)):
        date = df.index[i]
        price = df['Close'].iloc[i]
        
        # Kiểm tra tín hiệu mua
        if df['Buy_Signal'].iloc[i]:
            signal = TradingSignal(
                date=date,
                symbol=symbol,
                signal="BUY",
                price=price,
                confidence=df['Signal_Confidence'].iloc[i],
                reason=df['Signal_Reason'].iloc[i]
            )
            signals.append(signal)
        
        # Kiểm tra tín hiệu bán
        elif df['Sell_Signal'].iloc[i]:
            signal = TradingSignal(
                date=date,
                symbol=symbol,
                signal="SELL",
                price=price,
                confidence=df['Signal_Confidence'].iloc[i],
                reason=df['Signal_Reason'].iloc[i]
            )
            signals.append(signal)
    
    return signals

# =============================================================================
# 4. BACKTESTING ENGINE
# =============================================================================

@dataclass
class Trade:
    """Class đại diện cho một giao dịch"""
    entry_date: datetime
    exit_date: Optional[datetime]
    symbol: str
    side: str  # BUY or SELL
    quantity: int
    entry_price: float
    exit_price: Optional[float]
    pnl: Optional[float] = None
    pnl_pct: Optional[float] = None

class BacktestEngine:
    """Engine để backtest trading strategies"""
    
    def __init__(self, initial_balance: float = 10000000):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.portfolio: Dict[str, int] = {}
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = [initial_balance]
        self.current_positions: Dict[str, Trade] = {}
        
        logger.info(f"Backtest engine initialized with balance: {initial_balance:,.0f} VND")
    
    def execute_signal(self, signal: TradingSignal) -> Optional[Trade]:
        """Thực hiện tín hiệu giao dịch"""
        
        symbol = signal.symbol
        current_price = signal.price
        
        if signal.signal == "BUY":  # Vẫn giữ string "BUY"/"SELL" vì đây là TradingSignal object
            # Kiểm tra xem đã có position chưa
            if symbol in self.current_positions:
                logger.info(f"Already have position in {symbol}, skipping BUY signal")
                return None
            
            # MUA 100 CỔ PHIẾU CỐ ĐỊNH (theo yêu cầu)
            shares_to_buy = 100
            cost = shares_to_buy * current_price
            
            # Kiểm tra đủ tiền không
            if cost > self.balance:
                logger.warning(f"Insufficient balance to buy {shares_to_buy} {symbol}. Need {cost:,.0f} VND, have {self.balance:,.0f} VND")
                return None
            
            # Tạo trade
            trade = Trade(
                entry_date=signal.date,
                exit_date=None,
                symbol=symbol,
                side="BUY",
                quantity=shares_to_buy,
                entry_price=current_price,
                exit_price=None
            )
            
            # Cập nhật balance và portfolio
            self.balance -= cost
            self.portfolio[symbol] = self.portfolio.get(symbol, 0) + shares_to_buy
            self.current_positions[symbol] = trade
            
            logger.info(f"BUY {shares_to_buy} {symbol} @ {current_price:,.0f} VND (Cost: {cost:,.0f} VND)")
            return trade
        
        elif signal.signal == "SELL":  # Vẫn giữ string "BUY"/"SELL" vì đây là TradingSignal object
            # Kiểm tra xem có position để bán không
            if symbol not in self.current_positions:
                logger.info(f"No position in {symbol}, skipping SELL signal")
                return None
            
            # Lấy trade hiện tại
            current_trade = self.current_positions[symbol]
            quantity = current_trade.quantity
            
            # Cập nhật trade
            current_trade.exit_date = signal.date
            current_trade.exit_price = current_price
            current_trade.pnl = (current_price - current_trade.entry_price) * quantity
            current_trade.pnl_pct = ((current_price - current_trade.entry_price) / current_trade.entry_price) * 100
            
            # Cập nhật balance và portfolio
            revenue = quantity * current_price
            self.balance += revenue
            self.portfolio[symbol] = self.portfolio.get(symbol, 0) - quantity
            
            # Xóa position hiện tại
            del self.current_positions[symbol]
            
            # Thêm vào danh sách trades hoàn thành
            self.trades.append(current_trade)
            
            logger.info(f"SELL {quantity} {symbol} @ {current_price:,.0f} VND, P&L: {current_trade.pnl:,.0f} VND ({current_trade.pnl_pct:.2f}%)")
            return current_trade
        
        return None
    
    def run_backtest(self, df: pd.DataFrame, signals: List[TradingSignal]):
        """Chạy backtest với danh sách tín hiệu"""
        
        logger.info(f"Starting backtest with {len(signals)} signals")
        logger.info("📋 Quy tắc: Mua 100 CP với giá mở cửa nến tiếp theo, Bán toàn bộ với giá mở cửa nến tiếp theo")
        
        # Sắp xếp signals theo thời gian
        signals = sorted(signals, key=lambda x: x.date)
        
        for i, signal in enumerate(signals):
            # Tìm index của signal trong DataFrame
            signal_date = signal.date
            
            # Tìm nến tiếp theo sau signal để thực hiện giao dịch
            next_candle_idx = None
            for j in range(len(df)):
                if df.index[j] > signal_date:
                    next_candle_idx = j
                    break
            
            if next_candle_idx is None:
                logger.warning(f"Không tìm thấy nến tiếp theo cho signal {signal_date}")
                continue
            
            # Lấy giá mở cửa của nến tiếp theo
            next_open_price = df['Open'].iloc[next_candle_idx]
            next_date = df.index[next_candle_idx]
            
            # Tạo signal mới với giá mở cửa
            execution_signal = TradingSignal(
                date=next_date,
                symbol=signal.symbol,
                signal=signal.signal,
                price=next_open_price,  # Sử dụng giá mở cửa
                confidence=signal.confidence,
                reason=f"{signal.reason} (Executed at Open: {next_open_price:,.0f})"
            )
            
            # Thực hiện tín hiệu với giá mở cửa
            trade = self.execute_signal(execution_signal)
            
            # Cập nhật equity curve
            portfolio_value = sum(self.portfolio.get(s, 0) * next_open_price for s in self.portfolio)
            total_equity = self.balance + portfolio_value
            self.equity_curve.append(total_equity)
        
        # Đóng tất cả positions còn lại
        final_price = df['Close'].iloc[-1]
        for symbol, trade in self.current_positions.items():
            trade.exit_date = df.index[-1]
            trade.exit_price = final_price
            trade.pnl = (final_price - trade.entry_price) * trade.quantity
            trade.pnl_pct = ((final_price - trade.entry_price) / trade.entry_price) * 100
            
            self.trades.append(trade)
            logger.info(f"Closed position: {symbol}, P&L: {trade.pnl:,.0f} VND ({trade.pnl_pct:.2f}%)")
        
        logger.info("Backtest completed")
    
    def get_results(self) -> Dict[str, float]:
        """Lấy kết quả backtest"""
        
        if not self.equity_curve:
            return {}
        
        final_equity = self.equity_curve[-1]
        total_return = (final_equity - self.initial_balance) / self.initial_balance
        
        # Tính các metrics khác
        if self.trades:
            winning_trades = [t for t in self.trades if t.pnl and t.pnl > 0]
            losing_trades = [t for t in self.trades if t.pnl and t.pnl < 0]
            
            win_rate = len(winning_trades) / len(self.trades) if self.trades else 0
            avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
            avg_loss = np.mean([t.pnl for t in losing_trades]) if losing_trades else 0
            
            # Tính max drawdown
            peak = self.equity_curve[0]
            max_drawdown = 0
            for equity in self.equity_curve:
                if equity > peak:
                    peak = equity
                drawdown = (peak - equity) / peak
                max_drawdown = max(max_drawdown, drawdown)
        else:
            win_rate = 0
            avg_win = 0
            avg_loss = 0
            max_drawdown = 0
        
        return {
            "initial_balance": self.initial_balance,
            "final_equity": final_equity,
            "total_return": total_return,
            "total_return_pct": total_return * 100,
            "trade_count": len(self.trades),
            "win_rate": win_rate,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "max_drawdown": max_drawdown,
            "max_drawdown_pct": max_drawdown * 100,
            "equity_curve": self.equity_curve  # Thêm equity curve vào results
        }

# =============================================================================
# 5. VISUALIZATION
# =============================================================================

def plot_trading_analysis(df: pd.DataFrame, signals: List[TradingSignal], backtest_results: Dict[str, float]):
    """Vẽ biểu đồ phân tích trading sử dụng Plotly"""
    
    # Tạo subplot layout
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            'Giá cổ phiếu và Tín hiệu giao dịch',
            'RSI Indicator',
            'MACD Indicator', 
            'Bollinger Bands',
            'Volume',
            'Equity Curve'
        ),
        specs=[
            [{"secondary_y": False}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": False}]
        ]
    )
    
    # 1. Candlestick Chart với Moving Averages
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Candlestick',
            increasing_line_color='green',
            decreasing_line_color='red',
            increasing_fillcolor='green',
            decreasing_fillcolor='red'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df.index, y=df['SMA_5'],
            mode='lines', name='SMA 5',
            line=dict(color='orange', width=1, dash='dash')
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df.index, y=df['SMA_20'],
            mode='lines', name='SMA 20',
            line=dict(color='red', width=1, dash='dash')
        ),
        row=1, col=1
    )
    
    # Vẽ tín hiệu giao dịch
    buy_signals = [s for s in signals if s.signal == "BUY"]
    sell_signals = [s for s in signals if s.signal == "SELL"]
    
    if buy_signals:
        buy_dates = [s.date for s in buy_signals]
        buy_prices = [s.price for s in buy_signals]
        fig.add_trace(
            go.Scatter(
                x=buy_dates, y=buy_prices,
                mode='markers', name='Buy Signal',
                marker=dict(color='green', size=10, symbol='triangle-up')
            ),
            row=1, col=1
        )
    
    if sell_signals:
        sell_dates = [s.date for s in sell_signals]
        sell_prices = [s.price for s in sell_signals]
        fig.add_trace(
            go.Scatter(
                x=sell_dates, y=sell_prices,
                mode='markers', name='Sell Signal',
                marker=dict(color='red', size=10, symbol='triangle-down')
            ),
            row=1, col=1
        )
    
    # 2. RSI
    fig.add_trace(
        go.Scatter(
            x=df.index, y=df['RSI'],
            mode='lines', name='RSI',
            line=dict(color='purple', width=2)
        ),
        row=1, col=2
    )
    
    fig.add_hline(y=70, line_dash="dash", line_color="red", 
                  annotation_text="Overbought", row=1, col=2)
    fig.add_hline(y=30, line_dash="dash", line_color="green", 
                  annotation_text="Oversold", row=1, col=2)
    
    # 3. MACD
    fig.add_trace(
        go.Scatter(
            x=df.index, y=df['MACD'],
            mode='lines', name='MACD',
            line=dict(color='blue', width=2)
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df.index, y=df['MACD_Signal'],
            mode='lines', name='Signal',
            line=dict(color='red', width=2)
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=df.index, y=df['MACD_Histogram'],
            name='Histogram',
            marker_color='gray',
            opacity=0.3
        ),
        row=2, col=1
    )
    
    # 4. Bollinger Bands với Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Candlestick',
            increasing_line_color='green',
            decreasing_line_color='red',
            increasing_fillcolor='green',
            decreasing_fillcolor='red'
        ),
        row=2, col=2
    )
    
    fig.add_trace(
        go.Scatter(
            x=df.index, y=df['BB_Upper'],
            mode='lines', name='Upper Band',
            line=dict(color='red', width=1, dash='dash')
        ),
        row=2, col=2
    )
    
    fig.add_trace(
        go.Scatter(
            x=df.index, y=df['BB_Middle'],
            mode='lines', name='Middle Band',
            line=dict(color='blue', width=1, dash='dash')
        ),
        row=2, col=2
    )
    
    fig.add_trace(
        go.Scatter(
            x=df.index, y=df['BB_Lower'],
            mode='lines', name='Lower Band',
            line=dict(color='red', width=1, dash='dash'),
            fill='tonexty', fillcolor='rgba(128,128,128,0.1)'
        ),
        row=2, col=2
    )
    
    # 5. Volume
    fig.add_trace(
        go.Bar(
            x=df.index, y=df['Volume'],
            name='Volume',
            marker_color='orange',
            opacity=0.7
        ),
        row=3, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df.index, y=df['Volume_SMA'],
            mode='lines', name='Volume SMA',
            line=dict(color='red', width=2)
        ),
        row=3, col=1
    )
    
    # 6. Equity Curve
    initial_balance = backtest_results.get('initial_balance', 10000000)
    final_equity = backtest_results.get('final_equity', initial_balance)
    
    # Tạo equity curve thực tế từ backtest engine
    if hasattr(backtest_results, 'equity_curve') and backtest_results['equity_curve']:
        equity_curve = backtest_results['equity_curve']
        equity_dates = df.index[:len(equity_curve)]
    else:
        # Giả lập equity curve đơn giản
        equity_curve = np.linspace(initial_balance, final_equity, len(df))
        equity_dates = df.index
    
    fig.add_trace(
        go.Scatter(
            x=equity_dates, y=equity_curve,
            mode='lines', name='Equity',
            line=dict(color='green', width=2)
        ),
        row=3, col=2
    )
    
    # Cập nhật layout
    fig.update_layout(
        title={
            'text': 'Phân tích Trading Strategy',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': 'black'}
        },
        height=1200,
        width=1400,
        showlegend=True,
        template='plotly_white'
    )
    
    # Cập nhật axes labels
    fig.update_xaxes(title_text="Ngày", row=3, col=1)
    fig.update_xaxes(title_text="Ngày", row=3, col=2)
    fig.update_yaxes(title_text="Giá (VND)", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=1, col=2)
    fig.update_yaxes(title_text="MACD", row=2, col=1)
    fig.update_yaxes(title_text="Giá (VND)", row=2, col=2)
    fig.update_yaxes(title_text="Volume", row=3, col=1)
    fig.update_yaxes(title_text="Equity (VND)", row=3, col=2)
    
    # Cập nhật subplot titles để phản ánh candlestick
    fig.layout.annotations[0].update(text='Candlestick và Tín hiệu giao dịch')
    fig.layout.annotations[3].update(text='Bollinger Bands với Candlestick')
    
    # Hiển thị biểu đồ
    try:
        # Lưu biểu đồ thành file HTML
        fig.write_html("trading_analysis.html")
        print("✅ Biểu đồ đã được lưu vào file 'trading_analysis.html'")
        
        # Mở biểu đồ trong trình duyệt
        import webbrowser
        import os
        
        # Lấy đường dẫn tuyệt đối của file HTML
        html_path = os.path.abspath("trading_analysis.html")
        print(f"🌐 Đang mở biểu đồ trong trình duyệt: {html_path}")
        
        # Mở file HTML trong trình duyệt mặc định
        webbrowser.open(f"file://{html_path}")
        
        print("🎉 Biểu đồ đã được mở trong trình duyệt!")
        print("💡 Nếu trình duyệt không mở tự động, hãy mở file 'trading_analysis.html' thủ công")
        
    except Exception as e:
        print(f"❌ Lỗi khi hiển thị biểu đồ: {e}")
        print("📁 Biểu đồ đã được lưu vào file 'trading_analysis.html'")
        print("🌐 Hãy mở file này trong trình duyệt để xem biểu đồ")

def print_backtest_summary(results: Dict[str, float]):
    """In tóm tắt kết quả backtest"""
    
    print("=" * 60)
    print("KẾT QUẢ BACKTEST")
    print("=" * 60)
    print(f"Số dư ban đầu:     {results['initial_balance']:>15,.0f} VND")
    print(f"Equity cuối:        {results['final_equity']:>15,.0f} VND")
    print(f"Tổng lợi nhuận:     {results['total_return_pct']:>15.2f}%")
    print(f"Số giao dịch:       {results['trade_count']:>15}")
    print(f"Tỷ lệ thắng:        {results['win_rate']*100:>15.2f}%")
    print(f"Lợi nhuận TB:       {results['avg_win']:>15,.0f} VND")
    print(f"Thua lỗ TB:         {results['avg_loss']:>15,.0f} VND")
    print(f"Drawdown tối đa:    {results['max_drawdown_pct']:>15.2f}%")
    print("=" * 60)

# =============================================================================
# 6. MAIN EXECUTION
# =============================================================================

def main():
    """Hàm chính để chạy ví dụ"""
    
    print("🚀 Bắt đầu Trading Examples - Python Cơ Bản cho Trading")
    print("=" * 60)
    
    # 1. Lấy dữ liệu từ SSI
    print("1. Lấy dữ liệu từ SSI...")
    df = loaddataSSI("VNM", days=100) # VNM la ma co phieu cua VNM
    # df = loaddataMT5("VNM", days=100)
    print(f"   Dữ liệu: {len(df)} ngày giao dịch")
    # Chuyển đổi giá về float nếu cần
    current_price = float(df['Close'].iloc[-1])
    print(f"   Giá hiện tại: {current_price:,.0f} VND")
    
    # 2. Tính toán chỉ báo kỹ thuật
    print("\n2. Tính toán chỉ báo kỹ thuật...")
    df = calculate_technical_indicators(df)
    
    # 3. Tạo tín hiệu giao dịch
    print("\n3. Tạo tín hiệu giao dịch...")
    
    # Tạo DataFrame riêng cho từng chiến lược
    df_ma = df.copy()
    df_rsi = df.copy()
    df_macd = df.copy()
    
    # Áp dụng các chiến lược
    df_ma = simple_ma_strategy(df_ma)
    df_rsi = rsi_strategy(df_rsi)
    df_macd = macd_strategy(df_macd)
    
    # Thống kê tín hiệu cho từng chiến lược
    ma_buy_count = df_ma['Buy_Signal'].sum()
    ma_sell_count = df_ma['Sell_Signal'].sum()
    rsi_buy_count = df_rsi['Buy_Signal'].sum()
    rsi_sell_count = df_rsi['Sell_Signal'].sum()
    macd_buy_count = df_macd['Buy_Signal'].sum()
    macd_sell_count = df_macd['Sell_Signal'].sum()
    
    print(f"   MA Strategy: {ma_buy_count + ma_sell_count} tín hiệu")
    print(f"     - BUY signals: {ma_buy_count}")
    print(f"     - SELL signals: {ma_sell_count}")
    
    print(f"   RSI Strategy: {rsi_buy_count + rsi_sell_count} tín hiệu")
    print(f"     - BUY signals: {rsi_buy_count}")
    print(f"     - SELL signals: {rsi_sell_count}")
    
    print(f"   MACD Strategy: {macd_buy_count + macd_sell_count} tín hiệu")
    print(f"     - BUY signals: {macd_buy_count}")
    print(f"     - SELL signals: {macd_sell_count}")
    
    # Chọn chiến lược để hiển thị (mặc định là MA)
    selected_strategy = "MA"
    if selected_strategy == "MA":
        display_df = df_ma
        strategy_name = "Moving Average"
    elif selected_strategy == "RSI":
        display_df = df_rsi
        strategy_name = "RSI"
    elif selected_strategy == "MACD":
        display_df = df_macd
        strategy_name = "MACD"
    
    # Hiển thị 5 tín hiệu đầu tiên của chiến lược được chọn
    print(f"\n   📋 5 tín hiệu {strategy_name} đầu tiên:")
    signal_count = 0
    for i in range(20, len(display_df)):
        if signal_count >= 5:
            break
        if display_df['Buy_Signal'].iloc[i]:  # True = có tín hiệu mua
            print(f"     {signal_count+1}. {display_df.index[i].strftime('%Y-%m-%d')} - BUY @ {display_df['Close'].iloc[i]:,.0f} VND")
            print(f"        Lý do: {display_df['Signal_Reason'].iloc[i]}")
            print(f"        Độ tin cậy: {display_df['Signal_Confidence'].iloc[i]:.1%}")
            signal_count += 1
        elif display_df['Sell_Signal'].iloc[i]:  # True = có tín hiệu bán
            print(f"     {signal_count+1}. {display_df.index[i].strftime('%Y-%m-%d')} - SELL @ {display_df['Close'].iloc[i]:,.0f} VND")
            print(f"        Lý do: {display_df['Signal_Reason'].iloc[i]}")
            print(f"        Độ tin cậy: {display_df['Signal_Confidence'].iloc[i]:.1%}")
            signal_count += 1
    
    # 4. Hiển thị dữ liệu với signal
    print(f"\n4. Hiển thị dữ liệu với tín hiệu {strategy_name}...")
    print("   📊 10 dòng cuối với tín hiệu:")
    display_cols = ['Close', 'SMA_5', 'SMA_20', 'Buy_Signal', 'Sell_Signal', 'Signal_Confidence', 'Signal_Reason']
    print(display_df[display_cols].tail(10).to_string())
    
    # 5. Thống kê tổng hợp
    print("\n5. Thống kê tổng hợp các chiến lược:")
    print("=" * 60)
    print(f"{'Chiến lược':<15} {'BUY':<8} {'SELL':<8} {'Tổng':<8}")
    print("-" * 60)
    print(f"{'MA':<15} {ma_buy_count:<8} {ma_sell_count:<8} {ma_buy_count + ma_sell_count:<8}")
    print(f"{'RSI':<15} {rsi_buy_count:<8} {rsi_sell_count:<8} {rsi_buy_count + rsi_sell_count:<8}")
    print(f"{'MACD':<15} {macd_buy_count:<8} {macd_sell_count:<8} {macd_buy_count + macd_sell_count:<8}")
    print("=" * 60)
    
    # 6. Backtest chiến lược được chọn
    print(f"\n6. Backtest chiến lược {strategy_name}...")
    
    # Chuyển đổi DataFrame thành danh sách signals
    signals = dataframe_to_signals(display_df, "VNM")
    
    if signals:
        # Khởi tạo backtest engine
        backtest_engine = BacktestEngine(initial_balance=10000000)
        
        # Chạy backtest
        backtest_engine.run_backtest(display_df, signals)
        
        # Lấy kết quả
        results = backtest_engine.get_results()
        
        # In kết quả
        print_backtest_summary(results)
        
        # Vẽ biểu đồ
        print("\n7. Vẽ biểu đồ phân tích...")
        plot_trading_analysis(display_df, signals, results)
    else:
        print("   ⚠️ Không có tín hiệu giao dịch để backtest")
    
    print("\n✅ Hoàn thành Trading Examples!")
    print("\n📚 Tiếp tục học tập:")
    print("   - Buoi 1-2: Deep Learning cơ bản cho tài chính")
    print("   - Buoi 3-4: Recurrent Neural Networks")
    print("   - Buoi 5-6: Convolutional Neural Networks")

if __name__ == "__main__":
    main() 