"""
AIVONEX – Brand Monitoring System
Dashboard Page: Mentions Feed
"""

import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from dashboard.components.db_helpers import load_brands, load_mentions
from dashboard.components.charts import sentiment_badge, format_score


def render():
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <h1 style="margin:0;font-size:2rem;font-weight:900;color:#E0E0E0;">
            Mentions <span style="color:#00FF88;">Feed</span>
        </h1>
        <p style="color:#6B6B80;margin:4px 0 0;font-size:14px;">
            Browse, filter, and explore all captured brand mentions
        </p>
    </div>
    """, unsafe_allow_html=True)

    brands = load_brands()
    if not brands:
        st.info("No brands found.")
        return

    # ── Filters ───────────────────────────────────────────────────────────────
    brand_map = {"All Brands": None, **{b["name"]: b["id"] for b in brands}}

    f1, f2, f3, f4 = st.columns(4)
    with f1:
        brand_sel = st.selectbox("Brand", list(brand_map.keys()))
    with f2:
        sent_filter = st.selectbox("Sentiment", ["All", "positive", "negative", "neutral"])
    with f3:
        src_filter = st.selectbox("Source", ["All", "Twitter", "Reddit", "LinkedIn",
                                             "News", "CSV", "manual", "Forum"])
    with f4:
        limit = st.selectbox("Show", [50, 100, 200, 500], index=1)

    brand_id = brand_map[brand_sel]
    df = load_mentions(brand_id, limit=limit)

    if df.empty:
        st.warning("No mentions found with the selected filters.")
        return

    # Apply filters
    if sent_filter != "All":
        df = df[df["sentiment_label"] == sent_filter]
    if src_filter != "All":
        df = df[df["source"] == src_filter]

    # ── Summary bar ───────────────────────────────────────────────────────────
    if not df.empty:
        pos = (df["sentiment_label"] == "positive").sum()
        neg = (df["sentiment_label"] == "negative").sum()
        neu = (df["sentiment_label"] == "neutral").sum()

        b1, b2, b3, b4 = st.columns(4)
        with b1: st.metric("Showing", len(df))
        with b2: st.metric("Positive", pos)
        with b3: st.metric("Negative", neg)
        with b4: st.metric("Neutral", neu)

    st.markdown("---")

    # ── Search ────────────────────────────────────────────────────────────────
    search = st.text_input("🔍 Search mentions", placeholder="Type to filter by text...")
    if search:
        df = df[df["text"].str.contains(search, case=False, na=False)]
        st.caption(f"{len(df)} results for '{search}'")

    # ── Card view ─────────────────────────────────────────────────────────────
    view_mode = st.radio("View Mode", ["📋 Table", "🃏 Cards"], horizontal=True)

    if view_mode == "📋 Table":
        display = df[["sentiment_label", "vader_compound", "confidence",
                       "source", "author", "engagement", "text", "created_at"]].copy()
        display.columns = ["Sentiment", "Score", "Confidence", "Source",
                           "Author", "Engagement", "Text", "Created"]
        display["Text"] = display["Text"].str[:120] + "..."
        display["Created"] = pd.to_datetime(display["Created"]).dt.strftime("%Y-%m-%d %H:%M")
        st.dataframe(display, use_container_width=True, hide_index=True)

    else:
        # Card view
        for _, row in df.head(50).iterrows():
            label    = row["sentiment_label"]
            compound = row["vader_compound"]
            text     = row["text"]
            source   = row["source"]
            author   = row["author"]
            engage   = row["engagement"]
            conf     = row["confidence"]

            if label == "positive":
                border = "#00FF88"; icon = "🟢"
            elif label == "negative":
                border = "#FF4444"; icon = "🔴"
            else:
                border = "#444"; icon = "⚪"

            st.markdown(f"""
            <div style="background:#111118;border:1px solid {border}33;
                        border-left:4px solid {border};border-radius:10px;
                        padding:1rem;margin:0.5rem 0;">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                    <div style="flex:1">
                        <span style="color:#6B6B80;font-size:12px;">
                            {icon} <b style="color:#E0E0E0">{label.upper()}</b>
                            &nbsp;|&nbsp; Score: <b style="color:{border};font-family:monospace">{compound:+.3f}</b>
                            &nbsp;|&nbsp; Confidence: {conf:.0%}
                        </span>
                        <p style="margin:8px 0 0;color:#C0C0C0;font-size:14px;line-height:1.5">
                            {text[:300]}{"..." if len(text) > 300 else ""}
                        </p>
                    </div>
                </div>
                <div style="margin-top:8px;font-size:11px;color:#6B6B80;">
                    📡 {source} &nbsp;|&nbsp; 👤 {author} &nbsp;|&nbsp; ❤️ {engage:,}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Export ────────────────────────────────────────────────────────────────
    st.markdown("---")
    csv_data = df.to_csv(index=False).encode()
    st.download_button(
        "⬇️ Export Filtered Data as CSV",
        data=csv_data,
        file_name="mentions_export.csv",
        mime="text/csv",
    )
