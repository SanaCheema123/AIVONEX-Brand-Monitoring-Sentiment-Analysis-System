"""
AIVONEX – Brand Monitoring System
Dashboard Page: PDF Reports
"""

import streamlit as st
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from dashboard.components.db_helpers import (
    load_brands, load_mentions, load_reports, save_report
)
from app.services.analyzer import get_analyzer
from app.services.reporter import get_reporter


def render():
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <h1 style="margin:0;font-size:2rem;font-weight:900;color:#E0E0E0;">
            PDF <span style="color:#00FF88;">Reports</span>
        </h1>
        <p style="color:#6B6B80;margin:4px 0 0;font-size:14px;">
            Generate and download professional brand sentiment reports
        </p>
    </div>
    """, unsafe_allow_html=True)

    brands = load_brands()
    if not brands:
        st.warning("Add a brand first before generating reports.")
        return

    brand_map = {b["name"]: b["id"] for b in brands}

    tab1, tab2 = st.tabs(["📄 Generate Report", "📁 Report History"])

    with tab1:
        st.markdown("#### Configure Report")

        c1, c2, c3 = st.columns(3)
        with c1:
            brand_sel = st.selectbox("Brand", list(brand_map.keys()))
        with c2:
            period = st.selectbox("Period", [
                "Last 7 Days", "Last 30 Days", "Last 90 Days",
                "Last 6 Months", "All Time"
            ])
        with c3:
            report_type = st.selectbox("Report Type", ["custom", "weekly", "monthly"])

        brand_id = brand_map[brand_sel]
        df = load_mentions(brand_id)

        if df.empty:
            st.warning(f"No mentions found for **{brand_sel}**. Please add data first.")
            return

        # Stats preview
        analyzer = get_analyzer()
        results  = df[["sentiment_label", "vader_compound", "textblob_subjectivity"]].to_dict("records")
        summary  = analyzer.compute_summary(results)

        st.markdown("#### Preview Stats")
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("Total Mentions",  summary.get("total_mentions", 0))
        with m2: st.metric("Positive",        f"{summary.get('positive_pct', 0)}%")
        with m3: st.metric("Negative",        f"{summary.get('negative_pct', 0)}%")
        with m4: st.metric("Health Score",    f"{summary.get('brand_health_score', 0)}/100")

        if st.button("🖨️  Generate PDF Report", use_container_width=True, type="primary"):
            top_mentions = [
                {"text": row["text"], "sentiment_label": row["sentiment_label"],
                 "vader_compound": row["vader_compound"], "source": row["source"]}
                for _, row in df.nlargest(10, "vader_compound").iterrows()
            ]

            reporter = get_reporter()
            with st.spinner("Generating PDF report..."):
                path = reporter.generate_brand_report(
                    brand_sel, summary, results, period, top_mentions
                )

            save_report(brand_id, f"{brand_sel} – {period}", report_type, path)

            # Download
            with open(path, "rb") as f:
                pdf_bytes = f.read()

            st.success("✅ Report generated successfully!")
            st.download_button(
                "⬇️ Download PDF Report",
                data=pdf_bytes,
                file_name=f"brand_report_{brand_sel.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

    with tab2:
        st.markdown("#### Previous Reports")
        reports = load_reports()

        if not reports:
            st.info("No reports generated yet.")
            return

        brand_name_map = {b["id"]: b["name"] for b in brands}

        for r in reports:
            bname = brand_name_map.get(r["brand_id"], "Unknown Brand")
            exists = os.path.exists(r["file_path"]) if r["file_path"] else False

            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"""
                <div style="background:#111118;border:1px solid #1E1E2E;border-radius:8px;padding:0.8rem;">
                    <b style="color:#E0E0E0">{r['title']}</b><br>
                    <span style="font-size:12px;color:#6B6B80">
                        🏷️ {bname} &nbsp;|&nbsp; 📅 {str(r['created_at'])[:16]}
                        &nbsp;|&nbsp; {"✅ Available" if exists else "❌ File missing"}
                    </span>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                if exists:
                    with open(r["file_path"], "rb") as f:
                        st.download_button(
                            "⬇️ Download",
                            data=f.read(),
                            file_name=f"report_{r['id']}.pdf",
                            mime="application/pdf",
                            key=f"dl_{r['id']}",
                        )
                else:
                    st.button("Unavailable", key=f"na_{r['id']}", disabled=True)
