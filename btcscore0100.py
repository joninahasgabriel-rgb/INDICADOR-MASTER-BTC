import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
import plotly.express as px

st.set_page_config(page_title="BTC Flow Score 0-100", layout="wide")
st.title("🚀 BTC Capital Flow Dashboard - Score 0-100 (Fluxo Ouro → BTC)")
# ==================== DADOS AO VIVO ====================
col1, col2, col3, col4 = st.columns(4)

with col1:
    btc_data = yf.download("BTC-USD", period="1mo", interval="1h")
    if not btc_data.empty and len(btc_data) > 0:
        btc = btc_data['Close'].iloc[-1]
        if isinstance(btc, (int, float)):
    st.metric("BTC Price", f"${btc:,.0f}")
else:
    st.metric("BTC Price", "N/A")
    else:
        st.warning("Dados de BTC indisponíveis no momento.")
        st.metric("BTC Price", "N/A")

with col2:
    dxy_data = yf.download("DX-Y.NYB", period="7d")
    if not dxy_data.empty and len(dxy_data) >= 2:
        dxy_change = ((dxy_data['Close'].iloc[-1] - dxy_data['Close'].iloc[0]) / dxy_data['Close'].iloc[0]) * 100
        if isinstance(dxy_change, (int, float)):
    st.metric("DXY 7d", f"{dxy_change:.2f}%", delta=f"{dxy_change:.2f}%")
else:
    st.metric("DXY 7d", "N/A")
    else:
        st.warning("Dados de DXY indisponíveis.")
        st.metric("DXY 7d", "N/A")

with col3:
    tnx_data = yf.download("^TNX", period="7d")
    if not tnx_data.empty and len(tnx_data) >= 2:
        tnx_change = ((tnx_data['Close'].iloc[-1] - tnx_data['Close'].iloc[0]) / tnx_data['Close'].iloc[0]) * 100
        if isinstance(tnx_change, (int, float)):
    st.metric("10y Yield 7d", f"{tnx_change:.2f}%", delta=f"{tnx_change:.2f}%")
else:
    st.metric("10y Yield 7d", "N/A")
    else:
        st.warning("Dados de yields indisponíveis.")
        st.metric("10y Yield 7d", "N/A")

with col4:
    gold_data = yf.download("GC=F", period="7d")
    if not gold_data.empty and len(gold_data) >= 2:
        gold_change = ((gold_data['Close'].iloc[-1] - gold_data['Close'].iloc[0]) / gold_data['Close'].iloc[0]) * 100
        st.metric("Ouro 7d", f"{gold_change:.2f}%", delta=f"{gold_change:.2f}%")
    else:
        st.warning("Dados de ouro indisponíveis.")
        st.metric("Ouro 7d", "N/A")


with col3:
    tnx_data = yf.download("^TNX", period="7d")
    if not tnx_data.empty and len(tnx_data) >= 2:
        tnx_change = ((tnx_data['Close'].iloc[-1] - tnx_data['Close'].iloc[0]) / tnx_data['Close'].iloc[0]) * 100
        st.metric("10y Yield 7d", f"{tnx_change:.2f}%", delta=f"{tnx_change:.2f}%")
    else:
        st.warning("Dados de yields indisponíveis.")
        st.metric("10y Yield 7d", "N/A")

with col4:
    gold_data = yf.download("GC=F", period="7d")
    if not gold_data.empty and len(gold_data) >= 2:
        gold_change = ((gold_data['Close'].iloc[-1] - gold_data['Close'].iloc[0]) / gold_data['Close'].iloc[0]) * 100
        if isinstance(gold_change, (int, float)):
    st.metric("Ouro 7d", f"{gold_change:.2f}%", delta=f"{gold_change:.2f}%")
else:
    st.metric("Ouro 7d", "N/A")
    else:
        st.warning("Dados de ouro indisponíveis.")
        st.metric("Ouro 7d", "N/A")
# Fear & Greed
try:
    fg = requests.get("https://api.alternative.me/fng/").json()['data'][0]
    fg_value = int(fg['value'])
    fg_class = fg['value_classification']
except:
    fg_value, fg_class = 50, "Neutral"
st.metric("Fear & Greed", f"{fg_value} ({fg_class})")

# Funding Rate (Binance)
try:
    funding = requests.get("https://fapi.binance.com/fapi/v1/premiumIndex?symbol=BTCUSDT").json()['lastFundingRate']
    funding_pct = float(funding) * 100
except:
    funding_pct = 0.01
st.metric("Funding Rate BTC", f"{funding_pct:.3f}%")

# RSI simples (14 períodos)
btc_data = yf.download("BTC-USD", period="30d")['Close']
delta = btc_data.diff()
gain = (delta.where(delta > 0, 0)).rolling(14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
rs = gain / loss
rsi = 100 - (100 / (1 + rs)).iloc[-1]

# ==================== SCORE 0-100 ====================
def normalize(x, min_val, max_val):
    return max(0, min(100, (x - min_val) / (max_val - min_val) * 100))

score_dxy = normalize(-dxy_change, -5, 5)
score_yield = normalize(-tnx_change, -0.5, 0.5)
score_gold = normalize(-gold_change, -5, 5)
score_fg = (100 - fg_value)
score_funding = normalize(-funding_pct, -0.1, 0.1)
score_rsi = normalize(rsi, 20, 80)

# ETF Flow (entrada manual por enquanto)
etf_flow = st.number_input("ETF Net Inflow últimos 7d (US$ mi) - ex: 767", value=500.0, step=10.0)
score_etf = normalize(etf_flow, -1000, 1000)

score_final = (
    0.25 * score_fg +
    0.20 * score_dxy +
    0.15 * score_yield +
    0.15 * score_gold +
    0.10 * score_funding +
    0.10 * score_rsi +
    0.05 * score_etf
)

st.markdown("### 🎯 **SCORE DE OPORTUNIDADE BTC**")
col_a, col_b, col_c = st.columns([1, 3, 1])
with col_a:
    st.metric("Score Final", f"{score_final:.0f}/100", delta="COMPRA" if score_final > 70 else "VENDA" if score_final < 30 else "NEUTRO")
with col_b:
    fig = px.gauge(score_final, range=[0, 100],
                   steps=[{"range": [0, 30], "color": "red"},
                          {"range": [30, 70], "color": "yellow"},
                          {"range": [70, 100], "color": "green"}],
                   title="Quanto mais alto = melhor momento para comprar")
    st.plotly_chart(fig, use_container_width=True)

st.caption("Atualizado em tempo real • Baseado no fluxo de capital pós-deleveraging")

if st.button("🔄 Atualizar Dados Agora"):
    st.rerun()
