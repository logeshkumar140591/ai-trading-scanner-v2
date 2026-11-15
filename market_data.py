import yfinance as yf
import pandas as pd

def fetch_history(symbol: str, period="2y", interval="1d") -> pd.DataFrame:
    df = yf.download(symbol, period=period, interval=interval, auto_adjust=False, progress=False, threads=False)
    if df is None or df.empty: return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.rename(columns={c:str(c).title() for c in df.columns})
    required=["Open","High","Low","Close","Volume"]
    if not all(c in df.columns for c in required): return pd.DataFrame()
    return df[required].dropna().copy()

def fetch_quote_snapshot(symbol: str):
    ticker=yf.Ticker(symbol)
    hist=ticker.history(period="5d",interval="1d",auto_adjust=True)
    if hist.empty: return None
    hist=hist.dropna(subset=["Close"])
    if len(hist)<1: return None
    prev=float(hist["Close"].iloc[-2]) if len(hist)>1 else float(hist["Close"].iloc[-1])
    price=float(hist["Close"].iloc[-1])
    return {"Symbol":symbol,"Previous Close":prev,"Latest Available":price,"Change %":(price/prev-1)*100 if prev else 0}
