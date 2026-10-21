"""Module A: Dashboard View."""

import streamlit as st
import plotly.graph_objects as go

from diagnostics.local_config import run_local_config_diagnostic
from storage.database import list_sessions
from utils.platform import get_default_gateway_and_dns, get_hostname, get_os_type


def render_dashboard():
    st.header("Network Troubleshooting Dashboard")
    st.caption("Live monitoring of local network readiness, recent incident tracking, and active adapter metrics.")

    # Top Status & System Readiness
    col1, col2, col3, col4 = st.columns(4)

    os_type = get_os_type()
    hostname = get_hostname()
    gw, dns_servers = get_default_gateway_and_dns()

    with col1:
        st.markdown("**Device Hostname**")
        st.subheader(hostname)
        st.caption(f"OS: {os_type.capitalize()}")

    with col2:
        st.markdown("**Default Gateway**")
        if gw:
            st.subheader(gw)
            st.caption("Local routing active")
        else:
            st.subheader("Unavailable")
            st.caption("No gateway detected")

    with col3:
        st.markdown("**Configured DNS**")
        if dns_servers:
            st.subheader(dns_servers[0])
            st.caption(f"+{len(dns_servers)-1} backup" if len(dns_servers) > 1 else "Primary resolver")
        else:
            st.subheader("Unavailable")
            st.caption("No DNS server discovered")

    with col4:
        recent = list_sessions(limit=1)
        st.markdown("**Last Diagnosis**")
        if recent:
            last_top = recent[0].get("top_hypothesis") or "Healthy"
            st.subheader("Logged")
            st.caption(f"{last_top[:24]}...")
        else:
            st.subheader("None")
            st.caption("No sessions recorded yet")

    st.markdown("---")

    # Quick Action Buttons
    c_btn1, c_btn2, c_btn3 = st.columns(3)
    with c_btn1:
        if st.button("🚀 Start Live Diagnosis", use_container_width=True, type="primary"):
            st.session_state["nav_selection"] = "Diagnose"
            st.rerun()

    with c_btn2:
        if st.button("🧪 Open Fault Simulation Lab", use_container_width=True):
            st.session_state["nav_selection"] = "Fault Simulation Lab"
            st.rerun()

    with c_btn3:
        if st.button("🔄 Refresh Local Interface Stats", use_container_width=True):
            st.session_state["last_refresh"] = str(st.session_state.get("last_refresh", 0)) + "1"
            st.rerun()

    st.markdown("### Active Local Network Interfaces")
    # Run a fast local config check
    local_info = run_local_config_diagnostic()
    interfaces = local_info.measured_values.get("interfaces", [])

    if interfaces:
        cols = st.columns(min(len(interfaces), 3))
        for idx, iface in enumerate(interfaces[:3]):
            col = cols[idx % 3]
            with col:
                status_icon = "🟢 UP" if iface.get("is_up") else "🔴 DOWN"
                st.markdown(f"**{iface.get('name')}** ({status_icon})")
                ips = iface.get("ipv4", [])
                if ips:
                    st.write(f"IPv4: `{ips[0]}`")
                else:
                    st.write("IPv4: *No address assigned*")
                if iface.get("speed_mbps"):
                    st.caption(f"Link Speed: {iface.get('speed_mbps')} Mbps")
    else:
        st.info("No active local physical interfaces enumerated.")

    st.markdown("### Recent Diagnostic Incidents")
    recent_sessions = list_sessions(limit=5)
    if recent_sessions:
        for sess in recent_sessions:
            mode_tag = "🧪 SIMULATED" if sess.get("is_simulated") else "🌐 LIVE"
            top_h = sess.get("top_hypothesis") or "No fault"
            st.markdown(
                f"- **{sess.get('start_time')[:19]}** &bull; `{mode_tag}` &bull; "
                f"Target: `{sess.get('target_host') or 'Local'}` &bull; "
                f"**{top_h}**"
            )
    else:
        st.info("No incidents logged yet. Start a diagnosis or run a simulation to see history.")
