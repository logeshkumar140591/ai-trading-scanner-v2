import pandas as pd
import numpy as np

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    x=df.copy()
    close=x["Close"].astype(float); high=x["High"].astype(float); low=x["Low"].astype(float)
    x["EMA9"]=close.ewm(span=9,adjust=False).mean()
    x["EMA20"]=close.ewm(span=20,adjust=False).mean()
    x["EMA21"]=close.ewm(span=21,adjust=False).mean()
    x["EMA50"]=close.ewm(span=50,adjust=False).mean()
    x["EMA200"]=close.ewm(span=200,adjust=False).mean()
    delta=close.diff()
    gain=delta.clip(lower=0).ewm(alpha=1/14,adjust=False).mean()
    loss=(-delta.clip(upper=0)).ewm(alpha=1/14,adjust=False).mean()
    rs=gain/loss.replace(0,np.nan)
    x["RSI14"]=100-(100/(1+rs))
    x["ROC9"]=close.pct_change(9)*100
    prev=close.shift(1)
    tr=pd.concat([(high-low),(high-prev).abs(),(low-prev).abs()],axis=1).max(axis=1)
    x["ATR14"]=tr.ewm(alpha=1/14,adjust=False).mean()
    mf_mult=((close-low)-(high-close))/(high-low).replace(0,np.nan)
    mf_vol=mf_mult*x["Volume"].astype(float)
    x["CMF20"]=mf_vol.rolling(20).sum()/x["Volume"].rolling(20).sum().replace(0,np.nan)
    up=high.diff(); down=-low.diff()
    plus_dm=up.where((up>down)&(up>0),0.0)
    minus_dm=down.where((down>up)&(down>0),0.0)
    atr=x["ATR14"].replace(0,np.nan)
    plus_di=100*plus_dm.ewm(alpha=1/14,adjust=False).mean()/atr
    minus_di=100*minus_dm.ewm(alpha=1/14,adjust=False).mean()/atr
    dx=100*(plus_di-minus_di).abs()/(plus_di+minus_di).replace(0,np.nan)
    x["ADX14"]=dx.ewm(alpha=1/14,adjust=False).mean()
    return x

def completed_daily_bars(df: pd.DataFrame) -> pd.DataFrame:
    # Daily provider bars are treated as completed only after the trading date has passed.
    if df.empty: return df
    x=df.copy()
    today=pd.Timestamp.now(tz="Asia/Kolkata").date()
    idx=pd.to_datetime(x.index)
    last_date=idx[-1].date()
    if last_date == today and len(x)>1: x=x.iloc[:-1]
    return x
