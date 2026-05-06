"""Repository helpers."""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.storage.models import (
    MarketPrice, MarketIndicator, SectorScore, PortfolioSnapshot,
    DailySignal, Recommendation, DailyReport,
)
from backend.storage.db import SessionLocal
from datetime import datetime


def session() -> Session:
    return SessionLocal()


def upsert_market_price(s: Session, **fields):
    sym = fields["symbol"]; date = fields["date"]
    obj = s.query(MarketPrice).filter_by(symbol=sym, date=date).first()
    if obj:
        for k, v in fields.items():
            setattr(obj, k, v)
    else:
        s.add(MarketPrice(**fields))


def save_indicator(s: Session, **fields):
    s.add(MarketIndicator(**fields))


def upsert_signal(s: Session, **fields):
    date = fields["date"]
    obj = s.query(DailySignal).filter_by(date=date).first()
    if obj:
        for k, v in fields.items():
            setattr(obj, k, v)
    else:
        s.add(DailySignal(**fields))


def upsert_report(s: Session, **fields):
    date = fields["date"]
    obj = s.query(DailyReport).filter_by(date=date).first()
    if obj:
        for k, v in fields.items():
            setattr(obj, k, v)
    else:
        s.add(DailyReport(**fields))


def save_recommendations(s: Session, recs: List[Dict[str, Any]]):
    if not recs:
        return
    date = recs[0]["date"]
    s.query(Recommendation).filter_by(date=date).delete()
    for r in recs:
        s.add(Recommendation(**r))


def save_sector_scores(s: Session, scores: List[Dict[str, Any]]):
    if not scores:
        return
    date = scores[0]["date"]
    s.query(SectorScore).filter_by(date=date).delete()
    for sc in scores:
        s.add(SectorScore(**sc))


def save_portfolio_snapshot(s: Session, snaps: List[Dict[str, Any]]):
    if not snaps:
        return
    date = snaps[0]["date"]
    s.query(PortfolioSnapshot).filter_by(date=date).delete()
    for sp in snaps:
        s.add(PortfolioSnapshot(**sp))


def get_latest_signal(s: Session) -> Optional[DailySignal]:
    return s.query(DailySignal).order_by(desc(DailySignal.date)).first()


def get_signal_history(s: Session, n: int = 60) -> List[DailySignal]:
    return s.query(DailySignal).order_by(desc(DailySignal.date)).limit(n).all()


def get_latest_recs(s: Session, limit: int = 50) -> List[Recommendation]:
    sig = get_latest_signal(s)
    if not sig:
        return []
    return s.query(Recommendation).filter_by(date=sig.date).order_by(desc(Recommendation.score)).limit(limit).all()


def get_latest_sector_scores(s: Session) -> List[SectorScore]:
    sig = get_latest_signal(s)
    if not sig:
        return []
    return s.query(SectorScore).filter_by(date=sig.date).order_by(desc(SectorScore.heat_score)).all()


def get_latest_portfolio(s: Session) -> List[PortfolioSnapshot]:
    sig = get_latest_signal(s)
    if not sig:
        return []
    return s.query(PortfolioSnapshot).filter_by(date=sig.date).all()


def get_reports(s: Session, limit: int = 30) -> List[DailyReport]:
    return s.query(DailyReport).order_by(desc(DailyReport.date)).limit(limit).all()


def get_report_by_date(s: Session, date: str) -> Optional[DailyReport]:
    return s.query(DailyReport).filter_by(date=date).first()
