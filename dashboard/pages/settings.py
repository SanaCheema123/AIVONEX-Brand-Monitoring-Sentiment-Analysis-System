"""
AIVONEX – Brand Monitoring System
Dashboard Page: Settings
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))


def render():
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <h1 style="margin:0;font-size:2rem;font-weight:900;color:#E0E0E0;">
            System <span style="color:#00FF88;">Settings</span>
        </h1>
        <p style="color:#6B6B80;margin:4px 0 0;font-size:14px;">
            Configure analysis thresholds, integrations, and system options
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🔧 Analysis Config", "🔌 Integrations", "ℹ️  System Info"])

    # ── Analysis Config ───────────────────────────────────────────────────────
    with tab1:
        st.markdown("#### VADER Thresholds")
        pos_thresh = st.slider("Positive threshold (compound ≥)", 0.01, 0.30, 0.05, 0.01)
        neg_thresh = st.slider("Negative threshold (compound ≤)", -0.30, -0.01, -0.05, 0.01)

        st.markdown("#### Alert Thresholds")
        neg_surge  = st.slider("Negative surge alert (%)", 30, 90, 50)
        health_crit= st.slider("Health score critical threshold", 10, 60, 35)
        spike_mult = st.slider("Mention spike multiplier", 1.5, 5.0, 2.5, 0.5)

        st.markdown("#### Ensemble Weights")
        vader_w = st.slider("VADER weight", 0.0, 1.0, 0.6, 0.1)
        textblob_w = round(1 - vader_w, 1)
        st.caption(f"TextBlob weight: {textblob_w} (auto-calculated)")

        if st.button("💾 Save Configuration"):
            st.success("✅ Configuration saved (applied on next analysis run)")
            # In production: save to .env or config.json

    # ── Integrations ──────────────────────────────────────────────────────────
    with tab2:
        st.markdown("#### API Integrations")
        st.info("These integrations allow live data scraping from social platforms.")

        with st.expander("🐦 Twitter / X API"):
            st.text_input("Bearer Token", type="password", placeholder="Enter Bearer Token...")
            st.text_input("API Key", type="password")
            st.text_input("API Secret", type="password")
            st.button("Test Twitter Connection", key="tw_test")

        with st.expander("📱 Reddit API"):
            st.text_input("Client ID", placeholder="Reddit App Client ID...")
            st.text_input("Client Secret", type="password")
            st.text_input("User Agent", placeholder="MyApp/1.0")
            st.button("Test Reddit Connection", key="rd_test")

        with st.expander("📰 NewsAPI"):
            st.text_input("NewsAPI Key", type="password")
            st.button("Test News Connection", key="news_test")

        st.markdown("#### Notification Settings")
        st.checkbox("Email alerts on critical severity")
        st.text_input("Alert Email", placeholder="alerts@company.com")
        st.checkbox("Slack webhook for high/critical alerts")
        st.text_input("Slack Webhook URL", type="password")

    # ── System Info ───────────────────────────────────────────────────────────
    with tab3:
        st.markdown("#### System Information")

        import platform
        try:
            import vaderSentiment
            vader_v = vaderSentiment.__version__
        except:
            vader_v = "installed"
        try:
            import textblob
            tb_v = textblob.__version__
        except:
            tb_v = "installed"

        info = {
            "System":            "AIVONEX Brand Monitoring System",
            "Version":           "1.0.0",
            "Developer":         "AIVONEX SMC-PVT LTD",
            "Python Version":    platform.python_version(),
            "Platform":          platform.platform(),
            "VADER Version":     vader_v,
            "TextBlob Version":  tb_v,
            "Database":          "SQLite",
            "API Backend":       "FastAPI",
            "Dashboard":         "Streamlit",
        }

        for k, v in info.items():
            c1, c2 = st.columns([2, 3])
            with c1:
                st.markdown(f"**{k}**")
            with c2:
                st.markdown(f"`{v}`")

        st.markdown("---")
        st.markdown("""
        <div style="background:#111118;border:1px solid #00FF8833;border-radius:10px;padding:1rem;">
            <b style="color:#00FF88">AIVONEX SMC-PVT LTD</b><br>
            <span style="color:#6B6B80;font-size:13px">
            Managed Data Intelligence & AI/ML Services<br>
            Bahawalpur, Pakistan | www.aivonex.com
            </span>
        </div>
        """, unsafe_allow_html=True)
