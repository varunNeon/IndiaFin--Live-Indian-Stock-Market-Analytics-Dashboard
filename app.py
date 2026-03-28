import logging

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from Analysis import analyze_market_data
from DataCollection import fetch_all_stock_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="IndiaFin Dashboard", layout="wide")

st.markdown(
    """
<style>
  :root {
    --bg-main: #07111f;
    --bg-panel: rgba(10, 20, 38, 0.92);
    --bg-card: rgba(14, 28, 50, 0.88);
    --bg-card-soft: rgba(17, 35, 60, 0.72);
    --border: rgba(118, 162, 255, 0.22);
    --text-main: #e7eefc;
    --text-soft: #93a8cf;
    --accent: #5aa7ff;
    --accent-2: #33d0ff;
    --green: #3ddc97;
    --amber: #ffb347;
  }
  [data-testid="stAppViewContainer"] {
    background:
      radial-gradient(circle at top left, rgba(59, 130, 246, 0.18), transparent 32%),
      radial-gradient(circle at top right, rgba(51, 208, 255, 0.14), transparent 28%),
      linear-gradient(180deg, #08111d 0%, #07111f 48%, #040914 100%);
    color: var(--text-main);
  }
  [data-testid="stHeader"] {
    background: rgba(4, 9, 20, 0.25);
  }
  [data-testid="stSidebar"] {
    background:
      linear-gradient(180deg, rgba(9, 18, 34, 0.98) 0%, rgba(8, 16, 29, 0.98) 100%);
    border-right: 1px solid rgba(118, 162, 255, 0.12);
  }
  [data-testid="stSidebar"] * {
    color: var(--text-main) !important;
  }
  [data-testid="stSidebar"] .stSelectbox label,
  [data-testid="stSidebar"] .stMarkdown {
    color: var(--text-soft) !important;
  }
  [data-testid="stSidebar"] [data-baseweb="select"] > div,
  [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
    background: rgba(14, 28, 50, 0.9);
    border: 1px solid rgba(118, 162, 255, 0.18);
    border-radius: 14px;
    box-shadow: none;
  }
  [data-testid="stSidebar"] [data-baseweb="select"] svg {
    fill: var(--accent-2);
  }
  [data-testid="stMarkdownContainer"] p,
  [data-testid="stMarkdownContainer"] li,
  [data-testid="stCaptionContainer"] {
    color: var(--text-soft);
  }
  h1, h2, h3 {
    color: var(--text-main);
    letter-spacing: -0.02em;
  }
  .block-container {
    padding-top: 2.2rem;
  }
  .hero {
    padding: 1.5rem 1.6rem;
    border-radius: 24px;
    border: 1px solid var(--border);
    background:
      linear-gradient(135deg, rgba(15, 32, 56, 0.94) 0%, rgba(8, 18, 33, 0.94) 100%);
    box-shadow: 0 18px 50px rgba(0, 0, 0, 0.28);
    margin-bottom: 1.15rem;
  }
  .hero-kicker {
    color: #8cb6ff;
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    margin-bottom: 0.45rem;
    font-weight: 700;
  }
  .hero-title {
    font-size: 2.3rem;
    line-height: 1.05;
    font-weight: 800;
    color: #f5f8ff;
    margin-bottom: 0.55rem;
  }
  .hero-subtitle {
    max-width: 780px;
    color: var(--text-soft);
    font-size: 1rem;
    line-height: 1.6;
  }
  .hero-strip {
    display: flex;
    gap: 0.8rem;
    flex-wrap: wrap;
    margin-top: 1rem;
  }
  .hero-pill {
    padding: 0.45rem 0.8rem;
    border-radius: 999px;
    background: rgba(90, 167, 255, 0.12);
    border: 1px solid rgba(90, 167, 255, 0.18);
    color: #d7e7ff;
    font-size: 0.88rem;
  }
  [data-testid="metric-container"] {
    background:
      linear-gradient(180deg, rgba(15, 30, 55, 0.9) 0%, rgba(10, 22, 40, 0.9) 100%);
    border: 1px solid rgba(118, 162, 255, 0.16);
    border-radius: 20px;
    padding: 18px;
    box-shadow: 0 14px 32px rgba(0, 0, 0, 0.18);
  }
  [data-testid="stMetricLabel"] {
    color: var(--text-soft);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 0.74rem;
    font-weight: 700;
  }
  [data-testid="stMetricValue"] {
    color: #f5f8ff;
    font-weight: 800;
  }
  .stInfo, .stAlert, [data-testid="stNotification"] {
    background: rgba(12, 24, 44, 0.88) !important;
    border: 1px solid rgba(118, 162, 255, 0.16) !important;
    border-radius: 16px !important;
    color: var(--text-main) !important;
  }
  .stInfo {
    border-left: 4px solid var(--accent) !important;
  }
  .stWarning {
    background: rgba(45, 30, 10, 0.88) !important;
    border-left: 4px solid var(--amber) !important;
  }
  .stError {
    background: rgba(52, 18, 24, 0.88) !important;
    border-left: 4px solid #ff6b7a !important;
  }
  hr {
    border-color: rgba(118, 162, 255, 0.12);
  }
</style>
""",
    unsafe_allow_html=True,
)

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(8, 17, 31, 0)",
    plot_bgcolor="rgba(11, 22, 39, 0.88)",
    font_color="#dbe7ff",
    font_family="sans-serif",
    margin=dict(l=20, r=20, t=40, b=20),
    xaxis=dict(
        gridcolor="rgba(124, 151, 201, 0.16)",
        linecolor="rgba(124, 151, 201, 0.18)",
        tickcolor="#7f8fb3",
        zerolinecolor="rgba(124, 151, 201, 0.16)",
    ),
    yaxis=dict(
        gridcolor="rgba(124, 151, 201, 0.16)",
        linecolor="rgba(124, 151, 201, 0.18)",
        tickcolor="#7f8fb3",
        zerolinecolor="rgba(124, 151, 201, 0.16)",
    ),
    legend=dict(
        bgcolor="rgba(8, 18, 33, 0.92)",
        bordercolor="rgba(118, 162, 255, 0.18)",
        borderwidth=1,
        font=dict(color="#dbe7ff"),
    ),
)


@st.cache_data(ttl=900, show_spinner=False)
def load_market_data(period: str = "6mo"):
    combined = fetch_all_stock_data(period=period)
    analyzed = analyze_market_data(combined)
    return combined, analyzed


def prepare_display_data(combined, analyzed):
    display_combined = combined.copy()
    display_analyzed = analyzed.copy()

    if "Ticker" in display_combined.columns:
        display_combined["Ticker"] = display_combined["Ticker"].str.replace(".NS", "", regex=False)
    if "Ticker" in display_analyzed.columns:
        display_analyzed["Ticker"] = display_analyzed["Ticker"].str.replace(".NS", "", regex=False)

    return display_combined, display_analyzed


def render_empty_state():
    st.markdown(
        """
<div class="hero">
  <div class="hero-kicker">IndiaFin Terminal</div>
  <div class="hero-title">Market dashboard offline</div>
  <div class="hero-subtitle">
    The analytics layer is healthy, but live pricing is temporarily unavailable. The app will recover automatically once upstream data starts responding again.
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.error("Live market data is currently unavailable. Please try again in a few minutes.")
    st.info("The app stays available, but charts are hidden until we receive usable stock data.")


def render_dashboard(combined, analyzed):
    st.sidebar.header("Filters")
    tickers = analyzed["Ticker"].dropna().unique().tolist()

    if not tickers:
        logger.warning("No ticker values are available after analysis")
        render_empty_state()
        return

    selected_ticker = st.sidebar.selectbox("Select Stock", tickers)
    time_range = st.sidebar.selectbox("Time Range", ["1 Month", "3 Months", "6 Months"])
    range_map = {"1 Month": 30, "3 Months": 90, "6 Months": 180}
    days = range_map[time_range]

    stock_df = analyzed[analyzed["Ticker"] == selected_ticker].copy().tail(days)
    if stock_df.empty:
        logger.warning("No rows available for selected ticker %s", selected_ticker)
        st.warning(f"No data is available for {selected_ticker} right now.")
        return

    latest = stock_df.iloc[-1]
    current_price = latest["Close"]
    daily_return = latest["Daily_Return"]
    volatility = latest["Volatility"]
    above_ma30 = latest["Close"] > latest["MA30"]
    trend = "Bullish" if above_ma30 else "Bearish"
    trend_accent = "#3ddc97" if above_ma30 else "#ff8a65"

    st.markdown(
        f"""
<div class="hero">
  <div class="hero-kicker">IndiaFin Terminal</div>
  <div class="hero-title">{selected_ticker} intelligence dashboard</div>
  <div class="hero-subtitle">
    Track momentum, volatility, and cross-market relationships for key Indian equities with a cleaner dark trading-desk presentation.
  </div>
  <div class="hero-strip">
    <div class="hero-pill">Window: {time_range}</div>
    <div class="hero-pill">Ticker: {selected_ticker}</div>
    <div class="hero-pill">Trend: <span style="color:{trend_accent}; font-weight:700;">{trend}</span></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Price", f"Rs {current_price:.2f}")
    col2.metric("Daily Return", f"{daily_return:.2f}%")
    col3.metric("Volatility", f"{volatility:.2f}%")
    col4.metric("Trend", trend)

    st.markdown("---")

    ma7 = latest["MA7"]
    ma30 = latest["MA30"]

    if ma7 > ma30:
        signal = "Bullish - 7-day MA is above 30-day MA. Short-term momentum is positive."
    else:
        signal = "Bearish - 7-day MA is below 30-day MA. Short-term momentum is weakening."

    if volatility > stock_df["Volatility"].mean():
        vol_insight = "Volatility is above average - higher risk period."
    else:
        vol_insight = "Volatility is below average - relatively stable."

    st.subheader(f"Market Insight - {selected_ticker}")
    st.info(signal)
    st.info(vol_insight)

    st.markdown("---")

    st.subheader(f"Price Trend - {selected_ticker}")
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=stock_df["Date"],
            y=stock_df["Close"],
            name="Close Price",
            line=dict(color="#6cb7ff", width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=stock_df["Date"],
            y=stock_df["MA7"],
            name="7-Day MA",
            line=dict(color="#ffb347", width=1.8, dash="dot"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=stock_df["Date"],
            y=stock_df["MA30"],
            name="30-Day MA",
            line=dict(color="#3ddc97", width=1.8, dash="dash"),
        )
    )
    fig.update_layout(**CHART_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Volatility (7-Day Rolling Std Dev of Returns)")
    fig2 = go.Figure()
    fig2.add_trace(
        go.Scatter(
            x=stock_df["Date"],
            y=stock_df["Volatility"],
            name="Volatility",
            fill="tozeroy",
            fillcolor="rgba(51, 208, 255, 0.12)",
            line=dict(color="#33d0ff", width=2.4),
        )
    )
    fig2.update_layout(**CHART_LAYOUT)
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Trading Volume")
    fig3 = go.Figure()
    fig3.add_trace(
        go.Bar(
            x=stock_df["Date"],
            y=stock_df["Volume"],
            name="Volume",
            marker_color="#5aa7ff",
            marker_line_color="#79bdff",
            marker_line_width=0.5,
            opacity=0.9,
        )
    )
    fig3.update_layout(**CHART_LAYOUT)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    st.subheader("Stock Correlation Matrix")
    pivot = combined.pivot_table(index="Date", columns="Ticker", values="Close")
    returns = pivot.pct_change().dropna()
    corr = returns.corr()

    if corr.empty:
        logger.warning("Correlation matrix is empty because returns data is insufficient")
        st.warning("Not enough synchronized market data is available to build the correlation matrix yet.")
    else:
        fig4 = px.imshow(corr, text_auto=True, color_continuous_scale="Tealgrn", zmin=-1, zmax=1)
        fig4.update_layout(
            paper_bgcolor="rgba(8, 17, 31, 0)",
            plot_bgcolor="rgba(11, 22, 39, 0.88)",
            font_color="#dbe7ff",
            coloraxis_colorbar=dict(
                tickcolor="#7f8fb3",
                tickfont=dict(color="#dbe7ff"),
                outlinecolor="rgba(118, 162, 255, 0.18)",
            ),
        )
        st.plotly_chart(fig4, use_container_width=True)

    st.caption(
        """
**How to read this:** Each cell shows how closely two stocks move together, scored from -1 to +1.
- **+1 (dark blue)** -> They move in the same direction almost always
- **0 (light)** -> No relationship
- **-1** -> They move in opposite directions

**Why this matters:** If all your stocks are highly correlated, your portfolio has no diversification - when one falls, they all fall. A good portfolio mixes low-correlation stocks to reduce risk. This is a core concept in portfolio theory.
"""
    )


def main():
    try:
        combined, analyzed = load_market_data()
        combined, analyzed = prepare_display_data(combined, analyzed)
    except Exception:
        logger.exception("Unexpected application error while loading market data")
        render_empty_state()
        return

    if combined.empty or analyzed.empty:
        logger.warning("Dashboard entered empty state because combined=%s analyzed=%s", combined.empty, analyzed.empty)
        render_empty_state()
        return

    render_dashboard(combined, analyzed)


if __name__ == "__main__":
    main()
