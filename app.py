"""Network Troubleshooting Assistant - Main Application Entry Point."""

import streamlit as st
import os

from app_ui.components import CUSTOM_CSS, render_top_navbar
from app_ui.dashboard import render_dashboard
from app_ui.diagnose import render_diagnose
from app_ui.evaluation import render_evaluation
from app_ui.history import render_history
from app_ui.monitoring import render_monitoring
from app_ui.settings import render_settings
from app_ui.simulation import render_simulation_lab
from monitoring.scheduler import monitoring_scheduler
from storage.database import init_db

# Configure Streamlit page with collapsed sidebar for full top-layout view
st.set_page_config(
    page_title="Network Troubleshooting Assistant",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom dark glassmorphism CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize SQLite database
init_db("data/nta.db")

# Setup Navigation State
if "nav_selection" not in st.session_state:
    st.session_state["nav_selection"] = "Dashboard"

PAGES = {
    "Dashboard": render_dashboard,
    "Diagnose": render_diagnose,
    "Monitoring": render_monitoring,
    "Fault Simulation Lab": render_simulation_lab,
    "Incident History": render_history,
    "Evaluation": render_evaluation,
    "Settings": render_settings
}

NAV_DISPLAY_MAP = {
    "📊 Dashboard": "Dashboard",
    "🎯 Diagnose": "Diagnose",
    "📈 Monitoring": "Monitoring",
    "🧪 Fault Simulation Lab": "Fault Simulation Lab",
    "📜 Incident History": "Incident History",
    "📐 Evaluation": "Evaluation",
    "⚙️ Settings": "Settings"
}
REVERSE_NAV_MAP = {v: k for k, v in NAV_DISPLAY_MAP.items()}

# Render Top Glassmorphism Branding & Status Banner
render_top_navbar(sched_active=monitoring_scheduler.is_running())

# Render Top Horizontal Glass Navigation
current_nav_key = st.session_state.get("nav_selection", "Dashboard")
current_display = REVERSE_NAV_MAP.get(current_nav_key, "📊 Dashboard")

nav_options = list(NAV_DISPLAY_MAP.keys())
nav_idx = nav_options.index(current_display) if current_display in nav_options else 0

selected_display = st.radio(
    "Navigation Menu",
    options=nav_options,
    index=nav_idx,
    horizontal=True,
    label_visibility="collapsed"
)

# Keep session state updated
st.session_state["nav_selection"] = NAV_DISPLAY_MAP.get(selected_display, "Dashboard")

# Collapsed Secondary Sidebar Drawer (Useful reference tools)
with st.sidebar:
    st.markdown("### 🌐 **Assistant Utilities**")
    st.caption("RFC 1918 Compliant & Read-Only")
    st.markdown("---")
    sched_status = "🟢 Active" if monitoring_scheduler.is_running() else "⚪ Idle"
    st.markdown(
        f"""
        <div style="font-size: 12px; color: #94a3b8; line-height: 1.8;">
            <b>Operational Mode:</b> Read-Only (Advisory)<br>
            <b>Safety Policy:</b> RFC Compliant<br>
            <b>Diagnostic Engine:</b> Deterministic<br>
            <b>Storage:</b> SQLite DB Active<br>
            <b>Daemon Scheduler:</b> {sched_status}
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")
    st.caption("Tip: Use the top navigation bar to switch between Diagnostic, Simulation, and Monitoring views.")

# Render selected page
current_page_key = st.session_state["nav_selection"]
render_func = PAGES.get(current_page_key, render_dashboard)
render_func()
