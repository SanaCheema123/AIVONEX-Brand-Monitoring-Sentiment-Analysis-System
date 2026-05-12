"""
AIVONEX – Brand Monitoring System
Dashboard Page: Brands Management
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from dashboard.components.db_helpers import (
    load_brands, create_brand, delete_brand,
    simulate_and_save, clear_mentions, load_mentions
)
from app.services.alerts import AlertService
from dashboard.components.db_helpers import save_alert


INDUSTRY_OPTIONS = [
    "Technology", "E-commerce", "Healthcare", "Finance", "Education",
    "Food & Beverage", "Fashion", "Automotive", "Media & Entertainment",
    "Travel & Hospitality", "Real Estate", "Retail", "Other"
]


def render():
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <h1 style="margin:0;font-size:2rem;font-weight:900;color:#E0E0E0;">
            Brand <span style="color:#00FF88;">Management</span>
        </h1>
        <p style="color:#6B6B80;margin:4px 0 0;font-size:14px;">
            Add, configure, and manage brands for monitoring
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🏷️  Active Brands", "➕ Add New Brand"])

    # ── Active Brands ─────────────────────────────────────────────────────────
    with tab1:
        brands = load_brands()
        if not brands:
            st.info("No brands yet. Use the **Add New Brand** tab to get started.")
        else:
            for brand in brands:
                bid  = brand["id"]
                bname= brand["name"]
                df   = load_mentions(bid)

                with st.expander(f"**{bname}**  |  {brand['industry'] or 'No industry'}  |  {len(df)} mentions"):
                    c1, c2, c3 = st.columns(3)

                    with c1:
                        st.markdown(f"**🏭 Industry:** {brand['industry'] or '—'}")
                        st.markdown(f"**📝 Description:** {brand['description'] or '—'}")
                        st.markdown(f"**🎨 Color:** `{brand['color']}`")

                    with c2:
                        kw = brand.get("keywords", [])
                        st.markdown("**🔑 Tracked Keywords:**")
                        if kw:
                            kw_html = " ".join(
                                f'<span style="background:#1E1E2E;color:#00FF88;border:1px solid #2E2E4E;'
                                f'border-radius:6px;padding:2px 8px;margin:2px;font-size:11px;display:inline-block">'
                                f'{k}</span>'
                                for k in kw
                            )
                            st.markdown(kw_html, unsafe_allow_html=True)
                        else:
                            st.markdown("*No keywords set*")

                    with c3:
                        if not df.empty:
                            pos = (df["sentiment_label"] == "positive").sum()
                            neg = (df["sentiment_label"] == "negative").sum()
                            health = round(((df["vader_compound"].mean() + 1) / 2) * 100, 1)
                            st.metric("Health Score", f"{health}/100")
                            st.metric("Positive / Negative", f"{pos} / {neg}")
                        else:
                            st.markdown("*No data yet*")

                    st.markdown("---")
                    act1, act2, act3 = st.columns(3)

                    with act1:
                        n_sim = st.number_input(f"Simulate n mentions", 10, 500, 50,
                                                key=f"sim_n_{bid}")
                        if st.button(f"⚡ Generate Simulated Data", key=f"sim_{bid}"):
                            count, summary = simulate_and_save(bid, bname, n=int(n_sim))
                            alerts = AlertService().evaluate(bname, summary)
                            for a in alerts:
                                save_alert(bid, a["alert_type"], a["message"], a["severity"])
                            st.success(f"✅ Generated {count} mentions")
                            st.rerun()

                    with act2:
                        if st.button("🗑️  Clear All Mentions", key=f"clear_{bid}"):
                            clear_mentions(bid)
                            st.warning(f"Mentions cleared for {bname}")
                            st.rerun()

                    with act3:
                        if st.button("❌ Remove Brand", key=f"del_{bid}"):
                            delete_brand(bid)
                            st.warning(f"Brand '{bname}' removed")
                            st.rerun()

    # ── Add Brand ─────────────────────────────────────────────────────────────
    with tab2:
        st.markdown("#### Create a New Brand")

        c1, c2 = st.columns(2)
        with c1:
            name  = st.text_input("Brand Name *", placeholder="e.g. Tesla, Notion, Shopify")
        with c2:
            industry = st.selectbox("Industry", INDUSTRY_OPTIONS)

        desc  = st.text_area("Description (optional)",
                              placeholder="Short description of the brand...")

        kw_input = st.text_input(
            "Tracking Keywords (comma-separated)",
            placeholder="e.g. tesla, elon, model3, electric car"
        )

        color_col, _ = st.columns([1, 3])
        with color_col:
            color = st.color_picker("Brand Color", "#00FF88")

        if st.button("➕ Create Brand", use_container_width=True, type="primary"):
            if not name.strip():
                st.error("Brand name is required.")
            else:
                keywords = [k.strip() for k in kw_input.split(",") if k.strip()]
                result = create_brand(name.strip(), keywords, desc, industry, color)
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.success(f"✅ Brand **{name}** created! (ID: {result['id']})")
                    st.rerun()
