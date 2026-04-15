#!/usr/bin/env python3
"""
Trading Examples MT5 TimeFrame - Streamlit App
Ứng dụng web tương tác cho Trading Bot với MT5 và nhiều TimeFrame
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sys
import os
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import MetaTrader5 as mt5

# Import trading functions từ file gốc
import importlib.util
spec = importlib.util.spec_from_file_location(
    "trading_examples_timeframe", 
    "Trading Examples MT5 TimeFrame.py"
)
trading_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trading_module)

# Import các hàm cần thiết
loaddataMT5 = trading_module.loaddataMT5
calculate_technical_indicators = trading_module.calculate_technical_indicators
simple_ma_strategy = trading_module.simple_ma_strategy
rsi_strategy = trading_module.rsi_strategy
macd_strategy = trading_module.macd_strategy
dataframe_to_signals = trading_module.dataframe_to_signals
BacktestEngine = trading_module.BacktestEngine
TradingSignal = trading_module.TradingSignal

# Thiết lập trang
st.set_page_config(
    page_title="Trading Bot MT5 TimeFrame - Streamlit",
    page_icon="⏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS tùy chỉnh
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .strategy-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
    }
    .timeframe-card {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .profit-history-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #28a745;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def get_timeframe_options():
    """Lấy danh sách các timeframe có sẵn"""
    return {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "M30": mt5.TIMEFRAME_M30,
        "H1": mt5.TIMEFRAME_H1,
        "H4": mt5.TIMEFRAME_H4,
        "D1": mt5.TIMEFRAME_D1,
        "W1": mt5.TIMEFRAME_W1,
        "MN1": mt5.TIMEFRAME_MN1
    }

def get_timeframe_days(timeframe_key: str) -> int:
    """Lấy số ngày phù hợp cho timeframe"""
    timeframe_days = {
        "M1": 1,
        "M5": 1,
        "M15": 1,
        "M30": 1,
        "H1": 1,
        "H4": 7,
        "D1": 100,
        "W1": 365,
        "MN1": 3650
    }
    return timeframe_days.get(timeframe_key, 100)

def get_trading_history(days_back: int = 100, symbol: str = None) -> pd.DataFrame:
    """Lấy lịch sử giao dịch từ MT5"""
    try:
        # Kết nối MT5
        if not mt5.initialize():
            st.error("❌ Không thể kết nối với MetaTrader5")
            return None
        
        # Tính thời gian
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Lấy lịch sử giao dịch
        print(f"Đang lấy lịch sử giao dịch {days_back} ngày gần nhất cho {symbol}...")
        print("==================")
        if symbol:
            print(f"📊 Đang lấy lịch sử giao dịch {days_back} ngày gần nhất cho {symbol}...")
            trades = mt5.history_deals_get(start_date, end_date, symbol=symbol)
            print("Trades:", trades)
        else:
            trades = mt5.history_deals_get(start_date, end_date)
            print("Trades:", trades)
        
        if trades is None:
            st.warning("⚠️ Không thể lấy dữ liệu giao dịch")
            return None
        
        # Chuyển đổi thành DataFrame
        data = pd.DataFrame([t._asdict() for t in trades])
        
        # Chuyển đổi timestamp
        if 'time' in data.columns:
            data['time'] = pd.to_datetime(data['time'], unit='s')
        
        return data
        
    except Exception as e:
        st.error(f"❌ Lỗi khi lấy lịch sử giao dịch: {str(e)}")
        return None

def analyze_profit_history(trades_df: pd.DataFrame) -> Dict:
    """Phân tích lịch sử lợi nhuận"""
    try:
        # Lọc các giao dịch có profit khác 0
        profit_trades = trades_df[trades_df['profit'] != 0]['profit']
        
        if len(profit_trades) == 0:
            return None
        
        # Phân loại giao dịch thắng/thua
        winning_trades = profit_trades[profit_trades > 0]
        losing_trades = profit_trades[profit_trades < 0]
        
        # Tính các chỉ số
        winning_count = len(winning_trades)
        losing_count = len(losing_trades)
        total_trades = len(profit_trades)
        
        win_rate = winning_count / total_trades if total_trades > 0 else 0
        loss_rate = losing_count / total_trades if total_trades > 0 else 0
        
        sum_win = winning_trades.sum() if len(winning_trades) > 0 else 0
        sum_loss = abs(losing_trades.sum()) if len(losing_trades) > 0 else 0
        
        avg_win = winning_trades.mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades.mean() if len(losing_trades) > 0 else 0
        
        # Profit Factor
        profit_factor = sum_win / sum_loss if sum_loss > 0 else 999.99  # Thay inf bằng giá trị lớn
        
        # Sharpe Ratio
        returns = profit_trades / 100  # Chuyển về decimal
        sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
        
        # Tổng lợi nhuận
        total_profit = profit_trades.sum()
        
        # Maximum Drawdown
        cumulative_profit = profit_trades.cumsum()
        running_max = cumulative_profit.expanding().max()
        drawdown = cumulative_profit - running_max
        max_drawdown = drawdown.min()
        
        return {
            'total_trades': total_trades,
            'winning_count': winning_count,
            'losing_count': losing_count,
            'win_rate': win_rate,
            'loss_rate': loss_rate,
            'sum_win': sum_win,
            'sum_loss': sum_loss,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'total_profit': total_profit,
            'max_drawdown': max_drawdown,
            'profit_trades': profit_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'cumulative_profit': cumulative_profit
        }
        
    except Exception as e:
        st.error(f"❌ Lỗi khi phân tích lợi nhuận: {str(e)}")
        return None

def calculate_daily_profit(trades_df: pd.DataFrame) -> pd.DataFrame:
    """Tính toán lợi nhuận theo ngày từ dữ liệu giao dịch"""
    try:
        # Lọc các giao dịch có profit khác 0
        data_profit = trades_df[trades_df['profit'] != 0].copy()
        
        if len(data_profit) == 0:
            return None
        
        # Chuyển đổi time thành datetime nếu chưa có
        if 'time' in data_profit.columns and not pd.api.types.is_datetime64_any_dtype(data_profit['time']):
            data_profit['time'] = pd.to_datetime(data_profit['time'], unit='s')
        
        # Thêm cột date
        data_profit['date'] = data_profit['time'].dt.date
        
        # Chỉ tính tổng các cột số, không tính tổng các cột datetime
        numeric_columns = ['profit', 'volume', 'price', 'price_trigger', 'price_order', 'price_current', 'price_stoplimit', 'swap', 'fee', 'magic', 'order', 'position_id', 'external_id']
        available_numeric_columns = [col for col in numeric_columns if col in data_profit.columns]
        
        # Tính tổng theo ngày
        data_profit_daily = data_profit.groupby('date')[available_numeric_columns].sum()
        
        # Thêm các cột thống kê
        data_profit_daily['trade_count'] = data_profit.groupby('date').size()
        data_profit_daily['winning_trades'] = data_profit[data_profit['profit'] > 0].groupby('date').size()
        data_profit_daily['losing_trades'] = data_profit[data_profit['profit'] < 0].groupby('date').size()
        
        # Tính tỷ lệ thắng theo ngày
        data_profit_daily['win_rate'] = (data_profit_daily['winning_trades'] / data_profit_daily['trade_count']).fillna(0)
        
        # Tính lợi nhuận tích lũy
        data_profit_daily['cumulative_profit'] = data_profit_daily['profit'].cumsum()
        
        # Tính drawdown
        running_max = data_profit_daily['cumulative_profit'].expanding().max()
        data_profit_daily['drawdown'] = data_profit_daily['cumulative_profit'] - running_max
        
        return data_profit_daily
        
    except Exception as e:
        st.error(f"❌ Lỗi khi tính toán lợi nhuận hàng ngày: {str(e)}")
        return None

def display_daily_profit_table(trades_df: pd.DataFrame, selected_symbol: str):
    """Hiển thị bảng lợi nhuận hàng ngày"""
    st.subheader("📅 Lợi nhuận theo ngày")
    
    # Tính toán lợi nhuận hàng ngày
    daily_profit_df = calculate_daily_profit(trades_df)
    
    if daily_profit_df is None or len(daily_profit_df) == 0:
        st.warning("⚠️ Không có dữ liệu lợi nhuận hàng ngày để hiển thị")
        return
    
    # Tạo bảng hiển thị
    display_columns = ['trade_count', 'winning_trades', 'losing_trades', 'win_rate', 'profit', 'cumulative_profit', 'drawdown']
    available_columns = [col for col in display_columns if col in daily_profit_df.columns]
    
    display_df = daily_profit_df[available_columns].copy()
    
    # Đổi tên cột
    column_mapping = {
        'trade_count': 'Số giao dịch',
        'winning_trades': 'Giao dịch thắng',
        'losing_trades': 'Giao dịch thua',
        'win_rate': 'Tỷ lệ thắng',
        'profit': 'Lợi nhuận ngày',
        'cumulative_profit': 'Lợi nhuận tích lũy',
        'drawdown': 'Drawdown'
    }
    
    display_df = display_df.rename(columns=column_mapping)
    
    # Format các cột
    if 'Tỷ lệ thắng' in display_df.columns:
        display_df['Tỷ lệ thắng'] = display_df['Tỷ lệ thắng'].apply(lambda x: f"{x:.1%}")
    
    if 'Lợi nhuận ngày' in display_df.columns:
        display_df['Lợi nhuận ngày'] = display_df['Lợi nhuận ngày'].apply(lambda x: f"{x:,.2f}")
    
    if 'Lợi nhuận tích lũy' in display_df.columns:
        display_df['Lợi nhuận tích lũy'] = display_df['Lợi nhuận tích lũy'].apply(lambda x: f"{x:,.2f}")
    
    if 'Drawdown' in display_df.columns:
        display_df['Drawdown'] = display_df['Drawdown'].apply(lambda x: f"{x:,.2f}")
    
    # Sắp xếp theo ngày (mới nhất trước)
    display_df = display_df.sort_index(ascending=False)
    
    # Hiển thị bảng
    st.dataframe(display_df, use_container_width=True)
    
    # Tải xuống dữ liệu
    csv = daily_profit_df.to_csv()
    st.download_button(
        label="📥 Tải xuống dữ liệu lợi nhuận hàng ngày",
        data=csv,
        file_name=f"daily_profit_{selected_symbol}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    
    # Biểu đồ lợi nhuận hàng ngày
    st.subheader("📈 Biểu đồ lợi nhuận hàng ngày")
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Lợi nhuận theo ngày',
            'Lợi nhuận tích lũy',
            'Số giao dịch theo ngày',
            'Tỷ lệ thắng theo ngày'
        ),
        specs=[
            [{"secondary_y": False}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": False}]
        ]
    )
    
    # 1. Lợi nhuận theo ngày
    fig.add_trace(
        go.Bar(
            x=daily_profit_df.index,
            y=daily_profit_df['profit'],
            name='Lợi nhuận ngày',
            marker_color=['green' if x > 0 else 'red' for x in daily_profit_df['profit']]
        ),
        row=1, col=1
    )
    
    # 2. Lợi nhuận tích lũy
    fig.add_trace(
        go.Scatter(
            x=daily_profit_df.index,
            y=daily_profit_df['cumulative_profit'],
            mode='lines',
            name='Lợi nhuận tích lũy',
            line=dict(color='green', width=2)
        ),
        row=1, col=2
    )
    
    # 3. Số giao dịch theo ngày
    fig.add_trace(
        go.Bar(
            x=daily_profit_df.index,
            y=daily_profit_df['trade_count'],
            name='Số giao dịch',
            marker_color='blue',
            opacity=0.7
        ),
        row=2, col=1
    )
    
    # 4. Tỷ lệ thắng theo ngày
    fig.add_trace(
        go.Scatter(
            x=daily_profit_df.index,
            y=daily_profit_df['win_rate'] * 100,
            mode='lines+markers',
            name='Tỷ lệ thắng (%)',
            line=dict(color='purple', width=2)
        ),
        row=2, col=2
    )
    
    # Thêm đường tham chiếu 50%
    fig.add_hline(y=50, line_dash="dash", line_color="gray", 
                  annotation_text="50%", row=2, col=2)
    
    # Cập nhật layout
    fig.update_layout(
        title=f'Phân tích lợi nhuận hàng ngày - {selected_symbol}',
        height=600,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_profit_history(selected_symbol: str, days_back: int, backtest_results: Dict = None):
    """Hiển thị lịch sử lợi nhuận"""
    st.header("💰 Lịch sử lợi nhuận")
    
    # Lấy lịch sử giao dịch
    with st.spinner(f"Đang tải lịch sử giao dịch {days_back} ngày gần nhất..."):
        trades_df = get_trading_history(days_back, selected_symbol)
    
    if trades_df is None or len(trades_df) == 0:
        st.warning("⚠️ Không có dữ liệu giao dịch để phân tích")
        return
    
    # Phân tích lợi nhuận
    analysis = analyze_profit_history(trades_df)
    
    if analysis is None:
        st.warning("⚠️ Không có giao dịch có lợi nhuận để phân tích")
        return
    
    # Hiển thị thống kê tổng quan
    st.subheader("📊 Thống kê tổng quan")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="profit-history-card">', unsafe_allow_html=True)
        st.metric(
            "Tổng giao dịch",
            analysis['total_trades']
        )
        st.metric(
            "Tổng lợi nhuận",
            f"{analysis['total_profit']:,.2f} USD"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="profit-history-card">', unsafe_allow_html=True)
        st.metric(
            "Giao dịch thắng",
            analysis['winning_count'],
            f"{analysis['win_rate']:.1%}"
        )
        st.metric(
            "Giao dịch thua",
            analysis['losing_count'],
            f"{analysis['loss_rate']:.1%}"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="profit-history-card">', unsafe_allow_html=True)
        st.metric(
            "Lợi nhuận TB thắng",
            f"{analysis['avg_win']:.2f} USD"
        )
        st.metric(
            "Lỗ TB thua",
            f"{analysis['avg_loss']:.2f} USD"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="profit-history-card">', unsafe_allow_html=True)
        st.metric(
            "Profit Factor",
            f"{analysis['profit_factor']:.2f}"
        )
        st.metric(
            "Sharpe Ratio",
            f"{analysis['sharpe_ratio']:.2f}"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Biểu đồ phân tích
    st.subheader("📈 Biểu đồ phân tích")
    
    # Tạo subplot layout
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Lợi nhuận tích lũy',
            'Phân bố lợi nhuận',
            'Drawdown',
            'So sánh thắng/thua'
        ),
        specs=[
            [{"secondary_y": False}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": False}]
        ]
    )
    
    # 1. Lợi nhuận tích lũy
    if len(analysis['cumulative_profit']) > 0:
        fig.add_trace(
            go.Scatter(
                x=analysis['cumulative_profit'].index,
                y=analysis['cumulative_profit'],
                mode='lines',
                name='Lợi nhuận tích lũy',
                line=dict(color='green', width=2)
            ),
            row=1, col=1
        )
    
    # 2. Phân bố lợi nhuận
    fig.add_trace(
        go.Histogram(
            x=analysis['profit_trades'],
            nbinsx=30,
            name='Phân bố lợi nhuận',
            marker_color='blue',
            opacity=0.7
        ),
        row=1, col=2
    )
    
    # 3. Drawdown
    if len(analysis['cumulative_profit']) > 0:
        cumulative_profit = analysis['cumulative_profit']
        running_max = cumulative_profit.expanding().max()
        drawdown = cumulative_profit - running_max
        
        fig.add_trace(
            go.Scatter(
                x=drawdown.index,
                y=drawdown,
                mode='lines',
                name='Drawdown',
                line=dict(color='red', width=2),
                fill='tonexty',
                fillcolor='rgba(255,0,0,0.1)'
            ),
            row=2, col=1
        )
    
    # 4. So sánh thắng/thua
    fig.add_trace(
        go.Bar(
            x=['Thắng', 'Thua'],
            y=[analysis['winning_count'], analysis['losing_count']],
            name='Số lượng giao dịch',
            marker_color=['green', 'red']
        ),
        row=2, col=2
    )
    
    # Cập nhật layout
    fig.update_layout(
        title=f'Phân tích lịch sử lợi nhuận - {selected_symbol}',
        height=600,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Bảng chi tiết giao dịch
    st.subheader("📋 Chi tiết giao dịch")
    
    # Tùy chọn lọc
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_profit = st.selectbox(
            "Lọc theo lợi nhuận:",
            ["Tất cả", "Chỉ thắng", "Chỉ thua"],
            help="Lọc giao dịch theo kết quả"
        )
    
    with col2:
        min_profit = st.number_input(
            "Lợi nhuận tối thiểu (USD):",
            value=0.0,
            step=0.1,
            help="Chỉ hiển thị giao dịch có lợi nhuận >= giá trị này"
        )
    
    with col3:
        max_profit = st.number_input(
            "Lợi nhuận tối đa (USD):",
            value=999999.0,
            step=0.1,
            help="Chỉ hiển thị giao dịch có lợi nhuận <= giá trị này (999999 = không giới hạn)"
        )
    
    # Lọc và hiển thị các giao dịch có lợi nhuận
    profit_trades_df = trades_df[trades_df['profit'] != 0].copy()
    
    # Áp dụng bộ lọc
    if filter_profit == "Chỉ thắng":
        profit_trades_df = profit_trades_df[profit_trades_df['profit'] > 0]
    elif filter_profit == "Chỉ thua":
        profit_trades_df = profit_trades_df[profit_trades_df['profit'] < 0]
    
    if min_profit != 0:
        profit_trades_df = profit_trades_df[profit_trades_df['profit'] >= min_profit]
    
    if max_profit != 999999.0:
        profit_trades_df = profit_trades_df[profit_trades_df['profit'] <= max_profit]
    
    if len(profit_trades_df) > 0:
        # Chọn các cột quan trọng
        display_columns = ['time', 'symbol', 'volume', 'price', 'profit', 'type', 'magic']
        
        # Lọc các cột có sẵn
        available_columns = [col for col in display_columns if col in profit_trades_df.columns]
        
        # Tạo DataFrame hiển thị
        display_df = profit_trades_df[available_columns].copy()
        
        # Đổi tên cột
        column_mapping = {
            'time': 'Thời gian',
            'symbol': 'Cặp tiền',
            'volume': 'Khối lượng',
            'price': 'Giá',
            'profit': 'Lợi nhuận',
            'type': 'Loại',
            'magic': 'Magic Number'
        }
        
        display_df = display_df.rename(columns=column_mapping)
        
        # Format thời gian
        if 'Thời gian' in display_df.columns:
            display_df['Thời gian'] = display_df['Thời gian'].dt.strftime('%Y-%m-%d %H:%M')
        
        # Format lợi nhuận
        if 'Lợi nhuận' in display_df.columns:
            display_df['Lợi nhuận'] = display_df['Lợi nhuận'].apply(lambda x: f"{x:,.2f}")
        
        # Sắp xếp theo thời gian (mới nhất trước)
        display_df = display_df.sort_values('Thời gian', ascending=False)
        
        # Hiển thị bảng
        st.dataframe(display_df.head(20), use_container_width=True)
        
        # Tải xuống dữ liệu
        csv = profit_trades_df.to_csv(index=False)
        st.download_button(
            label="📥 Tải xuống dữ liệu giao dịch",
            data=csv,
            file_name=f"trading_history_{selected_symbol}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    else:
        st.info("Không có giao dịch có lợi nhuận để hiển thị")
    
    # So sánh với kết quả backtest (nếu có)
    if backtest_results and analysis:
        st.subheader("🔄 So sánh Backtest vs Thực tế")
        
        comparison_data = {
            'Chỉ số': ['Tổng lợi nhuận (%)', 'Tỷ lệ thắng (%)', 'Số giao dịch', 'Drawdown tối đa (%)'],
            'Backtest': [
                f"{backtest_results['total_return_pct']:.2f}%",
                f"{backtest_results['win_rate']*100:.1f}%",
                backtest_results['trade_count'],
                f"{backtest_results['max_drawdown_pct']:.2f}%"
            ],
            'Thực tế': [
                f"{(analysis['total_profit'] / 10000) * 100:.2f}%" if analysis['total_profit'] != 0 else "0.00%",
                f"{analysis['win_rate']*100:.1f}%",
                analysis['total_trades'],
                f"{(analysis['max_drawdown'] / 10000) * 100:.2f}%" if analysis['max_drawdown'] != 0 else "0.00%"
            ]
        }
        
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True)
        
        # Nhận xét
        st.info("💡 **Lưu ý**: So sánh này chỉ mang tính tham khảo. Kết quả backtest và thực tế có thể khác nhau do nhiều yếu tố như spread, slippage, và điều kiện thị trường.")
    
    # Hiển thị bảng lợi nhuận hàng ngày
    display_daily_profit_table(trades_df, selected_symbol)
    
    # Tóm tắt và nhận xét
    if analysis:
        st.subheader("📝 Tóm tắt và Nhận xét")
        
        # Đánh giá hiệu suất
        performance_rating = "🟢 Tốt" if analysis['win_rate'] > 0.6 and analysis['profit_factor'] > 1.5 else \
                            "🟡 Trung bình" if analysis['win_rate'] > 0.5 and analysis['profit_factor'] > 1.0 else \
                            "🔴 Cần cải thiện"
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 Đánh giá hiệu suất:**")
            st.write(f"- Xếp hạng: {performance_rating}")
            st.write(f"- Tỷ lệ thắng: {analysis['win_rate']:.1%}")
            st.write(f"- Profit Factor: {analysis['profit_factor']:.2f}")
            st.write(f"- Sharpe Ratio: {analysis['sharpe_ratio']:.2f}")
        
        with col2:
            st.markdown("**💡 Khuyến nghị:**")
            if analysis['win_rate'] < 0.5:
                st.write("- Cần cải thiện tỷ lệ thắng")
            if analysis['profit_factor'] < 1.0:
                st.write("- Cần tối ưu hóa risk/reward ratio")
            if analysis['sharpe_ratio'] < 1.0:
                st.write("- Cần giảm thiểu biến động lợi nhuận")
            if analysis['max_drawdown'] < -0.1:
                st.write("- Cần quản lý rủi ro tốt hơn")
        
        # Thống kê theo thời gian
        if 'time' in trades_df.columns:
            st.markdown("**📅 Thống kê theo thời gian:**")
            
            # Thống kê theo ngày
            trades_df['date'] = trades_df['time'].dt.date
            daily_stats = trades_df[trades_df['profit'] != 0].groupby('date').agg({
                'profit': ['count', 'sum', 'mean']
            }).round(2)
            
            daily_stats.columns = ['Số giao dịch', 'Tổng lợi nhuận', 'Lợi nhuận TB']
            st.dataframe(daily_stats.tail(10), use_container_width=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">⏰ Trading Bot MT5 TimeFrame - Streamlit</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar - Cấu hình
    st.sidebar.header("⚙️ Cấu hình")
    
    # Chọn symbol
    symbol_options = {
        "EURUSD.sml": "EUR/USD",
        "GBPUSD.sml": "GBP/USD", 
        "USDJPY.sml": "USD/JPY",
        "AUDUSD.sml": "AUD/USD",
        "USDCAD.sml": "USD/CAD"
    }
    
    selected_symbol = st.sidebar.selectbox(
        "Chọn cặp tiền tệ:",
        list(symbol_options.keys()),
        format_func=lambda x: symbol_options[x]
    )
    
    # Chọn TimeFrame
    timeframe_options = get_timeframe_options()
    selected_timeframe_key = st.sidebar.selectbox(
        "Chọn TimeFrame:",
        list(timeframe_options.keys()),
        help="M1=1 phút, M5=5 phút, M15=15 phút, M30=30 phút, H1=1 giờ, H4=4 giờ, D1=1 ngày, W1=1 tuần, MN1=1 tháng"
    )
    
    selected_timeframe = timeframe_options[selected_timeframe_key]
    
    # Hiển thị thông tin TimeFrame
    st.sidebar.markdown('<div class="timeframe-card">', unsafe_allow_html=True)
    st.sidebar.subheader(f"⏰ TimeFrame: {selected_timeframe_key}")
    
    timeframe_info = {
        "M1": "1 phút - Scalping",
        "M5": "5 phút - Scalping",
        "M15": "15 phút - Day Trading",
        "M30": "30 phút - Day Trading", 
        "H1": "1 giờ - Swing Trading",
        "H4": "4 giờ - Swing Trading",
        "D1": "1 ngày - Position Trading",
        "W1": "1 tuần - Long-term",
        "MN1": "1 tháng - Long-term"
    }
    
    st.sidebar.info(timeframe_info[selected_timeframe_key])
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Số ngày dữ liệu (tự động điều chỉnh theo timeframe)
    default_days = get_timeframe_days(selected_timeframe_key)
    max_days = default_days * 10  # Tăng gấp 10 lần để có nhiều dữ liệu
    
    days = st.sidebar.slider(
        "Số ngày dữ liệu:", 
        1, max_days, default_days,
        help=f"Khuyến nghị: {default_days} ngày cho {selected_timeframe_key}"
    )
    
    # Số dư ban đầu
    initial_balance = st.sidebar.number_input(
        "Số dư ban đầu (USD):",
        min_value=1000,
        max_value=1000000,
        value=10000,
        step=1000
    )
    
    # Chọn chiến lược
    strategy_options = {
        "MA": "Moving Average",
        "RSI": "RSI Strategy", 
        "MACD": "MACD Strategy",
        "ALL": "Tất cả chiến lược"
    }
    
    selected_strategy = st.sidebar.selectbox(
        "Chọn chiến lược:",
        list(strategy_options.keys()),
        format_func=lambda x: strategy_options[x]
    )
    
    # Tùy chọn hiển thị lịch sử lợi nhuận
    show_profit_history = st.sidebar.checkbox(
        "💰 Hiển thị lịch sử lợi nhuận",
        help="Hiển thị phân tích lịch sử giao dịch thực tế từ MT5"
    )
    
    # Tùy chọn hiển thị bảng lợi nhuận hàng ngày
    show_daily_profit = st.sidebar.checkbox(
        "📅 Hiển thị lợi nhuận hàng ngày",
        help="Hiển thị bảng và biểu đồ lợi nhuận theo ngày"
    )
    
    # Nút chạy phân tích
    run_analysis = st.sidebar.button("🚀 Chạy phân tích", type="primary")
    
    if run_analysis:
        with st.spinner(f"Đang tải dữ liệu {selected_timeframe_key} và phân tích..."):
            try:
                # 1. Lấy dữ liệu
                st.header(f"📊 Dữ liệu thị trường - {selected_timeframe_key}")
                
                df = loaddataMT5(selected_symbol, days, selected_timeframe)
                current_price = float(df['Close'].iloc[-1])
                
                # Hiển thị thông tin cơ bản
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Giá hiện tại",
                        f"{current_price:.5f}",
                        f"{df['Close'].pct_change().iloc[-1]*100:.2f}%"
                    )
                
                with col2:
                    st.metric(
                        "Giá cao nhất",
                        f"{df['High'].max():.5f}"
                    )
                
                with col3:
                    st.metric(
                        "Giá thấp nhất", 
                        f"{df['Low'].min():.5f}"
                    )
                
                with col4:
                    st.metric(
                        "Khối lượng TB",
                        f"{df['Volume'].mean():,.0f}"
                    )
                
                # Thông tin timeframe
                st.info(f"📈 TimeFrame: {selected_timeframe_key} | Dữ liệu: {len(df)} nến | Từ {df.index[0].strftime('%Y-%m-%d %H:%M')} đến {df.index[-1].strftime('%Y-%m-%d %H:%M')}")
                
                # 2. Tính toán chỉ báo kỹ thuật
                st.header("📈 Chỉ báo kỹ thuật")
                
                df = calculate_technical_indicators(df)
                
                # Hiển thị biểu đồ giá
                fig_price = go.Figure()
                
                fig_price.add_trace(go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name='Candlestick',
                    increasing_line_color='green',
                    decreasing_line_color='red'
                ))
                
                fig_price.add_trace(go.Scatter(
                    x=df.index, y=df['SMA_5'],
                    mode='lines', name='SMA 5',
                    line=dict(color='orange', width=1, dash='dash')
                ))
                
                fig_price.add_trace(go.Scatter(
                    x=df.index, y=df['SMA_20'],
                    mode='lines', name='SMA 20',
                    line=dict(color='red', width=1, dash='dash')
                ))
                
                fig_price.update_layout(
                    title=f"Biểu đồ giá {symbol_options[selected_symbol]} - {selected_timeframe_key}",
                    xaxis_title="Thời gian",
                    yaxis_title="Giá",
                    height=500
                )
                
                st.plotly_chart(fig_price, use_container_width=True)
                
                # 3. Tạo tín hiệu giao dịch
                st.header("🎯 Tín hiệu giao dịch")
                
                # Tạo DataFrame riêng cho từng chiến lược
                df_ma = df.copy()
                df_rsi = df.copy()
                df_macd = df.copy()
                
                # Áp dụng các chiến lược
                df_ma = simple_ma_strategy(df_ma)
                df_rsi = rsi_strategy(df_rsi)
                df_macd = macd_strategy(df_macd)
                
                # Thống kê tín hiệu
                ma_buy_count = df_ma['Buy_Signal'].sum()
                ma_sell_count = df_ma['Sell_Signal'].sum()
                rsi_buy_count = df_rsi['Buy_Signal'].sum()
                rsi_sell_count = df_rsi['Sell_Signal'].sum()
                macd_buy_count = df_macd['Buy_Signal'].sum()
                macd_sell_count = df_macd['Sell_Signal'].sum()
                
                # Hiển thị thống kê
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown('<div class="strategy-card">', unsafe_allow_html=True)
                    st.subheader("📊 MA Strategy")
                    st.metric("BUY Signals", ma_buy_count)
                    st.metric("SELL Signals", ma_sell_count)
                    st.metric("Tổng", ma_buy_count + ma_sell_count)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="strategy-card">', unsafe_allow_html=True)
                    st.subheader("📊 RSI Strategy")
                    st.metric("BUY Signals", rsi_buy_count)
                    st.metric("SELL Signals", rsi_sell_count)
                    st.metric("Tổng", rsi_buy_count + rsi_sell_count)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col3:
                    st.markdown('<div class="strategy-card">', unsafe_allow_html=True)
                    st.subheader("📊 MACD Strategy")
                    st.metric("BUY Signals", macd_buy_count)
                    st.metric("SELL Signals", macd_sell_count)
                    st.metric("Tổng", macd_buy_count + macd_sell_count)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # 4. Chọn chiến lược để hiển thị chi tiết
                if selected_strategy == "ALL":
                    # Hiển thị tất cả chiến lược
                    st.subheader("📋 Chi tiết tín hiệu - Tất cả chiến lược")
                    
                    # Tạo tabs cho từng chiến lược
                    tab1, tab2, tab3 = st.tabs(["MA Strategy", "RSI Strategy", "MACD Strategy"])
                    
                    with tab1:
                        display_signals(df_ma, "Moving Average", selected_timeframe_key)
                    
                    with tab2:
                        display_signals(df_rsi, "RSI", selected_timeframe_key)
                    
                    with tab3:
                        display_signals(df_macd, "MACD", selected_timeframe_key)
                    
                    # Chọn chiến lược có nhiều tín hiệu nhất để backtest
                    strategy_counts = {
                        "MA": ma_buy_count + ma_sell_count,
                        "RSI": rsi_buy_count + rsi_sell_count,
                        "MACD": macd_buy_count + macd_sell_count
                    }
                    best_strategy = max(strategy_counts, key=strategy_counts.get)
                    
                    if best_strategy == "MA":
                        display_df = df_ma
                        strategy_name = "Moving Average"
                    elif best_strategy == "RSI":
                        display_df = df_rsi
                        strategy_name = "RSI"
                    else:
                        display_df = df_macd
                        strategy_name = "MACD"
                    
                    st.info(f"🎯 Chiến lược được chọn để backtest: {strategy_name} (có {strategy_counts[best_strategy]} tín hiệu)")
                    
                else:
                    # Hiển thị chiến lược được chọn
                    if selected_strategy == "MA":
                        display_df = df_ma
                        strategy_name = "Moving Average"
                    elif selected_strategy == "RSI":
                        display_df = df_rsi
                        strategy_name = "RSI"
                    else:
                        display_df = df_macd
                        strategy_name = "MACD"
                    
                    st.subheader(f"📋 Chi tiết tín hiệu - {strategy_name}")
                    display_signals(display_df, strategy_name, selected_timeframe_key)
                
                # 5. Backtest
                st.header("💰 Kết quả Backtest")
                
                signals = dataframe_to_signals(display_df, selected_symbol)
                
                if signals:
                    # Khởi tạo backtest engine
                    backtest_engine = BacktestEngine(initial_balance=initial_balance)
                    
                    # Chạy backtest
                    backtest_engine.run_backtest(display_df, signals)
                    
                    # Lấy kết quả
                    results = backtest_engine.get_results()
                    
                    # Hiển thị kết quả
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "Tổng lợi nhuận",
                            f"{results['total_return_pct']:.2f}%",
                            f"{results['final_equity'] - results['initial_balance']:,.0f} USD"
                        )
                    
                    with col2:
                        st.metric(
                            "Số giao dịch",
                            results['trade_count']
                        )
                    
                    with col3:
                        st.metric(
                            "Tỷ lệ thắng",
                            f"{results['win_rate']*100:.1f}%"
                        )
                    
                    with col4:
                        st.metric(
                            "Drawdown tối đa",
                            f"{results['max_drawdown_pct']:.2f}%"
                        )
                    
                    # Biểu đồ equity curve
                    if results['equity_curve']:
                        fig_equity = go.Figure()
                        
                        fig_equity.add_trace(go.Scatter(
                            x=df.index[:len(results['equity_curve'])],
                            y=results['equity_curve'],
                            mode='lines',
                            name='Equity Curve',
                            line=dict(color='green', width=2)
                        ))
                        
                        fig_equity.update_layout(
                            title=f"Đường cong Equity - {selected_timeframe_key}",
                            xaxis_title="Thời gian",
                            yaxis_title="Equity (USD)",
                            height=400
                        )
                        
                        st.plotly_chart(fig_equity, use_container_width=True)
                    
                    # Bảng chi tiết giao dịch
                    if backtest_engine.trades:
                        st.subheader("📋 Chi tiết giao dịch")
                        
                        trades_data = []
                        for trade in backtest_engine.trades:
                            trades_data.append({
                                "Thời gian vào": trade.entry_date.strftime('%Y-%m-%d %H:%M'),
                                "Thời gian ra": trade.exit_date.strftime('%Y-%m-%d %H:%M') if trade.exit_date else "Đang mở",
                                "Loại": trade.side,
                                "Số lượng": trade.quantity,
                                "Giá vào": f"{trade.entry_price:.5f}",
                                "Giá ra": f"{trade.exit_price:.5f}" if trade.exit_price else "N/A",
                                "P&L": f"{trade.pnl:,.2f}" if trade.pnl else "N/A",
                                "P&L %": f"{trade.pnl_pct:.2f}%" if trade.pnl_pct else "N/A"
                            })
                        
                        trades_df = pd.DataFrame(trades_data)
                        st.dataframe(trades_df, use_container_width=True)
                
                else:
                    st.warning("⚠️ Không có tín hiệu giao dịch để backtest")
                
                # 6. Biểu đồ phân tích chi tiết
                if signals:
                    st.header("📊 Phân tích chi tiết")
                    
                    # Tạo subplot layout
                    fig = make_subplots(
                        rows=3, cols=2,
                        subplot_titles=(
                            'Candlestick và Tín hiệu giao dịch',
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
                    
                    # 1. Candlestick Chart
                    fig.add_trace(
                        go.Candlestick(
                            x=df.index,
                            open=df['Open'],
                            high=df['High'],
                            low=df['Low'],
                            close=df['Close'],
                            name='Candlestick',
                            increasing_line_color='green',
                            decreasing_line_color='red'
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
                    
                    # 4. Bollinger Bands
                    fig.add_trace(
                        go.Candlestick(
                            x=df.index,
                            open=df['Open'],
                            high=df['High'],
                            low=df['Low'],
                            close=df['Close'],
                            name='Candlestick',
                            increasing_line_color='green',
                            decreasing_line_color='red'
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
                    if results['equity_curve']:
                        fig.add_trace(
                            go.Scatter(
                                x=df.index[:len(results['equity_curve'])],
                                y=results['equity_curve'],
                                mode='lines', name='Equity',
                                line=dict(color='green', width=2)
                            ),
                            row=3, col=2
                        )
                    
                    # Cập nhật layout
                    fig.update_layout(
                        title=f'Phân tích Trading Strategy - {symbol_options[selected_symbol]} ({selected_timeframe_key})',
                        height=1200,
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # 7. Hiển thị lịch sử lợi nhuận (nếu được chọn)
                if show_profit_history:
                    st.markdown("---")
                    # Lấy kết quả backtest nếu có
                    backtest_results_for_comparison = None
                    if signals and 'results' in locals():
                        backtest_results_for_comparison = results
                    display_profit_history(selected_symbol, days, backtest_results_for_comparison)
                
                # 8. Hiển thị bảng lợi nhuận hàng ngày (nếu được chọn)
                if show_daily_profit:
                    st.markdown("---")
                    st.header("📅 Phân tích lợi nhuận hàng ngày")
                    
                    # Lấy lịch sử giao dịch
                    with st.spinner(f"Đang tải lịch sử giao dịch {days} ngày gần nhất..."):
                        trades_df = get_trading_history(days, selected_symbol)
                    
                    if trades_df is not None and len(trades_df) > 0:
                        display_daily_profit_table(trades_df, selected_symbol)
                    else:
                        st.warning("⚠️ Không có dữ liệu giao dịch để phân tích lợi nhuận hàng ngày")
                
            except Exception as e:
                st.error(f"❌ Lỗi: {str(e)}")
                st.info("💡 Hãy kiểm tra lại cấu hình và thử lại")
    
    else:
        # Hiển thị hướng dẫn khi chưa chạy
        st.info("👈 Vui lòng cấu hình các tham số ở sidebar và nhấn 'Chạy phân tích' để bắt đầu")
        
        # Hiển thị thông tin về ứng dụng
        st.markdown("""
        ## 🎯 Tính năng chính
        
        - **⏰ TimeFrame linh hoạt**: M1, M5, M15, M30, H1, H4, D1, W1, MN1
        - **📊 Dữ liệu thực**: Lấy từ MetaTrader 5
        - **📈 Chỉ báo kỹ thuật**: SMA, EMA, MACD, RSI, Bollinger Bands
        - **🎯 Chiến lược giao dịch**: MA, RSI, MACD
        - **💰 Backtest**: Mô phỏng giao dịch với kết quả chi tiết
        - **📊 Biểu đồ tương tác**: Candlestick, indicators, equity curve
        - **💰 Lịch sử lợi nhuận**: Phân tích giao dịch thực tế từ MT5
        - **📅 Lợi nhuận hàng ngày**: Bảng và biểu đồ lợi nhuận theo ngày
        - **🔄 So sánh Backtest vs Thực tế**: Đối chiếu kết quả mô phỏng và thực tế
        
        ## 🚀 Cách sử dụng
        
        1. Chọn cặp tiền tệ từ dropdown
        2. Chọn TimeFrame phù hợp với chiến lược
        3. Điều chỉnh số ngày dữ liệu
        4. Nhập số dư ban đầu
        5. Chọn chiến lược giao dịch
        6. Tích chọn "Hiển thị lịch sử lợi nhuận" (tùy chọn)
        7. Tích chọn "Hiển thị lợi nhuận hàng ngày" (tùy chọn)
        8. Nhấn "Chạy phân tích"
        
        ## ⏰ TimeFrame và Chiến lược
        
        - **M1-M5**: Scalping (giao dịch nhanh)
        - **M15-M30**: Day Trading (giao dịch trong ngày)
        - **H1-H4**: Swing Trading (giao dịch trung hạn)
        - **D1**: Position Trading (giao dịch dài hạn)
        - **W1-MN1**: Long-term (đầu tư dài hạn)
        """)

def display_signals(df, strategy_name, timeframe_key):
    """Hiển thị tín hiệu giao dịch"""
    
    # Đếm tín hiệu
    buy_count = df['Buy_Signal'].sum()
    sell_count = df['Sell_Signal'].sum()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("BUY Signals", buy_count)
    
    with col2:
        st.metric("SELL Signals", sell_count)
    
    # Hiển thị 10 tín hiệu gần nhất
    st.subheader("📋 10 tín hiệu gần nhất:")
    
    signals_data = []
    signal_count = 0
    
    for i in range(len(df)-1, -1, -1):  # Từ cuối lên đầu
        if signal_count >= 10:
            break
            
        if df['Buy_Signal'].iloc[i]:
            signals_data.append({
                "Thời gian": df.index[i].strftime('%Y-%m-%d %H:%M'),
                "Tín hiệu": "BUY",
                "Giá": f"{df['Close'].iloc[i]:.5f}",
                "Lý do": df['Signal_Reason'].iloc[i],
                "Độ tin cậy": f"{df['Signal_Confidence'].iloc[i]:.1%}"
            })
            signal_count += 1
        elif df['Sell_Signal'].iloc[i]:
            signals_data.append({
                "Thời gian": df.index[i].strftime('%Y-%m-%d %H:%M'),
                "Tín hiệu": "SELL", 
                "Giá": f"{df['Close'].iloc[i]:.5f}",
                "Lý do": df['Signal_Reason'].iloc[i],
                "Độ tin cậy": f"{df['Signal_Confidence'].iloc[i]:.1%}"
            })
            signal_count += 1
    
    if signals_data:
        signals_df = pd.DataFrame(signals_data)
        st.dataframe(signals_df, use_container_width=True)
    else:
        st.info("Không có tín hiệu giao dịch")

if __name__ == "__main__":
    main() 