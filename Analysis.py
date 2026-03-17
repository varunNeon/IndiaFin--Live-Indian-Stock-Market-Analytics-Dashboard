from DataCollection import combined

def add_features(df):
    df = df.copy()
    df["MA7"] = df["Close"].rolling(window=7).mean()
    df["MA30"] = df["Close"].rolling(window=30).mean()
    df["Daily_Return"] = df["Close"].pct_change() * 100
    df["Volatility"] = df["Daily_Return"].rolling(window=7).std()
    return df

analyzed = combined.groupby("Ticker", group_keys=False).apply(add_features).reset_index(drop=True)
print(analyzed.head(20))