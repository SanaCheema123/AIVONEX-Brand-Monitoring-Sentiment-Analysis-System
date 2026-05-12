"""
AIVONEX – Brand Monitoring System
Dashboard Page: CSV Import
"""

import streamlit as st
import pandas as pd
import io, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from dashboard.components.db_helpers import load_brands, save_mentions_bulk
from app.services.ingestion import get_ingestion_service


def render():
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <h1 style="margin:0;font-size:2rem;font-weight:900;color:#E0E0E0;">
            CSV <span style="color:#00FF88;">Data Import</span>
        </h1>
        <p style="color:#6B6B80;margin:4px 0 0;font-size:14px;">
            Bulk-import mentions from CSV files (social exports, review exports, etc.)
        </p>
    </div>
    """, unsafe_allow_html=True)

    brands = load_brands()
    if not brands:
        st.warning("Please add a brand first from the **🏷️ Brands** page.")
        return

    brand_map = {b["name"]: b["id"] for b in brands}

    # ── Upload Section ────────────────────────────────────────────────────────
    col_l, col_r = st.columns([3, 2])

    with col_l:
        uploaded = st.file_uploader(
            "Upload CSV File",
            type=["csv"],
            help="CSV must contain at least one text column"
        )

    with col_r:
        brand_sel = st.selectbox("Assign to Brand", list(brand_map.keys()))
        brand_id  = brand_map[brand_sel]

    if uploaded:
        content = uploaded.read()
        try:
            df_preview = pd.read_csv(io.BytesIO(content))
        except Exception as e:
            st.error(f"Could not read CSV: {e}")
            return

        st.markdown("#### 👁️ Preview (first 5 rows)")
        st.dataframe(df_preview.head(), use_container_width=True)

        st.markdown("#### ⚙️ Column Mapping")
        cols = list(df_preview.columns)
        default_text = next(
            (c for c in cols if any(k in c.lower() for k in ["text", "content", "review", "post", "comment"])),
            cols[0]
        )

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            text_col   = st.selectbox("Text Column *", cols,
                                       index=cols.index(default_text))
        with c2:
            source_col = st.selectbox("Source Column (optional)",
                                       ["(none)"] + cols)
        with c3:
            author_col = st.selectbox("Author Column (optional)",
                                       ["(none)"] + cols)
        with c4:
            engage_col = st.selectbox("Engagement Column (optional)",
                                       ["(none)"] + cols)

        source_col = None if source_col == "(none)" else source_col
        author_col = None if author_col == "(none)" else author_col
        engage_col = None if engage_col == "(none)" else engage_col

        st.markdown("---")
        st.markdown(f"**Total rows found:** {len(df_preview):,}  |  "
                    f"**Text column:** `{text_col}`")

        if st.button("🚀 Import & Analyze All Rows", use_container_width=True):
            ingestion = get_ingestion_service()

            with st.spinner("Parsing and analyzing... please wait"):
                records = []
                for _, row in df_preview.iterrows():
                    text = str(row.get(text_col, "")).strip()
                    if not text or text.lower() in ("nan", ""):
                        continue
                    rec = {
                        "text":       text,
                        "source":     str(row[source_col]) if source_col and source_col in row else "CSV",
                        "author":     str(row[author_col]) if author_col and author_col in row else "unknown",
                        "engagement": int(row[engage_col]) if engage_col and engage_col in row else 0,
                    }
                    records.append(rec)

                if not records:
                    st.error("No valid text rows found in the file.")
                    return

                count, summary = save_mentions_bulk(brand_id, records)

            st.success(f"✅ Imported and analyzed **{count}** mentions for **{brand_sel}**")

            # Summary
            m1, m2, m3, m4 = st.columns(4)
            with m1: st.metric("Positive", f"{summary['positive_count']} ({summary['positive_pct']}%)")
            with m2: st.metric("Negative", f"{summary['negative_count']} ({summary['negative_pct']}%)")
            with m3: st.metric("Neutral",  f"{summary['neutral_count']} ({summary['neutral_pct']}%)")
            with m4: st.metric("Health Score", f"{summary['brand_health_score']}/100")

    # ── Sample CSV Download ───────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📥 Download Sample CSV Template")

    sample_df = pd.DataFrame({
        "text": [
            "This product is absolutely amazing, highly recommend!",
            "Very disappointed with the service, will not buy again.",
            "Decent product, nothing special but works as expected.",
            "The customer support team resolved my issue instantly!",
            "Product quality has gone down significantly recently.",
        ],
        "source": ["Twitter", "Reddit", "Review Site", "LinkedIn", "Forum"],
        "author": ["user_a", "user_b", "user_c", "user_d", "user_e"],
        "engagement": [250, 45, 12, 180, 30],
    })

    csv_bytes = sample_df.to_csv(index=False).encode()
    st.download_button(
        "⬇️ Download sample_template.csv",
        data=csv_bytes,
        file_name="sample_mentions_template.csv",
        mime="text/csv",
    )
    st.dataframe(sample_df, use_container_width=True, hide_index=True)
