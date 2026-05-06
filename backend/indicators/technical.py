"""Technical indicators."""
import numpy as np
import pandas as pd
from typing import Dict, Any
from backend.core.utils import safe_float


def compute_indicators(df: pd.DataFrame) -> Dict[str, Any]:
    out = {}
    if df is None or len(df) < 20 or "close" not in df.columns:
        return out
    close = df["close"].astype(float)
    for n in [5, 10, 20, 60, 120, 200]:
        ma = close.rolling(n).mean()
        if not np.isnan(ma.iloc[-1]):
            out[f"ma{n}"] = safe_float(ma.iloc[-1])
            out[f"pct_from_ma{n}"] = safe_float((close.iloc[-1] / ma.iloc[-1] - 1) * 100)
        else:
            out[f"ma{n}"] = None
            out[f"pct_from_ma{n}"] = None

    for n in [20, 60, 120]:
        if len(close) > n:
            out[f"ret_{n}d"] = safe_float((close.iloc[-1] / close.iloc[-n] - 1) * 100)
        else:
            out[f"ret_{n}d"] = None

    if len(close) > 60:
        tail = close.tail(120)
        roll_max = tail.cummax()
        dd = (tail / roll_max - 1) * 100
        out["mdd_120d"] = safe_float(dd.min())

    if len(close) > 20:
        ret = close.pct_change().tail(20)
        out["vol_20d"] = safe_float(ret.std() * np.sqrt(252) * 100)

    if len(close) > 15:
        delta = close.diff()
        up = delta.clip(lower=0).rolling(14).mean()
        dn = -delta.clip(upper=0).rolling(14).mean()
        rs = up / dn.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        out["rsi_14"] = safe_float(rsi.iloc[-1]) if not np.isnan(rsi.iloc[-1]) else None

    if "volume" in df.columns and len(df) > 20:
        vol = df["volume"].astype(float)
        v20 = vol.tail(20).mean()
        out["volume_ratio"] = safe_float(vol.iloc[-1] / v20) if v20 > 0 else None

    out["last_close"] = safe_float(close.iloc[-1])
    if len(close) > 1:
        out["chg_pct"] = safe_float((close.iloc[-1] / close.iloc[-2] - 1) * 100)
    return out
