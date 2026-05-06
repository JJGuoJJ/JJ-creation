"""Main daily pipeline: refresh data -> compute -> save -> generate report."""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd
from backend.core.utils import to_jsonable, today_str, now_bj
from backend.core.logger import logger
from backend.core.config import get_data_sources
from backend.data_providers import akshare_provider, yfinance_provider, alternative_fng_provider
from backend.indicators.fear_greed import compute_global_fng, compute_china_tech_fng
from backend.indicators.sector_heat import compute_sector_heat
from backend.indicators.portfolio_metrics import diagnose_portfolio
from backend.indicators.technical import compute_indicators
from backend.strategy.regime_detector import detect_regime
from backend.strategy.allocation_engine import allocate
from backend.strategy.recommendation_engine import rank_watchlist
from backend.strategy.llm_interpretation import get_interpretation
from backend.report.daily_report import generate_daily_report
from backend.storage.repository import (
    session, upsert_signal, upsert_report, save_recommendations,
    save_sector_scores, save_portfolio_snapshot,
)
from backend.storage.models import Base
from backend.storage.db import engine

# Ensure tables
Base.metadata.create_all(bind=engine)


def run_pipeline(use_llm: bool = True, force_today: bool = True) -> Dict[str, Any]:
    """Run the daily pipeline. Returns full payload dict."""
    t0 = datetime.now()
    date = today_str()
    missing_sources: List[str] = []
    logger.info(f"=== Daily pipeline start ({date}) ===")

    # Clear caches to force fresh fetch
    akshare_provider.clear_cache()
    yfinance_provider.clear_cache()

    cfg = get_data_sources()
    cn_indices_cfg = cfg.get("cn_indices", {})
    global_tickers_cfg = cfg.get("global_tickers", {})

    # 1. CN indices
    logger.info("Fetching CN indices...")
    cn_idx: Dict[str, pd.DataFrame] = {}
    for code in cn_indices_cfg.keys():
        df = akshare_provider.fetch_index(code)
        if df is not None:
            cn_idx[code] = df
    if not cn_idx:
        missing_sources.append("akshare \u6307\u6570")

    # 2. Total turnover
    total_tv = akshare_provider.fetch_total_market_turnover_wanyi()
    if total_tv is None:
        missing_sources.append("\u4e24\u5e02\u603b\u6210\u4ea4\u989d")

    # 3. Global tickers (yfinance)
    logger.info("Fetching global tickers...")
    yf_data: Dict[str, pd.DataFrame] = {}
    for sym in global_tickers_cfg.keys():
        df = yfinance_provider.fetch_history(sym)
        if df is not None:
            yf_data[sym] = df
    if len(yf_data) < len(global_tickers_cfg) // 2:
        missing_sources.append("yfinance \u90e8\u5206\u4e22\u5931")

    # 4. Crypto F&G
    logger.info("Fetching Crypto F&G...")
    crypto_data = alternative_fng_provider.fetch_crypto_fng()
    crypto_now = crypto_data["current"] if crypto_data else None
    if crypto_now is None:
        missing_sources.append("Alternative.me Crypto F&G")

    # 5. Compute scores
    global_fng = compute_global_fng(yf_data, crypto_now)
    ak_data = {"indices": cn_idx, "total_turnover": total_tv}
    china_fng = compute_china_tech_fng(ak_data)

    # 6. Sector heat (loads watchlist stocks)
    logger.info("Computing sector heat...")
    sector_heat = compute_sector_heat()

    # 7. Regime + allocation
    regime = detect_regime(global_fng["score"], china_fng["score"], sector_heat)
    allocation = allocate(regime["regime"])

    # 8. Recommendations
    logger.info("Ranking watchlist...")
    recs = rank_watchlist(sector_heat)

    # 9. Portfolio diagnosis
    portfolio_diag = diagnose_portfolio(allocation, sector_heat)

    # 10. LLM interpretation
    llm_text = ""
    if use_llm:
        try:
            llm_text = get_interpretation({
                "global_fng": global_fng,
                "china_tech_fng": china_fng,
                "regime": regime,
                "allocation": allocation,
                "sector_heat": sector_heat,
                "recommendations": recs[:5],
            })
        except Exception as e:
            logger.warning(f"LLM failed: {e}")

    payload = {
        "date": date,
        "global_fng": global_fng,
        "china_tech_fng": china_fng,
        "crypto_fng": crypto_data,
        "regime": regime,
        "allocation": allocation,
        "sector_heat": sector_heat,
        "recommendations": recs,
        "portfolio": portfolio_diag,
        "llm_interpretation": llm_text,
        "missing_sources": missing_sources,
        "generated_at": now_bj().isoformat(),
        "elapsed_seconds": round((datetime.now() - t0).total_seconds(), 1),
    }

    # 11. Save
    md = generate_daily_report(payload)
    payload["report_markdown"] = md

    s = session()
    try:
        upsert_signal(
            s,
            date=date,
            global_fear_greed=global_fng["score"],
            china_fear_greed=china_fng["score"],
            crypto_fear_greed=float(crypto_now) if crypto_now is not None else None,
            ai_chain_score=regime["ai_peak_heat"],
            market_regime=regime["regime"],
            combined_score=regime["combined_score"],
            recommended_equity_weight_min=allocation.get("equity", [55, 65])[0],
            recommended_equity_weight_max=allocation.get("equity", [55, 65])[1],
            recommended_ai_weight_min=allocation.get("ai_tech", [35, 50])[0],
            recommended_ai_weight_max=allocation.get("ai_tech", [35, 50])[1],
            recommended_cash_weight_min=allocation.get("cash", [15, 25])[0],
            recommended_cash_weight_max=allocation.get("cash", [15, 25])[1],
            action_summary=regime["action"],
            full_payload=to_jsonable({
                "global_fng": global_fng,
                "china_tech_fng": china_fng,
                "crypto_fng": crypto_data,
                "regime": regime,
                "allocation": allocation,
                "sector_heat": sector_heat,
                "missing_sources": missing_sources,
                "llm_interpretation": llm_text,
            }),
        )
        # Sector scores
        sector_rows = []
        for sec, sc in sector_heat.items():
            if sc.get("heat") is None: continue
            sector_rows.append({
                "date": date, "sector": sec,
                "momentum_score": sc.get("momentum"),
                "valuation_score": None,
                "sentiment_score": sc.get("breadth"),
                "heat_score": sc.get("heat"),
                "risk_score": sc.get("risk_penalty"),
                "action_signal": sc.get("action"),
                "extra": to_jsonable(sc),
            })
        save_sector_scores(s, sector_rows)
        # Recommendations
        rec_rows = []
        for r in recs:
            rec_rows.append({
                "date": date, "symbol": r["symbol"], "name": r["name"],
                "sector": r["sector"], "market": r["market"],
                "score": r["score"], "action": r["action"],
                "reason": r["reason"], "indicators": to_jsonable(r["indicators"]),
                "suggested_weight_min": None, "suggested_weight_max": None,
                "risk_note": None,
            })
        save_recommendations(s, rec_rows)
        # Portfolio snapshot
        snap_rows = []
        for p in portfolio_diag.get("rows", []):
            snap_rows.append({
                "date": date, "symbol": p["symbol"], "name": p["name"],
                "sector": p["sector"], "market": p["market"],
                "shares": float(p.get("shares", 0) or 0),
                "weight": float(p.get("weight", 0) or 0),
                "price": float(p.get("price", 0) or 0),
                "market_value": float(p.get("market_value_cny", 0) or 0),
                "pnl_pct": p.get("chg_pct"),
                "risk_level": None,
            })
        save_portfolio_snapshot(s, snap_rows)
        # Report
        upsert_report(s, date=date, title=f"\u4e2a\u4eba\u6295\u884c\u7cfb\u7edf\u65e5\u62a5 {date}",
                      markdown=md, summary=regime["action"],
                      extra={"missing_sources": missing_sources})
        s.commit()
    except Exception as e:
        logger.error(f"DB save failed: {e}")
        s.rollback()
    finally:
        s.close()

    logger.info(f"=== Daily pipeline done ({payload['elapsed_seconds']}s, regime={regime['regime']}) ===")
    return payload
