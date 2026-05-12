"""
AIVONEX – Brand Monitoring System
Dashboard Page: Overview (Premium v2)
"""

import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from dashboard.components.db_helpers import load_brands, load_mentions, load_alerts, simulate_and_save, save_alert
from dashboard.components.charts import sentiment_donut, sentiment_timeline, health_gauge, compound_histogram, source_bar, engagement_scatter
from app.services.analyzer import get_analyzer
from app.services.alerts import AlertService


def stat_card(icon, label, value, sub, accent="#00FF88", icon_bg="rgba(0,255,136,0.1)"):
    return f"""
    <div style="background:#0D1321;border:1px solid rgba(255,255,255,0.055);
                border-radius:18px;padding:1.4rem 1.5rem;position:relative;
                overflow:hidden;transition:all .3s;height:100%">
        <div style="position:absolute;top:0;left:15%;right:15%;height:1px;
                    background:linear-gradient(90deg,transparent,{accent}80,transparent)"></div>
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:.8rem">
            <div style="width:38px;height:38px;background:{icon_bg};border-radius:10px;
                        display:flex;align-items:center;justify-content:center;font-size:17px">
                {icon}
            </div>
            <div style="font-size:9px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;
                        color:#2D3748;font-family:'Sora',sans-serif;margin-top:4px">
                {label}
            </div>
        </div>
        <div style="font-family:'Sora',sans-serif;font-size:2rem;font-weight:800;
                    color:#fff;letter-spacing:-.04em;line-height:1;margin-bottom:.35rem">
            {value}
        </div>
        <div style="font-family:'Inter',sans-serif;font-size:.72rem;color:#4A5568">
            {sub}
        </div>
    </div>"""


def section_header(title, subtitle=""):
    st.markdown(f"""
    <div style="margin:1.8rem 0 .9rem">
        <div style="font-family:'Sora',sans-serif;font-size:1rem;font-weight:700;
                    color:#EDF2F7;letter-spacing:-.01em">{title}</div>
        {f'<div style="font-family:Inter,sans-serif;font-size:.78rem;color:#4A5568;margin-top:2px">{subtitle}</div>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def chart_card(fig, title="", height=340):
    st.markdown(f"""
    <div style="background:#0D1321;border:1px solid rgba(255,255,255,0.055);
                border-radius:18px;padding:1.2rem 1.4rem .5rem;margin-bottom:0">
        {f'<div style="font-family:Sora,sans-serif;font-size:.78rem;font-weight:600;color:#718096;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.6rem">{title}</div>' if title else ''}
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)


def render():
    # ── Page header ───────────────────────────────────────────────────────────
    st.markdown("""
    <div style="margin-bottom:1.8rem;animation:fadeUp .4s ease">
        <div style="font-family:'Sora',sans-serif;font-size:1.8rem;font-weight:800;
                    color:#EDF2F7;letter-spacing:-.04em;line-height:1.1">
            Brand Intelligence <span style="color:#00FF88">Overview</span>
        </div>
        <div style="font-family:'Inter',sans-serif;font-size:.84rem;color:#4A5568;margin-top:.35rem">
            Real-time sentiment monitoring across all tracked brands
        </div>
    </div>
    """, unsafe_allow_html=True)

    brands = load_brands()
    if not brands:
        st.markdown("""
        <div style="background:#0D1321;border:1px solid rgba(0,255,136,0.15);border-radius:18px;
                    padding:3rem 2rem;text-align:center;margin-top:2rem">
            <div style="font-size:3rem;margin-bottom:1rem">📡</div>
            <div style="font-family:'Sora',sans-serif;font-size:1.1rem;font-weight:700;color:#EDF2F7;margin-bottom:.5rem">
                No Brands Tracked Yet
            </div>
            <div style="font-family:'Inter',sans-serif;font-size:.84rem;color:#4A5568">
                Go to <b style="color:#00FF88">Brands</b> to add your first brand and start monitoring
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Brand selector ─────────────────────────────────────────────────────────
    brand_names = [b["name"] for b in brands]
    brand_ids   = {b["name"]: b["id"] for b in brands}

    col_sel, col_ref = st.columns([5, 1])
    with col_sel:
        sel = st.selectbox("Select Brand", brand_names, key="overview_brand", label_visibility="collapsed")
    with col_ref:
        if st.button("⟳ Refresh", use_container_width=True):
            st.rerun()

    brand_id = brand_ids[sel]
    df = load_mentions(brand_id)

    if df.empty:
        st.markdown(f"""
        <div style="background:#0D1321;border:1px dashed rgba(0,255,136,0.2);border-radius:18px;
                    padding:2.5rem 2rem;text-align:center;margin-top:1.5rem">
            <div style="font-size:2.5rem;margin-bottom:.8rem">🔍</div>
            <div style="font-family:'Sora',sans-serif;font-size:.95rem;font-weight:700;
                        color:#EDF2F7;margin-bottom:.4rem">
                No Data for <span style="color:#00FF88">{sel}</span>
            </div>
            <div style="font-family:'Inter',sans-serif;font-size:.8rem;color:#4A5568">
                Use Analyze Text, CSV Import, or generate simulated data below
            </div>
        </div>
        """, unsafe_allow_html=True)
        _simulate_cta(brand_id, sel)
        return

    # ── Compute summary ────────────────────────────────────────────────────────
    analyzer = get_analyzer()
    results  = df[["sentiment_label", "vader_compound", "textblob_subjectivity"]].to_dict("records")
    summary  = analyzer.compute_summary(results)

    pos   = summary.get("positive_count", 0)
    neg   = summary.get("negative_count", 0)
    neu   = summary.get("neutral_count", 0)
    total = summary.get("total_mentions", 0)
    health= summary.get("brand_health_score", 0)
    avg_c = summary.get("avg_compound", 0)
    pos_p = summary.get("positive_pct", 0)
    neg_p = summary.get("negative_pct", 0)

    unread = len([a for a in load_alerts(brand_id) if not a["is_read"]])

    health_color = "#00FF88" if health >= 60 else ("#F6C453" if health >= 40 else "#FC4E6E")
    score_color  = "#00FF88" if avg_c > 0.05 else ("#FC4E6E" if avg_c < -0.05 else "#718096")

    # ── KPI stat cards ─────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    cards = [
        (c1, "📊", "Total Mentions", f"{total:,}",
         f"All time • brand activity", "#5B9EFF", "rgba(91,158,255,0.1)"),
        (c2, "🟢", "Positive",       f"{pos:,}",
         f"{pos_p}% of all mentions", "#00FF88", "rgba(0,255,136,0.1)"),
        (c3, "🔴", "Negative",       f"{neg:,}",
         f"{neg_p}% of all mentions", "#FC4E6E", "rgba(252,78,110,0.1)"),
        (c4, "💓", "Health Score",   f"{health:.0f}",
         f"Out of 100 • brand pulse", health_color, f"rgba(0,255,136,0.08)"),
        (c5, "🔔", "Alerts",         f"{unread}",
         "Unread notifications", "#F6C453" if unread else "#718096",
         "rgba(246,196,83,0.1)" if unread else "rgba(113,128,150,0.07)"),
    ]
    for col, icon, label, value, sub, accent, ibg in cards:
        with col:
            st.markdown(stat_card(icon, label, value, sub, accent, ibg), unsafe_allow_html=True)

    # ── Avg sentiment pill ─────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="display:flex;gap:10px;align-items:center;margin:1.2rem 0 .2rem;flex-wrap:wrap">
        <div style="background:#0D1321;border:1px solid rgba(255,255,255,0.06);
                    border-radius:30px;padding:.38rem 1rem;display:flex;align-items:center;gap:8px">
            <span style="font-size:11px;color:#718096;font-family:'Sora',sans-serif;
                         font-weight:600;text-transform:uppercase;letter-spacing:.1em">Avg Sentiment</span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:.9rem;
                         font-weight:600;color:{score_color}">{avg_c:+.4f}</span>
        </div>
        <div style="background:#0D1321;border:1px solid rgba(255,255,255,0.06);
                    border-radius:30px;padding:.38rem 1rem;display:flex;align-items:center;gap:8px">
            <span style="font-size:11px;color:#718096;font-family:'Sora',sans-serif;
                         font-weight:600;text-transform:uppercase;letter-spacing:.1em">Neutral</span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:.9rem;
                         font-weight:600;color:#718096">{neu}</span>
        </div>
        <div style="background:#0D1321;border:1px solid rgba(255,255,255,0.06);
                    border-radius:30px;padding:.38rem 1rem;display:flex;align-items:center;gap:8px">
            <span style="font-size:11px;color:#718096;font-family:'Sora',sans-serif;
                         font-weight:600;text-transform:uppercase;letter-spacing:.1em">Brand</span>
            <span style="font-family:'Sora',sans-serif;font-size:.82rem;
                         font-weight:700;color:#00FF88">{sel}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ── Charts Row 1: Donut + Timeline ─────────────────────────────────────────
    section_header("Sentiment Analysis", "Distribution and trend over time")
    c_left, c_right = st.columns([1, 2])

    with c_left:
        st.markdown("""<div style="background:#0D1321;border:1px solid rgba(255,255,255,0.055);
            border-radius:18px;padding:1.2rem 1rem .4rem">
            <div style="font-size:.68rem;font-weight:600;text-transform:uppercase;letter-spacing:.12em;
                color:#4A5568;font-family:'Sora',sans-serif;margin-bottom:.4rem">Distribution</div>
            </div>""", unsafe_allow_html=True)
        st.plotly_chart(sentiment_donut(pos, neg, neu), use_container_width=True)
        # Legend below
        st.markdown(f"""
        <div style="background:#0D1321;border:1px solid rgba(255,255,255,0.05);
                    border-radius:14px;padding:.9rem 1.2rem;margin-top:.4rem">
            <div style="display:flex;justify-content:space-between;margin-bottom:.5rem">
                <div style="display:flex;align-items:center;gap:7px">
                    <div style="width:8px;height:8px;border-radius:50%;background:#00FF88"></div>
                    <span style="font-size:.75rem;color:#718096;font-family:'Inter',sans-serif">Positive</span>
                </div>
                <span style="font-family:'JetBrains Mono',monospace;font-size:.75rem;color:#00FF88;font-weight:600">{pos_p}%</span>
            </div>
            <div style="display:flex;justify-content:space-between;margin-bottom:.5rem">
                <div style="display:flex;align-items:center;gap:7px">
                    <div style="width:8px;height:8px;border-radius:50%;background:#FC4E6E"></div>
                    <span style="font-size:.75rem;color:#718096;font-family:'Inter',sans-serif">Negative</span>
                </div>
                <span style="font-family:'JetBrains Mono',monospace;font-size:.75rem;color:#FC4E6E;font-weight:600">{neg_p}%</span>
            </div>
            <div style="display:flex;justify-content:space-between">
                <div style="display:flex;align-items:center;gap:7px">
                    <div style="width:8px;height:8px;border-radius:50%;background:#4A5568"></div>
                    <span style="font-size:.75rem;color:#718096;font-family:'Inter',sans-serif">Neutral</span>
                </div>
                <span style="font-family:'JetBrains Mono',monospace;font-size:.75rem;color:#718096;font-weight:600">{round(100-pos_p-neg_p,1)}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c_right:
        st.markdown("""<div style="background:#0D1321;border:1px solid rgba(255,255,255,0.055);
            border-radius:18px;padding:1.2rem 1rem .4rem">
            <div style="font-size:.68rem;font-weight:600;text-transform:uppercase;letter-spacing:.12em;
                color:#4A5568;font-family:'Sora',sans-serif;margin-bottom:.4rem">Sentiment Over Time</div>
            </div>""", unsafe_allow_html=True)
        st.plotly_chart(sentiment_timeline(df, sel), use_container_width=True)

    # ── Charts Row 2: Gauge + Histogram + Source ───────────────────────────────
    section_header("Brand Health & Distribution", "Score, score spread, and mention sources")
    c3a, c3b, c3c = st.columns(3)

    with c3a:
        st.markdown("""<div style="background:#0D1321;border:1px solid rgba(255,255,255,0.055);
            border-radius:18px;padding:1.2rem 1rem .2rem">
            <div style="font-size:.68rem;font-weight:600;text-transform:uppercase;letter-spacing:.12em;
                color:#4A5568;font-family:'Sora',sans-serif;margin-bottom:.4rem">Health Gauge</div>
            </div>""", unsafe_allow_html=True)
        st.plotly_chart(health_gauge(health), use_container_width=True)

    with c3b:
        st.markdown("""<div style="background:#0D1321;border:1px solid rgba(255,255,255,0.055);
            border-radius:18px;padding:1.2rem 1rem .4rem">
            <div style="font-size:.68rem;font-weight:600;text-transform:uppercase;letter-spacing:.12em;
                color:#4A5568;font-family:'Sora',sans-serif;margin-bottom:.4rem">Score Distribution</div>
            </div>""", unsafe_allow_html=True)
        st.plotly_chart(compound_histogram(df), use_container_width=True)

    with c3c:
        st.markdown("""<div style="background:#0D1321;border:1px solid rgba(255,255,255,0.055);
            border-radius:18px;padding:1.2rem 1rem .4rem">
            <div style="font-size:.68rem;font-weight:600;text-transform:uppercase;letter-spacing:.12em;
                color:#4A5568;font-family:'Sora',sans-serif;margin-bottom:.4rem">Sources Breakdown</div>
            </div>""", unsafe_allow_html=True)
        st.plotly_chart(source_bar(df), use_container_width=True)

    # ── Recent Mentions ────────────────────────────────────────────────────────
    section_header("Recent Mentions", f"Latest {min(15, len(df))} captured mentions")

    for _, row in df.head(15).iterrows():
        label    = row["sentiment_label"]
        compound = row["vader_compound"]
        text     = row["text"][:220]
        source   = row.get("source", "—")
        author   = row.get("author", "—")
        engage   = row.get("engagement", 0)

        if label == "positive":
            border = "#00FF88"; badge_bg = "rgba(0,255,136,0.08)"; badge_c = "#00FF88"
            dot = "🟢"
        elif label == "negative":
            border = "#FC4E6E"; badge_bg = "rgba(252,78,110,0.08)"; badge_c = "#FC4E6E"
            dot = "🔴"
        else:
            border = "#2D3748"; badge_bg = "rgba(45,55,72,0.5)"; badge_c = "#718096"
            dot = "⚪"

        st.markdown(f"""
        <div style="background:#0D1321;border:1px solid rgba(255,255,255,0.05);
                    border-left:3px solid {border};border-radius:0 14px 14px 0;
                    padding:1rem 1.3rem;margin:.4rem 0;transition:all .2s">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:.5rem;flex-wrap:wrap;gap:.4rem">
                <div style="display:flex;align-items:center;gap:8px">
                    <span style="background:{badge_bg};color:{badge_c};border:1px solid {border}40;
                                 border-radius:20px;padding:2px 10px;font-size:10px;font-weight:700;
                                 font-family:'Sora',sans-serif;letter-spacing:.06em">
                        {dot} {label.upper()}
                    </span>
                    <span style="font-family:'JetBrains Mono',monospace;font-size:.75rem;
                                 color:{border};font-weight:600">{compound:+.3f}</span>
                </div>
                <div style="display:flex;gap:1rem">
                    <span style="font-size:.7rem;color:#2D3748;font-family:'Inter',sans-serif">
                        📡 {source}
                    </span>
                    <span style="font-size:.7rem;color:#2D3748;font-family:'Inter',sans-serif">
                        👤 {author}
                    </span>
                    {f'<span style="font-size:.7rem;color:#2D3748;font-family:Inter,sans-serif">❤️ {engage:,}</span>' if engage else ''}
                </div>
            </div>
            <div style="font-family:'Inter',sans-serif;font-size:.83rem;color:#8B97A8;
                        line-height:1.55">{text}{"…" if len(row["text"]) > 220 else ""}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Simulate CTA ───────────────────────────────────────────────────────────
    st.markdown("---")
    _simulate_cta(brand_id, sel)


def _simulate_cta(brand_id, brand_name):
    st.markdown("""
    <div style="font-family:'Sora',sans-serif;font-size:.8rem;font-weight:700;
                color:#EDF2F7;margin-bottom:.8rem">
        ⚡ Generate Demo Data
    </div>""", unsafe_allow_html=True)
    col_n, col_btn = st.columns([3, 1])
    with col_n:
        n = st.slider("Number of simulated mentions", 20, 300, 50, key="sim_n_ov")
    with col_btn:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button(f"Generate {n}", use_container_width=True, key="sim_btn_ov"):
            from dashboard.components.db_helpers import simulate_and_save, save_alert
            count, summary = simulate_and_save(brand_id, brand_name, n=n)
            alerts = AlertService().evaluate(brand_name, summary)
            for a in alerts:
                save_alert(brand_id, a["alert_type"], a["message"], a["severity"])
            st.success(f"✅ Generated {count} mentions")
            st.rerun()