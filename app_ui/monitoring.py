"""Module: Continuous / Scheduled Monitoring & Alerting Dashboard."""

from __future__ import annotations

import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from integrations.alerter import alerter
from monitoring.models import MonitoringTarget
from monitoring.scheduler import monitoring_scheduler
from storage.database import (
    delete_monitoring_target,
    get_monitoring_alerts,
    get_monitoring_history,
    get_monitoring_targets,
    save_monitoring_target,
)
from utils.validation import validate_hostname_or_ip, validate_port


def render_monitoring():
    st.header("Continuous Network Monitoring & Alerting")
    st.caption("Autonomous scheduled sweeps, latency & packet loss degradation detection, and multi-channel alerting.")

    # Top Control Bar: Scheduler State & Aggregates
    targets = get_monitoring_targets()
    is_running = monitoring_scheduler.is_running()

    col_sched, col_actions = st.columns([3, 2])
    with col_sched:
        status_color = "green" if is_running else "gray"
        status_text = "🟢 ACTIVE (Running in background)" if is_running else "⚪ STOPPED (Idle)"
        st.markdown(f"**Scheduler Daemon:** `{status_text}`")
    with col_actions:
        b1, b2 = st.columns(2)
        with b1:
            if not is_running:
                if st.button("▶️ Start Scheduler", type="primary", use_container_width=True):
                    monitoring_scheduler.start()
                    st.rerun()
            else:
                if st.button("⏹️ Pause Scheduler", use_container_width=True):
                    monitoring_scheduler.stop()
                    st.rerun()
        with b2:
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.rerun()

    # Aggregate Metrics
    healthy_cnt = sum(1 for t in targets if t.current_status == "HEALTHY")
    degraded_cnt = sum(1 for t in targets if t.current_status == "DEGRADED")
    down_cnt = sum(1 for t in targets if t.current_status == "DOWN")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Monitored Targets", len(targets))
    m2.metric("🟢 Healthy", healthy_cnt)
    m3.metric("🟡 Degraded", degraded_cnt)
    m4.metric("🔴 Down", down_cnt)

    st.markdown("---")

    # Section 1: Active Targets
    st.subheader("Active Monitoring Targets")
    if not targets:
        st.info("No targets currently configured for scheduled monitoring. Add your first target below.")
    else:
        for t in targets:
            badge = {
                "HEALTHY": "🟢 HEALTHY",
                "DEGRADED": "🟡 DEGRADED",
                "DOWN": "🔴 DOWN",
                "UNKNOWN": "⚪ PENDING PROBE"
            }.get(t.current_status, "⚪")

            with st.expander(f"{badge} &bull; **{t.name}** (`{t.host}:{t.port}`) — Every {t.interval_seconds}s"):
                c_details, c_btns = st.columns([3, 1])
                with c_details:
                    st.markdown(f"- **Protocol:** `{t.service_type.upper()}` &bull; **Last Check:** `{t.last_run or 'Never'}`")
                    st.markdown(f"- **Degradation Thresholds:** Latency > `{t.latency_threshold_ms}ms`, Packet Loss > `{t.packet_loss_threshold_pct}%`")
                    channels = []
                    if t.alert_slack_webhook:
                        channels.append("Slack")
                    if t.alert_generic_webhook:
                        channels.append("Webhook")
                    if t.alert_email:
                        channels.append(f"Email ({t.alert_email})")
                    st.markdown(f"- **Alert Channels:** {', '.join(channels) if channels else 'Global defaults only'}")
                with c_btns:
                    if st.button("⚡ Run Check Now", key=f"check_{t.target_id}", use_container_width=True):
                        with st.spinner(f"Testing {t.name}..."):
                            rec = monitoring_scheduler.execute_check(t)
                            st.success(f"Outcome: {rec.status} (Latency: {rec.latency_ms}ms, Loss: {rec.packet_loss_pct}%)")
                            time.sleep(0.5)
                            st.rerun()

                    if st.button("🗑️ Delete Target", key=f"del_{t.target_id}", use_container_width=True):
                        delete_monitoring_target(t.target_id)
                        st.success(f"Removed {t.name}")
                        st.rerun()

    # Section 2: Add New Target Form
    st.markdown("---")
    with st.expander("➕ Register New Target for Continuous Monitoring", expanded=len(targets) == 0):
        with st.form("add_target_form"):
            ca, cb = st.columns(2)
            with ca:
                target_name = st.text_input("Display Name *", value="Production Gateway")
                target_host = st.text_input("Target Hostname or IP *", value="1.1.1.1")
                target_port = st.text_input("Port", value="443")
                service_proto = st.selectbox("Service Protocol", ["HTTPS", "HTTP", "TCP Generic"])
            with cb:
                interval_sec = st.number_input("Check Interval (seconds)", min_value=15, max_value=3600, value=60)
                lat_thresh = st.number_input("Degraded Latency Threshold (ms)", min_value=10.0, max_value=2000.0, value=150.0)
                loss_thresh = st.number_input("Degraded Packet Loss Threshold (%)", min_value=1.0, max_value=100.0, value=5.0)

            st.markdown("**Incident Alert Channels (Optional overrides)**")
            c_al1, c_al2 = st.columns(2)
            with c_al1:
                al_email = st.text_input("Alert Email", placeholder="noc@company.com")
                al_slack = st.text_input("Slack Webhook URL", placeholder="https://hooks.slack.com/services/...")
            with c_al2:
                al_generic = st.text_input("Generic ITSM Webhook URL", placeholder="https://api.pagerduty.com/...")

            btn_create = st.form_submit_button("Save Target", type="primary")

        if btn_create:
            if not target_name.strip():
                st.error("Target name is required.")
                return

            is_valid_host, clean_host, host_err = validate_hostname_or_ip(target_host)
            if not is_valid_host:
                st.error(f"Invalid Host: {host_err}")
                return

            is_valid_port, clean_port, port_err = validate_port(target_port)
            if not is_valid_port:
                st.error(f"Invalid Port: {port_err}")
                return

            new_target = MonitoringTarget(
                name=target_name.strip(),
                host=clean_host,
                port=clean_port,
                service_type=service_proto.lower(),
                interval_seconds=int(interval_sec),
                latency_threshold_ms=float(lat_thresh),
                packet_loss_threshold_pct=float(loss_thresh),
                alert_email=al_email.strip() or None,
                alert_slack_webhook=al_slack.strip() or None,
                alert_generic_webhook=al_generic.strip() or None
            )
            save_monitoring_target(new_target)
            st.success(f"Registered '{new_target.name}' for continuous monitoring.")
            st.rerun()

    # Section 3: Telemetry Trends & Charts
    st.markdown("---")
    st.subheader("Historical Telemetry Trends")
    history_records = get_monitoring_history(limit=150)

    if not history_records:
        st.info("No telemetry history recorded yet. Start the scheduler or trigger 'Run Check Now' on a target.")
    else:
        df_hist = pd.DataFrame(history_records)
        df_hist["timestamp"] = pd.to_datetime(df_hist["timestamp"])
        df_hist = df_hist.sort_values("timestamp")

        # Select target filter
        available_target_names = ["All Targets"] + list(df_hist["target_name"].dropna().unique())
        selected_filter = st.selectbox("Filter History by Target", options=available_target_names)

        chart_df = df_hist if selected_filter == "All Targets" else df_hist[df_hist["target_name"] == selected_filter]

        fig_lat = px.line(
            chart_df,
            x="timestamp",
            y="latency_ms",
            color="target_name",
            markers=True,
            title="Round-Trip Latency (ms) Over Time",
            labels={"latency_ms": "Latency (ms)", "timestamp": "Timestamp"}
        )
        fig_lat.update_layout(
            template="plotly_dark",
            height=320,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor="rgba(15, 23, 42, 0.45)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="'Inter', sans-serif", color="#e2e8f0")
        )
        st.plotly_chart(fig_lat, use_container_width=True)

        if "packet_loss_pct" in chart_df.columns:
            fig_loss = px.bar(
                chart_df,
                x="timestamp",
                y="packet_loss_pct",
                color="status",
                title="Packet Loss (%) Over Time",
                labels={"packet_loss_pct": "Packet Loss %", "timestamp": "Timestamp"}
            )
            fig_loss.update_layout(
                template="plotly_dark",
                height=260,
                margin=dict(l=20, r=20, t=40, b=20),
                plot_bgcolor="rgba(15, 23, 42, 0.45)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="'Inter', sans-serif", color="#e2e8f0")
            )
            st.plotly_chart(fig_loss, use_container_width=True)

    # Section 4: Incident Alert Dispatch Log
    st.markdown("---")
    st.subheader("Recent Alert Dispatch Log")
    recent_alerts = get_monitoring_alerts(limit=25)
    if not recent_alerts:
        st.caption("No incident alerts dispatched recently.")
    else:
        st.dataframe(pd.DataFrame(recent_alerts), use_container_width=True)

    # Send test alert button
    with st.expander("🧪 Test Alert Channel Configuration"):
        c_tst1, c_tst2 = st.columns([3, 1])
        with c_tst1:
            test_channel = st.selectbox("Channel", ["Slack", "Generic Webhook", "Email"])
            test_target = targets[0] if targets else MonitoringTarget(name="Test Target", host="1.1.1.1")
        with c_tst2:
            st.write("")
            st.write("")
            if st.button("Send Test Alert"):
                notifs = alerter.dispatch_incident_alert(
                    target=test_target,
                    status="DEGRADED",
                    reason="Manual test alert triggered from Monitoring Dashboard."
                )
                st.success(f"Dispatched {len(notifs)} test notifications.")
                st.rerun()
