"""Alternative.me Crypto Fear & Greed."""
import httpx
from datetime import datetime
from typing import Optional, Dict, Any
from backend.core.logger import logger


def fetch_crypto_fng(limit: int = 60) -> Optional[Dict[str, Any]]:
    try:
        r = httpx.get(f"https://api.alternative.me/fng/?limit={limit}", timeout=15.0)
        if r.status_code == 200:
            js = r.json()
            if js.get("data"):
                cur = js["data"][0]
                hist = [{
                    "date": datetime.fromtimestamp(int(x["timestamp"])).strftime("%Y-%m-%d"),
                    "value": int(x["value"]),
                    "classification": x["value_classification"],
                } for x in js["data"]]
                return {
                    "current": int(cur["value"]),
                    "classification": cur["value_classification"],
                    "history": hist,
                }
    except Exception as e:
        logger.warning(f"crypto_fng failed: {e}")
    return None
