"""AI chain heat / sector heat scoring."""
import numpy as np
import pandas as pd
from typing import Dict, Any
from backend.core.utils import clamp, safe_float
from backend.indicators.technical import compute_indicators
from backend.data_providers import akshare_provider, yfinance_provider
from backend.core.config import get_sectors


def compute_sector_heat() -> Dict[str, Dict[str, Any]]:
    sectors_cfg = get_sectors()
    out = {}
    for sector, cfg in sectors_cfg.items():
        cn_codes = cfg.get("representatives_cn", []) or []
        us_codes = cfg.get("representatives_us", []) or []
        members = []
        for code in cn_codes:
            df = akshare_provider.fetch_a_stock(code)
            if df is not None: members.append(("CN", code, df))
        for code in us_codes:
            df = yfinance_provider.fetch_history(code)
            if df is not None: members.append(("US", code, df))
        if not members:
            out[sector] = {"heat": None, "reason": "no data", "members": 0}
            continue

        rets20, rets60, vrs, mdds, rsis = [], [], [], [], []
        up_count = 0
        for _, _, df in members:
            ind = compute_indicators(df)
            if not ind: continue
            r20 = ind.get("ret_20d"); r60 = ind.get("ret_60d")
            if r20 is None or r60 is None: continue
            rets20.append(r20); rets60.append(r60)
            if ind.get("rsi_14") is not None:
                rsis.append(ind["rsi_14"])
            if ind.get("mdd_120d") is not None:
                mdds.append(ind["mdd_120d"])
            if ind.get("volume_ratio") is not None:
                vrs.append(ind["volume_ratio"])
            if r20 > 0: up_count += 1
        if not rets20:
            out[sector] = {"heat": None, "reason": "insufficient", "members": len(members)}
            continue
        r20_avg = float(np.mean(rets20)); r60_avg = float(np.mean(rets60))
        momentum = clamp(50 + r20_avg * 2 + r60_avg * 0.8)
        vr = float(np.mean(vrs)) if vrs else 1.0
        volume_score = clamp(30 + (vr - 1) * 40)
        breadth = clamp(up_count / len(rets20) * 100)
        rsi_avg = float(np.mean(rsis)) if rsis else 50
        risk_pen = 0
        if rsi_avg > 75: risk_pen += 15
        if rsi_avg > 80: risk_pen += 10
        if vr > 2.0: risk_pen += 10
        if r20_avg > 25: risk_pen += 10
        heat = 0.35 * momentum + 0.25 * volume_score + 0.20 * breadth + 0.20 * 50 - risk_pen
        heat = clamp(heat)
        out[sector] = {
            "heat": round(heat, 1),
            "momentum": round(momentum, 1),
            "volume": round(volume_score, 1),
            "breadth": round(breadth, 1),
            "risk_penalty": risk_pen,
            "r20_avg": round(r20_avg, 2),
            "r60_avg": round(r60_avg, 2),
            "rsi_avg": round(rsi_avg, 1),
            "vol_ratio": round(vr, 2),
            "members": len(members),
            "action": _action_from(heat, risk_pen, rsi_avg, r20_avg),
        }
    return out


def _action_from(heat: float, risk_pen: int, rsi: float, r20: float) -> str:
    if heat is None: return "\u89c2\u671b"
    if risk_pen >= 25 or rsi > 80 or r20 > 30:
        return "\u56de\u907f"
    if heat > 70 and rsi < 70 and r20 < 20:
        return "\u52a0\u4ed3"
    if heat > 55:
        return "\u6301\u6709"
    if heat < 35:
        return "\u51cf\u4ed3"
    return "\u89c2\u671b"
