import pandas as pd
from market_data import fetch_quote_snapshot

def premarket_scan(symbols):
    rows=[]
    for sym in symbols:
        try:
            q=fetch_quote_snapshot(sym)
            if q: rows.append(q)
        except Exception as e:
            rows.append({"Symbol":sym,"Error":str(e)[:100]})
    df=pd.DataFrame(rows)
    if not df.empty and "Change %" in df: df["Gap / Change"] = df["Change %"].apply(lambda x:"GAP UP" if x>=1 else ("GAP DOWN" if x<=-1 else "FLAT"))
    return df
