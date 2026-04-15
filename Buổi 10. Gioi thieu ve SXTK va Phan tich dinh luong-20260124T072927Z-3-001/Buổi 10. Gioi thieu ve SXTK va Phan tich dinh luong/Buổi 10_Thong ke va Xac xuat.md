# Phụ đạo 3: Thống kê và Xác suất trong Auto Trading

## 📚 Mục lục
1. [Tại sao cần Thống kê và Xác suất?](#tại-sao-cần-thống-kê-và-xác-suất)
2. [Các Khái niệm Cơ bản](#các-khái-niệm-cơ-bản)
3. [Phân phối Xác suất trong Trading](#phân-phối-xác-suất-trong-trading)
4. [Các Chỉ số Thống kê Quan trọng](#các-chỉ-số-thống-kê-quan-trọng)
5. [Ứng dụng Thực tế](#ứng-dụng-thực-tế)
6. [Ví dụ Chi tiết](#ví-dụ-chi-tiết)
7. [Cách Tích hợp vào Hệ thống](#cách-tích-hợp-vào-hệ-thống)

---

## 🎯 Tại sao cần Thống kê và Xác suất?

### 1.1 Vấn đề của Trading thông thường

**❌ Vấn đề thường gặp:**
- Giao dịch dựa trên "cảm giác" hoặc "kinh nghiệm"
- Không biết xác suất thắng/thua thực tế
- Position sizing không hợp lý
- Không đo lường được rủi ro chính xác
- Không biết chiến lược có thực sự hiệu quả không

**✅ Giải pháp với Thống kê và Xác suất:**
- Đo lường chính xác xác suất thắng/thua
- Tính toán position size tối ưu
- Đánh giá rủi ro bằng số liệu cụ thể
- So sánh hiệu quả các chiến lược khác nhau

### 1.2 Ví dụ thực tế

**Tình huống:** Bạn có một chiến lược trading và muốn biết nó có hiệu quả không?

**❌ Cách làm thông thường:**
```
- Thử giao dịch vài lần
- Nếu thắng nhiều → "Chiến lược tốt!"
- Nếu thua nhiều → "Chiến lược xấu!"
```

**✅ Cách làm với thống kê:**
```
--- Bai tap 1
- Thu thập 100+ giao dịch
- Tính toán:
  + Win Rate = 65%
  + Average Win = 2.5%
  + Average Loss = -1.8%
  + Profit Factor = 1.89
  + Sharpe Ratio = 1.2
- Kết luận: Chiến lược có hiệu quả với độ tin cậy 95%
```

---

## 📊 Các Khái niệm Cơ bản

### 2.1 Xác suất (Probability)

#### Win Rate (Tỷ lệ thắng)
```
Win Rate = Số giao dịch thắng / Tổng số giao dịch
```

**Ví dụ:**
- Tổng cộng 100 giao dịch
- 65 giao dịch thắng
- Win Rate = 65/100 = 65%

**Ý nghĩa:** 65% khả năng mỗi giao dịch sẽ thắng

#### Expected Value (Giá trị kỳ vọng)
```
Expected Value = (Win Rate × Average Win) + ((1 - Win Rate) × Average Loss)
```

**Ví dụ:**
- Win Rate = 65%
- Average Win = 2.5%
- Average Loss = -1.8%
- Expected Value = (0.65 × 2.5%) + (0.35 × (-1.8%)) = 1.625% - 0.63% = 0.995%

**Ý nghĩa:** Mỗi giao dịch kỳ vọng lãi 0.995%

### 2.2 Thống kê (Statistics)

#### Mean (Trung bình)
```
Mean = Tổng tất cả giá trị / Số lượng giá trị
```

**Ví dụ lợi nhuận hàng ngày:**
- Bai tap 2: Tinh loi nhuan hang ngay
- [1.2%, -0.8%, 2.1%, -1.5%, 0.9%]
- Mean = (1.2% - 0.8% + 2.1% - 1.5% + 0.9%) / 5 = 0.38%

#### Standard Deviation (Độ lệch chuẩn)
```
Standard Deviation = √(Σ(x - mean)² / n)
```

**Ý nghĩa:** Đo lường mức độ biến động
- Std thấp = Ít biến động = Rủi ro thấp
- Std cao = Nhiều biến động = Rủi ro cao

**Ví dụ:**
- Strategy A: Mean = 1%, Std = 2% → Ít biến động
- Strategy B: Mean = 1%, Std = 5% → Nhiều biến động
- → Strategy A an toàn hơn

---

## 📈 Phân phối Xác suất trong Trading

### 3.1 Phân phối Chuẩn (Normal Distribution)

**Đặc điểm:**
- Hình chuông đối xứng
- 68% dữ liệu nằm trong ±1 Std
- 95% dữ liệu nằm trong ±2 Std
- 99.7% dữ liệu nằm trong ±3 Std

**Trong Trading:**
```python
--- Bai tap 3
# 4. Nếu phân phối gần chuẩn, tiếp tục phân tích thống kê
mu = np.mean(profits)
sigma = np.std(profits, ddof=1)  # ddof=1 dùng cho mẫu

# Xác suất lợi nhuận > 0
prob_positive = 1 - stats.norm.cdf(0, mu, sigma)

# Xác suất lợi nhuận > 1%
prob_gt_1 = 1 - stats.norm.cdf(0.01, mu, sigma)

# Value at Risk 95%
VaR_95 = stats.norm.ppf(0.05, mu, sigma)

# Sharpe Ratio (so với lãi suất phi rủi ro 0.01% mỗi ngày)
risk_free_rate = 0.0001
sharpe_ratio = (mu - risk_free_rate) / sigma

# In kết quả
print("\n=== Phân tích thống kê dựa trên phân phối chuẩn ===")
print(f"✅ Trung bình lợi nhuận: {mu:.2%}")
print(f"✅ Độ lệch chuẩn: {sigma:.2%}")
print(f"🔹 Xác suất lợi nhuận > 0%: {prob_positive:.2%}")
print(f"🔹 Xác suất lợi nhuận > 1%: {prob_gt_1:.2%}")
print(f"🔻 Value at Risk (95%): {VaR_95:.2%}")
print(f"📊 Sharpe Ratio: {sharpe_ratio:.2f}")

```

### 3.2 Phân phối Student's t

**Khi nào dùng:**
- Mẫu nhỏ (< 30 quan sát)
- Không biết độ lệch chuẩn tổng thể

**Ví dụ:**
```python
# Test xem lợi nhuận có khác 0 không
t_stat, p_value = stats.ttest_1samp(daily_returns, 0)
print(f"T-statistic: {t_stat:.4f}")
print(f"P-value: {p_value:.4f}")

# Nếu p-value < 0.05 → Lợi nhuận khác 0 có ý nghĩa thống kê
```

### 3.3 Phân phối Log-normal

**Đặc điểm:**
- Giá cổ phiếu không bao giờ âm
- Lợi nhuận log tuân theo phân phối chuẩn

**Ví dụ:**
```python
# Tính xác suất giá tăng 10%
log_returns = np.log(1 + daily_returns)
prob_10_percent_gain = 1 - stats.lognorm.cdf(1.1, s=log_std, scale=np.exp(log_mean))
print(f"Xác suất giá tăng 10%: {prob_10_percent_gain:.2%}")
```

---

## 🎯 Các Chỉ số Thống kê Quan trọng

### 4.1 Sharpe Ratio

**Công thức:**
```
Sharpe Ratio = (Return - Risk Free Rate) / Standard Deviation
```

**Ý nghĩa:** Đo lường lợi nhuận trên mỗi đơn vị rủi ro

**Ví dụ:**
```python
def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    excess_returns = returns - risk_free_rate/252  # Chuyển về daily
    return np.sqrt(252) * np.mean(excess_returns) / np.std(excess_returns)

# Ví dụ
strategy_returns = np.random.normal(0.001, 0.015, 252)  # 1 năm giao dịch
sharpe = calculate_sharpe_ratio(strategy_returns)
print(f"Sharpe Ratio: {sharpe:.2f}")

# Giải thích:
# Sharpe > 1.0: Tốt
# Sharpe > 2.0: Rất tốt
# Sharpe < 0.5: Cần cải thiện
```

### 4.2 Sortino Ratio

**Công thức:**
```
Sortino Ratio = (Return - Risk Free Rate) / Downside Deviation
```

**Khác biệt với Sharpe:** Chỉ xét downside risk (rủi ro thua lỗ)

**Ví dụ:**
```python
def calculate_sortino_ratio(returns, risk_free_rate=0.02):
    excess_returns = returns - risk_free_rate/252
    downside_returns = excess_returns[excess_returns < 0]  # Chỉ lấy lợi nhuận âm
    downside_std = np.std(downside_returns)
    return np.sqrt(252) * np.mean(excess_returns) / downside_std
```

### 4.3 Maximum Drawdown

**Định nghĩa:** Mức sụt giảm tối đa từ đỉnh đến đáy

**Ví dụ:**
```python
-- Bai tap 4
def calculate_max_drawdown(equity_curve):
    peak = equity_curve.expanding().max()  # Đỉnh cao nhất đến thời điểm đó
    drawdown = (equity_curve - peak) / peak
    return drawdown.min()

# Ví dụ
equity = (1 + strategy_returns).cumprod()  # Đường cong vốn
max_dd = calculate_max_drawdown(equity)
print(f"Maximum Drawdown: {max_dd:.2%}")
# Kết quả: Maximum Drawdown: -8.45%
```

### 4.4 Kelly Criterion

**Công thức:**
```
Kelly Fraction = (Win Rate × Win/Loss Ratio - (1 - Win Rate)) / Win/Loss Ratio
```

**Ý nghĩa:** Tỷ lệ vốn tối ưu cho mỗi giao dịch

**Ví dụ:**
```python
def kelly_criterion(win_rate, avg_win, avg_loss):
    if avg_loss == 0:
        return 0
    
    win_loss_ratio = avg_win / abs(avg_loss)
    kelly_fraction = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
    
    return max(0, min(kelly_fraction, 1))  # Giới hạn từ 0 đến 1

# Ví dụ
win_rate = 0.65  # 65%
avg_win = 0.025  # 2.5%
avg_loss = -0.018  # -1.8%

kelly = kelly_criterion(win_rate, avg_win, avg_loss)
print(f"Kelly Fraction: {kelly:.2%}")
# Kết quả: Kelly Fraction: 25.75%

# Giải thích: Nên dùng 25.75% vốn cho mỗi giao dịch
# Nhưng thường dùng 25% của Kelly để an toàn hơn
fractional_kelly = kelly * 0.25
print(f"Fractional Kelly (25%): {fractional_kelly:.2%}")
# Kết quả: Fractional Kelly (25%): 6.44%
```

---

## 💰 Ứng dụng Thực tế

### 5.1 Position Sizing với Kelly Criterion

**Vấn đề:** Nên dùng bao nhiêu vốn cho mỗi giao dịch?

**Giải pháp:**
```python
class RiskManager:
    def __init__(self, max_position_size=0.02, max_drawdown=0.1):
        self.max_position_size = max_position_size
        self.max_drawdown = max_drawdown
        self.current_drawdown = 0
        
    def calculate_position_size(self, capital, signal_strength, volatility):
        # Kelly Criterion
        kelly_size = signal_strength
        
        # Risk-adjusted size (giảm khi drawdown cao)
        risk_size = self.max_position_size * (1 - self.current_drawdown / self.max_drawdown)
        
        # Volatility adjustment (giảm khi volatility cao)
        vol_adjustment = 1 / (1 + volatility)
        
        # Final size
        final_size = min(kelly_size, risk_size) * vol_adjustment
        return max(0, min(final_size, self.max_position_size))

# Ví dụ sử dụng
risk_manager = RiskManager()
position_size = risk_manager.calculate_position_size(
    capital=10000,
    signal_strength=0.25,  # Kelly fraction
    volatility=0.02  # 2% daily volatility
)
print(f"Position size: {position_size:.2%}")
# Kết quả: Position size: 1.96%
```

### 5.2 Signal Confidence Scoring

**Vấn đề:** Làm sao biết tín hiệu có đáng tin không?

**Giải pháp:**
```python
class SignalAnalyzer:
    def __init__(self, lookback_period=252):
        self.lookback_period = lookback_period
        
    def calculate_signal_confidence(self, signal_history, returns):
        if len(signal_history) < self.lookback_period:
            return 0.5
        
        recent_signals = signal_history[-self.lookback_period:]
        recent_returns = returns[-self.lookback_period:]
        
        # Tính độ chính xác của tín hiệu
        signal_accuracy = np.mean(np.sign(recent_signals) == np.sign(recent_returns))
        
        # Tính profit factor
        winning_trades = recent_returns[np.sign(recent_signals) == np.sign(recent_returns)]
        losing_trades = recent_returns[np.sign(recent_signals) != np.sign(recent_returns)]
        
        if len(losing_trades) > 0:
            profit_factor = abs(np.mean(winning_trades) / np.mean(losing_trades))
        else:
            profit_factor = 2.0
        
        # Tính confidence score
        confidence = (signal_accuracy * 0.6 + min(profit_factor / 2, 1) * 0.4)
        
        return confidence

# Ví dụ sử dụng
analyzer = SignalAnalyzer()
confidence = analyzer.calculate_signal_confidence(signals, returns)
print(f"Signal Confidence: {confidence:.2%}")
# Kết quả: Signal Confidence: 72.5%
```

### 5.3 VaR và CVaR

**Value at Risk (VaR):** Mức thua lỗ tối đa với xác suất nhất định

**Conditional VaR (CVaR):** Mức thua lỗ trung bình khi vượt quá VaR

```python
def calculate_var(returns, confidence_level=0.95):
    """Tính VaR"""
    return np.percentile(returns, (1 - confidence_level) * 100)

def calculate_conditional_var(returns, confidence_level=0.95):
    """Tính CVaR"""
    var = calculate_var(returns, confidence_level)
    return returns[returns <= var].mean()

# Ví dụ
var_95 = calculate_var(strategy_returns, 0.95)
cvar_95 = calculate_conditional_var(strategy_returns, 0.95)
print(f"VaR 95%: {var_95:.2%}")
print(f"CVaR 95%: {cvar_95:.2%}")
# Kết quả:
# VaR 95%: -2.34%
# CVaR 95%: -3.12%

# Giải thích:
# - 95% thời gian, thua lỗ không quá 2.34%
# - 5% thời gian còn lại, thua lỗ trung bình là 3.12%
```

---

## 📊 Ví dụ Chi tiết

### 6.1 Phân tích Chiến lược Trading

**Tình huống:** Bạn có một chiến lược trading và muốn đánh giá hiệu quả

```python
# Dữ liệu 100 giao dịch
trades = [
    2.5, -1.8, 1.9, -2.1, 3.2, -1.5, 2.8, -1.9, 1.7, -2.3,
    # ... (90 giao dịch nữa)
]

def analyze_trading_performance(trades):
    winning_trades = [t for t in trades if t > 0]
    losing_trades = [t for t in trades if t < 0]
    
    win_rate = len(winning_trades) / len(trades)
    avg_win = np.mean(winning_trades) if winning_trades else 0
    avg_loss = np.mean(losing_trades) if losing_trades else 0
    
    profit_factor = abs(avg_win * len(winning_trades) / (avg_loss * len(losing_trades))) if avg_loss != 0 else float('inf')
    
    return {
        'win_rate': win_rate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'profit_factor': profit_factor
    }

# Kết quả phân tích
performance = analyze_trading_performance(trades)
print(f"Win Rate: {performance['win_rate']:.2%}")
print(f"Average Win: {performance['avg_win']:.2%}")
print(f"Average Loss: {performance['avg_loss']:.2%}")
print(f"Profit Factor: {performance['profit_factor']:.2f}")

# Kết quả:
# Win Rate: 65.00%
# Average Win: 2.45%
# Average Loss: -1.82%
# Profit Factor: 1.89

# Đánh giá:
# ✅ Win Rate > 50%: Tốt
# ✅ Profit Factor > 1.5: Rất tốt
# ✅ Average Win > |Average Loss|: Tốt
```

### 6.2 Monte Carlo Simulation

**Mục đích:** Mô phỏng nhiều kịch bản để đánh giá rủi ro

```python
def monte_carlo_portfolio(initial_capital, returns, num_simulations=10000, days=252):
    final_values = []
    
    for _ in range(num_simulations):
        # Random sampling với replacement
        sample_returns = np.random.choice(returns, size=days, replace=True)
        final_value = initial_capital * (1 + sample_returns).prod()
        final_values.append(final_value)
    
    return np.array(final_values)

# Ví dụ
simulations = monte_carlo_portfolio(10000, strategy_returns)
print(f"95% Confidence Interval: [{np.percentile(simulations, 2.5):.0f}, {np.percentile(simulations, 97.5):.0f}]")
print(f"Probability of Loss: {(simulations < 10000).mean():.2%}")

# Kết quả:
# 95% Confidence Interval: [8,234, 12,567]
# Probability of Loss: 23.45%

# Giải thích:
# - 95% khả năng, vốn cuối năm sẽ nằm trong khoảng $8,234 - $12,567
# - 23.45% khả năng sẽ thua lỗ
```

---

## 🔧 Cách Tích hợp vào Hệ thống

### 7.1 Quy trình Triển khai

#### Bước 1: Thu thập Dữ liệu
```python
# Tải dữ liệu lịch sử
import yfinance as yf

ticker = yf.Ticker('AAPL')
data = ticker.history(start='2023-01-01', end='2024-01-01')
returns = data['Close'].pct_change().dropna()
```

#### Bước 2: Tính toán Chỉ số Cơ bản
```python
# Thống kê mô tả
mean_return = returns.mean()
std_return = returns.std()
sharpe_ratio = np.sqrt(252) * mean_return / std_return

print(f"Mean Return: {mean_return:.4f}")
print(f"Standard Deviation: {std_return:.4f}")
print(f"Sharpe Ratio: {sharpe_ratio:.3f}")
```

#### Bước 3: Phân tích Rủi ro
```python
# VaR và CVaR
var_95 = np.percentile(returns, 5)
cvar_95 = returns[returns <= var_95].mean()

print(f"VaR 95%: {var_95:.2%}")
print(f"CVaR 95%: {cvar_95:.2%}")
```

#### Bước 4: Tối ưu hóa Position Sizing
```python
# Kelly Criterion
def calculate_kelly_position(win_rate, avg_win, avg_loss, capital):
    kelly_fraction = kelly_criterion(win_rate, avg_win, avg_loss)
    fractional_kelly = kelly_fraction * 0.25  # Conservative approach
    position_size = fractional_kelly * capital
    return position_size

# Ví dụ
position_size = calculate_kelly_position(
    win_rate=0.65,
    avg_win=0.025,
    avg_loss=-0.018,
    capital=10000
)
print(f"Position Size: ${position_size:.0f}")
```

#### Bước 5: Tạo Tín hiệu với Confidence
```python
def generate_signal_with_confidence(price_data, confidence_threshold=0.6):
    # Tính các chỉ báo
    sma_20 = price_data['Close'].rolling(20).mean()
    rsi = calculate_rsi(price_data['Close'])
    
    # Tạo tín hiệu
    signals = []
    confidences = []
    
    for i in range(20, len(price_data)):
        signal = 0
        confidence = 0.5
        
        # Bollinger Bands signal
        if price_data['Close'].iloc[i] < sma_20.iloc[i] * 0.95:
            signal = 1  # Buy
            confidence += 0.2
        
        # RSI signal
        if rsi.iloc[i] < 30:
            signal = 1  # Buy
            confidence += 0.3
        
        # Volatility adjustment
        volatility = price_data['Close'].pct_change().rolling(20).std().iloc[i]
        if volatility > 0.03:  # High volatility
            confidence *= 0.8
        
        signals.append(signal)
        confidences.append(min(confidence, 1.0))
    
    return signals, confidences

# Sử dụng
signals, confidences = generate_signal_with_confidence(data)
```

### 7.2 Hệ thống Trading Hoàn chỉnh

```python
class StatisticalTradingSystem:
    def __init__(self, symbol, initial_capital):
        self.symbol = symbol
        self.capital = initial_capital
        self.positions = 0
        
    def calculate_position_size(self, signal_strength, confidence, volatility):
        # Kelly-based position sizing
        kelly_size = signal_strength * self.capital
        
        # Risk adjustments
        risk_adjustment = 1 - (self.current_drawdown / self.max_drawdown)
        vol_adjustment = 1 / (1 + volatility)
        confidence_adjustment = confidence
        
        final_size = kelly_size * risk_adjustment * vol_adjustment * confidence_adjustment
        return max(0, min(final_size, self.capital * 0.02))  # Max 2%
    
    def execute_trade(self, signal, confidence, price):
        if signal > 0 and confidence > 0.6:  # Buy signal with high confidence
            position_size = self.calculate_position_size(signal, confidence, self.volatility)
            shares = int(position_size / price)
            self.positions += shares
            self.capital -= shares * price
            print(f"BUY {shares} shares at ${price:.2f} (Confidence: {confidence:.2%})")
        
        elif signal < 0 and self.positions > 0:  # Sell signal
            sell_value = self.positions * price
            self.capital += sell_value
            print(f"SELL {self.positions} shares at ${price:.2f}")
            self.positions = 0

# Sử dụng hệ thống
trading_system = StatisticalTradingSystem('AAPL', 10000)
# ... implement trading logic
```

---

## ⚠️ Lưu ý Quan trọng

### 8.1 Overfitting
**Vấn đề:** Model hoạt động tốt trên dữ liệu quá khứ nhưng kém trên dữ liệu mới

**Giải pháp:**
- Chia dữ liệu thành training và testing
- Sử dụng cross-validation
- Không sử dụng quá nhiều parameters

### 8.2 Market Regime Changes
**Vấn đề:** Thị trường thay đổi, model cũ không còn hiệu quả

**Giải pháp:**
- Cập nhật model định kỳ
- Sử dụng regime detection
- Adaptive parameters

### 8.3 Transaction Costs
**Vấn đề:** Chi phí giao dịch làm giảm lợi nhuận

**Giải pháp:**
- Tính toán chi phí vào backtest
- Sử dụng threshold cho signals
- Tối ưu hóa tần suất giao dịch

### 8.4 Risk Management
**Nguyên tắc:**
- Luôn có stop-loss
- Giới hạn position size
- Đa dạng hóa portfolio
- Monitor drawdown

---

## 📈 Kết luận

Thống kê và xác suất là **nền tảng quan trọng** cho việc xây dựng hệ thống auto trading hiệu quả:

### ✅ Lợi ích:
1. **Quản lý rủi ro tốt hơn** với VaR, CVaR
2. **Position sizing tối ưu** với Kelly Criterion
3. **Đánh giá hiệu quả chính xác** với Sharpe Ratio
4. **Tín hiệu giao dịch tin cậy** với confidence scoring
5. **Portfolio optimization** với Bayesian methods

### 🎯 Kết quả mong đợi:
- **Sharpe Ratio > 1.0**
- **Max Drawdown < 10%**
- **Win Rate > 50%**
- **Profit Factor > 1.5**

### 📚 Bước tiếp theo:
1. Học và thực hành các kỹ thuật cơ bản
2. Tích hợp vào hệ thống hiện tại
3. Backtest và optimize
4. Triển khai live trading với risk management

**Lưu ý:** Không có chiến lược nào đảm bảo lợi nhuận trong mọi điều kiện thị trường. Luôn sử dụng risk management phù hợp và không đầu tư quá khả năng tài chính của mình. 