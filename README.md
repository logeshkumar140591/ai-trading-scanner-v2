# AI Trading Scanner V2.0

A standalone NSE research dashboard inspired by the supplied video workflow:
1. Pre-market / gap scan (Scanner A)
2. Trend Join strategy scan (Scanner B)
3. TradingView Pine Script strategy and alerts
4. Python daily-bar backtest extension
5. News catalyst headlines

## Independence guarantee
This is a **new separate project**. It does not modify, import, or overwrite the existing Equity Dashboard `app.py` (V1.9.7).

## Strategy implemented
Daily Trend Join long candidate:
- Close > EMA50
- EMA20 > EMA50 > EMA200
- RSI(14) > 50
- ROC(9) > 0
- CMF(20) > 0
- ADX(14) >= 16
- Fresh reclaim: previous close <= previous EMA20 and current completed close > current EMA20

Research backtest:
- Signal on completed daily close
- Entry at next daily bar open
- Stop = 2 x ATR(14)
- Target = 1.5R
- Maximum holding = 20 bars
- Risk budget defaults to ₹300 per trade

These are research assumptions, not validated profitable rules. The backtest is a simplified daily OHLC simulation. If stop and target are both touched in one bar, it assumes stop first.

## Install and run
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Mobile note
The dashboard can be deployed to Streamlit Community Cloud from GitHub and opened on Android. Editing/uploading many files from a phone may be easier through GitHub Desktop on a computer or GitHub web upload in batches.

## Data limitations
- Yahoo Finance data can be delayed, incomplete, rate-limited or adjusted.
- Gap scan uses latest available Yahoo snapshot and is not a guaranteed NSE pre-open auction feed.
- News comes from Google News RSS; headlines require manual verification.
- No Angel One API, no live order placement, no auto trading, no Telegram integration in this release.
- Use NSE / broker data to confirm all values.

## Safety
Paper/research only. No signal guarantees profit. Include brokerage, taxes, slippage, liquidity, gap risk and margin before evaluating real-world performance.
