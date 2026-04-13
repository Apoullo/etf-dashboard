"""Fetch all market data and export as JSON for the dashboard."""

import json
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf

# Category metadata: Chinese name -> (English name, group header color)
CAT_META: dict[str, tuple[str, str]] = {
    "核心配置": ("Core Holdings", "#1a3a5c"),
    "AI / 半導體": ("AI & Semiconductors", "#7c3aed"),
    "電力 / 核能": ("Power & Nuclear", "#059669"),
    "GLP-1 減肥藥": ("GLP-1 & Weight Loss", "#dc2626"),
    "現金 / 債券緩衝": ("Cash / Bond Buffer", "#78716c"),
}


def load_portfolio(path: Path | None = None) -> tuple[list[dict], list[str]]:
    """Load portfolio from JSON and return (PORTFOLIO groups, ticker list).

    Falls back to a minimal default if the file is missing or unreadable.
    """
    if path is None:
        path = Path(__file__).parent / "portfolio.json"

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"Warning: could not read {path} ({exc}); using empty portfolio")
        return [], []

    holdings: list[dict] = raw.get("holdings", [])

    # Group holdings by categoryZh, preserving insertion order
    groups_map: dict[str, list[dict]] = {}
    for h in holdings:
        cat_zh = h["categoryZh"]
        groups_map.setdefault(cat_zh, []).append(h)

    portfolio: list[dict] = []
    all_tickers: list[str] = []

    for cat_zh, items in groups_map.items():
        cat_en, group_color = CAT_META.get(cat_zh, (cat_zh, "#6b7280"))
        group_items: list[dict] = []
        for item in items:
            ticker = item["ticker"]
            info = yf.Ticker(ticker).info
            group_items.append({
                "ticker": ticker,
                "name": info.get("shortName", ticker),
                "nameZh": info.get("shortName", ticker),
                "weight": item["weight"],
                "expense": info.get("annualReportExpenseRatio", "N/A"),
                "desc": "",
                "color": item["color"],
            })
            all_tickers.append(ticker)

        portfolio.append({
            "category": cat_en,
            "categoryZh": cat_zh,
            "color": group_color,
            "items": group_items,
        })

    return portfolio, all_tickers


def fetch_all_data(tickers: list[str], days: int = 365) -> dict:
    """Fetch price history and PE data for all tickers."""
    end = datetime.now()
    start = end - timedelta(days=days)

    price_history = {}
    current_prices = {}
    pe_ratios = {}

    for ticker in tickers:
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
    print("Loading portfolio from portfolio.json...")
    portfolio, all_tickers = load_portfolio()

    print("Fetching market data...")
    market = fetch_all_data(all_tickers, 365)

    weights = {item["ticker"]: item["weight"] for group in portfolio for item in group["items"]}
    portfolio_series = compute_portfolio_series(market["priceHistory"], weights)
    monthly = compute_monthly_returns(market["priceHistory"])

    output = {
        "generatedAt": datetime.now().isoformat(),
        "portfolio": portfolio,
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
