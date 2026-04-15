#!/usr/bin/env python3
"""
Trading Examples - Streamlit App
Khóa AI Bot Autotrade Nâng Cao
"""

import streamlit as st
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

# Import các function từ file gốc
import sys
import os
sys.path.append(os.path.dirname(__file__))

# Import từ file Trading Examples.py
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("trading_examples", "Trading Examples.py")
    trading_examples = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(trading_examples)
    
    # Lấy các function từ module
    loaddataSSI = trading_examples.loaddataSSI
    calculate_technical_indicators = trading_examples.calculate_technical_indicators
    TradingSignal = trading_examples.TradingSignal
    simple_ma_strategy = trading_examples.simple_ma_strategy
    rsi_strategy = trading_examples.rsi_strategy
    macd_strategy = trading_examples.macd_strategy
    dataframe_to_signals = trading_examples.dataframe_to_signals
    BacktestEngine = trading_examples.BacktestEngine
    plot_trading_analysis = trading_examples.plot_trading_analysis
    print_backtest_summary = trading_examples.print_backtest_summary
    
except ImportError as e:
    st.error(f"Không thể import từ file Trading Examples.py: {e}")
    st.error("Vui lòng đảm bảo file tồn tại và có thể import được.")
    st.stop()

# Thiết lập trang
st.set_page_config(
    page_title="Trading Bot Analysis",
    page_icon="📈",
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
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🤖 Trading Bot Analysis</h1>', unsafe_allow_html=True)
    st.markdown("### Phân tích chiến lược giao dịch tự động với dữ liệu thực từ Chứng Khoán")
    
    # Sidebar - Cấu hình
    st.sidebar.header("⚙️ Cấu hình")
    
    # Chọn mã chứng khoán
    symbol = st.sidebar.text_input("Mã chứng khoán", value="VNM", help="Nhập mã chứng khoán (VD: VNM, VIC, FPT)")
    
    # Số ngày dữ liệu
    days = st.sidebar.slider("Số ngày dữ liệu", min_value=30, max_value=365, value=100, step=10)
    
    # Số dư ban đầu
    initial_balance = st.sidebar.number_input(
        "Số dư ban đầu (VND)", 
        min_value=1000000, 
        max_value=1000000000, 
        value=10000000, 
        step=1000000,
        format="%d"
    )
    
    # Chọn chiến lược
    st.sidebar.header("📊 Chiến lược giao dịch")
    
    strategy_options = {
        "Moving Average": "MA",
        "RSI": "RSI", 
        "MACD": "MACD",
        "Tất cả": "ALL"
    }
    
    selected_strategy = st.sidebar.selectbox(
        "Chọn chiến lược",
        options=list(strategy_options.keys()),
        index=0
    )
    
    # Tham số RSI
    if selected_strategy in ["RSI", "Tất cả"]:
        st.sidebar.subheader("RSI Parameters")
        rsi_oversold = st.sidebar.slider("RSI Oversold", min_value=10, max_value=40, value=30)
        rsi_overbought = st.sidebar.slider("RSI Overbought", min_value=60, max_value=90, value=70)
    
    # Tham số Moving Average
    if selected_strategy in ["Moving Average", "Tất cả"]:
        st.sidebar.subheader("MA Parameters")
        ma_short = st.sidebar.slider("MA ngắn hạn", min_value=3, max_value=20, value=5)
        ma_long = st.sidebar.slider("MA dài hạn", min_value=10, max_value=50, value=20)
    
    # Nút chạy
    run_button = st.sidebar.button("🚀 Chạy phân tích", type="primary")
    
    if run_button:
        with st.spinner("Đang tải dữ liệu và phân tích..."):
            try:
                # 1. Lấy dữ liệu
                st.header("📈 Dữ liệu thị trường")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.info(f"**Mã chứng khoán:** {symbol}")
                with col2:
                    st.info(f"**Số ngày:** {days}")
                with col3:
                    st.info(f"**Số dư:** {initial_balance:,.0f} VND")
                
                # Lấy dữ liệu
                df = loaddataSSI(symbol, days)
                
                if df is None or len(df) == 0:
                    st.error("Không thể lấy dữ liệu. Vui lòng kiểm tra lại mã chứng khoán.")
                    return
                
                # Hiển thị thông tin dữ liệu
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Ngày giao dịch", len(df))
                with col2:
                    st.metric("Giá hiện tại", f"{float(df['Close'].iloc[-1]):,.0f} VND")
                with col3:
                    price_change = ((df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
                    st.metric("Thay đổi (%)", f"{price_change:.2f}%")
                with col4:
                    st.metric("Volume TB", f"{df['Volume'].mean():,.0f}")
                
                # 2. Tính toán chỉ báo kỹ thuật
                st.header("🔧 Chỉ báo kỹ thuật")
                df = calculate_technical_indicators(df)
                
                # Hiển thị biểu đồ candlestick với MA
                fig_candlestick = go.Figure()
                
                # Candlestick
                fig_candlestick.add_trace(go.Candlestick(
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
                ))
                
                # Moving Averages
                fig_candlestick.add_trace(go.Scatter(
                    x=df.index, y=df['SMA_5'],
                    mode='lines', name='SMA 5',
                    line=dict(color='orange', width=2)
                ))
                fig_candlestick.add_trace(go.Scatter(
                    x=df.index, y=df['SMA_20'],
                    mode='lines', name='SMA 20',
                    line=dict(color='blue', width=2)
                ))
                
                fig_candlestick.update_layout(
                    title=f"Biểu đồ Candlestick {symbol} với Moving Averages",
                    xaxis_title="Ngày",
                    yaxis_title="Giá (VND)",
                    height=500
                )
                st.plotly_chart(fig_candlestick, use_container_width=True)
                
                # 3. Tạo tín hiệu giao dịch
                st.header("📊 Tín hiệu giao dịch")
                
                # Tạo bản sao DataFrame cho từng chiến lược
                df_ma = df.copy()
                df_rsi = df.copy()
                df_macd = df.copy()
                
                signals = []
                strategy_name = ""
                display_df = None
                
                if selected_strategy == "Moving Average":
                    df_ma = simple_ma_strategy(df_ma)
                    signals = dataframe_to_signals(df_ma, symbol)
                    strategy_name = "Moving Average"
                    display_df = df_ma
                elif selected_strategy == "RSI":
                    df_rsi = rsi_strategy(df_rsi, rsi_oversold, rsi_overbought)
                    signals = dataframe_to_signals(df_rsi, symbol)
                    strategy_name = "RSI"
                    display_df = df_rsi
                elif selected_strategy == "MACD":
                    df_macd = macd_strategy(df_macd)
                    signals = dataframe_to_signals(df_macd, symbol)
                    strategy_name = "MACD"
                    display_df = df_macd
                elif selected_strategy == "Tất cả":
                    # Chạy tất cả chiến lược
                    df_ma = simple_ma_strategy(df_ma)
                    df_rsi = rsi_strategy(df_rsi, rsi_oversold, rsi_overbought)
                    df_macd = macd_strategy(df_macd)
                    
                    # Đếm tín hiệu cho từng chiến lược
                    ma_buy = df_ma['Buy_Signal'].sum()
                    ma_sell = df_ma['Sell_Signal'].sum()
                    rsi_buy = df_rsi['Buy_Signal'].sum()
                    rsi_sell = df_rsi['Sell_Signal'].sum()
                    macd_buy = df_macd['Buy_Signal'].sum()
                    macd_sell = df_macd['Sell_Signal'].sum()
                    
                    # Hiển thị so sánh
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("MA Signals", f"Buy: {ma_buy}, Sell: {ma_sell}")
                    with col2:
                        st.metric("RSI Signals", f"Buy: {rsi_buy}, Sell: {rsi_sell}")
                    with col3:
                        st.metric("MACD Signals", f"Buy: {macd_buy}, Sell: {macd_sell}")
                    
                    # Chọn chiến lược tốt nhất để hiển thị (dựa trên số tín hiệu)
                    total_signals = {
                        'MA': ma_buy + ma_sell,
                        'RSI': rsi_buy + rsi_sell,
                        'MACD': macd_buy + macd_sell
                    }
                    best_strategy = max(total_signals, key=total_signals.get)
                    
                    if best_strategy == 'MA':
                        signals = dataframe_to_signals(df_ma, symbol)
                        strategy_name = "Moving Average"
                        display_df = df_ma
                    elif best_strategy == 'RSI':
                        signals = dataframe_to_signals(df_rsi, symbol)
                        strategy_name = "RSI"
                        display_df = df_rsi
                    else:
                        signals = dataframe_to_signals(df_macd, symbol)
                        strategy_name = "MACD"
                        display_df = df_macd
                
                # Hiển thị thống kê tín hiệu
                buy_signals = [s for s in signals if s.signal == "BUY"]
                sell_signals = [s for s in signals if s.signal == "SELL"]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Tín hiệu MUA", len(buy_signals), delta=len(buy_signals))
                with col2:
                    st.metric("Tín hiệu BÁN", len(sell_signals), delta=-len(sell_signals))
                
                # Hiển thị tín hiệu gần đây
                if signals:
                    st.subheader("📋 Tín hiệu gần đây")
                    recent_signals = signals[-10:]  # 10 tín hiệu gần nhất
                    signal_data = []
                    for signal in recent_signals:
                        signal_data.append({
                            'Ngày': signal.date.strftime('%Y-%m-%d'),
                            'Tín hiệu': signal.signal,
                            'Giá': f"{signal.price:,.0f}",
                            'Độ tin cậy': f"{signal.confidence:.2f}",
                            'Lý do': signal.reason
                        })
                    
                    if signal_data:
                        signal_df = pd.DataFrame(signal_data)
                        st.dataframe(signal_df, use_container_width=True)
                
                # 4. Chạy backtest
                st.header("💰 Kết quả Backtest")
                
                engine = BacktestEngine(initial_balance)
                engine.run_backtest(df, signals)
                results = engine.get_results()
                
                # Hiển thị kết quả
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric(
                        "Tổng lợi nhuận", 
                        f"{results['total_return_pct']:.2f}%",
                        delta=f"{results['total_return_pct']:.2f}%"
                    )
                with col2:
                    st.metric("Số giao dịch", results['trade_count'])
                with col3:
                    st.metric("Tỷ lệ thắng", f"{results['win_rate']*100:.1f}%")
                with col4:
                    st.metric("Drawdown tối đa", f"{results['max_drawdown_pct']:.2f}%")
                
                # Hiển thị chi tiết
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("📊 Chi tiết giao dịch")
                    st.write(f"**Số dư ban đầu:** {results['initial_balance']:,.0f} VND")
                    st.write(f"**Equity cuối:** {results['final_equity']:,.0f} VND")
                    st.write(f"**Lợi nhuận TB:** {results['avg_win']:,.0f} VND")
                    st.write(f"**Thua lỗ TB:** {results['avg_loss']:,.0f} VND")
                
                with col2:
                    st.subheader("📈 Equity Curve")
                    if 'equity_curve' in results and results['equity_curve']:
                        equity_df = pd.DataFrame({
                            'Date': df.index[:len(results['equity_curve'])],
                            'Equity': results['equity_curve']
                        })
                        
                        fig_equity = px.line(equity_df, x='Date', y='Equity', 
                                           title="Đường cong Equity")
                        fig_equity.update_layout(height=300)
                        st.plotly_chart(fig_equity, use_container_width=True)
                
                # 5. Biểu đồ phân tích chi tiết với candlestick
                st.header("📊 Phân tích chi tiết")
                
                if display_df is not None:
                    # Tạo biểu đồ với Plotly
                    fig = make_subplots(
                        rows=3, cols=2,
                        subplot_titles=(
                            'Candlestick và Tín hiệu giao dịch',
                            'RSI Indicator',
                            'MACD Indicator',
                            'Bollinger Bands với Candlestick',
                            'Volume',
                            'Equity Curve'
                        ),
                        specs=[
                            [{"secondary_y": False}, {"secondary_y": False}],
                            [{"secondary_y": False}, {"secondary_y": False}],
                            [{"secondary_y": False}, {"secondary_y": False}]
                        ],
                        vertical_spacing=0.08
                    )
                    
                    # 1. Candlestick và signals
                    fig.add_trace(
                        go.Candlestick(
                            x=display_df.index,
                            open=display_df['Open'],
                            high=display_df['High'],
                            low=display_df['Low'],
                            close=display_df['Close'],
                            name='Candlestick',
                            increasing_line_color='green',
                            decreasing_line_color='red',
                            increasing_fillcolor='green',
                            decreasing_fillcolor='red'
                        ),
                        row=1, col=1
                    )
                    
                    # Thêm tín hiệu mua/bán
                    if buy_signals:
                        buy_dates = [s.date for s in buy_signals]
                        buy_prices = [s.price for s in buy_signals]
                        fig.add_trace(
                            go.Scatter(x=buy_dates, y=buy_prices, mode='markers', 
                                     name='Buy Signal', marker=dict(color='green', size=10, symbol='triangle-up')),
                            row=1, col=1
                        )
                    
                    if sell_signals:
                        sell_dates = [s.date for s in sell_signals]
                        sell_prices = [s.price for s in sell_signals]
                        fig.add_trace(
                            go.Scatter(x=sell_dates, y=sell_prices, mode='markers', 
                                     name='Sell Signal', marker=dict(color='red', size=10, symbol='triangle-down')),
                            row=1, col=1
                        )
                    
                    # 2. RSI
                    fig.add_trace(
                        go.Scatter(x=display_df.index, y=display_df['RSI'], mode='lines', name='RSI'),
                        row=1, col=2
                    )
                    fig.add_hline(y=70, line_dash="dash", line_color="red", row=1, col=2)
                    fig.add_hline(y=30, line_dash="dash", line_color="green", row=1, col=2)
                    
                    # 3. MACD
                    fig.add_trace(
                        go.Scatter(x=display_df.index, y=display_df['MACD'], mode='lines', name='MACD'),
                        row=2, col=1
                    )
                    fig.add_trace(
                        go.Scatter(x=display_df.index, y=display_df['MACD_Signal'], mode='lines', name='Signal'),
                        row=2, col=1
                    )
                    
                    # 4. Bollinger Bands với Candlestick
                    fig.add_trace(
                        go.Candlestick(
                            x=display_df.index,
                            open=display_df['Open'],
                            high=display_df['High'],
                            low=display_df['Low'],
                            close=display_df['Close'],
                            name='Candlestick',
                            increasing_line_color='green',
                            decreasing_line_color='red',
                            increasing_fillcolor='green',
                            decreasing_fillcolor='red'
                        ),
                        row=2, col=2
                    )
                    fig.add_trace(
                        go.Scatter(x=display_df.index, y=display_df['BB_Upper'], mode='lines', name='Upper BB'),
                        row=2, col=2
                    )
                    fig.add_trace(
                        go.Scatter(x=display_df.index, y=display_df['BB_Lower'], mode='lines', name='Lower BB'),
                        row=2, col=2
                    )
                    
                    # 5. Volume
                    fig.add_trace(
                        go.Bar(x=display_df.index, y=display_df['Volume'], name='Volume'),
                        row=3, col=1
                    )
                    
                    # 6. Equity Curve
                    if 'equity_curve' in results and results['equity_curve']:
                        equity_df = pd.DataFrame({
                            'Date': display_df.index[:len(results['equity_curve'])],
                            'Equity': results['equity_curve']
                        })
                        fig.add_trace(
                            go.Scatter(x=equity_df['Date'], y=equity_df['Equity'], mode='lines', name='Equity'),
                            row=3, col=2
                        )
                    
                    fig.update_layout(height=800, title_text=f"Phân tích {strategy_name} Strategy")
                    st.plotly_chart(fig, use_container_width=True)
                
                # 6. Kết luận
                st.header("🎯 Kết luận")
                
                if results['total_return_pct'] > 0:
                    st.success(f"✅ Chiến lược {strategy_name} cho kết quả **dương** với lợi nhuận {results['total_return_pct']:.2f}%")
                else:
                    st.error(f"❌ Chiến lược {strategy_name} cho kết quả **âm** với thua lỗ {abs(results['total_return_pct']):.2f}%")
                
                # Gợi ý cải thiện
                st.subheader("💡 Gợi ý cải thiện")
                suggestions = []
                
                if results['win_rate'] < 0.5:
                    suggestions.append("Tỷ lệ thắng thấp - cần tinh chỉnh tham số")
                if results['max_drawdown_pct'] > 10:
                    suggestions.append("Drawdown cao - cần thêm stop loss")
                if results['trade_count'] < 5:
                    suggestions.append("Ít giao dịch - có thể tăng độ nhạy của tín hiệu")
                
                if suggestions:
                    for suggestion in suggestions:
                        st.write(f"• {suggestion}")
                else:
                    st.write("• Chiến lược có vẻ ổn định")
                
            except Exception as e:
                st.error(f"Lỗi: {str(e)}")
                st.error("Vui lòng kiểm tra lại tham số và thử lại")

if __name__ == "__main__":
    main() 