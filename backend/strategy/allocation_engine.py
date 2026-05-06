"""Allocation engine."""
from typing import Dict, Any
from backend.core.config import get_thresholds


def allocate(regime: str) -> Dict[str, Any]:
    th = get_thresholds()
    mapping = th.get("regime_allocation", {})
    bands = mapping.get(regime, mapping.get("Neutral", {
        "equity": [55, 65], "ai_tech": [35, 50],
        "packaging_hbm_cool": [20, 30], "gold_energy": [15, 25],
        "btc": [2, 7], "cash": [15, 25],
    }))
    return bands
