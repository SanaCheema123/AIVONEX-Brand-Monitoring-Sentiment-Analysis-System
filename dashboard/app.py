"""
AIVONEX – Brand Monitoring System
Streamlit Dashboard — Premium UI v2
"""

import streamlit as st

st.set_page_config(
    page_title="AIVONEX – Brand Monitor",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@300;400;500;600&display=swap');

:root {
    --green:       #00FF88;
    --green-dim:   #00CC6A;
    --green-glow:  rgba(0,255,136,0.18);
    --green-soft:  rgba(0,255,136,0.07);
    --bg:          #07090F;
    --bg2:         #0B0F1A;
    --bg3:         #0F1520;
    --card:        #0D1321;
    --card2:       #111827;
    --border:      rgba(255,255,255,0.055);
    --border-g:    rgba(0,255,136,0.2);
    --text:        #EDF2F7;
    --text2:       #718096;
    --text3:       #2D3748;
    --red:         #FC4E6E;
    --yellow:      #F6C453;
    --blue:        #5B9EFF;
}

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
    background: var(--bg) !important;
    color: var(--text) !important;
}

/* Subtle grid */
.stApp {
    background-image:
        linear-gradient(rgba(0,255,136,0.012) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,136,0.012) 1px, transparent 1px) !important;
    background-size: 52px 52px !important;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebarContent"] { padding: 0 !important; }
[data-testid="stSidebar"] .stButton > button { display: none !important; }

/* Hide Streamlit's auto-generated page navigation (from pages/ folder) */
[data-testid="stSidebarNav"] { display: none !important; }
section[data-testid="stSidebarNav"] { display: none !important; }
.st-emotion-cache-79elbk { display: none !important; }
div[data-testid="stSidebarNavItems"] { display: none !important; }
ul[data-testid="stSidebarNavItems"] { display: none !important; }

/* ── MAIN ── */
.main .block-container {
    padding: 2rem 2.5rem 4rem !important;
    max-width: 100% !important;
}

/* ── METRICS ── */
[data-testid="stMetric"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 18px !important;
    padding: 1.5rem 1.7rem 1.3rem !important;
    position: relative; overflow: hidden;
    transition: all 0.3s cubic-bezier(.4,0,.2,1);
}
[data-testid="stMetric"]:hover {
    border-color: var(--border-g) !important;
    box-shadow: 0 8px 48px var(--green-glow) !important;
    transform: translateY(-3px);
}
[data-testid="stMetric"]::after {
    content:'';position:absolute;top:0;left:15%;right:15%;height:1px;
    background:linear-gradient(90deg,transparent,rgba(0,255,136,0.6),transparent);
}
[data-testid="stMetricValue"] {
    color: #fff !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 2.1rem !important; font-weight: 700 !important;
    letter-spacing: -0.04em !important; line-height: 1.1 !important;
}
[data-testid="stMetricLabel"] {
    color: var(--text2) !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.68rem !important; font-weight: 600 !important;
    text-transform: uppercase !important; letter-spacing: 0.14em !important;
    margin-bottom: 0.2rem !important;
}
[data-testid="stMetricDelta"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.7rem !important; font-weight: 500 !important;
}

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg,#00FF88,#00CC6A) !important;
    color: #000 !important; font-weight: 700 !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.78rem !important; letter-spacing: 0.06em !important;
    border: none !important; border-radius: 10px !important;
    padding: 0.55rem 1.3rem !important;
    transition: all 0.22s !important;
    box-shadow: 0 2px 16px rgba(0,255,136,0.22) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 34px rgba(0,255,136,0.45) !important;
}
.stButton > button:active { transform: translateY(0) scale(0.98) !important; }

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--card) !important; border-radius: 12px !important;
    border: 1px solid var(--border) !important; padding: 4px 6px !important;
}
.stTabs [data-baseweb="tab"] {
    color: var(--text2) !important; font-weight: 500 !important;
    font-family: 'Sora', sans-serif !important; font-size: 0.8rem !important;
    border-radius: 8px !important; padding: 0.42rem 1rem !important;
    transition: all 0.18s !important; border: none !important;
}
.stTabs [aria-selected="true"] {
    background: var(--green-soft) !important;
    color: var(--green) !important;
    border-bottom: 2px solid var(--green) !important;
}

/* ── INPUTS ── */
.stSelectbox > div > div,
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
    background: var(--card) !important; color: var(--text) !important;
    border: 1px solid var(--border) !important; border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important; font-size: 0.86rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stSelectbox > div > div:focus-within,
.stTextInput > div > div:focus-within,
.stTextArea > div > div:focus-within {
    border-color: var(--border-g) !important;
    box-shadow: 0 0 0 3px var(--green-glow) !important;
}
label { color: var(--text2) !important; font-family: 'Sora', sans-serif !important;
    font-size: 0.7rem !important; font-weight: 600 !important;
    text-transform: uppercase !important; letter-spacing: 0.12em !important; }

/* ── SLIDER ── */
.stSlider > div > div > div > div { background: var(--green) !important; }
.stSlider > div > div > div { background: var(--bg3) !important; }

/* ── EXPANDER ── */
.streamlit-expanderHeader {
    background: var(--card) !important; border: 1px solid var(--border) !important;
    border-radius: 12px !important; color: var(--text) !important;
    font-family: 'Sora', sans-serif !important; font-weight: 600 !important;
    font-size: 0.84rem !important;
}
.streamlit-expanderContent {
    background: var(--card2) !important; border: 1px solid var(--border) !important;
    border-top: none !important; border-radius: 0 0 12px 12px !important;
}

/* ── FILE UPLOAD ── */
[data-testid="stFileUploader"] {
    background: var(--card) !important;
    border: 2px dashed var(--border-g) !important;
    border-radius: 16px !important; transition: all 0.2s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--green) !important; background: var(--green-soft) !important;
}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] {
    border-radius: 14px !important; overflow: hidden !important;
    border: 1px solid var(--border) !important;
}

/* ── ALERTS ── */
.stAlert { border-radius: 12px !important; }
[data-testid="stInfo"] { background: rgba(91,158,255,0.05) !important; border: 1px solid rgba(91,158,255,0.18) !important; }
[data-testid="stSuccess"] { background: rgba(0,255,136,0.05) !important; border: 1px solid rgba(0,255,136,0.18) !important; }
[data-testid="stWarning"] { background: rgba(246,196,83,0.05) !important; border: 1px solid rgba(246,196,83,0.18) !important; }
[data-testid="stError"] { background: rgba(252,78,110,0.05) !important; border: 1px solid rgba(252,78,110,0.18) !important; }

/* ── DOWNLOAD ── */
.stDownloadButton > button {
    background: transparent !important; color: var(--green) !important;
    border: 1px solid var(--border-g) !important; border-radius: 10px !important;
    font-family: 'Sora', sans-serif !important; font-weight: 600 !important;
    font-size: 0.78rem !important; transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
    background: var(--green-soft) !important;
    box-shadow: 0 0 22px var(--green-glow) !important;
    transform: translateY(-1px) !important;
}

/* ── MISC ── */
hr { border-color: var(--border) !important; margin: 1.8rem 0 !important; }
h1, h2, h3, h4 { font-family: 'Sora', sans-serif !important; }
::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.07); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,255,136,0.25); }

/* Badges */
.badge-pos { background:rgba(0,255,136,0.1);color:#00FF88;border:1px solid rgba(0,255,136,0.25);padding:3px 12px;border-radius:20px;font-size:11px;font-weight:700;font-family:'Sora',sans-serif;letter-spacing:.06em; }
.badge-neg { background:rgba(252,78,110,0.1);color:#FC4E6E;border:1px solid rgba(252,78,110,0.25);padding:3px 12px;border-radius:20px;font-size:11px;font-weight:700;font-family:'Sora',sans-serif;letter-spacing:.06em; }
.badge-neu { background:rgba(113,128,150,0.1);color:#718096;border:1px solid rgba(113,128,150,0.2);padding:3px 12px;border-radius:20px;font-size:11px;font-weight:700;font-family:'Sora',sans-serif;letter-spacing:.06em; }

@keyframes pulse { 0%,100%{box-shadow:0 0 7px rgba(0,255,136,0.9);opacity:1} 50%{box-shadow:0 0 2px rgba(0,255,136,0.2);opacity:.4} }
@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:translateY(0)} }
.fade-up { animation:fadeUp .38s ease forwards; }
</style>
""", unsafe_allow_html=True)

# ── Session ────────────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "overview"

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1.8rem 1.4rem 1.2rem">
        <div style="display:flex;align-items:center;gap:11px;margin-bottom:1.5rem">
            <div style="width:38px;height:38px;
                background:linear-gradient(135deg,#00FF88,#00A85A);
                border-radius:11px;display:flex;align-items:center;
                justify-content:center;box-shadow:0 4px 18px rgba(0,255,136,0.4);flex-shrink:0">
                <span style="font-size:17px;font-weight:900;color:#000;font-family:'Sora',sans-serif">A</span>
            </div>
            <div>
                <div style="font-family:'Sora',sans-serif;font-size:16px;font-weight:800;
                            color:#EDF2F7;letter-spacing:-0.4px;line-height:1.1">AIVONEX</div>
                <div style="font-size:9px;color:#2D3748;letter-spacing:.06em;
                            font-family:'Inter',sans-serif;margin-top:2px">
                    Brand Intelligence Platform
                </div>
            </div>
        </div>
        <div style="height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.05),transparent);
                    margin:0 -1.4rem .8rem"></div>
    </div>
    """, unsafe_allow_html=True)

    sections = {
        "MAIN": [
            ("📊", "Overview",      "overview"),
            ("🔍", "Analyze Text",  "analyze"),
            ("📁", "CSV Import",    "csv_import"),
        ],
        "DATA": [
            ("🏷️", "Brands",       "brands"),
            ("📋", "Mentions Feed", "mentions"),
            ("🔔", "Alerts",        "alerts"),
        ],
        "REPORTS": [
            ("📄", "Reports",       "reports"),
        ],
        "SYSTEM": [
            ("⚙️", "Settings",     "settings"),
        ],
    }

    cur = st.session_state.page
    for section, items in sections.items():
        st.markdown(f"""
        <div style="font-family:'Sora',sans-serif;font-size:.58rem;font-weight:700;
                    letter-spacing:.2em;text-transform:uppercase;color:#1A2035;
                    padding:0 1.4rem;margin:1rem 0 .3rem">
            {section}
        </div>
        """, unsafe_allow_html=True)
        for icon, label, key in items:
            is_active = cur == key
            if is_active:
                bg = "background:rgba(0,255,136,0.08);border-left:2.5px solid #00FF88;color:#00FF88;font-weight:600;"
            else:
                bg = "border-left:2.5px solid transparent;color:#3D4F68;"
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;
                        padding:.58rem 1rem .58rem 1.1rem;margin:1px 6px 1px 0;
                        border-radius:0 10px 10px 0;font-family:'Sora',sans-serif;
                        font-size:.81rem;{bg}transition:all .18s;">
                <span style="font-size:14px;line-height:1">{icon}</span>
                <span>{label}</span>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"{icon} {label}", key=f"nav_{key}", use_container_width=True):
                st.session_state.page = key
                st.rerun()

    st.markdown("""
    <div style="margin:2rem 1.4rem 1rem;padding-top:1.2rem;
                border-top:1px solid rgba(255,255,255,0.04)">
        <div style="font-size:9px;color:#1A2035;font-family:'Inter',sans-serif;
                    line-height:1.9;letter-spacing:.04em">
            AIVONEX © 2025 &nbsp;·&nbsp; v1.0
        </div>
        <div style="display:flex;align-items:center;gap:8px;margin-top:8px">
            <div style="width:6px;height:6px;border-radius:50%;background:#00FF88;
                        animation:pulse 2.2s ease infinite;flex-shrink:0"></div>
            <span style="font-family:'Sora',sans-serif;font-size:9px;color:#00FF88;
                         font-weight:600;letter-spacing:.08em">SYSTEM ONLINE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Router ─────────────────────────────────────────────────────────────────────
page = st.session_state.get("page", "overview")
if page == "overview":
    from dashboard.pages import overview;    overview.render()
elif page == "analyze":
    from dashboard.pages import analyze;     analyze.render()
elif page == "csv_import":
    from dashboard.pages import csv_import;  csv_import.render()
elif page == "brands":
    from dashboard.pages import brands;      brands.render()
elif page == "mentions":
    from dashboard.pages import mentions;    mentions.render()
elif page == "alerts":
    from dashboard.pages import alerts_page; alerts_page.render()
elif page == "reports":
    from dashboard.pages import reports;     reports.render()
elif page == "settings":
    from dashboard.pages import settings;    settings.render()