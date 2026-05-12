"""
AIVONEX – Brand Monitoring System
Database Configuration & Models
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, Float,
    DateTime, Text, Boolean, ForeignKey, JSON
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import os

# ─── Engine ───────────────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "../../data/brand_monitor.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ─── Models ───────────────────────────────────────────────────────────────────

class Brand(Base):
    __tablename__ = "brands"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), unique=True, nullable=False)
    keywords    = Column(JSON, default=[])           # list of tracking keywords
    description = Column(Text, default="")
    industry    = Column(String(100), default="")
    color       = Column(String(10), default="#00FF88") # chart color
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime, default=datetime.utcnow)

    mentions = relationship("Mention", back_populates="brand", cascade="all, delete")


class Mention(Base):
    __tablename__ = "mentions"

    id              = Column(Integer, primary_key=True, index=True)
    brand_id        = Column(Integer, ForeignKey("brands.id"), nullable=False)
    text            = Column(Text, nullable=False)
    source          = Column(String(50), default="manual")   # twitter/reddit/news/csv/manual
    url             = Column(Text, default="")
    author          = Column(String(100), default="unknown")

    # Sentiment scores
    sentiment_label = Column(String(20), default="neutral")   # positive/negative/neutral
    vader_compound  = Column(Float, default=0.0)
    vader_pos       = Column(Float, default=0.0)
    vader_neg       = Column(Float, default=0.0)
    vader_neu       = Column(Float, default=0.0)
    textblob_polarity    = Column(Float, default=0.0)
    textblob_subjectivity= Column(Float, default=0.0)
    confidence      = Column(Float, default=0.0)

    # Metadata
    language        = Column(String(10), default="en")
    engagement      = Column(Integer, default=0)   # likes/upvotes/shares
    reach           = Column(Integer, default=0)
    keywords_found  = Column(JSON, default=[])
    entities        = Column(JSON, default=[])
    created_at      = Column(DateTime, default=datetime.utcnow)
    mention_date    = Column(DateTime, default=datetime.utcnow)

    brand = relationship("Brand", back_populates="mentions")


class Alert(Base):
    __tablename__ = "alerts"

    id          = Column(Integer, primary_key=True, index=True)
    brand_id    = Column(Integer, ForeignKey("brands.id"))
    alert_type  = Column(String(50))   # spike/negative_surge/keyword_hit/sentiment_drop
    message     = Column(Text)
    severity    = Column(String(20), default="medium")  # low/medium/high/critical
    is_read     = Column(Boolean, default=False)
    created_at  = Column(DateTime, default=datetime.utcnow)


class Report(Base):
    __tablename__ = "reports"

    id          = Column(Integer, primary_key=True, index=True)
    brand_id    = Column(Integer, ForeignKey("brands.id"), nullable=True)
    title       = Column(String(200))
    report_type = Column(String(50))   # daily/weekly/monthly/custom
    file_path   = Column(Text)
    created_at  = Column(DateTime, default=datetime.utcnow)


# ─── Init ─────────────────────────────────────────────────────────────────────

def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
