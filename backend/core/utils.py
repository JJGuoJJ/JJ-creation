"""Common utility helpers."""
import math
import numpy as np
import pandas as pd
from typing import Any
from datetime import datetime, timezone, timedelta

BJ = timezone(timedelta(hours=8))


def clamp(x: float, lo: float = 0, hi: float = 100) -> float:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return lo
    return max(lo, min(hi, x))


def safe_float(x: Any) -> float:
    try:
        v = float(x)
        if math.isnan(v) or math.isinf(v):
            return 0.0
        return v
    except Exception:
        return 0.0


def to_jsonable(o: Any) -> Any:
    """Recursively convert objects to JSON-serializable forms."""
    if isinstance(o, dict):
        return {k: to_jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [to_jsonable(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        v = float(o)
        if math.isnan(v) or math.isinf(v):
            return None
        return v
    if isinstance(o, np.ndarray):
        return [to_jsonable(v) for v in o.tolist()]
    if isinstance(o, (pd.DataFrame, pd.Series)):
        return f"<DataFrame shape={o.shape}>"
    if isinstance(o, (pd.Timestamp, datetime)):
        return o.isoformat()
    if isinstance(o, float):
        if math.isnan(o) or math.isinf(o):
            return None
        return o
    return o


def now_bj() -> datetime:
    return datetime.now(BJ)


def today_str() -> str:
    return now_bj().strftime("%Y-%m-%d")
