import math
import pandas as pd
from .indicators import completed_daily_bars

def trend_join_signal(df: pd.DataFrame) -> str:
    x=completed_daily_bars(df)
    if len(x)<205: return "INSUFFICIENT DATA"
    last=x.iloc[-1]; prev=x.iloc[-2]
    bull=(last.Close>last.EMA50 and last.EMA20>last.EMA50 and last.EMA50>last.EMA200)
    momentum=(last.RSI14>50 and last.ROC9>0 and last.CMF20>0 and last.ADX14>=16)
    reclaim=(prev.Close<=prev.EMA20 and last.Close>last.EMA20)
    return "BUY CANDIDATE" if bull and momentum and reclaim else "WAIT"

def backtest_trend_join(df: pd.DataFrame, capital=60000, risk_per_trade=300):
    x=df.dropna().copy()
    cash=float(capital); peak=cash; max_dd=0.0; equity=[]; logs=[]
    position=None
    for i in range(205,len(x)-1):
        row=x.iloc[i]; nxt=x.iloc[i+1]
        if position:
            exit_price=None; reason=None
            # Conservative daily OHLC handling: if stop and target both touched, assume stop first.
            if row.Low<=position["stop"]:
                exit_price=position["stop"]; reason="STOP"
            elif row.High>=position["target"]:
                exit_price=position["target"]; reason="TARGET"
            elif i-position["entry_i"]>=20:
                exit_price=float(row.Close); reason="TIME EXIT"
            if exit_price is not None:
                pnl=(exit_price-position["entry"])*position["qty"]
                cash+=pnl
                logs.append({"Entry Date":str(position["date"]),"Exit Date":str(x.index[i]),"Entry":round(position["entry"],2),"Exit":round(exit_price,2),"Qty":position["qty"],"P&L":round(pnl,2),"Reason":reason})
                position=None
        if position is None:
            prev=x.iloc[i-1]
            trend=(row.Close>row.EMA50 and row.EMA20>row.EMA50 and row.EMA50>row.EMA200)
            mom=(row.RSI14>50 and row.ROC9>0 and row.CMF20>0 and row.ADX14>=16)
            reclaim=(prev.Close<=prev.EMA20 and row.Close>row.EMA20)
            if trend and mom and reclaim and row.ATR14>0:
                entry=float(nxt.Open); stop=entry-2*float(row.ATR14); target=entry+1.5*(entry-stop)
                per_share=entry-stop
                qty=int(min(risk_per_trade/per_share, cash/entry)) if per_share>0 else 0
                if qty>0: position={"entry":entry,"stop":stop,"target":target,"qty":qty,"entry_i":i+1,"date":x.index[i+1]}
        peak=max(peak,cash); max_dd=max(max_dd,peak-cash); equity.append(cash)
    wins=[t["P&L"] for t in logs if t["P&L"]>0]; losses=[t["P&L"] for t in logs if t["P&L"]<0]
    gross_win=sum(wins); gross_loss=abs(sum(losses))
    return {"net_pnl":cash-capital,"trades":len(logs),"win_rate":100*len(wins)/len(logs) if logs else 0,
            "max_drawdown":max_dd,"profit_factor":gross_win/gross_loss if gross_loss else (float("inf") if gross_win else 0),
            "trade_log":logs,"equity_curve":equity}
