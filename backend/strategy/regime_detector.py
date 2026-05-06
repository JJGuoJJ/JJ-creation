"""Market regime detection."""
from typing import Dict, Any


def detect_regime(global_fng: float, china_fng: float, ai_chain_scores: Dict[str, Any]) -> Dict[str, Any]:
    valid_heat = [v["heat"] for v in ai_chain_scores.values() if v.get("heat") is not None]
    ai_peak = max(valid_heat) if valid_heat else 50
    combined = 0.40 * global_fng + 0.40 * china_fng + 0.20 * ai_peak
    combined = round(combined, 1)

    if combined < 25:
        regime = "Extreme Fear"; cn = "\u6781\u5ea6\u6050\u614c"; action = "\u5206\u6279\u4f4e\u5438\u6838\u5fc3\u8d44\u4ea7"
    elif combined < 40:
        regime = "Fear"; cn = "\u6050\u614c"; action = "\u9010\u6b65\u52a0\u4ed3\u9ad8\u8d28\u91cf\u4e3b\u7ebf"
    elif combined < 60:
        regime = "Neutral"; cn = "\u4e2d\u6027"; action = "\u6309\u76ee\u6807\u4ed3\u4f4d\u914d\u7f6e"
    elif combined < 75:
        regime = "Greed"; cn = "\u8d2a\u5a6a"; action = "\u6301\u6709\u6838\u5fc3\uff0c\u4e0d\u8ffd\u6da8"
    elif combined < 90:
        regime = "Extreme Greed"; cn = "\u6781\u5ea6\u8d2a\u5a6a"; action = "\u9ad8\u5f39\u6027\u4ed3\u5206\u6279\u6b62\u76c8"
    else:
        regime = "Bubble Risk"; cn = "\u6ce1\u6cab\u98ce\u9669"; action = "\u964d\u4f4e\u9ad8 beta \u4ed3\u4f4d\uff0c\u4fdd\u7559\u73b0\u91d1"
    return {
        "combined_score": combined,
        "regime": regime,
        "regime_cn": cn,
        "action": action,
        "global_fng": global_fng,
        "china_fng": china_fng,
        "ai_peak_heat": ai_peak,
    }
