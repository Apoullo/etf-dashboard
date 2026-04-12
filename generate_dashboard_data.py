"""Fetch all market data and export as JSON for the dashboard."""

import json
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf

PORTFOLIO = [
    {
        "category": "Core Holdings",
        "categoryZh": "核心配置",
        "color": "#1a3a5c",
        "items": [
            {"ticker": "VOO", "name": "Vanguard S&P 500 ETF", "nameZh": "Vanguard 標普500 ETF", "weight": 30, "expense": "0.03%", "desc": "S&P 500 大盤，最分散的核心基石", "color": "#2563eb"},
            {"ticker": "QQQM", "name": "Invesco NASDAQ 100 ETF", "nameZh": "Invesco 那斯達克100 ETF", "weight": 25, "expense": "0.15%", "desc": "NASDAQ-100 科技成長，AI 天然曝險", "color": "#3b82f6"},
        ],
    },
    {
        "category": "AI & Semiconductors",
        "categoryZh": "AI / 半導體",
        "color": "#7c3aed",
        "items": [
            {"ticker": "SMH", "name": "VanEck Semiconductor ETF", "nameZh": "VanEck 半導體 ETF", "weight": 10, "expense": "0.35%", "desc": "集中型半導體，重壓 NVIDIA + TSMC", "color": "#8b5cf6"},
            {"ticker": "AIQ", "name": "Global X AI & Technology ETF", "nameZh": "Global X AI科技 ETF", "weight": 5, "expense": "0.68%", "desc": "廣泛 AI 價值鏈，84+ 持股分散風險", "color": "#a78bfa"},
        ],
    },
    {
        "category": "Power & Nuclear",
        "categoryZh": "電力 / 核能",
        "color": "#059669",
        "items": [
            {"ticker": "GRID", "name": "First Trust Smart Grid Infrastructure", "nameZh": "First Trust 智慧電網 ETF", "weight": 8, "expense": "0.56%", "desc": "電網現代化，受惠 AI 資料中心用電需求", "color": "#10b981"},
            {"ticker": "XLU", "name": "Utilities Select Sector SPDR", "nameZh": "SPDR 公用事業精選 ETF", "weight": 5, "expense": "0.08%", "desc": "防禦型公用事業，提供穩定股息收益", "color": "#34d399"},
            {"ticker": "NLR", "name": "VanEck Uranium and Nuclear ETF", "nameZh": "VanEck 鈾與核能 ETF", "weight": 4, "expense": "0.56%", "desc": "核能全價值鏈，礦商 + 核電公用事業", "color": "#6ee7b7"},
        ],
    },
    {
        "category": "GLP-1 & Weight Loss",
        "categoryZh": "GLP-1 減肥藥",
        "color": "#dc2626",
        "items": [
            {"ticker": "OZEM", "name": "Roundhill GLP-1 & Weight Loss ETF", "nameZh": "Roundhill GLP-1減重 ETF", "weight": 5, "expense": "0.59%", "desc": "純 GLP-1 概念，Eli Lilly + Novo Nordisk", "color": "#ef4444"},
            {"ticker": "PPH", "name": "VanEck Pharmaceutical ETF", "nameZh": "VanEck 製藥 ETF", "weight": 4, "expense": "0.36%", "desc": "大型藥廠，GLP-1 權重 ~23%，較分散", "color": "#f87171"},
        ],
    },
    {
        "category": "Cash / Bond Buffer",
        "categoryZh": "現金 / 債券緩衝",
        "color": "#78716c",
        "items": [
            {"ticker": "BND", "name": "Vanguard Total Bond Market ETF", "nameZh": "Vanguard 全債券市場 ETF", "weight": 4, "expense": "0.03%", "desc": "降低整體波動，逢低加碼的彈藥庫", "color": "#a8a29e"},
        ],
    },
]

ALL_TICKERS = [item["ticker"] for group in PORTFOLIO for item in group["items"]]


def fetch_all_data(days: int = 365) -> dict:
    """Fetch price history and PE data for all tickers."""
    end = datetime.now()
    start = end - timedelta(days=days)

    price_history = {}
    current_prices = {}
    pe_ratios = {}

    for ticker in ALL_TICKERS:
        print(f"  Fetching {ticker}...")
        df = yf.download(ticker, start=start, end=end, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        dates = [d.strftime("%Y-%m-%d") for d in df.index]
        closes = [round(float(v), 2) for v in df["Close"]]
        price_history[ticker] = {"dates": dates, "closes": closes}
        current_prices[ticker] = closes[-1] if closes else 0

        try:
            info = yf.Ticker(ticker).info
            pe = info.get("trailingPE") or info.get("trailingPe")
            pe_ratios[ticker] = round(float(pe), 2) if pe else None
        except Exception:
            pe_ratios[ticker] = None

    return {
        "priceHistory": price_history,
        "currentPrices": current_prices,
        "peRatios": pe_ratios,
    }


def compute_portfolio_series(
    price_history: dict, weights: dict[str, int]
) -> dict:
    """Compute weighted portfolio normalized series."""
    all_frames = {}
    for ticker, w in weights.items():
        ph = price_history[ticker]
        s = pd.Series(ph["closes"], index=pd.to_datetime(ph["dates"]))
        all_frames[ticker] = s

    combined = pd.DataFrame(all_frames).dropna()
    portfolio_val = pd.Series(0.0, index=combined.index)
    for ticker, w in weights.items():
        col = combined[ticker]
        portfolio_val += (col / col.iloc[0]) * w / 100

    portfolio_norm = (portfolio_val / portfolio_val.iloc[0]) * 100
    return {
        "dates": [d.strftime("%Y-%m-%d") for d in portfolio_norm.index],
        "values": [round(float(v), 2) for v in portfolio_norm],
    }


def compute_monthly_returns(price_history: dict) -> dict:
    """Compute monthly returns per ticker."""
    result = {}
    for ticker, ph in price_history.items():
        s = pd.Series(ph["closes"], index=pd.to_datetime(ph["dates"]))
        monthly = s.resample("ME").last()
        ret = monthly.pct_change().dropna() * 100
        result[ticker] = {
            "months": [d.strftime("%Y-%m") for d in ret.index],
            "returns": [round(float(v), 2) for v in ret],
        }
    return result


def main() -> None:
    print("Fetching market data...")
    market = fetch_all_data(365)

    weights = {item["ticker"]: item["weight"] for group in PORTFOLIO for item in group["items"]}
    portfolio_series = compute_portfolio_series(market["priceHistory"], weights)
    monthly = compute_monthly_returns(market["priceHistory"])

    output = {
        "generatedAt": datetime.now().isoformat(),
        "portfolio": PORTFOLIO,
        "currentPrices": market["currentPrices"],
        "peRatios": market["peRatios"],
        "priceHistory": market["priceHistory"],
        "portfolioSeries": portfolio_series,
        "monthlyReturns": monthly,
    }

    out_path = Path(__file__).parent / "charts" / "dashboard_data.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, ensure_ascii=False), encoding="utf-8")
    print(f"Data saved to {out_path}")


if __name__ == "__main__":
    main()
