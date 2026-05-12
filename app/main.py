"""
AIVONEX – Brand Monitoring System
FastAPI Backend — REST API
"""

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
import json

from app.database.db import init_db, get_db, Brand, Mention, Alert, Report
from app.services.analyzer import get_analyzer
from app.services.ingestion import get_ingestion_service
from app.services.reporter import get_reporter
from app.services.alerts import AlertService

# ─── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AIVONEX Brand Monitoring API",
    description="Sentiment Analysis & Brand Monitoring System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


# ─── Schemas ──────────────────────────────────────────────────────────────────

class BrandCreate(BaseModel):
    name:        str
    keywords:    list[str] = []
    description: str = ""
    industry:    str = ""
    color:       str = "#00FF88"


class AnalyzeTextRequest(BaseModel):
    text:     str
    brand_id: Optional[int] = None
    source:   str = "manual"


class SimulateRequest(BaseModel):
    brand_id:  int
    n:         int = 50
    days_back: int = 30


# ─── Health ───────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": "AIVONEX Brand Monitoring System", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# ─── Brands ───────────────────────────────────────────────────────────────────

@app.post("/brands", tags=["Brands"])
def create_brand(payload: BrandCreate, db: Session = Depends(get_db)):
    existing = db.query(Brand).filter(Brand.name == payload.name).first()
    if existing:
        raise HTTPException(400, f"Brand '{payload.name}' already exists")
    brand = Brand(**payload.model_dump())
    db.add(brand); db.commit(); db.refresh(brand)
    return {"id": brand.id, "name": brand.name, "message": "Brand created"}


@app.get("/brands", tags=["Brands"])
def list_brands(db: Session = Depends(get_db)):
    brands = db.query(Brand).filter(Brand.is_active == True).all()
    return [{"id": b.id, "name": b.name, "keywords": b.keywords,
             "description": b.description, "industry": b.industry,
             "color": b.color, "created_at": b.created_at} for b in brands]


@app.get("/brands/{brand_id}", tags=["Brands"])
def get_brand(brand_id: int, db: Session = Depends(get_db)):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(404, "Brand not found")
    return brand


@app.delete("/brands/{brand_id}", tags=["Brands"])
def delete_brand(brand_id: int, db: Session = Depends(get_db)):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(404, "Brand not found")
    brand.is_active = False
    db.commit()
    return {"message": f"Brand '{brand.name}' deactivated"}


# ─── Analysis ─────────────────────────────────────────────────────────────────

@app.post("/analyze/text", tags=["Analysis"])
def analyze_text(payload: AnalyzeTextRequest, db: Session = Depends(get_db)):
    analyzer = get_analyzer()
    brand_keywords = []

    if payload.brand_id:
        brand = db.query(Brand).filter(Brand.id == payload.brand_id).first()
        if brand:
            brand_keywords = brand.keywords or []

    result = analyzer.analyze(payload.text, brand_keywords)

    # Save mention
    mention = Mention(
        brand_id=payload.brand_id,
        text=payload.text,
        source=payload.source,
        **{k: result[k] for k in [
            "sentiment_label", "vader_compound", "vader_pos", "vader_neg",
            "vader_neu", "textblob_polarity", "textblob_subjectivity", "confidence"
        ]},
        keywords_found=result["keywords_found"],
    )
    db.add(mention); db.commit()

    return {**result, "mention_id": mention.id}


@app.post("/analyze/batch", tags=["Analysis"])
def analyze_batch(brand_id: int, db: Session = Depends(get_db),
                  texts: list[str] = []):
    analyzer = get_analyzer()
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    brand_keywords = brand.keywords if brand else []

    results = analyzer.analyze_batch(texts, brand_keywords)

    for text, result in zip(texts, results):
        mention = Mention(
            brand_id=brand_id, text=text, source="batch",
            **{k: result[k] for k in [
                "sentiment_label", "vader_compound", "vader_pos", "vader_neg",
                "vader_neu", "textblob_polarity", "textblob_subjectivity", "confidence"
            ]},
            keywords_found=result["keywords_found"],
        )
        db.add(mention)
    db.commit()

    summary = analyzer.compute_summary(results)
    return {"results": results, "summary": summary, "total": len(results)}


@app.post("/analyze/csv", tags=["Analysis"])
async def analyze_csv(
    brand_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    content  = await file.read()
    ingestion = get_ingestion_service()
    analyzer  = get_analyzer()

    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(404, "Brand not found")

    records = ingestion.parse_csv_bytes(content)
    brand_keywords = brand.keywords or []

    saved = 0
    results = []
    for rec in records:
        result = analyzer.analyze(rec["text"], brand_keywords)
        mention = Mention(
            brand_id=brand_id,
            text=rec["text"],
            source=rec.get("source", "CSV"),
            author=rec.get("author", "unknown"),
            engagement=int(rec.get("engagement", 0)),
            **{k: result[k] for k in [
                "sentiment_label", "vader_compound", "vader_pos", "vader_neg",
                "vader_neu", "textblob_polarity", "textblob_subjectivity", "confidence"
            ]},
            keywords_found=result["keywords_found"],
        )
        db.add(mention)
        results.append(result)
        saved += 1

    db.commit()
    summary = analyzer.compute_summary(results)
    return {"saved": saved, "summary": summary}


@app.post("/analyze/simulate", tags=["Analysis"])
def simulate_mentions(payload: SimulateRequest, db: Session = Depends(get_db)):
    brand = db.query(Brand).filter(Brand.id == payload.brand_id).first()
    if not brand:
        raise HTTPException(404, "Brand not found")

    ingestion = get_ingestion_service()
    analyzer  = get_analyzer()

    records  = ingestion.generate_simulated_mentions(brand.name, n=payload.n,
                                                     days_back=payload.days_back)
    results  = []
    for rec in records:
        result = analyzer.analyze(rec["text"], brand.keywords or [])
        mention = Mention(
            brand_id=payload.brand_id,
            text=rec["text"], source=rec["source"], author=rec["author"],
            engagement=rec.get("engagement", 0), reach=rec.get("reach", 0),
            **{k: result[k] for k in [
                "sentiment_label", "vader_compound", "vader_pos", "vader_neg",
                "vader_neu", "textblob_polarity", "textblob_subjectivity", "confidence"
            ]},
            keywords_found=result["keywords_found"],
        )
        db.add(mention)
        results.append(result)

    db.commit()
    summary = analyzer.compute_summary(results)

    # Alert evaluation
    alert_svc = AlertService()
    alerts    = alert_svc.evaluate(brand.name, summary)
    for a in alerts:
        db.add(Alert(brand_id=payload.brand_id, **a))
    db.commit()

    return {"simulated": len(records), "summary": summary, "alerts": len(alerts)}


# ─── Mentions ─────────────────────────────────────────────────────────────────

@app.get("/mentions", tags=["Mentions"])
def get_mentions(
    brand_id: Optional[int] = None,
    sentiment: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    q = db.query(Mention)
    if brand_id:   q = q.filter(Mention.brand_id == brand_id)
    if sentiment:  q = q.filter(Mention.sentiment_label == sentiment)
    if source:     q = q.filter(Mention.source == source)
    total = q.count()
    rows  = q.order_by(Mention.created_at.desc()).offset(offset).limit(limit).all()
    return {
        "total": total,
        "mentions": [
            {
                "id": m.id, "text": m.text, "source": m.source,
                "author": m.author, "sentiment_label": m.sentiment_label,
                "vader_compound": m.vader_compound,
                "textblob_polarity": m.textblob_polarity,
                "confidence": m.confidence, "engagement": m.engagement,
                "created_at": m.created_at, "keywords_found": m.keywords_found,
            }
            for m in rows
        ],
    }


@app.get("/mentions/summary/{brand_id}", tags=["Mentions"])
def mention_summary(brand_id: int, db: Session = Depends(get_db)):
    analyzer = get_analyzer()
    mentions = db.query(Mention).filter(Mention.brand_id == brand_id).all()
    results  = [{"sentiment_label": m.sentiment_label,
                 "vader_compound": m.vader_compound,
                 "textblob_subjectivity": m.textblob_subjectivity} for m in mentions]
    return analyzer.compute_summary(results)


# ─── Alerts ───────────────────────────────────────────────────────────────────

@app.get("/alerts", tags=["Alerts"])
def get_alerts(brand_id: Optional[int] = None, unread_only: bool = False,
               db: Session = Depends(get_db)):
    q = db.query(Alert)
    if brand_id:   q = q.filter(Alert.brand_id == brand_id)
    if unread_only: q = q.filter(Alert.is_read == False)
    rows = q.order_by(Alert.created_at.desc()).limit(50).all()
    return [{"id": a.id, "alert_type": a.alert_type, "message": a.message,
             "severity": a.severity, "is_read": a.is_read,
             "created_at": a.created_at} for a in rows]


@app.patch("/alerts/{alert_id}/read", tags=["Alerts"])
def mark_alert_read(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(404, "Alert not found")
    alert.is_read = True
    db.commit()
    return {"message": "Alert marked as read"}


# ─── Reports ──────────────────────────────────────────────────────────────────

@app.post("/reports/generate/{brand_id}", tags=["Reports"])
def generate_report(brand_id: int, period: str = "Last 30 Days",
                    db: Session = Depends(get_db)):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(404, "Brand not found")

    analyzer = get_analyzer()
    mentions = db.query(Mention).filter(Mention.brand_id == brand_id).all()
    results  = [{"sentiment_label": m.sentiment_label,
                 "vader_compound":  m.vader_compound,
                 "textblob_subjectivity": m.textblob_subjectivity} for m in mentions]
    summary  = analyzer.compute_summary(results)

    top_mentions = [
        {"text": m.text, "sentiment_label": m.sentiment_label,
         "vader_compound": m.vader_compound, "source": m.source}
        for m in sorted(mentions, key=lambda x: abs(x.vader_compound), reverse=True)[:10]
    ]

    reporter = get_reporter()
    path = reporter.generate_brand_report(brand.name, summary,
                                          results, period, top_mentions)

    # Save record
    report = Report(brand_id=brand_id, title=f"{brand.name} – {period} Report",
                    report_type="custom", file_path=path)
    db.add(report); db.commit()

    return {"report_id": report.id, "file_path": path, "summary": summary}


@app.get("/reports/download/{report_id}", tags=["Reports"])
def download_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(404, "Report not found")
    return FileResponse(report.file_path, media_type="application/pdf",
                        filename=f"brand_report_{report_id}.pdf")
