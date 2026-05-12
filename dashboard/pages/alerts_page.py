"""
AIVONEX – Brand Monitoring System
Dashboard Page: Alerts
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from dashboard.components.db_helpers import load_brands, load_alerts, mark_alert_read


def render():
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <h1 style="margin:0;font-size:2rem;font-weight:900;color:#E0E0E0;">
            Alert <span style="color:#00FF88;">Center</span>
        </h1>
        <p style="color:#6B6B80;margin:4px 0 0;font-size:14px;">
            Automated alerts for sentiment spikes, negative surges, and health drops
        </p>
    </div>
    """, unsafe_allow_html=True)

    brands = load_brands()
    brand_map = {"All": None, **{b["name"]: b["id"] for b in brands}}

    f1, f2 = st.columns([2, 1])
    with f1:
        brand_sel = st.selectbox("Filter by Brand", list(brand_map.keys()))
    with f2:
        unread_only = st.checkbox("Unread only", value=False)

    brand_id = brand_map[brand_sel]
    alerts   = load_alerts(brand_id)

    if unread_only:
        alerts = [a for a in alerts if not a["is_read"]]

    unread_count = sum(1 for a in alerts if not a["is_read"])

    # Summary
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Total Alerts", len(alerts))
    with c2: st.metric("Unread",       unread_count)
    with c3:
        critical = sum(1 for a in alerts if a["severity"] == "critical")
        st.metric("Critical", critical)

    st.markdown("---")

    if not alerts:
        st.success("✅ No alerts! Everything looks healthy.")
        return

    SEVERITY_CONFIG = {
        "critical": ("#FF4444", "🔴"),
        "high":     ("#FF8800", "🟠"),
        "medium":   ("#FFD700", "🟡"),
        "low":      ("#00FF88", "🟢"),
    }

    TYPES = {
        "negative_surge": "📉 Negative Surge",
        "sentiment_drop": "⬇️ Sentiment Drop",
        "spike":          "📈 Mention Spike",
        "keyword_hit":    "🎯 Keyword Hit",
    }

    for alert in alerts:
        severity = alert["severity"]
        color, icon = SEVERITY_CONFIG.get(severity, ("#888", "⚪"))
        is_read  = alert["is_read"]
        atype    = TYPES.get(alert["alert_type"], alert["alert_type"])
        bg       = "#0A0A0A" if is_read else "#111118"
        opacity  = "0.5" if is_read else "1.0"

        st.markdown(f"""
        <div style="background:{bg};border:1px solid {color}33;
                    border-left:4px solid {color};border-radius:10px;
                    padding:1rem;margin:0.4rem 0;opacity:{opacity};">
            <div style="display:flex;justify-content:space-between;">
                <span style="font-weight:700;color:{color};font-size:13px;">
                    {icon} {atype.upper()} &nbsp;
                    <span style="background:{color}22;border:1px solid {color}55;
                                 border-radius:20px;padding:1px 8px;font-size:10px">
                        {severity.upper()}
                    </span>
                </span>
                <span style="font-size:11px;color:#6B6B80;">
                    {"✓ READ" if is_read else "● UNREAD"}
                </span>
            </div>
            <p style="margin:6px 0 0;color:#C0C0C0;font-size:13px">
                {alert['message']}
            </p>
        </div>
        """, unsafe_allow_html=True)

        if not is_read:
            if st.button("Mark as Read", key=f"read_{alert['id']}"):
                mark_alert_read(alert["id"])
                st.rerun()
