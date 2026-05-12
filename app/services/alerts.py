"""
AIVONEX – Brand Monitoring System
Alert Engine – detects spikes, sentiment drops, negative surges
"""

from datetime import datetime, timedelta
from typing import Optional
from loguru import logger


class AlertService:

    # Thresholds (configurable)
    NEGATIVE_SURGE_THRESHOLD = 0.50      # >50% negative → alert
    SENTIMENT_DROP_THRESHOLD = -0.30     # compound drops below -0.3
    MENTION_SPIKE_MULTIPLIER = 2.5       # 2.5× normal volume
    HEALTH_CRITICAL_THRESHOLD = 35.0     # brand health < 35 → critical

    def evaluate(self, brand_name: str, summary: dict,
                 prev_summary: Optional[dict] = None) -> list[dict]:
        """
        Evaluate current summary vs previous, return list of alert dicts.
        """
        alerts = []
        now = datetime.utcnow().isoformat()

        # ── Negative Surge ────────────────────────────────────────────────────
        neg_pct = summary.get("negative_pct", 0) / 100
        if neg_pct > self.NEGATIVE_SURGE_THRESHOLD:
            severity = "critical" if neg_pct > 0.70 else "high"
            alerts.append({
                "alert_type": "negative_surge",
                "message": (
                    f"⚠️  {brand_name}: {summary['negative_pct']}% of recent mentions "
                    f"are NEGATIVE — exceeds {int(self.NEGATIVE_SURGE_THRESHOLD*100)}% threshold."
                ),
                "severity": severity,
                "created_at": now,
            })

        # ── Brand Health Critical ─────────────────────────────────────────────
        health = summary.get("brand_health_score", 50)
        if health < self.HEALTH_CRITICAL_THRESHOLD:
            alerts.append({
                "alert_type": "sentiment_drop",
                "message": (
                    f"🔴 {brand_name}: Brand Health Score is {health}/100 — "
                    f"critically low. Immediate attention required."
                ),
                "severity": "critical",
                "created_at": now,
            })
        elif health < 45:
            alerts.append({
                "alert_type": "sentiment_drop",
                "message": (
                    f"🟡 {brand_name}: Brand Health Score dropped to {health}/100. "
                    f"Monitor closely."
                ),
                "severity": "medium",
                "created_at": now,
            })

        # ── Mention Volume Spike ──────────────────────────────────────────────
        if prev_summary:
            prev_total = prev_summary.get("total_mentions", 0)
            curr_total = summary.get("total_mentions", 0)
            if prev_total > 0 and curr_total > prev_total * self.MENTION_SPIKE_MULTIPLIER:
                alerts.append({
                    "alert_type": "spike",
                    "message": (
                        f"📈 {brand_name}: Mention volume spiked from {prev_total} → {curr_total} "
                        f"({round(curr_total/prev_total,1)}× normal)."
                    ),
                    "severity": "medium",
                    "created_at": now,
                })

            # Sentiment deterioration
            prev_health = prev_summary.get("brand_health_score", 50)
            if health < prev_health - 15:
                alerts.append({
                    "alert_type": "sentiment_drop",
                    "message": (
                        f"📉 {brand_name}: Brand Health dropped {round(prev_health-health,1)} "
                        f"points ({prev_health} → {health})."
                    ),
                    "severity": "high",
                    "created_at": now,
                })

        logger.info(f"Alert evaluation for '{brand_name}': {len(alerts)} alerts generated")
        return alerts

    def format_severity_emoji(self, severity: str) -> str:
        return {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(severity, "⚪")
