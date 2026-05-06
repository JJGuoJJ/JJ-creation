"""Personal Investment Bank System - FastAPI server."""
import os
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, HTTPException, Body
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")

# Make package imports work both as `backend.xxx` and direct
import sys
sys.path.insert(0, str(ROOT.parent))

from backend.core.logger import logger
from backend.core.utils import to_jsonable, today_str, now_bj
from backend.core.config import (
    get_portfolio, get_watchlist, get_sectors, get_thresholds,
    get_strategy_profile, get_data_sources, save_yaml, load_yaml,
)
from backend.storage.db import engine, SessionLocal
from backend.storage.models import Base
from backend.storage import repository as repo
from backend.main_pipeline import run_pipeline
from backend.scheduler.jobs import start_scheduler

# Init DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Personal Investment Bank System", version="1.0")
api_router = APIRouter(prefix="/api")

# In-memory state for pipeline running
_pipeline_state = {"running": False, "last_run": None, "last_error": None}


class PortfolioUpdateItem(BaseModel):
    symbol: str
    shares: float = 0.0


class ThresholdsUpdate(BaseModel):
    risk_profile: Optional[str] = None
    fng_thresholds: Optional[Dict[str, float]] = None
    risk_signals: Optional[Dict[str, float]] = None


# ============ Health & meta ============
@api_router.get("/")
async def root():
    return {"app": "Personal Investment Bank", "version": "1.0", "today": today_str()}


@api_router.get("/health")
async def health():
    s = repo.session()
    try:
        sig = repo.get_latest_signal(s)
        last_date = sig.date if sig else None
    finally:
        s.close()
    return {
        "status": "ok",
        "service_time": now_bj().isoformat(),
        "last_data_date": last_date,
        "pipeline_running": _pipeline_state["running"],
        "pipeline_last_run": _pipeline_state["last_run"],
    }


# ============ Refresh Pipeline ============
@api_router.post("/refresh-data")
async def refresh_data(use_llm: bool = True):
    if _pipeline_state["running"]:
        raise HTTPException(409, "Pipeline already running")
    _pipeline_state["running"] = True
    _pipeline_state["last_error"] = None
    try:
        loop = asyncio.get_event_loop()
        payload = await loop.run_in_executor(None, run_pipeline, use_llm, True)
        _pipeline_state["last_run"] = now_bj().isoformat()
        return {
            "ok": True,
            "date": payload["date"],
            "elapsed_seconds": payload["elapsed_seconds"],
            "regime": payload["regime"]["regime"],
            "regime_cn": payload["regime"]["regime_cn"],
            "global_fng": payload["global_fng"]["score"],
            "china_fng": payload["china_tech_fng"]["score"],
            "missing_sources": payload["missing_sources"],
        }
    except Exception as e:
        logger.exception("refresh_data failed")
        _pipeline_state["last_error"] = str(e)
        raise HTTPException(500, f"Pipeline failed: {e}")
    finally:
        _pipeline_state["running"] = False


# ============ Market Overview ============
@api_router.get("/market/overview")
async def market_overview():
    s = repo.session()
    try:
        sig = repo.get_latest_signal(s)
        if not sig:
            return {"empty": True, "message": "No data yet. Please run /api/refresh-data."}
        return {
            "date": sig.date,
            "regime": sig.market_regime,
            "regime_cn": _regime_cn(sig.market_regime),
            "combined_score": sig.combined_score,
            "global_fng": sig.global_fear_greed,
            "china_tech_fng": sig.china_fear_greed,
            "crypto_fng": sig.crypto_fear_greed,
            "ai_chain_score": sig.ai_chain_score,
            "allocation": {
                "equity": [sig.recommended_equity_weight_min, sig.recommended_equity_weight_max],
                "ai_tech": [sig.recommended_ai_weight_min, sig.recommended_ai_weight_max],
                "cash": [sig.recommended_cash_weight_min, sig.recommended_cash_weight_max],
            },
            "action_summary": sig.action_summary,
            "full_payload": sig.full_payload or {},
        }
    finally:
        s.close()


def _regime_cn(regime: str) -> str:
    return {
        "Extreme Fear": "极度恐慌",
        "Fear": "恐慌",
        "Neutral": "中性",
        "Greed": "贪婪",
        "Extreme Greed": "极度贪婪",
        "Bubble Risk": "泡沫风险",
    }.get(regime, regime)


# ============ Fear & Greed history ============
@api_router.get("/indicators/fear-greed")
async def fear_greed_history(days: int = 60):
    s = repo.session()
    try:
        rows = repo.get_signal_history(s, n=days)
        rows = list(reversed(rows))
        return {
            "history": [
                {
                    "date": r.date,
                    "global_fng": r.global_fear_greed,
                    "china_tech_fng": r.china_fear_greed,
                    "crypto_fng": r.crypto_fear_greed,
                    "ai_chain_score": r.ai_chain_score,
                    "regime": r.market_regime,
                    "combined_score": r.combined_score,
                }
                for r in rows
            ]
        }
    finally:
        s.close()


# ============ Sectors ============
@api_router.get("/sectors")
async def sectors():
    s = repo.session()
    try:
        rows = repo.get_latest_sector_scores(s)
        return {
            "sectors": [
                {
                    "sector": r.sector,
                    "heat_score": r.heat_score,
                    "momentum": r.momentum_score,
                    "sentiment": r.sentiment_score,
                    "risk": r.risk_score,
                    "action": r.action_signal,
                    "detail": r.extra or {},
                }
                for r in rows
            ]
        }
    finally:
        s.close()


# ============ Watchlist / Recommendations ============
@api_router.get("/watchlist")
async def watchlist(sector: Optional[str] = None, action: Optional[str] = None,
                    market: Optional[str] = None):
    s = repo.session()
    try:
        recs = repo.get_latest_recs(s, limit=200)
        out = []
        for r in recs:
            if sector and r.sector != sector:
                continue
            if action and r.action != action:
                continue
            if market and r.market != market:
                continue
            out.append({
                "symbol": r.symbol, "name": r.name, "sector": r.sector,
                "market": r.market, "score": r.score, "action": r.action,
                "action_cn": _action_cn(r.action), "reason": r.reason,
                "indicators": r.indicators or {},
            })
        return {"recommendations": out}
    finally:
        s.close()


@api_router.get("/recommendations/today")
async def recs_today(limit: int = 20):
    s = repo.session()
    try:
        recs = repo.get_latest_recs(s, limit=limit)
        return {
            "recommendations": [
                {
                    "symbol": r.symbol, "name": r.name, "sector": r.sector,
                    "market": r.market, "score": r.score, "action": r.action,
                    "action_cn": _action_cn(r.action), "reason": r.reason,
                    "indicators": r.indicators or {},
                }
                for r in recs
            ]
        }
    finally:
        s.close()


def _action_cn(a: str) -> str:
    return {
        "Strong Buy on Pullback": "回调加仓",
        "Buy Small": "小仓位布局",
        "Hold": "持有",
        "Wait": "等待",
        "Trim": "减仓止盈",
        "Avoid Chasing": "回避追涨",
        "Risk Control": "风险控制",
    }.get(a, a)


# ============ Portfolio ============
@api_router.get("/portfolio")
async def portfolio():
    s = repo.session()
    try:
        snaps = repo.get_latest_portfolio(s)
        sig = repo.get_latest_signal(s)
        positions = get_portfolio()
        rows = []
        for sym, info in positions.items():
            snap = next((x for x in snaps if x.symbol == sym), None)
            rows.append({
                "symbol": sym,
                "name": info.get("name", sym),
                "sector": info.get("sector", ""),
                "market": info.get("market", "CN"),
                "shares": float(info.get("shares", 0) or 0),
                "weight": snap.weight if snap else 0,
                "price": snap.price if snap else 0,
                "market_value": snap.market_value if snap else 0,
                "chg_pct": snap.pnl_pct if snap else None,
            })
        # buckets and target bands
        buckets = {}
        target_bands = {}
        if sig and sig.full_payload:
            target_bands = sig.full_payload.get("regime", {}).get("regime") and (
                sig.full_payload.get("allocation") or {}
            )
        full = (sig.full_payload or {}) if sig else {}
        return {
            "positions": rows,
            "buckets": full.get("regime", {}) and {},  # placeholder; use diagnose endpoint for full
            "target_bands": full.get("allocation", {}),
            "date": sig.date if sig else None,
        }
    finally:
        s.close()


@api_router.get("/portfolio/diagnose")
async def portfolio_diagnose():
    """Returns full portfolio diagnostics (current weights, buckets, target bands, add/trim lists)."""
    from backend.indicators.portfolio_metrics import diagnose_portfolio
    from backend.strategy.allocation_engine import allocate
    s = repo.session()
    try:
        sig = repo.get_latest_signal(s)
        if not sig:
            raise HTTPException(404, "No data yet. Please run /api/refresh-data first.")
        regime = sig.market_regime
        allocation = allocate(regime)
        sector_heat = (sig.full_payload or {}).get("sector_heat", {})
    finally:
        s.close()
    diag = diagnose_portfolio(allocation, sector_heat)
    return {"date": sig.date if sig else today_str(), **diag}


@api_router.post("/portfolio/update")
async def update_portfolio(items: List[PortfolioUpdateItem]):
    data = load_yaml("portfolio.yaml")
    positions = data.get("current_positions", {})
    for item in items:
        if item.symbol not in positions:
            continue
        positions[item.symbol]["shares"] = float(item.shares)
    data["current_positions"] = positions
    save_yaml("portfolio.yaml", data)
    return {"ok": True, "updated": len(items)}


# ============ Reports ============
@api_router.get("/reports/list")
async def reports_list():
    s = repo.session()
    try:
        reports = repo.get_reports(s, limit=60)
        return {
            "reports": [
                {"date": r.date, "title": r.title, "summary": r.summary}
                for r in reports
            ]
        }
    finally:
        s.close()


@api_router.get("/reports/{date}")
async def report_get(date: str):
    if date == "latest":
        s = repo.session()
        try:
            sig = repo.get_latest_signal(s)
            if not sig:
                raise HTTPException(404, "No reports yet")
            r = repo.get_report_by_date(s, sig.date)
        finally:
            s.close()
    else:
        s = repo.session()
        try:
            r = repo.get_report_by_date(s, date)
        finally:
            s.close()
    if not r:
        raise HTTPException(404, "Report not found")
    return {
        "date": r.date,
        "title": r.title,
        "summary": r.summary,
        "markdown": r.markdown,
        "extra": r.extra or {},
    }


@api_router.get("/reports/{date}/download")
async def report_download(date: str):
    s = repo.session()
    try:
        r = repo.get_report_by_date(s, date)
    finally:
        s.close()
    if not r:
        raise HTTPException(404, "Report not found")
    return PlainTextResponse(r.markdown, headers={
        "Content-Disposition": f'attachment; filename="report_{r.date}.md"'
    })


# ============ Settings ============
@api_router.get("/settings/thresholds")
async def get_thresholds_api():
    return get_thresholds()


@api_router.post("/settings/thresholds")
async def update_thresholds(payload: Dict[str, Any] = Body(...)):
    cur = get_thresholds()
    cur.update(payload)
    save_yaml("thresholds.yaml", cur)
    return {"ok": True, "thresholds": cur}


@api_router.get("/settings/risk-profile")
async def get_risk_profile():
    p = get_strategy_profile()
    return {"risk_profile": p.get("risk_profile", "medium_high"),
            "options": list(p.get("risk_profiles", {}).keys())}


@api_router.post("/settings/risk-profile")
async def set_risk_profile(payload: Dict[str, str] = Body(...)):
    cur = get_strategy_profile()
    cur["risk_profile"] = payload.get("risk_profile", cur.get("risk_profile", "medium_high"))
    save_yaml("strategy_profile.yaml", cur)
    return {"ok": True, "risk_profile": cur["risk_profile"]}


@api_router.get("/settings/watchlist")
async def get_watchlist_api():
    return {"watchlist": get_watchlist()}


# ============ Backtest (basic placeholder) ============
@api_router.post("/backtest/run")
async def backtest_run(symbol: str = "^IXIC", days: int = 250):
    """Very simple backtest: F&G-like rule (RSI/MA based) vs buy & hold on a single ticker."""
    from backend.data_providers import yfinance_provider
    from backend.indicators.technical import compute_indicators
    import numpy as np
    df = yfinance_provider.fetch_history(symbol, period="2y")
    if df is None or len(df) < 200:
        raise HTTPException(404, "Insufficient data")
    close = df["close"].astype(float).values
    n = len(close)
    # Strategy: hold 100% if close > MA200, else 50%
    ma200 = np.array([np.nan] * n)
    for i in range(n):
        if i >= 199:
            ma200[i] = np.mean(close[i - 199:i + 1])
    weights = np.where(close > ma200, 1.0, 0.5)
    weights[np.isnan(ma200)] = 1.0
    daily_ret = np.diff(close) / close[:-1]
    strat_ret = weights[:-1] * daily_ret
    bh_curve = np.cumprod(1 + daily_ret)
    st_curve = np.cumprod(1 + strat_ret)
    bh_total = float(bh_curve[-1] - 1)
    st_total = float(st_curve[-1] - 1)
    # MDD
    def mdd(curve):
        roll_max = np.maximum.accumulate(curve)
        dd = curve / roll_max - 1
        return float(dd.min())
    return {
        "symbol": symbol,
        "n_days": int(n),
        "buy_hold_return_pct": round(bh_total * 100, 2),
        "strategy_return_pct": round(st_total * 100, 2),
        "buy_hold_mdd_pct": round(mdd(bh_curve) * 100, 2),
        "strategy_mdd_pct": round(mdd(st_curve) * 100, 2),
        "curves": {
            "dates": [str(d.date()) for d in df.index[1:]],
            "buy_hold": [round(float(x), 4) for x in bh_curve.tolist()],
            "strategy": [round(float(x), 4) for x in st_curve.tolist()],
        },
    }


# Mount
app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    logger.info("Personal Investment Bank starting...")
    try:
        start_scheduler()
    except Exception as e:
        logger.warning(f"Scheduler start failed (non-fatal): {e}")


@app.on_event("shutdown")
async def shutdown():
    logger.info("Personal Investment Bank shutting down...")
