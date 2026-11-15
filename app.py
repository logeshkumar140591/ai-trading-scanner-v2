import streamlit as st
import pandas as pd
from datetime import date, timedelta
from market_data import fetch_history, fetch_quote_snapshot
from indicators import add_indicators
from strategies import trend_join_signal, backtest_trend_join
from premarket import premarket_scan
from news import fetch_news
from risk import position_size
from config import DEFAULT_WATCHLIST, DEFAULT_CAPITAL, DEFAULT_RISK
from pathlib import Path
st.set_page_config(page_title="AI Trading Scanner V2.0", page_icon="📈", layout="wide")
st.title("📈 AI Trading Scanner V2.0")
st.caption("Separate research project • NSE • Paper trading only • No broker order execution")

with st.sidebar:
    st.header("Settings")
    capital = st.number_input("Research capital (₹)", min_value=1000, value=DEFAULT_CAPITAL, step=5000)
    risk = st.number_input("Risk per trade (₹)", min_value=50, value=DEFAULT_RISK, step=50)
    watch_text = st.text_area("NSE watchlist (Yahoo Finance symbols)", value="\\n".join(DEFAULT_WATCHLIST), height=220)
    watchlist = [x.strip().upper() for x in watch_text.splitlines() if x.strip()]
    st.caption("Example: RELIANCE.NS, TCS.NS, SBIN.NS")

tabs = st.tabs(["Overview", "Pre-Market Gap Scan", "Trend Strategy Scan", "News Catalyst", "Backtest", "Risk Calculator", "Pine Script", "Setup"])

with tabs[0]:
    st.subheader("System overview")
    c1,c2,c3 = st.columns(3)
    c1.metric("Watchlist symbols", len(watchlist))
    c2.metric("Research capital", f"₹{capital:,.0f}")
    c3.metric("Risk per trade", f"₹{risk:,.0f}")
    st.info("This dashboard screens public market data for research. Signals are not guaranteed; use paper trading and verify prices with your broker before any decision.")
    st.markdown("""
    **Included modules**
    - Pre-market gap scan: previous close vs latest available price; during market hours this is an intraday snapshot, not a true pre-open auction feed.
    - Trend Join scan: daily trend + momentum filters based on the strategy logic documented in this project.
    - News catalyst: Google News RSS headlines for each symbol/company query.
    - Historical backtest: daily-bar trend-following simulation with next-bar-open entry and ATR stop/target.
    - Risk sizing: risk-based quantity calculator.
    """)

with tabs[1]:
    st.subheader("Pre-Market / Gap Scanner")
    st.caption("Uses Yahoo Finance snapshots. Yahoo data may be delayed; before market open this is not guaranteed to represent NSE pre-open auction prices.")
    if st.button("Run Gap Scan", key="gap"):
        with st.spinner("Fetching quotes..."):
            df = premarket_scan(watchlist)
        if df.empty: st.warning("No quote data returned. Try again later.")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button("Download gap scan CSV", df.to_csv(index=False), "premarket_gap_scan.csv", "text/csv")

with tabs[2]:
    st.subheader("Trend Join Strategy Scanner")
    st.write("Daily timeframe • EMA20/50 trend • Close above EMA50 • RSI14 > 50 • Fresh reclaim of EMA20.")
    if st.button("Run Strategy Scan", key="trend"):
        rows=[]
        progress=st.progress(0)
        for i,sym in enumerate(watchlist):
            try:
                raw=fetch_history(sym, period="2y", interval="1d")
                if raw.empty or len(raw)<60: continue
                data=add_indicators(raw)
                sig=trend_join_signal(data)
                last=data.iloc[-1]
                rows.append({"Symbol":sym,"Signal":sig,"Close":round(float(last.Close),2),"EMA20":round(float(last.EMA20),2),"EMA50":round(float(last.EMA50),2),"RSI14":round(float(last.RSI14),1),"ATR14":round(float(last.ATR14),2),"Volume":int(last.Volume)})
            except Exception as e:
                rows.append({"Symbol":sym,"Signal":"DATA ERROR","Close":None,"EMA20":None,"EMA50":None,"RSI14":None,"ATR14":None,"Volume":None,"Error":str(e)[:100]})
            progress.progress((i+1)/max(1,len(watchlist)))
        out=pd.DataFrame(rows)
        if out.empty: st.warning("No usable daily data.")
        else:
            st.dataframe(out, use_container_width=True, hide_index=True)
            st.download_button("Download strategy signals CSV",out.to_csv(index=False),"trend_strategy_scan.csv","text/csv")

with tabs[3]:
    st.subheader("News Catalyst Scanner")
    st.caption("Headlines are retrieved from Google News RSS. Headlines are not a verified trading signal; check the original source.")
    if st.button("Fetch latest headlines", key="news"):
        with st.spinner("Fetching news headlines..."):
            news=fetch_news(watchlist[:20])
        if news.empty: st.warning("No news returned.")
        else:
            st.dataframe(news, use_container_width=True, hide_index=True)
            st.download_button("Download news CSV",news.to_csv(index=False),"news_catalysts.csv","text/csv")

with tabs[4]:
    st.subheader("Historical Backtest")
    symbol=st.selectbox("Symbol",watchlist if watchlist else DEFAULT_WATCHLIST)
    period=st.selectbox("History",["1y","2y","5y"],index=1)
    if st.button("Run daily backtest",key="bt"):
        with st.spinner("Downloading history and testing..."):
            raw=fetch_history(symbol,period=period,interval="1d")
            if raw.empty: st.error("No data returned.")
            else:
                result=backtest_trend_join(add_indicators(raw),capital=capital,risk_per_trade=risk)
                st.metric("Net P&L",f"₹{result['net_pnl']:,.2f}")
                a,b,c,d=st.columns(4)
                a.metric("Trades",result["trades"])
                b.metric("Win rate",f"{result['win_rate']:.1f}%")
                c.metric("Max drawdown",f"₹{result['max_drawdown']:,.2f}")
                d.metric("Profit factor",f"{result['profit_factor']:.2f}" if result["profit_factor"]!=float("inf") else "∞")
                st.caption("Illustrative daily-bar backtest. Uses next session open for entry; does not model intraday fills, slippage perfectly, corporate actions beyond provider adjustments, or taxes/charges.")
                trades=pd.DataFrame(result["trade_log"])
                if not trades.empty:
                    st.dataframe(trades,use_container_width=True,hide_index=True)
                    st.download_button("Download trade log",trades.to_csv(index=False),"backtest_trades.csv","text/csv")
                st.line_chart(pd.DataFrame({"Equity":result["equity_curve"]}))

with tabs[5]:
    st.subheader("Position Size / Risk Calculator")
    c1,c2,c3=st.columns(3)
    entry=c1.number_input("Entry price",min_value=0.01,value=100.0,step=0.5)
    stop=c2.number_input("Stop-loss price",min_value=0.0,value=97.0,step=0.5)
    risk_budget=c3.number_input("Risk budget (₹)",min_value=1.0,value=float(risk),step=50.0)
    qty,actual=position_size(entry,stop,risk_budget)
    st.metric("Suggested quantity (shares)",qty)
    st.metric("Estimated price risk",f"₹{actual:,.2f}")
    st.caption("Excludes brokerage, taxes, slippage, gaps and liquidity risk. Quantity is a theoretical ceiling, not an order instruction.")

with tabs[6]:
    st.subheader("TradingView Pine Script")
    p=Path("pine/trend_join_daily.pine")
    if p.exists():
        code=p.read_text()
        st.code(code,language="pine")
        st.download_button("Download Pine Script",code,"trend_join_daily.pine","text/plain")
    else: st.error("Pine Script file missing.")

with tabs[7]:
    st.subheader("Setup")
    st.markdown("""
    1. Install dependencies: `pip install -r requirements.txt`
    2. Run: `streamlit run app.py`
    3. Edit the watchlist in the sidebar.
    4. Data comes from Yahoo Finance and Google News RSS; no API key is required.
    5. This app does **not** connect to Angel One or place trades.

    **Important:** The project is independent. It does not overwrite or import your existing Equity Dashboard `app.py`.
    """)
    st.warning("Market data availability, timestamps and symbol coverage depend on Yahoo Finance. Confirm all values from NSE / your broker.")
