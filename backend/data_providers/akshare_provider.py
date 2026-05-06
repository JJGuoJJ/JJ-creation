"""akshare provider for A-share market with disk-cached helper."""
import time
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict
import pandas as pd
from backend.core.config import CACHE_DIR
from backend.core.logger import logger

_CACHE: Dict[str, pd.DataFrame] = {}
_RATE_SLEEP = 0.25
_DISK_CACHE_TTL_HOURS = 12


def _disk_path(code: str) -> Path:
    return CACHE_DIR / f"akshare_{code}.pkl"


def _load_disk_cache(code: str) -> Optional[pd.DataFrame]:
    p = _disk_path(code)
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


def _save_disk_cache(code: str, df: pd.DataFrame) -> None:
    try:
        with open(_disk_path(code), "wb") as f:
            pickle.dump(df, f)
    except Exception:
        pass


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {"日期": "date", "开盘": "open", "收盘": "close",
                  "最高": "high", "最低": "low", "成交量": "volume",
                  "成交额": "turnover", "涨跌幅": "pct_change"}
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    df.columns = [str(c).lower() for c in df.columns]
    return df


def fetch_index(code: str, days: int = 250) -> Optional[pd.DataFrame]:
    if code in _CACHE:
        return _CACHE[code]
    cached = _load_disk_cache(code)
    if cached is not None:
        _CACHE[code] = cached
        return cached
    try:
        import akshare as ak
        df = ak.stock_zh_index_daily(symbol=code)
        if df is None or len(df) < 30:
            return None
        df = _normalize(df).tail(days).copy()
        _CACHE[code] = df
        _save_disk_cache(code, df)
        time.sleep(_RATE_SLEEP)
        return df
    except Exception as e:
        logger.warning(f"akshare fetch_index({code}) failed: {e}")
        return None


def _fetch_eastmoney(pure: str) -> Optional[pd.DataFrame]:
    import akshare as ak
    start = (datetime.now() - timedelta(days=250)).strftime("%Y%m%d")
    end = datetime.now().strftime("%Y%m%d")
    df = ak.stock_zh_a_hist(symbol=pure, period="daily",
                            start_date=start, end_date=end, adjust="qfq")
    if df is not None and len(df) > 30:
        return _normalize(df).copy()
    return None


def _fetch_sina(pure: str) -> Optional[pd.DataFrame]:
    """Fallback: use sina via stock_zh_a_daily. Needs sh/sz prefix."""
    import akshare as ak
    # Determine exchange: 6xx -> sh, 0xx/3xx -> sz
    if pure.startswith("6"):
        sym = "sh" + pure
    elif pure.startswith(("0", "3")):
        sym = "sz" + pure
    elif pure.startswith("8"):
        sym = "bj" + pure  # 北交所
    else:
        return None
    start = (datetime.now() - timedelta(days=250)).strftime("%Y%m%d")
    end = datetime.now().strftime("%Y%m%d")
    df = ak.stock_zh_a_daily(symbol=sym, start_date=start, end_date=end, adjust="qfq")
    if df is None or len(df) < 30:
        return None
    df.columns = [str(c).lower() for c in df.columns]
    # ensure required columns
    if "close" not in df.columns:
        return None
    return df.copy()


def fetch_a_stock(code: str, days: int = 250, max_retries: int = 1) -> Optional[pd.DataFrame]:
    pure = code.split(".")[0]
    if pure in _CACHE:
        return _CACHE[pure]
    cached = _load_disk_cache(pure)
    if cached is not None:
        _CACHE[pure] = cached
        return cached
    # Try East Money first (preferred, has full columns and adj=qfq)
    last_exc = None
    for attempt in range(max_retries + 1):
        try:
            df = _fetch_eastmoney(pure)
            if df is not None:
                _CACHE[pure] = df
                _save_disk_cache(pure, df)
                time.sleep(_RATE_SLEEP)
                return df
        except Exception as e:
            last_exc = e
            time.sleep(0.5 * (attempt + 1))
    # Fallback to Sina
    try:
        df = _fetch_sina(pure)
        if df is not None:
            _CACHE[pure] = df
            _save_disk_cache(pure, df)
            time.sleep(_RATE_SLEEP)
            logger.info(f"  akshare {pure}: used sina fallback")
            return df
    except Exception as e:
        logger.debug(f"  akshare {pure} sina fallback failed: {e}")
    if last_exc:
        logger.debug(f"  akshare {pure} all sources failed: {last_exc}")
    _CACHE[pure] = None
    return None


def fetch_total_market_turnover_wanyi() -> Optional[float]:
    try:
        import akshare as ak
        df = ak.stock_zh_a_spot_em()
        if df is not None and "成交额" in df.columns:
            return float(df["成交额"].sum()) / 1e12
    except Exception as e:
        logger.debug(f"total turnover failed: {e}")
    return None


def clear_cache():
    """Clears in-memory cache only. Disk cache survives across runs."""
    _CACHE.clear()
