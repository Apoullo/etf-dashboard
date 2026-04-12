"""Fetch and analyze all ETFs from the catalog using yfinance.

Produces charts/etf_analysis.json with per-ETF metrics:
- price, 1Y return, 6M return, 3M return
- P/E, P/B, dividend yield
- beta, max drawdown, volatility (annualized std)
- Sharpe ratio (approx, using 5% risk-free rate)
- AUM, avg volume, expense ratio (from catalog)
"""

import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

# Import catalog from build_dashboard
sys.path.insert(0, str(Path(__file__).parent))
from build_dashboard import ETF_CATALOG

RISK_FREE_RATE = 0.05  # ~5% annualized (T-bill proxy)


def analyze_etf(ticker: str, cat: str, cat_color: str, meta: dict) -> dict | None:
    """Fetch and compute all metrics for a single ETF."""
    try:
        tk = yf.Ticker(ticker)
        info = tk.info or {}

        end = datetime.now()
        start_1y = end - timedelta(days=365)
        hist = tk.history(start=start_1y, end=end)

        if hist.empty or len(hist) < 20:
            return None

        close = hist["Close"]
        current_price = float(close.iloc[-1])

        # Returns
        ret_1y = (close.iloc[-1] / close.iloc[0] - 1) * 100 if len(close) > 200 else None
        idx_6m = max(0, len(close) - 126)
        ret_6m = (close.iloc[-1] / close.iloc[idx_6m] - 1) * 100
        idx_3m = max(0, len(close) - 63)
        ret_3m = (close.iloc[-1] / close.iloc[idx_3m] - 1) * 100

        # Drawdown
        peak = close.cummax()
        dd = (close - peak) / peak
        max_dd = float(dd.min()) * 100

        # Volatility (annualized)
        daily_ret = close.pct_change().dropna()
        vol = float(daily_ret.std() * np.sqrt(252) * 100)

        # Sharpe ratio (annualized)
        ann_ret = float((close.iloc[-1] / close.iloc[0]) ** (252 / len(close)) - 1)
        sharpe = (ann_ret - RISK_FREE_RATE) / (daily_ret.std() * np.sqrt(252)) if daily_ret.std() > 0 else 0

        # Beta (vs SPY)
        beta = info.get("beta") or info.get("beta3Year")

        # Fundamentals
        pe = info.get("trailingPE") or info.get("trailingPe")
        pb = info.get("priceToBook")
        div_yield = info.get("dividendYield") or info.get("trailingAnnualDividendYield")
        avg_vol = info.get("averageVolume") or info.get("averageDailyVolume10Day")

        # Price history for sparkline (weekly sampled)
        weekly = close.resample("W").last().dropna()
        sparkline = [round(float(v), 2) for v in weekly]

        return {
            "ticker": ticker,
            "cat": cat,
            "catColor": cat_color,
            "name": meta["n"],
            "desc": meta["d"],
            "expenseRatio": meta["er"],
            "aumText": meta["aum"],
            "price": round(current_price, 2),
            "ret1y": round(float(ret_1y), 2) if ret_1y is not None else None,
            "ret6m": round(float(ret_6m), 2),
            "ret3m": round(float(ret_3m), 2),
            "pe": round(float(pe), 1) if pe else None,
            "pb": round(float(pb), 2) if pb else None,
            "divYield": round(float(div_yield) * 100, 2) if div_yield else None,
            "beta": round(float(beta), 2) if beta else None,
            "maxDD": round(max_dd, 2),
            "volatility": round(vol, 2),
            "sharpe": round(float(sharpe), 2),
            "avgVolume": int(avg_vol) if avg_vol else None,
            "sparkline": sparkline,
        }
    except Exception as e:
        print(f"    ERROR: {e}")
        return None


def main() -> None:
    all_tickers = []
    for group in ETF_CATALOG:
        for etf in group["etfs"]:
            all_tickers.append((etf["t"], group["cat"], group["color"], etf))

    total = len(all_tickers)
    print(f"Analyzing {total} ETFs...")

    results = []
    for i, (ticker, cat, color, meta) in enumerate(all_tickers):
        print(f"  [{i+1}/{total}] {ticker}...", end=" ", flush=True)
        result = analyze_etf(ticker, cat, color, meta)
        if result:
            results.append(result)
            print(f"OK (${result['price']}, {result.get('ret1y','N/A')}%)")
        else:
            print("SKIP (no data)")
        if i % 10 == 9:
            time.sleep(1)  # rate limit courtesy

    out_path = Path(__file__).parent / "charts" / "etf_analysis.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps({"generatedAt": datetime.now().isoformat(), "etfs": results},
                    ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nSaved {len(results)}/{total} ETFs to {out_path}")


if __name__ == "__main__":
    main()
