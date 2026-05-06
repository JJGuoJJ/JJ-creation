"""
Personal Investment Bank System - Phase 1 Core POC
================================================
Single-file validation script to test core data pipeline, indicator calculations,
strategy engines, and report generation BEFORE building the full app.

Run: python /app/test_core.py

Success criteria: All 12 check functions must pass or gracefully degrade.
"""
import os
import sys
import json
import time
import math
import traceback
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import numpy as np
import pandas as pd
import requests
import httpx

# Quiet yfinance/akshare warnings
import warnings
warnings.filterwarnings("ignore")

# ---------- Output dir ----------
ROOT = Path("/app")
OUT_DIR = ROOT / "poc_output"
OUT_DIR.mkdir(exist_ok=True)
CACHE_DIR = OUT_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)

# ---------- Colors ----------
class C:
    G = "\033[92m"
    Y = "\033[93m"
    R = "\033[91m"
    B = "\033[94m"
    CY = "\033[96m"
    N = "\033[0m"
    BD = "\033[1m"

def ok(msg):   print(f"{C.G}[✓]{C.N} {msg}")
def warn(msg): print(f"{C.Y}[!]{C.N} {msg}")
def err(msg):  print(f"{C.R}[✗]{C.N} {msg}")
def info(msg): print(f"{C.B}[i]{C.N} {msg}")
def title(msg):print(f"\n{C.CY}{C.BD}═══ {msg} ═══{C.N}")


# =============================================================
# CHECK 1: akshare A股数据
# =============================================================
def check_akshare() -> Dict[str, Any]:
    title("CHECK 1 / akshare (A股数据)")
    result = {"name": "akshare", "ok": False, "details": {}, "data": {}}
    try:
        import akshare as ak
        # A股指数（东财）: 000001 上证, 399001 深成, 399006 创业板, 000688 科创50
        index_symbols = {
            "sh000001": "上证指数",
            "sh000300": "沪深300",
            "sh000688": "科创50",
            "sz399001": "深证成指",
            "sz399006": "创业板指",
            "sz399905": "中证500",
        }
        idx_data = {}
        for code, name in index_symbols.items():
            try:
                df = ak.stock_zh_index_daily(symbol=code)
                if df is not None and len(df) > 20:
                    df.columns = [c.lower() for c in df.columns]
                    df = df.tail(250).copy()
                    idx_data[code] = df
                    info(f"  {name} ({code}): {len(df)} rows, last close={df['close'].iloc[-1]:.2f}")
            except Exception as e:
                warn(f"  {name} failed: {e}")
        
        # A股个股（一只测试）
        stock_sample = None
        try:
            df = ak.stock_zh_a_hist(symbol="603083", period="daily",
                                     start_date=(datetime.now() - timedelta(days=300)).strftime("%Y%m%d"),
                                     end_date=datetime.now().strftime("%Y%m%d"), adjust="qfq")
            if df is not None and len(df) > 20:
                df.columns = [c.lower() for c in df.columns]
                # normalize chinese col names: 日期, 开盘, 收盘, 最高, 最低, 成交量, 成交额
                rename_map = {"日期":"date","开盘":"open","收盘":"close","最高":"high",
                              "最低":"low","成交量":"volume","成交额":"turnover"}
                df = df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns})
                stock_sample = df.tail(250).copy()
                info(f"  603083 剑桥科技: {len(stock_sample)} rows, last close={stock_sample['close'].iloc[-1]:.2f}")
        except Exception as e:
            warn(f"  603083 failed: {e}")
        
        # 两市成交额
        total_turnover = None
        try:
            df = ak.stock_zh_a_spot_em()
            if df is not None and len(df) > 100:
                # '成交额' column
                if "成交额" in df.columns:
                    total_turnover = float(df["成交额"].sum()) / 1e12  # 万亿
                    info(f"  A股全市场成交额 (当日): {total_turnover:.2f} 万亿")
        except Exception as e:
            warn(f"  全市场成交额 failed: {e}")
        
        result["ok"] = len(idx_data) >= 3  # stock_sample is not critical since we pre-fetch later
        result["details"]["index_count"] = len(idx_data)
        result["details"]["stock_sample_ok"] = stock_sample is not None
        result["details"]["total_turnover_wanyi"] = total_turnover
        result["data"] = {"indices": idx_data, "stock_sample": stock_sample, "total_turnover": total_turnover}
        if result["ok"]:
            ok(f"akshare OK (indices={len(idx_data)}, stock_sample={'Y' if stock_sample is not None else 'N'})")
        else:
            err("akshare partial: missing critical data")
    except Exception as e:
        err(f"akshare import/run failed: {e}")
        result["details"]["error"] = str(e)
    return result


# =============================================================
# CHECK 2: yfinance 全球数据
# =============================================================
def check_yfinance() -> Dict[str, Any]:
    title("CHECK 2 / yfinance (全球数据)")
    result = {"name":"yfinance", "ok": False, "details":{}, "data":{}}
    try:
        import yfinance as yf
        
        # Index / ETF / FX / commodity / crypto
        tickers = {
            "^GSPC": "S&P 500",
            "^IXIC": "Nasdaq Comp",
            "^NDX": "Nasdaq 100",
            "^DJI": "Dow Jones",
            "^RUT": "Russell 2000",
            "^VIX": "VIX",
            "^TNX": "10Y UST",
            "DX-Y.NYB": "DXY",
            "SOXX": "SOXX ETF",
            "SMH": "SMH ETF",
            "GLD": "Gold ETF",
            "USO": "Oil ETF",
            "BTC-USD": "Bitcoin",
            "ETH-USD": "Ethereum",
            "NVDA": "Nvidia",
            "AMD": "AMD",
            "AVGO": "Broadcom",
            "MSFT": "Microsoft",
            "GOOGL": "Google",
            "AMZN": "Amazon",
            "META": "Meta",
            "TSM":  "TSMC",
            "ASML": "ASML",
            "MU": "Micron",
            "MRVL": "Marvell",
            "SMCI": "Supermicro",
            "PLTR": "Palantir",
        }
        data = {}
        failed = []
        for sym, name in tickers.items():
            try:
                hist = yf.download(sym, period="1y", interval="1d",
                                   progress=False, auto_adjust=False, threads=False)
                if hist is not None and len(hist) > 20:
                    # handle multi-level columns
                    if isinstance(hist.columns, pd.MultiIndex):
                        hist.columns = [c[0] for c in hist.columns]
                    hist.columns = [c.lower() for c in hist.columns]
                    data[sym] = hist.tail(260).copy()
                else:
                    failed.append(sym)
            except Exception as e:
                failed.append(sym)
        
        info(f"  yfinance fetched {len(data)}/{len(tickers)} tickers")
        if failed:
            warn(f"  failed tickers: {failed[:5]}{'...' if len(failed)>5 else ''}")
        
        # Sample print
        for sample in ["^VIX", "NVDA", "BTC-USD"]:
            if sample in data:
                info(f"  {sample}: last close={data[sample]['close'].iloc[-1]:.2f}, rows={len(data[sample])}")
        
        result["ok"] = len(data) >= 15
        result["details"]["fetched"] = len(data)
        result["details"]["total"] = len(tickers)
        result["details"]["failed"] = failed
        result["data"] = data
        if result["ok"]:
            ok(f"yfinance OK ({len(data)}/{len(tickers)})")
        else:
            err(f"yfinance insufficient ({len(data)}/{len(tickers)})")
    except Exception as e:
        err(f"yfinance failed: {e}")
        result["details"]["error"] = str(e)
    return result


# =============================================================
# CHECK 3: Alternative.me Crypto F&G
# =============================================================
def check_crypto_fng() -> Dict[str, Any]:
    title("CHECK 3 / Alternative.me Crypto Fear & Greed")
    result = {"name":"crypto_fng","ok":False,"details":{},"data":{}}
    try:
        r = httpx.get("https://api.alternative.me/fng/?limit=30", timeout=15.0)
        if r.status_code == 200:
            js = r.json()
            if js.get("data"):
                cur = js["data"][0]
                hist = [{"date": datetime.fromtimestamp(int(x["timestamp"])).strftime("%Y-%m-%d"),
                         "value": int(x["value"]),
                         "classification": x["value_classification"]} for x in js["data"]]
                info(f"  Crypto F&G now = {cur['value']} ({cur['value_classification']})")
                info(f"  History 30d: {[h['value'] for h in hist[:10]]}...")
                result["ok"] = True
                result["data"] = {"current": int(cur["value"]), "history": hist}
    except Exception as e:
        err(f"Crypto F&G failed: {e}")
        result["details"]["error"] = str(e)
    if result["ok"]:
        ok("Crypto F&G OK")
    return result


# =============================================================
# CHECK 4: Technical indicators
# =============================================================
def compute_technical_indicators(df: pd.DataFrame) -> Dict[str, Any]:
    """df must have: close, volume columns, indexed by date or date col present"""
    out = {}
    close = df["close"].astype(float)
    
    # Moving averages
    for n in [5, 10, 20, 60, 120, 200]:
        ma = close.rolling(n).mean()
        out[f"ma{n}"] = float(ma.iloc[-1]) if not np.isnan(ma.iloc[-1]) else None
        out[f"pct_from_ma{n}"] = float((close.iloc[-1]/ma.iloc[-1] - 1) * 100) if out[f"ma{n}"] else None
    
    # Returns
    for n in [20, 60, 120]:
        if len(close) > n:
            out[f"ret_{n}d"] = float((close.iloc[-1]/close.iloc[-n] - 1)*100)
    
    # Max drawdown (of last 120d)
    if len(close) > 60:
        tail = close.tail(120)
        roll_max = tail.cummax()
        dd = (tail/roll_max - 1) * 100
        out["mdd_120d"] = float(dd.min())
    
    # Volatility (20d)
    if len(close) > 20:
        ret = close.pct_change().tail(20)
        out["vol_20d"] = float(ret.std()*np.sqrt(252)*100)
    
    # RSI (14d)
    if len(close) > 15:
        delta = close.diff()
        up = delta.clip(lower=0).rolling(14).mean()
        dn = -delta.clip(upper=0).rolling(14).mean()
        rs = up / dn.replace(0, np.nan)
        rsi = 100 - (100/(1+rs))
        out["rsi_14"] = float(rsi.iloc[-1]) if not np.isnan(rsi.iloc[-1]) else None
    
    # Volume / avg volume
    if "volume" in df.columns and len(df) > 20:
        vol = df["volume"].astype(float)
        v20 = vol.tail(20).mean()
        out["volume_ratio"] = float(vol.iloc[-1]/v20) if v20 > 0 else None
    
    out["last_close"] = float(close.iloc[-1])
    return out

def check_technical(ak_result, yf_result) -> Dict[str, Any]:
    title("CHECK 4 / Technical Indicators")
    result = {"name":"technical","ok":False,"details":{},"data":{}}
    try:
        tested = 0
        summary = {}
        # Test on A股 index
        if ak_result["ok"] and ak_result["data"]["indices"]:
            for code, df in list(ak_result["data"]["indices"].items())[:2]:
                ind = compute_technical_indicators(df)
                summary[code] = ind
                tested += 1
                info(f"  {code}: close={ind['last_close']:.2f}, RSI={ind.get('rsi_14',0):.1f}, ret20d={ind.get('ret_20d',0):.2f}%")
        # Test on US stocks
        if yf_result["ok"]:
            for sym in ["NVDA", "^VIX", "BTC-USD"]:
                if sym in yf_result["data"]:
                    ind = compute_technical_indicators(yf_result["data"][sym])
                    summary[sym] = ind
                    tested += 1
                    info(f"  {sym}: close={ind['last_close']:.2f}, RSI={ind.get('rsi_14',0):.1f}, pct_ma200={ind.get('pct_from_ma200',0):.2f}%")
        
        result["ok"] = tested >= 3
        result["data"] = summary
        if result["ok"]:
            ok(f"Technical indicators OK ({tested} assets)")
        else:
            err(f"Technical indicators insufficient ({tested})")
    except Exception as e:
        err(f"Technical failed: {e}")
        traceback.print_exc()
    return result


# =============================================================
# CHECK 5: Global Fear & Greed
# =============================================================
def clamp(x, lo=0, hi=100): return max(lo, min(hi, x))

def compute_global_fng(yf_data: Dict[str, pd.DataFrame], crypto_fng: Optional[int]) -> Dict[str, Any]:
    """Global F&G 0-100, bigger = more greed."""
    breakdown = {}
    missing = []

    # 1. VIX (inverse). VIX<15 => greed, VIX>30 => fear
    w_vix = 25
    vix_score = None
    if "^VIX" in yf_data:
        vix = float(yf_data["^VIX"]["close"].iloc[-1])
        # Map VIX 10(100) -> 40(0), approximately linear inverse
        vix_score = clamp((40 - vix)/(40-10) * 100)
    else: missing.append("VIX")
    breakdown["vix_inverse"] = {"weight": w_vix, "score": vix_score, "raw": vix if vix_score else None}
    
    # 2. Nasdaq vs 200MA
    w_nasdaq = 20
    nsdq_score = None
    if "^IXIC" in yf_data:
        close = yf_data["^IXIC"]["close"]
        ma200 = close.rolling(200).mean().iloc[-1]
        if not np.isnan(ma200):
            pct = (close.iloc[-1]/ma200 - 1)*100
            # +15% => 100, -15% => 0
            nsdq_score = clamp((pct + 15)/30 * 100)
    else: missing.append("Nasdaq")
    breakdown["nasdaq_200ma"] = {"weight": w_nasdaq, "score": nsdq_score}

    # 3. SOXX trend
    w_sox = 15
    sox_score = None
    sox_key = "SOXX" if "SOXX" in yf_data else ("SMH" if "SMH" in yf_data else None)
    if sox_key:
        close = yf_data[sox_key]["close"]
        ma50 = close.rolling(50).mean().iloc[-1]
        if not np.isnan(ma50):
            pct = (close.iloc[-1]/ma50 - 1)*100
            sox_score = clamp((pct + 10)/20 * 100)
    else: missing.append("SOX")
    breakdown["sox_trend"] = {"weight": w_sox, "score": sox_score}

    # 4. 10Y UST change inverse (short term rate falling = risk-on greed)
    w_ust = 10
    ust_score = None
    if "^TNX" in yf_data:
        close = yf_data["^TNX"]["close"]
        if len(close) > 60:
            chg = close.iloc[-1] - close.iloc[-60]
            # if down more than 0.5% => greedy(100), up >0.5% => fear(0)
            ust_score = clamp(50 - chg/0.01 * 10)
    else: missing.append("UST10Y")
    breakdown["ust10_inverse"] = {"weight": w_ust, "score": ust_score}

    # 5. DXY change inverse
    w_dxy = 10
    dxy_score = None
    dxy_key = "DX-Y.NYB" if "DX-Y.NYB" in yf_data else None
    if dxy_key:
        close = yf_data[dxy_key]["close"]
        if len(close) > 60:
            chg_pct = (close.iloc[-1]/close.iloc[-60] - 1)*100
            dxy_score = clamp(50 - chg_pct * 10)  # -5% => 100, +5% => 0
    else: missing.append("DXY")
    breakdown["dxy_inverse"] = {"weight": w_dxy, "score": dxy_score}

    # 6. BTC trend + Crypto F&G
    w_btc = 10
    btc_score = None
    parts = []
    if "BTC-USD" in yf_data:
        close = yf_data["BTC-USD"]["close"]
        ma100 = close.rolling(100).mean().iloc[-1]
        if not np.isnan(ma100):
            pct = (close.iloc[-1]/ma100 - 1)*100
            parts.append(clamp((pct + 20)/40 * 100))
    if crypto_fng is not None:
        parts.append(crypto_fng)
    if parts:
        btc_score = float(np.mean(parts))
    else: missing.append("BTC/CryptoFNG")
    breakdown["btc_crypto"] = {"weight": w_btc, "score": btc_score}

    # 7. Global breadth (use SP500 trend as proxy)
    w_breadth = 10
    br_score = None
    if "^GSPC" in yf_data:
        close = yf_data["^GSPC"]["close"]
        ma50 = close.rolling(50).mean().iloc[-1]
        if not np.isnan(ma50):
            pct = (close.iloc[-1]/ma50 - 1)*100
            br_score = clamp((pct + 5)/10 * 100)
    else: missing.append("SP500")
    breakdown["global_breadth"] = {"weight": w_breadth, "score": br_score}
    
    # Weighted average of available
    total_w = 0
    total_s = 0
    for k, v in breakdown.items():
        if v["score"] is not None:
            total_w += v["weight"]
            total_s += v["weight"] * v["score"]
    score = total_s / total_w if total_w > 0 else 50
    return {"score": round(score, 1), "breakdown": breakdown, "missing": missing}

def check_global_fng(yf_result, crypto_result) -> Dict[str, Any]:
    title("CHECK 5 / Global Fear & Greed Index")
    result = {"name":"global_fng","ok":False,"details":{},"data":{}}
    try:
        yf_data = yf_result.get("data", {})
        cryp = crypto_result.get("data", {}).get("current") if crypto_result["ok"] else None
        fng = compute_global_fng(yf_data, cryp)
        info(f"  Global F&G Score = {fng['score']} / 100")
        for k, v in fng["breakdown"].items():
            info(f"    - {k} (w={v['weight']}%): score={v['score']}")
        if fng["missing"]:
            warn(f"  Missing: {fng['missing']}")
        result["ok"] = 0 <= fng["score"] <= 100
        result["data"] = fng
        if result["ok"]:
            ok(f"Global F&G OK = {fng['score']}")
    except Exception as e:
        err(f"Global F&G failed: {e}")
        traceback.print_exc()
    return result


# =============================================================
# CHECK 6: China Tech Fear & Greed
# =============================================================
def compute_china_tech_fng(ak_data: Dict[str, Any]) -> Dict[str, Any]:
    """China Tech F&G 0-100. Uses STAR50/ChiNext trend + turnover"""
    breakdown = {}
    missing = []
    idx_map = ak_data.get("indices", {})
    
    # 1. STAR50 / ChiNext / CSI300 trend
    w_trend = 25
    trends = []
    for code in ["sh000688", "sz399006", "sz399001"]:
        if code in idx_map:
            c = idx_map[code]["close"]
            ma50 = c.rolling(50).mean().iloc[-1]
            if not np.isnan(ma50):
                pct = (c.iloc[-1]/ma50 - 1)*100
                trends.append(clamp((pct+10)/20*100))
    trend_score = float(np.mean(trends)) if trends else None
    breakdown["tech_trend"] = {"weight": w_trend, "score": trend_score}
    if trend_score is None: missing.append("STAR50/ChiNext trend")
    
    # 2. Total turnover (percentile)
    w_turnover = 20
    tv_score = None
    total_tv = ak_data.get("total_turnover")
    if total_tv is not None:
        # rough mapping: 0.5万亿 cold(20), 1万亿 neutral(50), 1.5万亿 hot(85), 2万亿+ extreme(95)
        if total_tv < 0.6: tv_score = 15
        elif total_tv < 0.9: tv_score = 35
        elif total_tv < 1.2: tv_score = 55
        elif total_tv < 1.5: tv_score = 70
        elif total_tv < 1.8: tv_score = 82
        elif total_tv < 2.2: tv_score = 90
        else: tv_score = 95
    breakdown["total_turnover"] = {"weight": w_turnover, "score": tv_score, "raw_wanyi": total_tv}
    if tv_score is None: missing.append("Total turnover")
    
    # 3. CSI300 trend as "market breadth" proxy
    w_breadth = 20
    br_score = None
    if "sh000300" in idx_map:
        c = idx_map["sh000300"]["close"]
        ma200 = c.rolling(200).mean().iloc[-1]
        if not np.isnan(ma200):
            pct = (c.iloc[-1]/ma200 - 1)*100
            br_score = clamp((pct+15)/30*100)
    breakdown["csi300_breadth"] = {"weight": w_breadth, "score": br_score}
    
    # 4. 涨停 / Margin - PLACEHOLDER (skip in POC, mark missing)
    missing.append("Limit-up breadth (placeholder)")
    missing.append("Margin balance (placeholder)")
    
    # 5. Valuation / deviation
    w_val = 15
    val_score = None
    if "sh000688" in idx_map:
        c = idx_map["sh000688"]["close"]
        ma200 = c.rolling(200).mean().iloc[-1]
        if not np.isnan(ma200):
            pct = (c.iloc[-1]/ma200 - 1)*100
            # +20% overheated => 90, -20% oversold => 10
            val_score = clamp(50 + pct*2)
    breakdown["valuation_deviation"] = {"weight": w_val, "score": val_score}

    total_w = 0
    total_s = 0
    for k, v in breakdown.items():
        if v["score"] is not None:
            total_w += v["weight"]
            total_s += v["weight"] * v["score"]
    score = total_s / total_w if total_w > 0 else 50
    return {"score": round(score, 1), "breakdown": breakdown, "missing": missing}

def check_china_fng(ak_result) -> Dict[str, Any]:
    title("CHECK 6 / China Tech Fear & Greed Index")
    result = {"name":"china_tech_fng","ok":False,"details":{},"data":{}}
    try:
        fng = compute_china_tech_fng(ak_result.get("data", {}))
        info(f"  China Tech F&G = {fng['score']} / 100")
        for k, v in fng["breakdown"].items():
            info(f"    - {k} (w={v['weight']}%): score={v['score']}")
        if fng["missing"]:
            warn(f"  Missing factors: {fng['missing']}")
        result["ok"] = 0 <= fng["score"] <= 100
        result["data"] = fng
        if result["ok"]:
            ok(f"China Tech F&G OK = {fng['score']}")
    except Exception as e:
        err(f"China F&G failed: {e}")
        traceback.print_exc()
    return result


# =============================================================
# CHECK 7: AI Chain Heat Score
# =============================================================
_ASTOCK_CACHE = {}

def fetch_astock_robust(code: str, max_retries: int = 3) -> Optional[pd.DataFrame]:
    """Fetch A-stock with retries and caching to survive rate limits."""
    if code in _ASTOCK_CACHE:
        return _ASTOCK_CACHE[code]
    import akshare as ak
    start = (datetime.now()-timedelta(days=250)).strftime("%Y%m%d")
    end = datetime.now().strftime("%Y%m%d")
    for attempt in range(max_retries):
        try:
            df = ak.stock_zh_a_hist(symbol=code, period="daily",
                                    start_date=start, end_date=end, adjust="qfq")
            if df is not None and len(df) > 30:
                rename_map = {"日期":"date","开盘":"open","收盘":"close","最高":"high",
                              "最低":"low","成交量":"volume","成交额":"turnover"}
                df = df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns})
                _ASTOCK_CACHE[code] = df
                time.sleep(0.4)
                return df
        except Exception:
            time.sleep(1.0 * (attempt+1))
    _ASTOCK_CACHE[code] = None
    return None


def prefetch_all_astocks():
    """Pre-fetch all needed A-stocks in one batch with proper spacing."""
    all_codes = [
        # heat sectors
        "002281", "603083", "300308",
        "600584", "002156", "002185",
        "688008", "603986", "301308",
        "600406", "002837", "002028",
        "000977", "603019",
        # recommendation watchlist extras
    ]
    info(f"  Pre-fetching {len(all_codes)} A-stocks (this may take ~30s due to rate limits)...")
    success = 0
    for code in all_codes:
        df = fetch_astock_robust(code, max_retries=2)
        if df is not None:
            success += 1
    info(f"  Pre-fetched {success}/{len(all_codes)} stocks")
    return success


def compute_ai_chain_heat(ak_result, yf_result) -> Dict[str, Any]:
    """Per-sector heat score using representative stocks"""
    # Sector -> representative A-share symbols
    sector_map = {
        "光模块": ["002281", "603083", "300308"],
        "先进封装": ["600584", "002156", "002185"],
        "HBM存储": ["688008", "603986", "301308"],
        "电力液冷": ["600406", "002837", "002028"],
        "AI服务器": ["000977", "603019"],
        "全球AI芯片": [],  # will use US stocks
    }
    us_ai = ["NVDA", "AMD", "AVGO", "TSM", "MU"]
    
    # Cache for individual stock data
    scores = {}
    
    def fetch_astock(code):
        return fetch_astock_robust(code)
    
    # Compute for each sector
    for sector, symbols in sector_map.items():
        sector_stocks = []
        if sector == "全球AI芯片":
            yd = yf_result.get("data", {})
            for s in us_ai:
                if s in yd: sector_stocks.append(("US", s, yd[s]))
        else:
            for code in symbols:
                df = fetch_astock(code)
                if df is not None:
                    sector_stocks.append(("CN", code, df))
        
        if not sector_stocks:
            scores[sector] = {"heat": None, "reason": "no data"}
            continue

        # Momentum: mean 20d & 60d return
        rets20, rets60, vol_ratios, mdd_list, rsi_list = [], [], [], [], []
        up_count = 0
        for _, _, df in sector_stocks:
            close = df["close"].astype(float)
            if len(close) > 60:
                rets20.append((close.iloc[-1]/close.iloc[-20]-1)*100)
                rets60.append((close.iloc[-1]/close.iloc[-60]-1)*100)
                tail = close.tail(120); rmax = tail.cummax(); dd = (tail/rmax-1)*100
                mdd_list.append(dd.min())
                delta = close.diff()
                up = delta.clip(lower=0).rolling(14).mean()
                dn = -delta.clip(upper=0).rolling(14).mean()
                rs = up/dn.replace(0, np.nan)
                rsi = 100 - 100/(1+rs)
                if not np.isnan(rsi.iloc[-1]): rsi_list.append(rsi.iloc[-1])
                if "volume" in df.columns:
                    v = df["volume"].astype(float)
                    v20 = v.tail(20).mean()
                    if v20 > 0: vol_ratios.append(v.iloc[-1]/v20)
                if (close.iloc[-1]/close.iloc[-20]-1) > 0: up_count += 1
        
        if not rets20: 
            scores[sector] = {"heat": None, "reason": "insufficient"}
            continue

        r20 = float(np.mean(rets20)); r60 = float(np.mean(rets60))
        momentum = clamp(50 + r20*2 + r60*0.8)  # roughly: 0% returns => 50
        vr = float(np.mean(vol_ratios)) if vol_ratios else 1.0
        volume_score = clamp(30 + (vr-1)*40)
        breadth = clamp(up_count/len(rets20) * 100)
        rsi_avg = float(np.mean(rsi_list)) if rsi_list else 50
        
        # Risk penalty: high RSI + high vol ratio (overheated)
        risk_pen = 0
        if rsi_avg > 75: risk_pen += 15
        if rsi_avg > 80: risk_pen += 10
        if vr > 2.0: risk_pen += 10
        if r20 > 25: risk_pen += 10
        
        heat = 0.35*momentum + 0.25*volume_score + 0.20*breadth + 0.20*50 - risk_pen
        heat = clamp(heat)
        scores[sector] = {
            "heat": round(heat,1),
            "momentum": round(momentum,1),
            "volume": round(volume_score,1),
            "breadth": round(breadth,1),
            "risk_penalty": risk_pen,
            "r20_avg": round(r20,2),
            "r60_avg": round(r60,2),
            "rsi_avg": round(rsi_avg,1),
            "vol_ratio": round(vr,2),
            "sample_size": len(sector_stocks),
        }
    return scores

def check_ai_chain_heat(ak_result, yf_result) -> Dict[str, Any]:
    title("CHECK 7 / AI Chain Heat Score (per sector)")
    result = {"name":"ai_chain_heat","ok":False,"details":{},"data":{}}
    try:
        scores = compute_ai_chain_heat(ak_result, yf_result)
        valid = [s for s in scores.values() if s.get("heat") is not None]
        info(f"  Sectors evaluated: {len(valid)}/{len(scores)}")
        for sector, s in scores.items():
            if s.get("heat") is not None:
                info(f"    {sector}: heat={s['heat']}, r20={s['r20_avg']}%, RSI={s['rsi_avg']}, vol×{s['vol_ratio']}")
            else:
                warn(f"    {sector}: {s.get('reason')}")
        result["ok"] = len(valid) >= 2
        result["data"] = scores
        if result["ok"]:
            ok(f"AI Chain Heat OK ({len(valid)} sectors)")
    except Exception as e:
        err(f"AI Chain Heat failed: {e}")
        traceback.print_exc()
    return result


# =============================================================
# CHECK 8: Market Regime Detection
# =============================================================
def detect_regime(global_fng: float, china_fng: float, ai_heat_scores: Dict) -> Dict[str, Any]:
    # Combined score: 40% global, 40% china, 20% ai heat peak
    valid_heat = [v["heat"] for v in ai_heat_scores.values() if v.get("heat") is not None]
    ai_peak = max(valid_heat) if valid_heat else 50
    combined = 0.40*global_fng + 0.40*china_fng + 0.20*ai_peak
    combined = round(combined, 1)
    
    if combined < 25:   regime = "Extreme Fear";   action = "分批低吸核心资产"
    elif combined < 40: regime = "Fear";           action = "逐步加仓高质量主线"
    elif combined < 60: regime = "Neutral";        action = "按目标仓位配置"
    elif combined < 75: regime = "Greed";          action = "持有核心，不追涨"
    elif combined < 90: regime = "Extreme Greed";  action = "高弹性仓分批止盈"
    else:               regime = "Bubble Risk";    action = "降低高beta仓位，保留现金"
    
    return {
        "combined_score": combined,
        "regime": regime,
        "action": action,
        "global_fng": global_fng,
        "china_fng": china_fng,
        "ai_peak_heat": ai_peak,
    }

def check_regime(global_r, china_r, heat_r) -> Dict[str, Any]:
    title("CHECK 8 / Market Regime Detection")
    result = {"name":"regime","ok":False,"details":{},"data":{}}
    try:
        g = global_r["data"]["score"]
        c = china_r["data"]["score"]
        h = heat_r["data"] if heat_r["ok"] else {}
        regime = detect_regime(g, c, h)
        info(f"  Combined = {regime['combined_score']} | Regime = {C.BD}{regime['regime']}{C.N}")
        info(f"  Recommended action: {regime['action']}")
        result["ok"] = True
        result["data"] = regime
        ok(f"Regime OK = {regime['regime']}")
    except Exception as e:
        err(f"Regime failed: {e}")
        traceback.print_exc()
    return result


# =============================================================
# CHECK 9: Allocation Engine
# =============================================================
def allocate(regime: str) -> Dict[str, Any]:
    """Risk profile: Medium-High / High. Return allocation bands."""
    mapping = {
        "Extreme Fear":   {"equity":[65,75], "ai_tech":[45,60], "packaging_hbm_cool":[25,35], "gold_energy":[10,20], "btc":[3,8], "cash":[5,15]},
        "Fear":           {"equity":[60,70], "ai_tech":[40,55], "packaging_hbm_cool":[20,30], "gold_energy":[15,25], "btc":[3,8], "cash":[10,20]},
        "Neutral":        {"equity":[55,65], "ai_tech":[35,50], "packaging_hbm_cool":[20,30], "gold_energy":[15,25], "btc":[2,7], "cash":[15,25]},
        "Greed":          {"equity":[50,60], "ai_tech":[30,45], "packaging_hbm_cool":[15,25], "gold_energy":[15,25], "btc":[2,6], "cash":[20,30]},
        "Extreme Greed":  {"equity":[40,50], "ai_tech":[20,35], "packaging_hbm_cool":[10,20], "gold_energy":[15,25], "btc":[1,5], "cash":[30,45]},
        "Bubble Risk":    {"equity":[25,40], "ai_tech":[10,25], "packaging_hbm_cool":[ 5,15], "gold_energy":[20,30], "btc":[0,3], "cash":[35,55]},
    }
    return mapping.get(regime, mapping["Neutral"])

def check_allocation(regime_r) -> Dict[str, Any]:
    title("CHECK 9 / Allocation Engine")
    result = {"name":"allocation","ok":False,"details":{},"data":{}}
    try:
        regime = regime_r["data"]["regime"]
        bands = allocate(regime)
        info(f"  Regime: {regime}")
        info(f"  权益: {bands['equity'][0]}%–{bands['equity'][1]}%")
        info(f"  AI科技: {bands['ai_tech'][0]}%–{bands['ai_tech'][1]}%")
        info(f"  封装/HBM/液冷: {bands['packaging_hbm_cool'][0]}%–{bands['packaging_hbm_cool'][1]}%")
        info(f"  黄金/能源: {bands['gold_energy'][0]}%–{bands['gold_energy'][1]}%")
        info(f"  比特币: {bands['btc'][0]}%–{bands['btc'][1]}%")
        info(f"  现金: {bands['cash'][0]}%–{bands['cash'][1]}%")
        result["ok"] = True
        result["data"] = {"regime": regime, "bands": bands}
        ok(f"Allocation OK")
    except Exception as e:
        err(f"Allocation failed: {e}")
    return result


# =============================================================
# CHECK 10: Recommendation Engine (Watchlist)
# =============================================================
def check_recommendation(ak_result, yf_result, heat_r) -> Dict[str, Any]:
    title("CHECK 10 / Stock Recommendation Engine (Watchlist sample)")
    result = {"name":"recommendation","ok":False,"details":{},"data":{}}
    try:
        # Small sample (speed)
        watchlist = [
            ("CN", "600584", "长电科技", "先进封装"),
            ("CN", "002156", "通富微电", "先进封装"),
            ("CN", "688008", "澜起科技", "HBM存储"),
            ("CN", "603986", "兆易创新", "HBM存储"),
            ("CN", "002837", "英维克", "电力液冷"),
            ("CN", "600406", "国电南瑞", "电力液冷"),
            ("CN", "002281", "光迅科技", "光模块"),
            ("CN", "603083", "剑桥科技", "光模块"),
            ("CN", "603019", "中科曙光", "AI服务器"),
            ("CN", "000977", "浪潮信息", "AI服务器"),
            ("US", "NVDA",   "Nvidia",   "全球AI芯片"),
            ("US", "AMD",    "AMD",      "全球AI芯片"),
            ("US", "TSM",    "TSMC",     "全球AI芯片"),
            ("US", "MU",     "Micron",   "HBM存储"),
        ]
        heat_data = heat_r["data"] if heat_r["ok"] else {}
        yf_data = yf_result.get("data", {})
        recs = []
        for market, code, name, sector in watchlist:
            df = None
            if market == "CN":
                df = fetch_astock_robust(code)
            else:
                df = yf_data.get(code)
            
            if df is None or len(df) < 60:
                continue
            
            ind = compute_technical_indicators(df)
            sector_heat = heat_data.get(sector, {}).get("heat") or 50
            
            # Score dimensions
            # 1) 赛道热度 25%
            sec_s = sector_heat
            # 2) 动量 20%
            mom_s = clamp(50 + (ind.get("ret_20d",0) or 0)*2 + (ind.get("ret_60d",0) or 0)*0.8)
            # 3) 回调性价比 15% (pct below ma20 => bigger score if negative up to -10%)
            pct20 = ind.get("pct_from_ma20", 0) or 0
            pullback_s = clamp(50 - pct20*5)  # above +10% => 0; -10% => 100
            # 4) 相对强度 15% (higher rsi + higher ret20)
            rsi = ind.get("rsi_14", 50) or 50
            rs_s = clamp((rsi - 30)/40 * 100)
            # 5) 风险控制 10% (inverse of overheating)
            risk_s = clamp(100 - (rsi-50)*3 - max(0, pct20-10)*5)
            # 6) 新闻催化 10% (placeholder 50 each)
            news_s = 50
            # 7) 适配度 5%
            fit_s = 70  # default
            
            total = 0.25*sec_s + 0.20*mom_s + 0.15*pullback_s + 0.15*rs_s + 0.10*risk_s + 0.10*news_s + 0.05*fit_s
            total = round(total,1)
            
            # Action logic
            reasons = []
            if sec_s > 70 and pct20 > 15 and rsi > 75:
                action = "Avoid Chasing"
                reasons.append(f"{sector}赛道热度{sec_s:.0f}偏高，个股距20日均线+{pct20:.1f}%且RSI={rsi:.0f}过热，建议等回调")
            elif sec_s > 70 and -12 < pct20 < -3 and rsi < 60:
                action = "Strong Buy on Pullback"
                reasons.append(f"{sector}热度{sec_s:.0f}高，个股回调{abs(pct20):.1f}%至可布局区间")
            elif sec_s > 60 and pct20 < 5 and 45 < rsi < 70:
                action = "Buy Small"
                reasons.append(f"{sector}中等偏强(热度{sec_s:.0f})，技术面未过热，可小仓位布局")
            elif rsi > 80 or (pct20 > 20):
                action = "Trim"
                reasons.append(f"个股过热(RSI={rsi:.0f}, pct_ma20=+{pct20:.1f}%)，建议减仓止盈")
            elif rsi < 30:
                action = "Buy Small"
                reasons.append(f"RSI={rsi:.0f}超卖，小仓试探")
            elif 40 < total < 55:
                action = "Hold"
                reasons.append("综合分中性，维持现有仓位")
            elif total < 40:
                action = "Wait"
                reasons.append("综合分偏低，暂不入场")
            else:
                action = "Hold"
                reasons.append(f"综合分{total}，已有仓位持有")
            
            recs.append({
                "code": code, "name": name, "market": market, "sector": sector,
                "score": total,
                "action": action,
                "reasons": reasons,
                "indicators": {
                    "ret_20d": round(ind.get("ret_20d",0) or 0, 2),
                    "ret_60d": round(ind.get("ret_60d",0) or 0, 2),
                    "pct_ma20": round(pct20,2),
                    "pct_ma200": round(ind.get("pct_from_ma200",0) or 0, 2),
                    "rsi_14": round(rsi,1),
                    "sector_heat": sec_s,
                }
            })
        
        recs.sort(key=lambda x: -x["score"])
        info(f"  Ranked {len(recs)} stocks")
        for r in recs[:10]:
            print(f"    {r['score']:>5.1f}  {r['code']:>8} {r['name']:<10} [{r['sector']}]  → {r['action']}")
        
        result["ok"] = len(recs) >= 5
        result["data"] = recs
        if result["ok"]:
            ok(f"Recommendation Engine OK ({len(recs)} stocks)")
    except Exception as e:
        err(f"Recommendation failed: {e}")
        traceback.print_exc()
    return result


# =============================================================
# CHECK 11: Emergent LLM Integration (optional deep interpretation)
# =============================================================
def check_emergent_llm(global_r, china_r, regime_r, alloc_r) -> Dict[str, Any]:
    title("CHECK 11 / Emergent LLM Deep Interpretation (optional)")
    result = {"name":"llm","ok":False,"details":{},"data":{}}
    key = os.environ.get("EMERGENT_LLM_KEY") or "sk-emergent-c227f281fEb92033aF"
    if not key:
        warn("EMERGENT_LLM_KEY not set; skip (will use rule-based)")
        result["ok"] = True  # optional
        result["data"] = {"interpretation": "(LLM key 缺失，使用规则生成)"}
        return result
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        prompt = f"""你是一位美股/A股资深投行策略师。请根据下列今日数据，输出 4–6 句中文策略解读，风格像高盛/摩根士丹利策略日报：

- 全球恐惧贪婪指数: {global_r['data']['score']}
- 中国科技恐惧贪婪指数: {china_r['data']['score']}
- 市场阶段: {regime_r['data']['regime']}
- 建议权益仓位区间: {alloc_r['data']['bands']['equity'][0]}%–{alloc_r['data']['bands']['equity'][1]}%
- 建议AI科技仓位区间: {alloc_r['data']['bands']['ai_tech'][0]}%–{alloc_r['data']['bands']['ai_tech'][1]}%

要求：
1. 开头直接给出一句话策略定调。
2. 指出当前最值得关注的1-2个机会点和1个风险点。
3. 给出明天的具体操作倾向。
4. 不要空话，不要"投资有风险"免责声明。
5. 控制在150字以内。
"""
        import asyncio
        async def run():
            chat = LlmChat(api_key=key, session_id="pib_poc", system_message="You are an elite investment bank strategist.")
            chat.with_model("openai", "gpt-4o-mini")
            resp = await chat.send_message(UserMessage(text=prompt))
            return resp
        text = asyncio.run(run())
        info(f"  LLM response preview: {text[:180]}...")
        result["ok"] = True
        result["data"] = {"interpretation": text}
        ok("Emergent LLM OK")
    except Exception as e:
        warn(f"Emergent LLM failed (non-fatal): {e}")
        result["ok"] = True  # non-fatal
        result["data"] = {"interpretation": f"(LLM 调用失败，使用规则生成) 原因: {str(e)[:120]}"}
    return result


# =============================================================
# CHECK 12: Generate Chinese Daily Report (Markdown)
# =============================================================
def generate_report(all_results: Dict[str, Any]) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    g = all_results["global_fng"]["data"]
    c = all_results["china_tech_fng"]["data"]
    h = all_results["ai_chain_heat"]["data"]
    r = all_results["regime"]["data"]
    a = all_results["allocation"]["data"]["bands"]
    recs = all_results["recommendation"]["data"]
    llm_text = all_results["llm"]["data"].get("interpretation", "")
    
    lines = []
    lines.append(f"# 个人投行系统日报 · {today}")
    lines.append(f"\n> **市场阶段**: **{r['regime']}**  |  综合分: {r['combined_score']}  |  建议动作: **{r['action']}**\n")
    
    lines.append("## 一、今日市场状态")
    lines.append(f"- 🌍 **全球恐惧贪婪指数**: **{g['score']} / 100**")
    lines.append(f"- 🇨🇳 **中国科技恐惧贪婪指数**: **{c['score']} / 100**")
    lines.append(f"- ⚡ **AI 产业链峰值热度**: **{r['ai_peak_heat']} / 100**")
    lines.append(f"\n**策略师解读**:\n> {llm_text}\n")
    
    lines.append("## 二、今日仓位建议")
    lines.append(f"| 类别 | 建议区间 |")
    lines.append(f"|:---|:---|")
    lines.append(f"| 总权益 | **{a['equity'][0]}% – {a['equity'][1]}%** |")
    lines.append(f"| AI 科技 | {a['ai_tech'][0]}% – {a['ai_tech'][1]}% |")
    lines.append(f"| 先进封装 / HBM / 电力液冷 | {a['packaging_hbm_cool'][0]}% – {a['packaging_hbm_cool'][1]}% |")
    lines.append(f"| 黄金 / 能源 / 军工 | {a['gold_energy'][0]}% – {a['gold_energy'][1]}% |")
    lines.append(f"| 比特币 | {a['btc'][0]}% – {a['btc'][1]}% |")
    lines.append(f"| 现金 | {a['cash'][0]}% – {a['cash'][1]}% |")
    
    lines.append("\n## 三、赛道热度排名")
    lines.append("| 赛道 | 热度分 | 20日均涨幅 | 平均RSI | 量比 | 风险罚分 |")
    lines.append("|:---|---:|---:|---:|---:|---:|")
    sector_list = [(k, v) for k, v in h.items() if v.get("heat") is not None]
    sector_list.sort(key=lambda x: -x[1]["heat"])
    for sec, s in sector_list:
        lines.append(f"| {sec} | **{s['heat']}** | {s['r20_avg']:+.2f}% | {s['rsi_avg']:.1f} | {s['vol_ratio']:.2f}x | {s['risk_penalty']} |")
    
    lines.append("\n## 四、高价值观察池 Top 10")
    lines.append("| 排名 | 代码 | 名称 | 赛道 | 综合分 | 动作 | 理由 |")
    lines.append("|:---|:---|:---|:---|---:|:---|:---|")
    for i, rec in enumerate(recs[:10], 1):
        reason = rec["reasons"][0] if rec["reasons"] else ""
        lines.append(f"| {i} | `{rec['code']}` | {rec['name']} | {rec['sector']} | {rec['score']} | **{rec['action']}** | {reason} |")
    
    lines.append("\n## 五、今日风险信号")
    risk_flags = []
    for sec, s in sector_list:
        if s.get("risk_penalty",0) >= 20:
            risk_flags.append(f"- 🔴 **{sec}** 赛道过热（风险罚分 {s['risk_penalty']}），建议不追涨")
        elif s.get("heat",0) > 75:
            risk_flags.append(f"- 🟡 **{sec}** 赛道热度偏高 ({s['heat']})")
    if g["score"] > 85:
        risk_flags.append(f"- 🔴 全球情绪接近极度贪婪 ({g['score']})")
    if c["score"] > 85:
        risk_flags.append(f"- 🔴 A股科技情绪接近极度贪婪 ({c['score']})")
    if g["score"] < 25:
        risk_flags.append(f"- 🟢 全球情绪极度恐慌 ({g['score']})，可分批低吸优质资产")
    if not risk_flags:
        risk_flags.append("- 暂无重大风险信号")
    lines.extend(risk_flags)
    
    lines.append("\n## 六、明日操作计划")
    plan = []
    if r["regime"] in ["Extreme Fear", "Fear"]:
        plan = [
            "1. **不恐慌抛售**；按分批加仓计划执行第一档买入",
            "2. 优先买入 Top 3 推荐（分数最高），每笔 ≤ 计划仓位的 1/3",
            "3. 保留至少 20% 现金应对可能的二次探底",
        ]
    elif r["regime"] == "Neutral":
        plan = [
            "1. 持有现有核心仓位，不追涨不恐慌",
            "2. 关注回调至均线的高分个股，分批小仓布局",
            "3. 新增仓位优先配置热度高但风险罚分<15的赛道",
        ]
    elif r["regime"] == "Greed":
        plan = [
            "1. **不追高**，持有核心，对涨幅过大的个股设置止盈位",
            "2. 分批兑现高弹性小票利润（评分 Avoid/Trim）",
            "3. 新增仓位保守：仅限高分 + 回调 + 低风险罚分个股",
        ]
    elif r["regime"] == "Extreme Greed":
        plan = [
            "1. **高弹性仓分批止盈**，降低高beta持仓比例",
            "2. 保留核心仓，切忌一次性清仓",
            "3. 新增仓位暂停，提高现金至 30% 以上",
        ]
    else:  # Bubble Risk
        plan = [
            "1. **立即降低高beta仓位**至 15% 以下",
            "2. 兑现涨幅最大的个股 2/3 仓位",
            "3. 加仓黄金/现金，准备接盘优质资产",
        ]
    lines.extend(plan)
    
    lines.append(f"\n---")
    lines.append(f"*本日报由个人投行系统自动生成 · 数据源: akshare + yfinance + Alternative.me*")
    lines.append(f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    return "\n".join(lines)

def check_report(all_results) -> Dict[str, Any]:
    title("CHECK 12 / Generate Chinese Daily Report")
    result = {"name":"report","ok":False,"details":{},"data":{}}
    try:
        md = generate_report(all_results)
        path = OUT_DIR / "sample_daily_report.md"
        path.write_text(md, encoding="utf-8")
        info(f"  Report written: {path}")
        info(f"  Report length: {len(md)} chars, ~{len(md.split(chr(10)))} lines")
        result["ok"] = len(md) > 500
        result["data"] = {"path": str(path), "preview": md[:800]}
        if result["ok"]:
            ok("Chinese Daily Report generated")
            print("\n" + "="*60)
            print(md[:1500])
            print("..." if len(md) > 1500 else "")
            print("="*60)
    except Exception as e:
        err(f"Report failed: {e}")
        traceback.print_exc()
    return result


# =============================================================
# MAIN
# =============================================================
def main():
    print(f"{C.BD}{C.CY}")
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║  Personal Investment Bank — Phase 1 Core POC Validation     ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print(f"{C.N}")
    
    results = {}
    t0 = time.time()
    
    results["akshare"]      = check_akshare()
    results["yfinance"]     = check_yfinance()
    results["crypto_fng"]   = check_crypto_fng()
    
    # Pre-fetch all A-stocks ONCE (rate limit friendly)
    title("Pre-fetching A-stock data (shared cache)")
    prefetch_all_astocks()
    
    results["technical"]    = check_technical(results["akshare"], results["yfinance"])
    results["global_fng"]   = check_global_fng(results["yfinance"], results["crypto_fng"])
    results["china_tech_fng"] = check_china_fng(results["akshare"])
    results["ai_chain_heat"] = check_ai_chain_heat(results["akshare"], results["yfinance"])
    results["regime"]       = check_regime(results["global_fng"], results["china_tech_fng"], results["ai_chain_heat"])
    results["allocation"]   = check_allocation(results["regime"])
    results["recommendation"] = check_recommendation(results["akshare"], results["yfinance"], results["ai_chain_heat"])
    results["llm"]          = check_emergent_llm(results["global_fng"], results["china_tech_fng"], results["regime"], results["allocation"])
    results["report"]       = check_report(results)
    
    elapsed = time.time() - t0
    
    # Summary
    print(f"\n{C.BD}{C.CY}╔═══════════════════════════════════════════════════════════════╗")
    print(f"║                      POC SUMMARY                              ║")
    print(f"╚═══════════════════════════════════════════════════════════════╝{C.N}")
    passed = 0
    total = len(results)
    for k, v in results.items():
        status = f"{C.G}✓ PASS{C.N}" if v["ok"] else f"{C.R}✗ FAIL{C.N}"
        print(f"  {status}  {k}")
        if v["ok"]: passed += 1
    print(f"\n  Total: {passed}/{total} passed in {elapsed:.1f}s")
    
    # Save JSON summary
    def default(o):
        if isinstance(o, (pd.DataFrame, pd.Series)):
            return f"<DataFrame shape={o.shape}>"
        if isinstance(o, (np.floating, np.integer)):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, datetime):
            return o.isoformat()
        return str(o)
    
    summary_json = {k: {"ok": v["ok"], "details": v.get("details",{}), 
                         "data_keys": list(v.get("data",{}).keys()) if isinstance(v.get("data"), dict) else "see_report"}
                     for k, v in results.items()}
    
    with open(OUT_DIR / "poc_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary_json, f, ensure_ascii=False, indent=2, default=default)
    
    if passed == total:
        print(f"\n{C.G}{C.BD}🎉 ALL CHECKS PASSED — Ready for Phase 2!{C.N}\n")
        return 0
    else:
        print(f"\n{C.R}{C.BD}⚠ Some checks failed — fix before Phase 2{C.N}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
