"""SQLAlchemy ORM models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Index
from backend.storage.db import Base


class MarketPrice(Base):
    __tablename__ = "market_price"
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, index=True)
    name = Column(String, nullable=True)
    market = Column(String, index=True)        # CN/US/Crypto/Index
    asset_type = Column(String, nullable=True)  # stock/index/etf/crypto
    date = Column(String, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    turnover = Column(Float, nullable=True)
    pct_change = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (Index("ix_mp_sym_date", "symbol", "date", unique=True),)


class MarketIndicator(Base):
    __tablename__ = "market_indicator"
    id = Column(Integer, primary_key=True, autoincrement=True)
    indicator_name = Column(String, index=True)  # global_fng / china_tech_fng / crypto_fng / regime / ...
    region = Column(String, nullable=True)
    date = Column(String, index=True)
    value = Column(Float)
    extra = Column(JSON, nullable=True)
    source = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (Index("ix_mi_name_date", "indicator_name", "date"),)


class SectorScore(Base):
    __tablename__ = "sector_score"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String, index=True)
    sector = Column(String, index=True)
    momentum_score = Column(Float)
    valuation_score = Column(Float, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    heat_score = Column(Float)
    risk_score = Column(Float, nullable=True)
    action_signal = Column(String, nullable=True)
    extra = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshot"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String, index=True)
    symbol = Column(String, index=True)
    name = Column(String)
    sector = Column(String)
    market = Column(String)
    shares = Column(Float, default=0)
    weight = Column(Float, default=0)
    price = Column(Float, default=0)
    market_value = Column(Float, default=0)
    pnl_pct = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class DailySignal(Base):
    __tablename__ = "daily_signal"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String, index=True, unique=True)
    global_fear_greed = Column(Float)
    china_fear_greed = Column(Float)
    crypto_fear_greed = Column(Float, nullable=True)
    ai_chain_score = Column(Float)
    market_regime = Column(String)
    combined_score = Column(Float)
    recommended_equity_weight_min = Column(Float)
    recommended_equity_weight_max = Column(Float)
    recommended_ai_weight_min = Column(Float)
    recommended_ai_weight_max = Column(Float)
    recommended_cash_weight_min = Column(Float)
    recommended_cash_weight_max = Column(Float)
    action_summary = Column(Text)
    full_payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String, index=True)
    symbol = Column(String, index=True)
    name = Column(String)
    sector = Column(String)
    market = Column(String)
    score = Column(Float)
    action = Column(String)
    reason = Column(Text)
    indicators = Column(JSON, nullable=True)
    suggested_weight_min = Column(Float, nullable=True)
    suggested_weight_max = Column(Float, nullable=True)
    risk_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class DailyReport(Base):
    __tablename__ = "daily_report"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String, index=True, unique=True)
    title = Column(String)
    markdown = Column(Text)
    summary = Column(Text, nullable=True)
    extra = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
