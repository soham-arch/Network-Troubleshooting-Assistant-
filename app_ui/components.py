"""Custom CSS and UI Components for Streamlit with Dark, Thin, Glassmorphism Aesthetic."""

CUSTOM_CSS = """
<style>
/* Modern typography and performance-optimized font loading */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --bg-dark-base: #0a0d14;
    --bg-dark-surface: rgba(18, 24, 38, 0.65);
    --bg-glass-card: rgba(22, 30, 48, 0.55);
    --bg-glass-input: rgba(15, 23, 42, 0.6);
    --border-glass: rgba(255, 255, 255, 0.08);
    --border-glass-hover: rgba(56, 189, 248, 0.35);
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --accent-cyan: #38bdf8;
    --accent-blue: #3b82f6;
    --accent-emerald: #10b981;
    --accent-rose: #f43f5e;
    --accent-amber: #f59e0b;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    color: var(--text-primary);
}

/* Base App Dark Background with subtle mesh gradient */
.stApp {
    background-color: var(--bg-dark-base) !important;
    background-image: 
        radial-gradient(at 0% 0%, rgba(30, 41, 59, 0.4) 0px, transparent 45%),
        radial-gradient(at 100% 0%, rgba(14, 165, 233, 0.08) 0px, transparent 40%),
        radial-gradient(at 50% 100%, rgba(15, 23, 42, 0.5) 0px, transparent 55%) !important;
    background-attachment: fixed !important;
}

/* Top App Header bar - clean & transparent */
header[data-testid="stHeader"] {
    background: rgba(10, 13, 20, 0.75) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border-bottom: 1px solid var(--border-glass) !important;
}

/* Thin sleek dark scrollbars */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: #0a0d14;
}
::-webkit-scrollbar-thumb {
    background: #334155;
    border-radius: 9999px;
}
::-webkit-scrollbar-thumb:hover {
    background: #475569;
}

/* ─── Top Brand Header & Glass Banner ──────────────────────────── */
.nta-top-navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 1rem;
    padding: 1rem 1.4rem;
    margin-bottom: 1rem;
    background: var(--bg-dark-surface);
    backdrop-filter: blur(16px) saturate(180%);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--border-glass);
    border-radius: 14px;
    box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.4);
}

.nta-brand-col {
    display: flex;
    align-items: center;
    gap: 12px;
}

.nta-logo-icon {
    font-size: 1.8rem;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    border-radius: 10px;
    background: rgba(56, 189, 248, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.25);
    box-shadow: 0 0 16px rgba(56, 189, 248, 0.15);
}

.nta-brand-title {
    font-size: 1.15rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    color: #ffffff;
    line-height: 1.2;
}

.nta-brand-sub {
    font-size: 0.78rem;
    font-weight: 400;
    color: var(--text-secondary);
}

.nta-chips-row {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}

.nta-status-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.75rem;
    font-weight: 500;
    padding: 4px 10px;
    border-radius: 9999px;
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid var(--border-glass);
    color: #cbd5e1;
}

.nta-status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    display: inline-block;
}
.nta-status-dot.online {
    background-color: var(--accent-emerald);
    box-shadow: 0 0 8px var(--accent-emerald);
}
.nta-status-dot.idle {
    background-color: var(--text-muted);
}

/* ─── Top Horizontal Radio Navigation Bar (Turn radio into glass segmented tabs) ─── */
div[data-testid="stRadio"] > div[role="radiogroup"] {
    background: rgba(15, 23, 42, 0.65) !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    border: 1px solid var(--border-glass) !important;
    border-radius: 12px !important;
    padding: 5px 6px !important;
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 6px !important;
    margin-bottom: 1.5rem !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25) !important;
}

/* Hide default circular radio input */
div[data-testid="stRadio"] input[type="radio"],
div[data-testid="stRadio"] span[data-baseweb="radio-checked-marker"],
div[data-testid="stRadio"] div[class*="StyledRadio"] {
    display: none !important;
}

div[data-testid="stRadio"] label[data-baseweb="radio"] {
    margin: 0 !important;
    padding: 8px 16px !important;
    border-radius: 8px !important;
    border: 1px solid transparent !important;
    cursor: pointer !important;
    transition: all 0.16s ease-in-out !important;
    background: transparent !important;
    color: var(--text-secondary) !important;
    font-size: 0.86rem !important;
    font-weight: 500 !important;
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
}

div[data-testid="stRadio"] label[data-baseweb="radio"]:hover {
    background: rgba(255, 255, 255, 0.05) !important;
    color: #ffffff !important;
    border-color: rgba(255, 255, 255, 0.1) !important;
}

div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {
    background: rgba(56, 189, 248, 0.14) !important;
    color: #38bdf8 !important;
    border-color: rgba(56, 189, 248, 0.35) !important;
    box-shadow: 0 0 14px rgba(56, 189, 248, 0.15) !important;
    font-weight: 600 !important;
}

/* ─── Glassmorphism Card System ─────────────────────────────────── */
.nta-card {
    background: var(--bg-glass-card);
    backdrop-filter: blur(14px) saturate(160%);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid var(--border-glass);
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    transition: border-color 0.2s ease;
}

.nta-card:hover {
    border-color: var(--border-glass-hover);
}

.nta-card-alert {
    background: rgba(69, 10, 10, 0.3);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(244, 63, 94, 0.25);
    border-left: 4px solid var(--accent-rose);
    border-radius: 10px;
    padding: 1.25rem;
    margin-bottom: 1rem;
}

/* Badges */
.nta-badge {
    display: inline-block;
    padding: 3px 9px;
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.nta-badge-pass {
    background-color: rgba(16, 185, 129, 0.15);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.3);
}
.nta-badge-fail {
    background-color: rgba(239, 68, 68, 0.15);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.3);
}
.nta-badge-warning {
    background-color: rgba(245, 158, 11, 0.15);
    color: #fbbf24;
    border: 1px solid rgba(245, 158, 11, 0.3);
}
.nta-badge-skipped {
    background-color: rgba(100, 116, 139, 0.15);
    color: #94a3b8;
    border: 1px solid rgba(100, 116, 139, 0.3);
}

/* Metric styling */
.nta-metric-value {
    font-size: 1.75rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.02em;
}
.nta-metric-label {
    font-size: 0.8rem;
    color: var(--text-secondary);
    font-weight: 500;
}

/* Stage Flow Bar */
.nta-stage-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 8px;
    background: rgba(15, 23, 42, 0.5);
    border: 1px solid var(--border-glass);
    font-size: 0.83rem;
    font-weight: 500;
}

/* ─── Streamlit Native Widgets Dark Polish ──────────────────────── */
/* Metrics */
div[data-testid="stMetric"] {
    background: var(--bg-glass-card) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid var(--border-glass) !important;
    border-radius: 12px !important;
    padding: 0.9rem 1.15rem !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
}

/* Buttons */
.stButton > button {
    background: rgba(30, 41, 59, 0.6) !important;
    backdrop-filter: blur(8px) !important;
    border: 1px solid rgba(148, 163, 184, 0.2) !important;
    color: #f1f5f9 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    transition: all 0.15s ease-in-out !important;
    padding: 0.45rem 1rem !important;
}
.stButton > button:hover {
    background: rgba(51, 65, 85, 0.8) !important;
    border-color: rgba(56, 189, 248, 0.45) !important;
    color: #38bdf8 !important;
    box-shadow: 0 0 12px rgba(56, 189, 248, 0.2) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, rgba(14, 165, 233, 0.8), rgba(59, 130, 246, 0.8)) !important;
    border: 1px solid rgba(56, 189, 248, 0.4) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 14px rgba(14, 165, 233, 0.25) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, rgba(2, 132, 199, 0.9), rgba(37, 99, 235, 0.9)) !important;
    box-shadow: 0 6px 18px rgba(14, 165, 233, 0.4) !important;
}

/* Inputs & Text Areas */
.stTextInput input, .stTextArea textarea {
    background: var(--bg-glass-input) !important;
    border: 1px solid var(--border-glass) !important;
    color: #f8fafc !important;
    border-radius: 8px !important;
    backdrop-filter: blur(8px) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent-cyan) !important;
    box-shadow: 0 0 10px rgba(56, 189, 248, 0.2) !important;
}

/* Selectboxes */
div[data-baseweb="select"] > div {
    background: var(--bg-glass-input) !important;
    border: 1px solid var(--border-glass) !important;
    border-radius: 8px !important;
    color: #f8fafc !important;
}

/* Tabs */
div[data-testid="stTabs"] button[data-baseweb="tab"] {
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    border-bottom: 2px solid transparent !important;
    padding-bottom: 8px !important;
}
div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--accent-cyan) !important;
    border-bottom-color: var(--accent-cyan) !important;
    font-weight: 600 !important;
}

/* Expanders */
div[data-testid="stExpander"] {
    background: var(--bg-glass-card) !important;
    border: 1px solid var(--border-glass) !important;
    border-radius: 10px !important;
}

/* Plotly charts dark background fit */
.js-plotly-plot .plotly .main-svg {
    background: transparent !important;
}

/* Sidebar styling - sleek drawer fallback */
section[data-testid="stSidebar"] {
    background: rgba(10, 13, 20, 0.85) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border-right: 1px solid var(--border-glass) !important;
}
</style>
"""


def render_top_navbar(sched_active: bool = False):
    """Renders the top branding and real-time status chips."""
    import streamlit as st

    dot_class = "online" if sched_active else "idle"
    dot_label = "Daemon: Active" if sched_active else "Daemon: Idle"

    navbar_html = f"""
    <div class="nta-top-navbar">
        <div class="nta-brand-col">
            <div class="nta-logo-icon">🌐</div>
            <div>
                <div class="nta-brand-title">NETWORK TROUBLESHOOTING ASSISTANT</div>
                <div class="nta-brand-sub">Autonomous Multi-Stage Diagnostic & Root Cause Engine</div>
            </div>
        </div>
        <div class="nta-chips-row">
            <div class="nta-status-chip">
                <span class="nta-status-dot {dot_class}"></span>
                <span>{dot_label}</span>
            </div>
            <div class="nta-status-chip">
                <span>🛡️ Mode: Read-Only (RFC)</span>
            </div>
            <div class="nta-status-chip">
                <span>⚡ Engine: Deterministic</span>
            </div>
            <div class="nta-status-chip">
                <span>💾 SQLite Active</span>
            </div>
        </div>
    </div>
    """
    st.markdown(navbar_html, unsafe_allow_html=True)
