"""
4-Agent Rule-Based ETF Analysis Engine

Four pure-Python agents analyze each ETF from multiple angles:
  1. technical_analyst  - EMA, RSI, MACD signals
  2. fundamental_analyst - PE, expense ratio, AUM, dividend yield
  3. risk_manager        - volatility, max drawdown, beta, liquidity
  4. portfolio_manager   - weighted synthesis of the above three
"""

import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Helper: parse human-readable strings into floats
# ---------------------------------------------------------------------------

def parse_aum(s: str) -> float:
    """Convert '$9.0B' / '$320M' / '$1.2T' to a float in dollars."""
    if not s:
        return 0.0
    s = s.strip().replace("$", "").replace(",", "")
    multipliers = {"T": 1e12, "B": 1e9, "M": 1e6, "K": 1e3}
    for suffix, mult in multipliers.items():
        if s.upper().endswith(suffix):
            return float(s[:-1]) * mult
    try:
        return float(s)
    except ValueError:
        return 0.0


def parse_er(s: str) -> float:
    """Convert '0.55%' to 0.55 (as a percentage number, not decimal)."""
    if not s:
        return 0.0
    s = s.strip().replace("%", "")
    try:
        return float(s)
    except ValueError:
        return 0.0


# ---------------------------------------------------------------------------
# Technical indicators
# ---------------------------------------------------------------------------

def _ema(prices: list[float], span: int) -> list[float]:
    """Exponential moving average."""
    if not prices:
        return []
    k = 2.0 / (span + 1)
    result = [prices[0]]
    for p in prices[1:]:
        result.append(p * k + result[-1] * (1 - k))
    return result


def _rsi(prices: list[float], period: int = 14) -> float:
    """RSI based on the last *period* price changes."""
    if len(prices) < period + 1:
        return 50.0  # neutral fallback
    deltas = [prices[i] - prices[i - 1] for i in range(len(prices) - period, len(prices))]
    gains = [d for d in deltas if d > 0]
    losses = [-d for d in deltas if d < 0]
    avg_gain = sum(gains) / period if gains else 0.0
    avg_loss = sum(losses) / period if losses else 0.0001
    rs = avg_gain / avg_loss
    return 100.0 - 100.0 / (1.0 + rs)


def _macd_histogram(prices: list[float]) -> float:
    """MACD histogram = MACD line - signal line."""
    if len(prices) < 26:
        return 0.0
    ema12 = _ema(prices, 12)
    ema26 = _ema(prices, 26)
    macd_line = [a - b for a, b in zip(ema12, ema26)]
    signal = _ema(macd_line, 9)
    return macd_line[-1] - signal[-1]


# ---------------------------------------------------------------------------
# Agent 1: Technical Analyst
# ---------------------------------------------------------------------------

def technical_analyst(ticker: str, closes: list[float]) -> dict:
    """Analyse weekly close prices and return a technical signal."""
    if not closes or len(closes) < 10:
        return {"signal": "neutral", "confidence": 10, "reasoning": "价格数据不足，无法进行技术分析。"}

    price = closes[-1]
    ema20 = _ema(closes, 20)[-1]
    ema50_vals = _ema(closes, min(50, len(closes)))
    ema50 = ema50_vals[-1]
    rsi = _rsi(closes, 14)
    macd_hist = _macd_histogram(closes)

    above_ema50 = price > ema50
    above_ema20 = price > ema20
    rsi_overbought = rsi > 70
    rsi_oversold = rsi < 30
    rsi_healthy = 40 <= rsi <= 65
    macd_positive = macd_hist > 0

    bullish_points = 0
    bearish_points = 0
    reasons = []

    if above_ema50:
        bullish_points += 1
        reasons.append(f"价格({price:.2f})高于EMA50({ema50:.2f})")
    else:
        bearish_points += 1
        reasons.append(f"价格({price:.2f})低于EMA50({ema50:.2f})")

    if above_ema20:
        bullish_points += 1
    else:
        bearish_points += 1

    if rsi_oversold:
        bullish_points += 1
        reasons.append(f"RSI({rsi:.1f})超卖，可能反弹")
    elif rsi_healthy:
        bullish_points += 1
        reasons.append(f"RSI({rsi:.1f})处于健康区间")
    elif rsi_overbought:
        bearish_points += 1
        reasons.append(f"RSI({rsi:.1f})超买，存在回调风险")
    else:
        reasons.append(f"RSI({rsi:.1f})处于中性区间")

    if macd_positive:
        bullish_points += 1
        reasons.append("MACD柱状图为正，动能向上")
    else:
        bearish_points += 1
        reasons.append("MACD柱状图为负，动能向下")

    # Determine signal
    if bullish_points >= 3 and above_ema50:
        signal = "bullish"
    elif bearish_points >= 3 and not above_ema50:
        signal = "bearish"
    else:
        signal = "neutral"

    total = bullish_points + bearish_points
    dominant = max(bullish_points, bearish_points)
    confidence = int(min(95, max(10, (dominant / max(total, 1)) * 80 + 10)))

    return {
        "signal": signal,
        "confidence": confidence,
        "reasoning": "；".join(reasons),
    }


# ---------------------------------------------------------------------------
# Agent 2: Fundamental Analyst
# ---------------------------------------------------------------------------

def fundamental_analyst(ticker: str, metrics: dict) -> dict:
    """Score ETF fundamentals: PE, expense ratio, AUM, dividend yield."""
    pe = metrics.get("pe")
    er = metrics.get("er_num", 0.0)   # percentage number, e.g. 0.55
    aum = metrics.get("aum_num", 0.0)  # dollar amount
    div_yield = metrics.get("divYield")

    score = 0
    reasons = []

    # PE scoring
    if pe is not None and pe > 0:
        if pe < 20:
            score += 2
            reasons.append(f"PE({pe:.1f})偏低，估值合理")
        elif pe < 30:
            score += 1
            reasons.append(f"PE({pe:.1f})适中")
        elif pe < 40:
            reasons.append(f"PE({pe:.1f})偏高")
        else:
            score -= 1
            reasons.append(f"PE({pe:.1f})过高，估值昂贵")
    else:
        reasons.append("PE数据缺失")

    # Expense ratio scoring
    if er <= 0.2:
        score += 2
        reasons.append(f"费率({er:.2f}%)极低，成本优势明显")
    elif er <= 0.5:
        score += 1
        reasons.append(f"费率({er:.2f}%)合理")
    elif er <= 0.7:
        reasons.append(f"费率({er:.2f}%)中等")
    else:
        score -= 1
        reasons.append(f"费率({er:.2f}%)偏高")

    # AUM scoring
    if aum >= 5e9:
        score += 1
        reasons.append("资产规模大，流动性强")
    elif aum >= 200e6:
        reasons.append("资产规模适中")
    elif aum >= 50e6:
        score -= 1
        reasons.append("资产规模偏小")
    else:
        score -= 2
        reasons.append("资产规模过小，存在流动性风险")

    # Dividend yield scoring
    if div_yield is not None and div_yield > 2:
        score += 1
        reasons.append(f"股息率({div_yield:.1f}%)具吸引力")

    # Signal
    if score >= 3:
        signal = "bullish"
    elif score <= -1:
        signal = "bearish"
    else:
        signal = "neutral"

    confidence = int(min(95, max(10, abs(score) * 18 + 20)))

    return {
        "signal": signal,
        "confidence": confidence,
        "reasoning": "；".join(reasons),
    }


# ---------------------------------------------------------------------------
# Agent 3: Risk Manager
# ---------------------------------------------------------------------------

def risk_manager(ticker: str, metrics: dict) -> dict:
    """Assess risk: volatility, max drawdown, beta, average volume."""
    vol = metrics.get("volatility") or 0
    mdd = metrics.get("maxDD") or 0
    beta = metrics.get("beta")
    avg_vol = metrics.get("avgVolume") or 0

    risk_score = 0
    reasons = []

    # Volatility scoring
    if vol < 15:
        reasons.append(f"波动率({vol:.1f}%)较低，走势平稳")
    elif vol < 25:
        risk_score += 1
        reasons.append(f"波动率({vol:.1f}%)适中")
    elif vol < 35:
        risk_score += 2
        reasons.append(f"波动率({vol:.1f}%)偏高")
    else:
        risk_score += 3
        reasons.append(f"波动率({vol:.1f}%)极高，风险显著")

    # Max drawdown scoring
    if mdd > -15:
        reasons.append(f"最大回撤({mdd:.1f}%)可控")
    elif mdd > -25:
        risk_score += 1
        reasons.append(f"最大回撤({mdd:.1f}%)中等")
    else:
        risk_score += 2
        reasons.append(f"最大回撤({mdd:.1f}%)较大，需注意")

    # Beta scoring
    if beta is not None:
        if 0.5 <= beta <= 1.2:
            reasons.append(f"Beta({beta:.2f})处于正常范围")
        elif beta <= 1.5:
            risk_score += 1
            reasons.append(f"Beta({beta:.2f})偏高")
        else:
            risk_score += 2
            reasons.append(f"Beta({beta:.2f})过高，市场波动放大")
    else:
        reasons.append("Beta数据缺失")

    # Volume scoring
    if avg_vol < 50_000:
        risk_score += 1
        reasons.append(f"日均成交量({avg_vol:,.0f})偏低，流动性不足")
    else:
        reasons.append(f"日均成交量({avg_vol:,.0f})充足")

    # Signal
    if risk_score <= 1:
        signal = "safe"
    elif risk_score <= 3:
        signal = "caution"
    else:
        signal = "warning"

    confidence = int(min(95, max(10, 80 - risk_score * 8)))

    return {
        "signal": signal,
        "confidence": confidence,
        "reasoning": "；".join(reasons),
    }


# ---------------------------------------------------------------------------
# Agent 4: Portfolio Manager (weighted synthesis)
# ---------------------------------------------------------------------------

_SIGNAL_SCORE = {
    "bullish": 1.0,
    "neutral": 0.0,
    "bearish": -1.0,
    "safe": 0.5,
    "caution": 0.0,
    "warning": -0.5,
}


def portfolio_manager(tech: dict, fund: dict, risk: dict) -> dict:
    """Weighted synthesis: technical 30% + fundamental 40% + risk 30%."""
    t_score = _SIGNAL_SCORE.get(tech["signal"], 0) * (tech["confidence"] / 100) * 0.30
    f_score = _SIGNAL_SCORE.get(fund["signal"], 0) * (fund["confidence"] / 100) * 0.40
    r_score = _SIGNAL_SCORE.get(risk["signal"], 0) * (risk["confidence"] / 100) * 0.30

    composite = t_score + f_score + r_score

    if composite > 0.25:
        signal = "bullish"
    elif composite < -0.15:
        signal = "bearish"
    else:
        signal = "neutral"

    confidence = int(min(95, max(10, abs(composite) * 120 + 25)))

    parts = []
    parts.append(f"技术面{tech['signal']}({tech['confidence']}%)")
    parts.append(f"基本面{fund['signal']}({fund['confidence']}%)")
    risk_label = {"safe": "安全", "caution": "注意", "warning": "警告"}.get(risk["signal"], risk["signal"])
    parts.append(f"风险{risk_label}({risk['confidence']}%)")
    parts.append(f"综合得分{composite:+.3f}")

    return {
        "signal": signal,
        "confidence": confidence,
        "reasoning": "；".join(parts),
    }


# ---------------------------------------------------------------------------
# Main: read data, run all agents, write output
# ---------------------------------------------------------------------------

def main() -> None:
    base = Path(__file__).resolve().parent
    input_path = base / "charts" / "etf_analysis.json"
    output_path = base / "charts" / "ai_signals.json"

    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    etfs = data.get("etfs", data)
    if isinstance(etfs, dict):
        etf_list = list(etfs.values())
    else:
        etf_list = etfs

    signals: dict[str, dict] = {}

    for etf in etf_list:
        ticker = etf.get("ticker", "UNKNOWN")
        closes = etf.get("sparkline", [])

        metrics = {
            "pe": etf.get("pe"),
            "er_num": parse_er(etf.get("expenseRatio", "")),
            "aum_num": parse_aum(etf.get("aumText", "")),
            "divYield": etf.get("divYield"),
            "volatility": etf.get("volatility"),
            "maxDD": etf.get("maxDD"),
            "beta": etf.get("beta"),
            "avgVolume": etf.get("avgVolume"),
        }

        tech = technical_analyst(ticker, closes)
        fund = fundamental_analyst(ticker, metrics)
        risk = risk_manager(ticker, metrics)
        overall = portfolio_manager(tech, fund, risk)

        signals[ticker] = {
            "overall": overall,
            "agents": {
                "technical": tech,
                "fundamental": fund,
                "risk": risk,
            },
        }

    result = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "signals": signals,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Summary
    bull = sum(1 for s in signals.values() if s["overall"]["signal"] == "bullish")
    bear = sum(1 for s in signals.values() if s["overall"]["signal"] == "bearish")
    neut = sum(1 for s in signals.values() if s["overall"]["signal"] == "neutral")
    print(f"AI ETF Analyst complete: {len(signals)} ETFs analyzed")
    print(f"  Bullish: {bull}  |  Neutral: {neut}  |  Bearish: {bear}")
    print(f"  Output: {output_path}")


if __name__ == "__main__":
    main()
