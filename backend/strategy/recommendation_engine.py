"""Stock recommendation engine."""
from typing import Dict, Any, List
import numpy as np
from backend.core.utils import clamp, safe_float
from backend.core.config import get_watchlist, get_strategy_profile
from backend.indicators.technical import compute_indicators
from backend.data_providers import akshare_provider, yfinance_provider


def _decide_action(score: float, sec_heat: float, rsi: float, pct20: float, ret20: float) -> (str, str):
    """Return (action, action_cn) and reason text."""
    if sec_heat > 70 and pct20 > 15 and rsi > 75:
        return ("Avoid Chasing", "\u56de\u907f\u8ffd\u6da8"), f"\u8d5b\u9053\u70ed\u5ea6\u504f\u9ad8({sec_heat:.0f})\u4e14\u4e2a\u80a1\u8ddd20\u65e5\u5747\u7ebf+{pct20:.1f}%\u3001RSI={rsi:.0f}\u8fc7\u70ed\uff0c\u5efa\u8bae\u7b49\u56de\u8c03"
    if sec_heat > 70 and -12 < pct20 < -3 and rsi < 60:
        return ("Strong Buy on Pullback", "\u56de\u8c03\u52a0\u4ed3"), f"\u8d5b\u9053\u70ed\u5ea6\u9ad8({sec_heat:.0f})\uff0c\u4e2a\u80a1\u56de\u8c03 {abs(pct20):.1f}% \u81f3\u5e03\u5c40\u533a\u95f4"
    if sec_heat > 60 and pct20 < 5 and 45 < rsi < 70:
        return ("Buy Small", "\u5c0f\u4ed3\u4f4d\u5e03\u5c40"), f"\u8d5b\u9053\u4e2d\u7b49\u504f\u5f3a({sec_heat:.0f})\uff0c\u6280\u672f\u9762\u672a\u8fc7\u70ed"
    if rsi > 80 or pct20 > 20:
        return ("Trim", "\u51cf\u4ed3\u6b62\u76c8"), f"\u4e2a\u80a1\u8fc7\u70ed\uff08RSI={rsi:.0f}, vs MA20=+{pct20:.1f}%\uff09"
    if rsi < 30:
        return ("Buy Small", "\u8d85\u5356\u5c0f\u4ed3\u4f4d"), f"RSI={rsi:.0f} \u8d85\u5356\uff0c\u53ef\u5c0f\u4ed3\u8bd5\u63a2"
    if score >= 60:
        return ("Hold", "\u6301\u6709"), f"\u7efc\u5408\u5206{score:.0f}\uff0c\u6301\u6709\u73b0\u6709\u4ed3\u4f4d"
    if score < 40:
        return ("Wait", "\u7b49\u5f85"), f"\u7efc\u5408\u5206{score:.0f}\u504f\u4f4e\uff0c\u6682\u4e0d\u5165\u573a"
    return ("Hold", "\u6301\u6709"), f"\u7efc\u5408\u5206{score:.0f}\uff0c\u4e2d\u6027"


def rank_watchlist(sector_heat: Dict[str, Any]) -> List[Dict[str, Any]]:
    wl = get_watchlist()
    weights = get_strategy_profile().get("recommendation_weights", {})
    out = []
    for sym, info in wl.items():
        market = info.get("market", "CN")
        sector = info.get("sector", "")
        name = info.get("name", sym)
        role = info.get("role", "")
        df = None
        if market == "CN":
            df = akshare_provider.fetch_a_stock(sym)
        else:
            df = yfinance_provider.fetch_history(sym)
        if df is None:
            continue
        ind = compute_indicators(df)
        if not ind:
            continue
        sec_h = sector_heat.get(sector, {}).get("heat")
        sec_score = sec_h if sec_h is not None else 50
        ret20 = ind.get("ret_20d", 0) or 0
        ret60 = ind.get("ret_60d", 0) or 0
        pct20 = ind.get("pct_from_ma20", 0) or 0
        rsi = ind.get("rsi_14", 50) or 50
        mom_s = clamp(50 + ret20 * 2 + ret60 * 0.8)
        pullback_s = clamp(50 - pct20 * 5)
        rs_s = clamp((rsi - 30) / 40 * 100)
        risk_s = clamp(100 - (rsi - 50) * 3 - max(0, pct20 - 10) * 5)
        news_s = 50
        fit_s = 70
        total = (
            weights.get("sector_heat", 0.25) * sec_score
            + weights.get("momentum", 0.20) * mom_s
            + weights.get("pullback_value", 0.15) * pullback_s
            + weights.get("relative_strength", 0.15) * rs_s
            + weights.get("risk_control", 0.10) * risk_s
            + weights.get("news_catalyst", 0.10) * news_s
            + weights.get("portfolio_fit", 0.05) * fit_s
        )
        total = round(total, 1)
        (action_en, action_cn), reason = _decide_action(total, sec_score, rsi, pct20, ret20)
        out.append({
            "symbol": sym,
            "name": name,
            "market": market,
            "sector": sector,
            "role": role,
            "score": total,
            "action": action_en,
            "action_cn": action_cn,
            "reason": reason,
            "indicators": {
                "last_close": ind.get("last_close"),
                "chg_pct": ind.get("chg_pct"),
                "ret_20d": ind.get("ret_20d"),
                "ret_60d": ind.get("ret_60d"),
                "pct_from_ma20": ind.get("pct_from_ma20"),
                "pct_from_ma60": ind.get("pct_from_ma60"),
                "pct_from_ma200": ind.get("pct_from_ma200"),
                "rsi_14": ind.get("rsi_14"),
                "vol_20d": ind.get("vol_20d"),
                "volume_ratio": ind.get("volume_ratio"),
                "mdd_120d": ind.get("mdd_120d"),
                "sector_heat": sec_score,
            },
            "score_breakdown": {
                "sector_heat": round(sec_score, 1),
                "momentum": round(mom_s, 1),
                "pullback_value": round(pullback_s, 1),
                "relative_strength": round(rs_s, 1),
                "risk_control": round(risk_s, 1),
            },
        })
    out.sort(key=lambda x: -x["score"])
    return out
