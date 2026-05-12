"""
AIVONEX – Brand Monitoring System
Dashboard DB helpers — direct SQLite access for Streamlit
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import pandas as pd
from sqlalchemy.orm import Session
from app.database.db import SessionLocal, Brand, Mention, Alert, Report, init_db
from app.services.analyzer import get_analyzer
from app.services.ingestion import get_ingestion_service

init_db()


def get_session() -> Session:
    return SessionLocal()


# ── Brands ────────────────────────────────────────────────────────────────────

def load_brands() -> list[dict]:
    db = get_session()
    brands = db.query(Brand).filter(Brand.is_active == True).all()
    result = [{"id": b.id, "name": b.name, "keywords": b.keywords or [],
               "description": b.description, "industry": b.industry,
               "color": b.color} for b in brands]
    db.close()
    return result


def create_brand(name: str, keywords: list, description: str = "",
                 industry: str = "", color: str = "#00FF88") -> dict:
    db = get_session()
    existing = db.query(Brand).filter(Brand.name == name).first()
    if existing:
        db.close()
        return {"error": f"Brand '{name}' already exists"}
    brand = Brand(name=name, keywords=keywords, description=description,
                  industry=industry, color=color)
    db.add(brand); db.commit(); db.refresh(brand)
    result = {"id": brand.id, "name": brand.name}
    db.close()
    return result


def delete_brand(brand_id: int):
    db = get_session()
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if brand:
        brand.is_active = False
        db.commit()
    db.close()


# ── Mentions ──────────────────────────────────────────────────────────────────

def load_mentions(brand_id: int = None, limit: int = 500) -> pd.DataFrame:
    db = get_session()
    q = db.query(Mention)
    if brand_id:
        q = q.filter(Mention.brand_id == brand_id)
    rows = q.order_by(Mention.created_at.desc()).limit(limit).all()
    data = [
        {
            "id": m.id, "brand_id": m.brand_id, "text": m.text,
            "source": m.source, "author": m.author,
            "sentiment_label": m.sentiment_label,
            "vader_compound": m.vader_compound,
            "vader_pos": m.vader_pos, "vader_neg": m.vader_neg,
            "textblob_polarity": m.textblob_polarity,
            "textblob_subjectivity": m.textblob_subjectivity,
            "confidence": m.confidence, "engagement": m.engagement,
            "reach": m.reach, "created_at": m.created_at,
            "keywords_found": m.keywords_found or [],
        }
        for m in rows
    ]
    db.close()
    return pd.DataFrame(data) if data else pd.DataFrame()


def save_mention(brand_id: int, text: str, source: str = "manual",
                 author: str = "manual_input", engagement: int = 0,
                 reach: int = 0) -> dict:
    db = get_session()
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    brand_keywords = brand.keywords if brand else []
    analyzer = get_analyzer()
    result = analyzer.analyze(text, brand_keywords)

    mention = Mention(
        brand_id=brand_id, text=text, source=source,
        author=author, engagement=engagement, reach=reach,
        sentiment_label=result["sentiment_label"],
        vader_compound=result["vader_compound"],
        vader_pos=result["vader_pos"], vader_neg=result["vader_neg"],
        vader_neu=result["vader_neu"],
        textblob_polarity=result["textblob_polarity"],
        textblob_subjectivity=result["textblob_subjectivity"],
        confidence=result["confidence"],
        keywords_found=result["keywords_found"],
    )
    db.add(mention); db.commit()
    db.close()
    return result


def save_mentions_bulk(brand_id: int, records: list[dict]) -> tuple[int, dict]:
    db = get_session()
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    brand_keywords = brand.keywords if brand else []
    analyzer = get_analyzer()

    results = []
    for rec in records:
        result = analyzer.analyze(rec["text"], brand_keywords)
        mention = Mention(
            brand_id=brand_id, text=rec["text"],
            source=rec.get("source", "CSV"), author=rec.get("author", "unknown"),
            engagement=int(rec.get("engagement", 0)),
            sentiment_label=result["sentiment_label"],
            vader_compound=result["vader_compound"],
            vader_pos=result["vader_pos"], vader_neg=result["vader_neg"],
            vader_neu=result["vader_neu"],
            textblob_polarity=result["textblob_polarity"],
            textblob_subjectivity=result["textblob_subjectivity"],
            confidence=result["confidence"],
            keywords_found=result["keywords_found"],
        )
        db.add(mention)
        results.append(result)

    db.commit(); db.close()
    summary = analyzer.compute_summary(results)
    return len(results), summary


def simulate_and_save(brand_id: int, brand_name: str, n: int = 50,
                      days_back: int = 30) -> tuple[int, dict]:
    ingestion = get_ingestion_service()
    records = ingestion.generate_simulated_mentions(brand_name, n=n, days_back=days_back)
    return save_mentions_bulk(brand_id, records)


def clear_mentions(brand_id: int):
    db = get_session()
    db.query(Mention).filter(Mention.brand_id == brand_id).delete()
    db.commit(); db.close()


# ── Alerts ────────────────────────────────────────────────────────────────────

def load_alerts(brand_id: int = None) -> list[dict]:
    db = get_session()
    q = db.query(Alert)
    if brand_id:
        q = q.filter(Alert.brand_id == brand_id)
    rows = q.order_by(Alert.created_at.desc()).limit(100).all()
    result = [{"id": a.id, "brand_id": a.brand_id, "alert_type": a.alert_type,
               "message": a.message, "severity": a.severity,
               "is_read": a.is_read, "created_at": a.created_at} for a in rows]
    db.close()
    return result


def save_alert(brand_id: int, alert_type: str, message: str, severity: str = "medium"):
    db = get_session()
    alert = Alert(brand_id=brand_id, alert_type=alert_type,
                  message=message, severity=severity)
    db.add(alert); db.commit(); db.close()


def mark_alert_read(alert_id: int):
    db = get_session()
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert:
        alert.is_read = True
        db.commit()
    db.close()


# ── Reports ───────────────────────────────────────────────────────────────────

def load_reports() -> list[dict]:
    db = get_session()
    rows = db.query(Report).order_by(Report.created_at.desc()).limit(20).all()
    result = [{"id": r.id, "brand_id": r.brand_id, "title": r.title,
               "report_type": r.report_type, "file_path": r.file_path,
               "created_at": r.created_at} for r in rows]
    db.close()
    return result


def save_report(brand_id: int, title: str, report_type: str, file_path: str):
    db = get_session()
    report = Report(brand_id=brand_id, title=title,
                    report_type=report_type, file_path=file_path)
    db.add(report); db.commit(); db.close()
