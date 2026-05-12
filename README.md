# 📡 AIVONEX Brand Monitoring & Sentiment Analysis System
<img width="1600" height="726" alt="WhatsApp Image 2026-05-07 at 10 32 34 AM" src="https://github.com/user-attachments/assets/5031cf6b-1826-4a76-ac6f-c514899eca0e" />


> **Built by AIVONEX SMC-PVT LTD** — Managed Data Intelligence & AI/ML Services

A full-featured, production-ready **Brand Monitoring System** powered by dual-engine sentiment analysis (VADER + TextBlob). Track brands, analyze mentions, detect alerts, and generate professional PDF reports — all from a sleek dark-mode dashboard.

---

## 🏗️ Architecture

```
brand_monitoring/
├── app/                        ← FastAPI Backend
│   ├── main.py                 ← REST API endpoints
│   ├── database/
│   │   └── db.py               ← SQLAlchemy models + SQLite
│   └── services/
│       ├── analyzer.py         ← VADER + TextBlob sentiment engine
│       ├── ingestion.py        ← CSV parser + simulation engine
│       ├── reporter.py         ← ReportLab PDF generator
│       └── alerts.py           ← Alert detection engine
├── dashboard/                  ← Streamlit Frontend
│   ├── app.py                  ← Main dashboard entry point
│   ├── components/
│   │   ├── charts.py           ← Plotly chart builders
│   │   └── db_helpers.py       ← Dashboard ↔ DB bridge
│   └── pages/
│       ├── overview.py         ← Executive overview + KPIs
│       ├── analyze.py          ← Real-time text analysis
│       ├── csv_import.py       ← Bulk CSV import
│       ├── brands.py           ← Brand management
│       ├── mentions.py         ← Mentions feed + search
│       ├── alerts_page.py      ← Alert center
│       ├── reports.py          ← PDF report generator
│       └── settings.py         ← System configuration
├── data/
│   ├── brand_monitor.db        ← SQLite database (auto-created)
│   └── sample_mentions.csv     ← Sample import data
├── reports/                    ← Generated PDF reports
├── assets/
│   └── aivonex_logo.png        ← Company logo
├── requirements.txt
├── .env.example
├── run.py                      ← Launcher (API + Dashboard)
└── README.md
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys (optional for live scraping)
```

### 3. Launch the System
```bash
# Start both API + Dashboard
python run.py

# Or separately:
python run.py --api-only         # API only → http://localhost:8000
python run.py --dashboard-only   # Dashboard only → http://localhost:8501
```

### 4. Access the System
| Service | URL |
|---------|-----|
| 📊 Dashboard | http://localhost:8501 |
| 🔌 REST API | http://localhost:8000 |
| 📖 API Docs | http://localhost:8000/docs |

---

## ✨ Features

### 🔬 Dual-Engine Sentiment Analysis
| Engine | Type | Strengths |
|--------|------|-----------|
| **VADER** | Rule-based | Social media slang, emoji, punctuation |
| **TextBlob** | Statistical | Polarity + subjectivity scoring |
| **Ensemble** | Weighted (60/40) | Best overall accuracy |

### 📊 Dashboard Pages
| Page | Description |
|------|-------------|
| **Overview** | KPI cards, charts, timeline, health gauge |
| **Analyze Text** | Real-time single/batch sentiment analysis |
| **CSV Import** | Bulk import with column mapping UI |
| **Brands** | Add/manage/simulate brand data |
| **Mentions Feed** | Search, filter, card/table view |
| **Alert Center** | Automated alerts by severity |
| **Reports** | Generate & download PDF reports |
| **Settings** | Configure thresholds & integrations |

### 🔔 Automated Alerts
- **Negative Surge** — >50% negative mentions
- **Sentiment Drop** — Health score drops below threshold
- **Mention Spike** — Volume exceeds 2.5× normal rate
- **Critical Health** — Brand health score < 35/100

### 📄 PDF Reports
- Executive summary with KPI table
- Sentiment distribution breakdown
- Top mentions (positive/negative)
- Professional AIVONEX branding

### 🌐 REST API Endpoints
```
GET    /brands                    → List all brands
POST   /brands                    → Create brand
POST   /analyze/text              → Analyze single text
POST   /analyze/batch             → Analyze multiple texts
POST   /analyze/csv               → Upload and analyze CSV
POST   /analyze/simulate          → Generate demo data
GET    /mentions                  → Get mentions (filterable)
GET    /mentions/summary/{id}     → Brand summary stats
GET    /alerts                    → Get alerts
POST   /reports/generate/{id}     → Generate PDF report
GET    /reports/download/{id}     → Download PDF
```

---

## 📦 Data Sources Supported

| Source | Method |
|--------|--------|
| **CSV Upload** | Bulk import via dashboard |
| **Manual Text** | Direct input via analyze page |
| **Simulated Data** | Built-in demo data generator |
| **Twitter/X** | Configure API keys in .env |
| **Reddit** | Configure API keys in .env |
| **NewsAPI** | Configure API key in .env |

---

## 📊 Metrics Explained

| Metric | Range | Meaning |
|--------|-------|---------|
| VADER Compound | -1 to +1 | Overall sentiment score |
| TextBlob Polarity | -1 to +1 | Statistical sentiment |
| Subjectivity | 0 to 1 | 0=objective, 1=subjective |
| Confidence | 0–100% | How certain the model is |
| Brand Health Score | 0–100 | Overall brand sentiment health |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend API** | FastAPI + Uvicorn |
| **Dashboard** | Streamlit |
| **Sentiment** | VADER + TextBlob + NLTK |
| **Database** | SQLite + SQLAlchemy |
| **Visualization** | Plotly |
| **Reports** | ReportLab |
| **Data Processing** | Pandas + NumPy |

---

## 📄 License
Proprietary — AIVONEX SMC-PVT LTD © 2025. All rights reserved.
