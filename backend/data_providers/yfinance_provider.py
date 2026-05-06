"""yfinance provider for global markets with disk caching."""
import pickle
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
import pandas as pd
from backend.core.config import CACHE_DIR
from backend.core.logger import logger

_CACHE: Dict[str, pd.DataFrame] = {}
_DISK_CACHE_TTL_HOURS = 6  # global markets update more frequently


def _disk_path(symbol: str) -> Path:
    safe = symbol.replace("^", "_").replace("=", "_").replace("/", "_")
    return CACHE_DIR / f"yf_{safe}.pkl"


def _load_disk_cache(symbol: str) -> Optional[pd.DataFrame]:
    p = _disk_path(symbol)
    if not p.exists():
        return None
    age = (datetime.now().timestamp() - p.stat().st_mtime) / 3600
    if age > _DISK_CACHE_TTL_HOURS:
        return None
    try:
        with open(p, "rb") as f:
            return pickle.load(f)
    except Exception:
        return None


def _save_disk_cache(symbol: str, df: pd.DataFrame) -> None:
    try:
        with open(_disk_path(symbol), "wb") as f:
            pickle.dump(df, f)
    except Exception:
        pass


def _normalize(hist: pd.DataFrame) -> pd.DataFrame:
    if isinstance(hist.columns, pd.MultiIndex):
        hist.columns = [c[0] for c in hist.columns]
    hist.columns = [str(c).lower() for c in hist.columns]
    return hist


def fetch_history(symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
    if symbol in _CACHE:
        return _CACHE[symbol]
    cached = _load_disk_cache(symbol)
    if cached is not None:
        _CACHE[symbol] = cached
        return cached
    try:
        import yfinance as yf
        hist = yf.download(symbol, period=period, interval="1d",
                           progress=False, auto_adjust=False, threads=False)
        if hist is not None and len(hist) > 30:
            hist = _normalize(hist).tail(260).copy()
            _CACHE[symbol] = hist
            _save_disk_cache(symbol, hist)
            return hist
    except Exception as e:
        logger.warning(f"yfinance {symbol} failed: {e}")
    return None


def fetch_batch(symbols: List[str]) -> Dict[str, pd.DataFrame]:
    out = {}
    for s in symbols:
        df = fetch_history(s)
        if df is not None:
            out[s] = df
    return out


def clear_cache():
    """Clears in-memory cache only. Disk cache survives across runs."""
    _CACHE.clear()
