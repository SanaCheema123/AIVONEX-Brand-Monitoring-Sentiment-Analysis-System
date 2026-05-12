"""
AIVONEX – Brand Monitoring System
PDF Report Generator (ReportLab)
"""

import os
from datetime import datetime
from typing import Optional
from loguru import logger

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "../../reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

# Brand colors
GREEN  = colors.HexColor("#00FF88")
DARK   = colors.HexColor("#0A0A0A")
GRAY   = colors.HexColor("#1A1A2E")
LGRAY  = colors.HexColor("#8B8B9B")
WHITE  = colors.white
RED    = colors.HexColor("#FF4444")
YELLOW = colors.HexColor("#FFD700")


class ReportGenerator:

    def generate_brand_report(
        self,
        brand_name: str,
        summary: dict,
        mentions: list[dict],
        period: str = "Last 30 Days",
        top_mentions: Optional[list] = None,
    ) -> str:
        """
        Generate a full PDF brand sentiment report.
        Returns the file path.
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_name = brand_name.replace(" ", "_")
        filename  = f"brand_report_{safe_name}_{timestamp}.pdf"
        filepath  = os.path.join(REPORTS_DIR, filename)

        doc = SimpleDocTemplate(
            filepath, pagesize=A4,
            rightMargin=2*cm, leftMargin=2*cm,
            topMargin=2*cm, bottomMargin=2*cm,
        )

        styles = getSampleStyleSheet()
        story  = []

        # ── Header ────────────────────────────────────────────────────────────
        story.append(Paragraph(
            "AIVONEX",
            ParagraphStyle("co", fontName="Helvetica-Bold", fontSize=10,
                           textColor=GREEN, alignment=TA_RIGHT)
        ))
        story.append(Paragraph(
            "Managed Data Intelligence & AI/ML Services",
            ParagraphStyle("sub", fontName="Helvetica", fontSize=8,
                           textColor=LGRAY, alignment=TA_RIGHT)
        ))
        story.append(Spacer(1, 0.5*cm))
        story.append(HRFlowable(width="100%", thickness=1, color=GREEN))
        story.append(Spacer(1, 0.5*cm))

        story.append(Paragraph(
            f"Brand Sentiment Report",
            ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=24,
                           textColor=DARK)
        ))
        story.append(Paragraph(
            f"<b>Brand:</b> {brand_name} &nbsp;&nbsp; <b>Period:</b> {period}",
            ParagraphStyle("meta", fontName="Helvetica", fontSize=11,
                           textColor=LGRAY, spaceBefore=6)
        ))
        story.append(Paragraph(
            f"<b>Generated:</b> {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')}",
            ParagraphStyle("meta2", fontName="Helvetica", fontSize=9,
                           textColor=LGRAY)
        ))
        story.append(Spacer(1, 0.8*cm))

        # ── KPI Summary Table ─────────────────────────────────────────────────
        story.append(Paragraph(
            "Executive Summary",
            ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=14,
                           textColor=DARK, spaceBefore=8, spaceAfter=6)
        ))

        health = summary.get("brand_health_score", 0)
        health_color = GREEN if health >= 60 else (YELLOW if health >= 40 else RED)

        kpi_data = [
            ["Metric", "Value", "Metric", "Value"],
            ["Total Mentions",        str(summary.get("total_mentions", 0)),
             "Brand Health Score",    f"{health}/100"],
            ["Positive Mentions",     f"{summary.get('positive_count', 0)} ({summary.get('positive_pct', 0)}%)",
             "Average Sentiment",     str(summary.get("avg_compound", 0))],
            ["Negative Mentions",     f"{summary.get('negative_count', 0)} ({summary.get('negative_pct', 0)}%)",
             "Avg Subjectivity",      str(summary.get("avg_subjectivity", 0))],
            ["Neutral Mentions",      f"{summary.get('neutral_count', 0)} ({summary.get('neutral_pct', 0)}%)",
             "Analysis Model",        "VADER + TextBlob"],
        ]

        kpi_table = Table(kpi_data, colWidths=[4.5*cm, 4.5*cm, 4.5*cm, 4.5*cm])
        kpi_table.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, 0),  DARK),
            ("TEXTCOLOR",    (0, 0), (-1, 0),  GREEN),
            ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",     (0, 0), (-1, 0),  10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F8F8")]),
            ("FONTNAME",     (0, 1), (0, -1),  "Helvetica-Bold"),
            ("FONTNAME",     (2, 1), (2, -1),  "Helvetica-Bold"),
            ("FONTSIZE",     (0, 1), (-1, -1), 9),
            ("ALIGN",        (0, 0), (-1, -1), "LEFT"),
            ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
            ("GRID",         (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),
            ("PADDING",      (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 0), (-1, 0), [DARK]),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 0.8*cm))

        # ── Sentiment Distribution ────────────────────────────────────────────
        story.append(Paragraph(
            "Sentiment Distribution",
            ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=14,
                           textColor=DARK, spaceBefore=8, spaceAfter=6)
        ))

        sent_data = [
            ["Sentiment", "Count", "Percentage", "Indicator"],
            ["Positive", str(summary.get("positive_count", 0)),
             f"{summary.get('positive_pct', 0)}%", "🟢"],
            ["Negative", str(summary.get("negative_count", 0)),
             f"{summary.get('negative_pct', 0)}%", "🔴"],
            ["Neutral",  str(summary.get("neutral_count", 0)),
             f"{summary.get('neutral_pct', 0)}%", "⚪"],
        ]
        sent_table = Table(sent_data, colWidths=[4.5*cm, 3*cm, 4*cm, 3*cm])
        sent_table.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (-1, 0),  DARK),
            ("TEXTCOLOR",   (0, 0), (-1, 0),  GREEN),
            ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("BACKGROUND",  (0, 1), (-1, 1),  colors.HexColor("#E8FFF3")),
            ("BACKGROUND",  (0, 2), (-1, 2),  colors.HexColor("#FFF0F0")),
            ("BACKGROUND",  (0, 3), (-1, 3),  colors.HexColor("#F5F5F5")),
            ("FONTSIZE",    (0, 0), (-1, -1), 10),
            ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),
            ("PADDING",     (0, 0), (-1, -1), 10),
            ("ALIGN",       (1, 0), (-1, -1), "CENTER"),
        ]))
        story.append(sent_table)
        story.append(Spacer(1, 0.8*cm))

        # ── Top Mentions ──────────────────────────────────────────────────────
        if top_mentions:
            story.append(Paragraph(
                "Top Mentions",
                ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=14,
                               textColor=DARK, spaceBefore=8, spaceAfter=6)
            ))

            for i, m in enumerate(top_mentions[:8], 1):
                label  = m.get("sentiment_label", "neutral")
                score  = m.get("vader_compound", 0)
                source = m.get("source", "unknown")
                text   = m.get("text", "")[:200]

                lcolor = "#2ECC71" if label == "positive" else ("#E74C3C" if label == "negative" else "#95A5A6")

                mention_data = [
                    [f"#{i}  [{label.upper()}]  Score: {score}  |  Source: {source}"],
                    [text],
                ]
                mt = Table(mention_data, colWidths=[17*cm])
                mt.setStyle(TableStyle([
                    ("BACKGROUND",  (0, 0), (-1, 0),  colors.HexColor(lcolor + "22")),
                    ("TEXTCOLOR",   (0, 0), (-1, 0),  colors.HexColor(lcolor)),
                    ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
                    ("FONTSIZE",    (0, 0), (-1, 0),  9),
                    ("BACKGROUND",  (0, 1), (-1, 1),  colors.HexColor("#FAFAFA")),
                    ("FONTSIZE",    (0, 1), (-1, 1),  8),
                    ("FONTNAME",    (0, 1), (-1, 1),  "Helvetica"),
                    ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),
                    ("PADDING",     (0, 0), (-1, -1), 8),
                ]))
                story.append(mt)
                story.append(Spacer(1, 0.2*cm))

        story.append(Spacer(1, 0.8*cm))

        # ── Footer ────────────────────────────────────────────────────────────
        story.append(HRFlowable(width="100%", thickness=1, color=GREEN))
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph(
            "Confidential | Generated by AIVONEX Brand Monitoring System | www.aivonex.com",
            ParagraphStyle("footer", fontName="Helvetica", fontSize=7,
                           textColor=LGRAY, alignment=TA_CENTER)
        ))

        doc.build(story)
        logger.info(f"Report saved → {filepath}")
        return filepath


_reporter: Optional[ReportGenerator] = None


def get_reporter() -> ReportGenerator:
    global _reporter
    if _reporter is None:
        _reporter = ReportGenerator()
    return _reporter
