"""Fear & Greed score computation."""
import numpy as np
from typing import Dict, Any, Optional, List
import pandas as pd
from backend.core.utils import clamp


def compute_global_fng(yf_data: Dict[str, pd.DataFrame], crypto_fng: Optional[int] = None) -> Dict[str, Any]:
    breakdown = {}
    missing = []

    # 1. VIX inverse 25%
    vix_score = None; vix_val = None
    if "^VIX" in yf_data:
        vix_val = float(yf_data["^VIX"]["close"].iloc[-1])
        vix_score = clamp((40 - vix_val) / (40 - 10) * 100)
    else:
        missing.append("VIX")
    breakdown["vix_inverse"] = {"weight": 25, "score": vix_score, "raw": vix_val, "label": "VIX 反向分"}

    # 2. Nasdaq vs 200MA 20%
    ndq_score = None
    if "^IXIC" in yf_data:
        c = yf_data["^IXIC"]["close"]
        ma200 = c.rolling(200).mean().iloc[-1]
        if not np.isnan(ma200):
            pct = (c.iloc[-1] / ma200 - 1) * 100
            ndq_score = clamp((pct + 15) / 30 * 100)
    else:
        missing.append("Nasdaq")
    breakdown["nasdaq_200ma"] = {"weight": 20, "score": ndq_score, "label": "Nasdaq vs 200日均线"}

    # 3. SOX 15%
    sox_score = None
    sox_key = "SOXX" if "SOXX" in yf_data else ("SMH" if "SMH" in yf_data else None)
    if sox_key:
        c = yf_data[sox_key]["close"]
        ma50 = c.rolling(50).mean().iloc[-1]
        if not np.isnan(ma50):
            pct = (c.iloc[-1] / ma50 - 1) * 100
            sox_score = clamp((pct + 10) / 20 * 100)
    else:
        missing.append("SOX")
    breakdown["sox_trend"] = {"weight": 15, "score": sox_score, "label": "\u534a\u5bfc\u4f53 ETF \u8d8b\u52bf"}

    # 4. UST10Y change inverse 10%
    ust_score = None
    if "^TNX" in yf_data:
        c = yf_data["^TNX"]["close"]
        if len(c) > 60:
            chg = c.iloc[-1] - c.iloc[-60]
            ust_score = clamp(50 - chg / 0.01 * 10)
    else:
        missing.append("UST10Y")
    breakdown["ust10_inverse"] = {"weight": 10, "score": ust_score, "label": "10Y \u7f8e\u503a\u53cd\u5411\u5206"}

    # 5. DXY change inverse 10%
    dxy_score = None
    if "DX-Y.NYB" in yf_data:
        c = yf_data["DX-Y.NYB"]["close"]
        if len(c) > 60:
            pct = (c.iloc[-1] / c.iloc[-60] - 1) * 100
            dxy_score = clamp(50 - pct * 10)
    else:
        missing.append("DXY")
    breakdown["dxy_inverse"] = {"weight": 10, "score": dxy_score, "label": "DXY \u53cd\u5411\u5206"}

    # 6. BTC + Crypto F&G 10%
    btc_score = None
    parts = []
    if "BTC-USD" in yf_data:
        c = yf_data["BTC-USD"]["close"]
        ma100 = c.rolling(100).mean().iloc[-1]
        if not np.isnan(ma100):
            pct = (c.iloc[-1] / ma100 - 1) * 100
            parts.append(clamp((pct + 20) / 40 * 100))
    if crypto_fng is not None:
        parts.append(crypto_fng)
    if parts:
        btc_score = float(np.mean(parts))
    else:
        missing.append("BTC/CryptoFNG")
    breakdown["btc_crypto"] = {"weight": 10, "score": btc_score, "label": "BTC \u8d8b\u52bf + Crypto F&G"}

    # 7. SP500 breadth 10%
    br_score = None
    if "^GSPC" in yf_data:
        c = yf_data["^GSPC"]["close"]
        ma50 = c.rolling(50).mean().iloc[-1]
        if not np.isnan(ma50):
            pct = (c.iloc[-1] / ma50 - 1) * 100
            br_score = clamp((pct + 5) / 10 * 100)
    else:
        missing.append("SP500")
    breakdown["global_breadth"] = {"weight": 10, "score": br_score, "label": "S&P500 \u8d8b\u52bf\u4ee3\u7406\u5e7f\u5ea6"}

    total_w = sum(v["weight"] for v in breakdown.values() if v["score"] is not None)
    total_s = sum(v["weight"] * v["score"] for v in breakdown.values() if v["score"] is not None)
    score = total_s / total_w if total_w > 0 else 50
    return {"score": round(score, 1), "breakdown": breakdown, "missing": missing}


def compute_china_tech_fng(ak_data: Dict[str, Any]) -> Dict[str, Any]:
    breakdown = {}
    missing = []
    idx = ak_data.get("indices", {})

    # 1. Tech indices trend 25%
    trends = []
    for code in ["sh000688", "sz399006", "sz399001"]:
        if code in idx:
            c = idx[code]["close"]
            ma50 = c.rolling(50).mean().iloc[-1]
            if not np.isnan(ma50):
                pct = (c.iloc[-1] / ma50 - 1) * 100
                trends.append(clamp((pct + 10) / 20 * 100))
    trend_score = float(np.mean(trends)) if trends else None
    breakdown["tech_trend"] = {"weight": 25, "score": trend_score, "label": "\u79d1\u521b50/\u521b\u4e1a\u677f/\u6df1\u6210\u6307 \u8d8b\u52bf"}

    # 2. Total turnover 20%
    tv_score = None
    total_tv = ak_data.get("total_turnover")
    if total_tv is not None:
        if total_tv < 0.6: tv_score = 15
        elif total_tv < 0.9: tv_score = 35
        elif total_tv < 1.2: tv_score = 55
        elif total_tv < 1.5: tv_score = 70
        elif total_tv < 1.8: tv_score = 82
        elif total_tv < 2.2: tv_score = 90
        else: tv_score = 95
    else:
        missing.append("Total turnover")
    breakdown["total_turnover"] = {"weight": 20, "score": tv_score, "raw_wanyi": total_tv,
                                    "label": "\u4e24\u5e02\u603b\u6210\u4ea4\u989d"}

    # 3. CSI300 breadth 20%
    br_score = None
    if "sh000300" in idx:
        c = idx["sh000300"]["close"]
        ma200 = c.rolling(200).mean().iloc[-1]
        if not np.isnan(ma200):
            pct = (c.iloc[-1] / ma200 - 1) * 100
            br_score = clamp((pct + 15) / 30 * 100)
    breakdown["csi300_breadth"] = {"weight": 20, "score": br_score, "label": "\u6caa\u6df1300 vs 200\u65e5\u5e73\u5747\u7ebf"}

    # 4-5: Limit-up + Margin (placeholder - can be added later)
    missing.append("\u6da8\u505c\u6570 \u5360\u4f4d")
    missing.append("\u878d\u8d44\u4f59\u989d \u5360\u4f4d")

    # 6. STAR50 valuation deviation 15%
    val_score = None
    if "sh000688" in idx:
        c = idx["sh000688"]["close"]
        ma200 = c.rolling(200).mean().iloc[-1]
        if not np.isnan(ma200):
            pct = (c.iloc[-1] / ma200 - 1) * 100
            val_score = clamp(50 + pct * 2)
    breakdown["valuation_deviation"] = {"weight": 15, "score": val_score,
                                          "label": "\u79d1\u521b50 \u4f30\u503c\u504f\u79bb\u5ea6"}

    total_w = sum(v["weight"] for v in breakdown.values() if v["score"] is not None)
    total_s = sum(v["weight"] * v["score"] for v in breakdown.values() if v["score"] is not None)
    score = total_s / total_w if total_w > 0 else 50
    return {"score": round(score, 1), "breakdown": breakdown, "missing": missing}
