import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from DataCollection import combined
from Analysis import analyzed

st.set_page_config(page_title="IndiaFin Dashboard", layout="wide")

# Fix .NS suffix
analyzed["Ticker"] = analyzed["Ticker"].str.replace(".NS", "", regex=False)
combined["Ticker"] = combined["Ticker"].str.replace(".NS", "", regex=False)

st.title("💹 IndiaFin — Indian Stock Market Dashboard")
st.markdown("---")

# Sidebar controls
st.sidebar.header("Filters")
tickers = analyzed["Ticker"].unique().tolist()
selected_ticker = st.sidebar.selectbox("Select Stock", tickers)

# Time range selector
time_range = st.sidebar.selectbox("Time Range", ["1 Month", "3 Months", "6 Months"])
range_map = {"1 Month": 30, "3 Months": 90, "6 Months": 180}
days = range_map[time_range]

# Filter data
stock_df = analyzed[analyzed["Ticker"] == selected_ticker].copy()
stock_df = stock_df.tail(days)

# --- KEY METRICS PANEL ---
latest = stock_df.iloc[-1]
prev = stock_df.iloc[-2]

current_price = latest["Close"]
daily_return = latest["Daily_Return"]
volatility = latest["Volatility"]
above_ma30 = latest["Close"] > latest["MA30"]
trend = "Bullish 📈" if above_ma30 else "Bearish 📉"

col1, col2, col3, col4 = st.columns(4)
col1.metric("Current Price", f"₹{current_price:.2f}")
col2.metric("Daily Return", f"{daily_return:.2f}%")
col3.metric("Volatility", f"{volatility:.2f}%")
col4.metric("Trend", trend)

st.markdown("---")

# --- INSIGHT TEXT ---
ma7 = latest["MA7"]
ma30 = latest["MA30"]

if ma7 > ma30:
    signal = "🟢 Bullish — 7-day MA is above 30-day MA. Short-term momentum is positive."
else:
    signal = "🔴 Bearish — 7-day MA is below 30-day MA. Short-term momentum is weakening."

if volatility > stock_df["Volatility"].mean():
    vol_insight = "⚠️ Volatility is above average — higher risk period."
else:
    vol_insight = "✅ Volatility is below average — relatively stable."

st.subheader(f"Market Insight — {selected_ticker}")
st.info(signal)
st.info(vol_insight)

st.markdown("---")

# --- PRICE CHART ---
st.subheader(f"Price Trend — {selected_ticker}")
fig = go.Figure()
fig.add_trace(go.Scatter(x=stock_df["Date"], y=stock_df["Close"], name="Close Price", line=dict(color="white")))
fig.add_trace(go.Scatter(x=stock_df["Date"], y=stock_df["MA7"], name="7-Day MA", line=dict(color="orange")))
fig.add_trace(go.Scatter(x=stock_df["Date"], y=stock_df["MA30"], name="30-Day MA", line=dict(color="cyan")))
st.plotly_chart(fig, use_container_width=True)

# --- VOLATILITY CHART ---
st.subheader("Volatility (7-Day Rolling Std Dev of Returns)")
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=stock_df["Date"], y=stock_df["Volatility"], name="Volatility", fill="tozeroy", line=dict(color="#4FC3F7")))
st.plotly_chart(fig2, use_container_width=True)

# --- VOLUME CHART ---
st.subheader("Trading Volume")
fig3 = go.Figure()
fig3.add_trace(go.Bar(x=stock_df["Date"], y=stock_df["Volume"], name="Volume", marker_color="steelblue"))
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# --- CORRELATION HEATMAP ---
st.subheader("Stock Correlation Matrix")
pivot = combined.pivot_table(index="Date", columns="Ticker", values="Close")
returns = pivot.pct_change().dropna()
corr = returns.corr()

fig4 = px.imshow(corr, text_auto=True, color_continuous_scale="Blues", zmin=-1, zmax=1)
st.plotly_chart(fig4, use_container_width=True)

st.caption("""
**How to read this:** Each cell shows how closely two stocks move together, scored from -1 to +1.
- **+1 (dark blue)** → They move in the same direction almost always
- **0 (light)** → No relationship
- **-1** → They move in opposite directions

**Why this matters:** If all your stocks are highly correlated, your portfolio has no diversification — when one falls, they all fall. A good portfolio mixes low-correlation stocks to reduce risk. This is a core concept in portfolio theory.
""")
