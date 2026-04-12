"""Generate interactive Plotly HTML charts for financial data comparison.

Usage:
    python chart.py VOO QQQM --days 180 --output charts/comparison.html
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from plotly.subplots import make_subplots


def fetch_data(
    symbols: list[str], days: int
) -> dict[str, pd.DataFrame]:
    """Fetch historical price data for given symbols."""
    end = datetime.now()
    start = end - timedelta(days=days)
    result = {}
    for symbol in symbols:
        df = yf.download(symbol, start=start, end=end, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        result[symbol] = df
    return result


def compute_normalized_returns(
    data: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Compute normalized cumulative returns (base=100) for comparison."""
    frames = {}
    for symbol, df in data.items():
        close = df["Close"]
        normalized = (close / close.iloc[0]) * 100
        frames[symbol] = normalized
    return pd.DataFrame(frames)


def compute_drawdowns(
    data: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Compute drawdown series for each symbol."""
    frames = {}
    for symbol, df in data.items():
        close = df["Close"]
        peak = close.cummax()
        drawdown = (close - peak) / peak * 100
        frames[symbol] = drawdown
    return pd.DataFrame(frames)


def compute_monthly_returns(
    data: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Compute monthly returns for each symbol."""
    frames = {}
    for symbol, df in data.items():
        monthly = df["Close"].resample("ME").last()
        ret = monthly.pct_change().dropna() * 100
        frames[symbol] = ret
    return pd.DataFrame(frames).dropna()


def build_chart(
    data: dict[str, pd.DataFrame],
    symbols: list[str],
    days: int,
) -> go.Figure:
    """Build a multi-panel Plotly figure."""
    normalized = compute_normalized_returns(data)
    drawdowns = compute_drawdowns(data)
    monthly = compute_monthly_returns(data)

    colors = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A"]

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        subplot_titles=(
            "Cumulative Return (Base = 100)",
            "Drawdown (%)",
            "Monthly Return (%)",
        ),
        row_heights=[0.45, 0.25, 0.30],
    )

    # Panel 1: Normalized cumulative returns
    for i, symbol in enumerate(symbols):
        if symbol in normalized.columns:
            fig.add_trace(
                go.Scatter(
                    x=normalized.index,
                    y=normalized[symbol],
                    name=symbol,
                    line={"color": colors[i % len(colors)]},
                    hovertemplate=f"{symbol}: %{{y:.2f}}<extra></extra>",
                ),
                row=1,
                col=1,
            )

    # Panel 2: Drawdown
    for i, symbol in enumerate(symbols):
        if symbol in drawdowns.columns:
            fig.add_trace(
                go.Scatter(
                    x=drawdowns.index,
                    y=drawdowns[symbol],
                    name=symbol,
                    line={"color": colors[i % len(colors)]},
                    fill="tozeroy",
                    opacity=0.3,
                    showlegend=False,
                    hovertemplate=f"{symbol}: %{{y:.2f}}%<extra></extra>",
                ),
                row=2,
                col=1,
            )

    # Panel 3: Monthly returns bar chart
    bar_width = 20 * 24 * 3600 * 1000 / len(symbols)
    for i, symbol in enumerate(symbols):
        if symbol in monthly.columns:
            offset = (i - len(symbols) / 2 + 0.5) * bar_width
            fig.add_trace(
                go.Bar(
                    x=monthly.index + pd.Timedelta(milliseconds=offset),
                    y=monthly[symbol],
                    name=symbol,
                    marker_color=colors[i % len(colors)],
                    showlegend=False,
                    hovertemplate=f"{symbol}: %{{y:+.2f}}%<extra></extra>",
                    width=bar_width,
                ),
                row=3,
                col=1,
            )

    # Summary stats annotation
    stats_lines = []
    for symbol in symbols:
        df = data[symbol]
        close = df["Close"]
        start_p = float(close.iloc[0])
        end_p = float(close.iloc[-1])
        ret = (end_p - start_p) / start_p * 100
        peak = close.cummax()
        dd = float(((close - peak) / peak).min() * 100)
        stats_lines.append(f"{symbol}: {ret:+.2f}% (MDD: {dd:.2f}%)")

    date_range = (
        f"{data[symbols[0]].index[0].strftime('%Y-%m-%d')} ~ "
        f"{data[symbols[0]].index[-1].strftime('%Y-%m-%d')}"
    )

    fig.update_layout(
        title={
            "text": (
                f"{'  vs  '.join(symbols)} - {days}D Performance<br>"
                f"<sub>{date_range}  |  {'  |  '.join(stats_lines)}</sub>"
            ),
            "x": 0.5,
            "xanchor": "center",
        },
        height=900,
        template="plotly_dark",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "center", "x": 0.5},
        hovermode="x unified",
        margin={"t": 120, "b": 40},
    )

    fig.update_yaxes(title_text="Value", row=1, col=1)
    fig.update_yaxes(title_text="DD %", row=2, col=1)
    fig.update_yaxes(title_text="Return %", row=3, col=1)

    return fig


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare ETF/stock performance")
    parser.add_argument("symbols", nargs="+", help="Ticker symbols to compare")
    parser.add_argument("--days", type=int, default=180, help="Lookback period in days")
    parser.add_argument("--output", type=str, default=None, help="Output HTML file path")
    args = parser.parse_args()

    symbols = [s.upper() for s in args.symbols]
    output = args.output or f"charts/{'_vs_'.join(symbols)}_{args.days}d.html"
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Fetching data for {', '.join(symbols)} ({args.days} days)...")
    data = fetch_data(symbols, args.days)

    for symbol in symbols:
        if data[symbol].empty:
            print(f"Error: No data found for {symbol}", file=sys.stderr)
            sys.exit(1)

    print("Building chart...")
    fig = build_chart(data, symbols, args.days)
    fig.write_html(str(output_path), include_plotlyjs=True)
    print(f"Chart saved to: {output_path.resolve()}")


if __name__ == "__main__":
    main()
