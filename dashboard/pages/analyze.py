"""
AIVONEX – Brand Monitoring System
Dashboard Page: Analyze Text (Real-time sentiment)
"""

import streamlit as st
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from dashboard.components.db_helpers import load_brands, save_mention
from dashboard.components.charts import sentiment_badge, format_score, CHART_LAYOUT
from app.services.analyzer import get_analyzer


def render():
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <h1 style="margin:0;font-size:2rem;font-weight:900;color:#E0E0E0;">
            Real-time <span style="color:#00FF88;">Sentiment Analysis</span>
        </h1>
        <p style="color:#6B6B80;margin:4px 0 0;font-size:14px;">
            Analyze any text instantly using VADER + TextBlob dual-model engine
        </p>
    </div>
    """, unsafe_allow_html=True)

    brands = load_brands()
    brand_options = {"(No brand – standalone analysis)": None}
    brand_options.update({b["name"]: b["id"] for b in brands})

    # ── Input Panel ───────────────────────────────────────────────────────────
    col_in, col_cfg = st.columns([3, 1])

    with col_cfg:
        brand_sel = st.selectbox("Attach to Brand", list(brand_options.keys()))
        source    = st.selectbox("Source", ["manual", "Twitter", "Reddit",
                                            "LinkedIn", "News", "Review", "Forum"])
        save_flag = st.checkbox("Save to database", value=True)

    with col_in:
        text_input = st.text_area(
            "Enter text to analyze",
            placeholder="Paste a tweet, review, comment, or any text here...",
            height=150,
        )

    analyze_btn = st.button("🔬 Run Sentiment Analysis", use_container_width=True)

    # ── Batch Analysis ────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📦 Batch Analysis (multiple texts)")
    batch_text = st.text_area(
        "Enter one text per line",
        placeholder="Text 1\nText 2\nText 3...",
        height=100,
        key="batch_input",
    )
    batch_btn = st.button("🔬 Analyze All", key="batch_btn")

    # ── Single Analysis ───────────────────────────────────────────────────────
    if analyze_btn and text_input.strip():
        brand_id = brand_options[brand_sel]
        analyzer = get_analyzer()

        brand_keywords = []
        if brand_id:
            brand = next((b for b in brands if b["id"] == brand_id), None)
            if brand:
                brand_keywords = brand.get("keywords", [])

        with st.spinner("Analyzing..."):
            result = analyzer.analyze(text_input, brand_keywords)

            if save_flag and brand_id:
                save_mention(brand_id, text_input, source)

        # ── Result Display ────────────────────────────────────────────────────
        label = result["sentiment_label"]
        compound = result["vader_compound"]

        # Header color
        if label == "positive":
            hdr_color = "#00FF88"; emoji = "🟢"
        elif label == "negative":
            hdr_color = "#FF4444"; emoji = "🔴"
        else:
            hdr_color = "#888888"; emoji = "⚪"

        st.markdown(f"""
        <div style="background:#111118;border:1px solid {hdr_color}33;
                    border-left:4px solid {hdr_color};border-radius:12px;
                    padding:1.5rem;margin:1rem 0;">
            <div style="font-size:1.5rem;font-weight:900;color:{hdr_color}">
                {emoji} {label.upper()}
            </div>
            <div style="color:#6B6B80;font-size:13px;margin-top:4px;">
                Confidence: <b style="color:#E0E0E0">{result['confidence']:.1%}</b>
                &nbsp;|&nbsp; VADER Compound: 
                <b style="color:{hdr_color};font-family:monospace">{compound:+.4f}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Score cards
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("VADER Compound", f"{compound:+.4f}")
        with m2:
            st.metric("Positive Score", f"{result['vader_pos']:.4f}")
        with m3:
            st.metric("Negative Score", f"{result['vader_neg']:.4f}")
        with m4:
            st.metric("TextBlob Polarity", f"{result['textblob_polarity']:+.4f}")

        m5, m6, m7, m8 = st.columns(4)
        with m5:
            st.metric("Neutral Score", f"{result['vader_neu']:.4f}")
        with m6:
            st.metric("Subjectivity", f"{result['textblob_subjectivity']:.4f}")
        with m7:
            st.metric("Word Count", result["word_count"])
        with m8:
            st.metric("Ensemble Score", f"{result['ensemble_score']:+.4f}")

        # Gauge
        score_norm = (compound + 1) / 2 * 100
        gauge_color = hdr_color
        fig = go.Figure(go.Bar(
            x=[result["vader_pos"], result["vader_neu"], result["vader_neg"]],
            y=["Positive", "Neutral", "Negative"],
            orientation="h",
            marker=dict(color=["#00FF88", "#6B6B80", "#FF4444"]),
            text=[f"{v:.3f}" for v in [result["vader_pos"], result["vader_neu"], result["vader_neg"]]],
            textposition="outside",
        ))
        fig.update_layout(**CHART_LAYOUT, title="VADER Component Scores",
                          height=200, xaxis_range=[0, 1])
        st.plotly_chart(fig, use_container_width=True)

        # Keywords
        if result.get("keywords"):
            st.markdown("**🔑 Top Keywords Extracted:**")
            kw_html = "".join(
                f'<span style="background:#1E1E2E;color:#00FF88;border:1px solid #2E2E4E;'
                f'border-radius:6px;padding:3px 10px;margin:3px;font-size:12px;'
                f'display:inline-block">{kw}</span>'
                for kw in result["keywords"]
            )
            st.markdown(kw_html, unsafe_allow_html=True)

        if result.get("keywords_found"):
            st.markdown(f"**🎯 Brand Keywords Matched:** {', '.join(result['keywords_found'])}")

        st.markdown(f"**✏️ Cleaned Text:** *{result['clean_text'][:200]}*")

    # ── Batch Analysis ────────────────────────────────────────────────────────
    if batch_btn and batch_text.strip():
        lines = [l.strip() for l in batch_text.strip().splitlines() if l.strip()]
        analyzer = get_analyzer()

        with st.spinner(f"Analyzing {len(lines)} texts..."):
            results = analyzer.analyze_batch(lines)
            summary = analyzer.compute_summary(results)

        st.success(f"✅ Analyzed {len(lines)} texts")

        # Summary metrics
        b1, b2, b3, b4 = st.columns(4)
        with b1: st.metric("Total", summary["total_mentions"])
        with b2: st.metric("Positive", f"{summary['positive_count']} ({summary['positive_pct']}%)")
        with b3: st.metric("Negative", f"{summary['negative_count']} ({summary['negative_pct']}%)")
        with b4: st.metric("Health Score", f"{summary['brand_health_score']}/100")

        # Results table
        rows = []
        for text, r in zip(lines, results):
            rows.append({
                "Text": text[:80] + "..." if len(text) > 80 else text,
                "Sentiment": r["sentiment_label"].upper(),
                "Compound": f"{r['vader_compound']:+.3f}",
                "Confidence": f"{r['confidence']:.1%}",
                "Subjectivity": f"{r['textblob_subjectivity']:.2f}",
            })

        import pandas as pd
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
