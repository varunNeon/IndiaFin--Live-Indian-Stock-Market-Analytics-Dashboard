import yfinance as yf
import pandas as pd

# Our watchlist - 8 Indian stocks
STOCKS = {
    "Reliance": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "Zomato": "ETERNAL.NS",
    "Infosys": "INFY.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "Adani Ports": "ADANIPORTS.NS",
    "Wipro": "WIPRO.NS",
    "ITC": "ITC.NS"
}


def fetch_stock_data(ticker, period="6mo"):
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)
    if df.empty:
        print(f"Warning: No data found for {ticker}")
        return None
    # drop Dividends, Splits
    df = df[["Open", "High", "Low", "Close", "Volume"]]
    df["Ticker"] = ticker
    return df


# Fetch and combine all
all_data = []
for name, ticker in STOCKS.items():
    print(f"Fetching {name}...")
    df = fetch_stock_data(ticker)

    if df is not None:
        all_data.append(df)


combined = pd.concat(all_data).reset_index()
print("\nTotal rows fetched:", len(combined))
print(combined.head(10))
