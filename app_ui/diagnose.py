"""Adaptive Network Diagnosis UI.

Supports:
1. Natural language symptom intake with smart target & stage parsing.
2. Single target adaptive investigation with bounded execution.
3. Interactive Plotly traceroute path diagram with bottleneck detection.
4. LLM-assisted executive explanation grounded in deterministic findings.
5. Jira & Webhook incident ticket creation.
6. Multi-target / batch parallel diagnostics with comparison matrix.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st
import time

from batch.orchestrator import BatchDiagnosticOrchestrator, BatchTargetItem
from diagnostics.models import DiagnosticSession, DiagnosticStage, TestStatus, VerificationOutcome
from diagnostics.traceroute_visualizer import create_traceroute_path_figure, parse_traceroute_hops
from engine.orchestrator import DiagnosticOrchestrator
from integrations.ticketing import GenericTicketWebhookConnector, JiraConnector
from llm.client import LLMClient
from llm.explanation_service import generate_session_explanation
from llm.symptom_parser import parse_symptom
from reports.html_report import generate_html_report
from reports.pdf_report import generate_pdf_report
from storage.database import get_session, save_session
from utils.validation import validate_hostname_or_ip, validate_port


def render_diagnose():
    st.header("Adaptive Network Diagnosis & Audit")
    st.caption("AI-assisted symptom parsing, deterministic multi-stage diagnostics, route visualization, and batch audits.")

    tab1, tab2 = st.tabs(["🎯 Single Target Investigation", "📦 Multi-Target / Batch Audit"])

    with tab1:
        _render_single_target_diagnosis()

    with tab2:
        _render_batch_diagnosis()


def _render_single_target_diagnosis():
    # Session state for parsed symptom auto-fill
    if "parsed_symptom" not in st.session_state:
        st.session_state["parsed_symptom"] = None

    # Symptom input box outside form for interactive parsing
    st.markdown("### 1. Problem Symptom Intake")
    col_sym, col_btn = st.columns([4, 1])
    with col_sym:
        symptom_input = st.text_input(
            "Natural Language Problem Description *",
            value=st.session_state.get("symptom_text", "The website is slow and Teams calls are dropping to google.com"),
            key="symptom_text_input",
            help="Describe what you are observing in plain English."
        )
    with col_btn:
        st.write("")
        st.write("")
        if st.button("🧠 Smart Parse", help="Parse host, port, protocol, and recommended stages automatically"):
            with st.spinner("Analyzing symptom with NLP parser..."):
                client = LLMClient()
                parsed = parse_symptom(symptom_input, client if client.is_configured() else None)
                st.session_state["parsed_symptom"] = parsed
                st.session_state["symptom_text"] = symptom_input
                st.rerun()

    # Show parsed info banner if available
    parsed = st.session_state.get("parsed_symptom")
    if parsed:
        st.info(
            f"**Parsed Category:** `{parsed.category}` &bull; "
            f"**Detected Target:** `{parsed.target_host or 'N/A'}:{parsed.target_port or 'N/A'}` &bull; "
            f"**Recommended Stages:** `{', '.join(parsed.recommended_stages)}`\n\n"
            f"*{parsed.reasoning}*"
        )

    # Main Target Configuration Form
    with st.form("diagnosis_form"):
        st.markdown("### 2. Target Configuration & Test Policy")
        c1, c2, c3, c4 = st.columns([3, 1, 2, 2])
        with c1:
            default_host = parsed.target_host if (parsed and parsed.target_host) else "google.com"
            target_host = st.text_input("Target Hostname or IP", value=default_host)
        with c2:
            default_port = str(parsed.target_port) if (parsed and parsed.target_port) else "443"
            target_port = st.text_input("Port (Optional)", value=default_port)
        with c3:
            proto_opts = ["HTTPS", "HTTP", "TCP Generic", "None"]
            default_proto_idx = 0
            if parsed and parsed.service_type:
                proto_map = {"https": 0, "http": 1, "tcp": 2}
                default_proto_idx = proto_map.get(parsed.service_type.lower(), 0)
            service_type = st.selectbox("Service Protocol", options=proto_opts, index=default_proto_idx)
        with c4:
            st.write("")
            run_traceroute = st.checkbox("Include Traceroute Path", value=True, help="Executes bounded route trace to render interactive hop diagram.")

        submit = st.form_submit_button("🚀 Run Adaptive Investigation", type="primary", use_container_width=True)

    if submit:
        symptom_val = symptom_input.strip() or "General network connectivity check"
        is_valid_host, clean_host, host_err = validate_hostname_or_ip(target_host)
        if target_host.strip() and not is_valid_host:
            st.error(f"Invalid Target: {host_err}")
            return

        is_valid_port, clean_port, port_err = validate_port(target_port)
        if not is_valid_port:
            st.error(f"Invalid Port: {port_err}")
            return

        orchestrator = DiagnosticOrchestrator()
        progress_bar = st.progress(0)
        status_text = st.empty()

        def on_step(res, cur_step, total_steps):
            pct = min(1.0, cur_step / total_steps)
            progress_bar.progress(pct)
            status_text.text(f"Executing: {res.test_name} ({res.status.value})")

        with st.spinner("Running adaptive network investigation across OSI layers..."):
            session = orchestrator.run_investigation(
                user_symptom=symptom_val,
                target_host=clean_host if target_host.strip() else None,
                target_port=clean_port,
                service_type=service_type.lower() if service_type != "None" else None,
                run_traceroute=run_traceroute,
                on_test_complete=on_step
            )

        progress_bar.progress(1.0)
        status_text.text("Investigation complete.")
        st.session_state["current_session"] = session

    # Render results if available
    session: DiagnosticSession = st.session_state.get("current_session")
    if session and not session.is_simulated:
        st.markdown("---")
        _render_session_results(session)


def _render_session_results(session: DiagnosticSession):
    st.subheader(f"Diagnostic Findings (Session: `{session.session_id[:8]}`)")

    # 1. Primary Root Cause Box
    if session.hypotheses:
        top_h = session.hypotheses[0]
        st.markdown(
            f"""
            <div style="background-color: #fef2f2; border-left: 5px solid #ef4444; padding: 16px; border-radius: 6px; margin-bottom: 20px;">
                <h3 style="margin-top:0; color: #991b1b;">Probable Root Cause: {top_h.title}</h3>
                <p><strong>Confidence:</strong> {top_h.confidence.value} ({int(top_h.confidence_score*100)}%)</p>
                <p><strong>Diagnosis:</strong> {top_h.probable_root_cause}</p>
                <p><strong>Next Action:</strong> {top_h.suggested_corrective_action}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.expander("🔬 View Technical Context & Alternative Explanations"):
            st.markdown("**Alternative Possible Explanations:**")
            for alt in top_h.alternative_explanations:
                st.markdown(f"- {alt}")
            st.markdown("**Verification Checklist:**")
            for v in top_h.verification_steps:
                st.markdown(f"- {v}")

    # 2. Interactive Traceroute Visualization
    traceroute_tests = [t for t in session.test_results if t.stage == DiagnosticStage.TRACEROUTE]
    if traceroute_tests:
        st.markdown("### 🌐 Interactive Route Path & Failure Bottleneck")
        trace_test = traceroute_tests[0]
        hops = parse_traceroute_hops(traceroute_result=trace_test)
        if hops:
            fig = create_traceroute_path_figure(hops, target_host=session.target_host or "")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No intermediate hop responses captured.")

    # 3. LLM-Assisted Explanation & Remediation Plan
    st.markdown("### 🤖 LLM-Assisted Executive Explanation & Plan")
    with st.expander("✨ View Grounded AI Explanation & Incident Briefing", expanded=True):
        explanation_key = f"explanation_{session.session_id}"
        if explanation_key not in st.session_state:
            with st.spinner("Generating grounded executive summary..."):
                client = LLMClient()
                st.session_state[explanation_key] = generate_session_explanation(session, client)

        st.markdown(st.session_state[explanation_key])

        if st.button("🔄 Refresh Explanation", key=f"refresh_{session.session_id}"):
            with st.spinner("Regenerating explanation..."):
                client = LLMClient()
                st.session_state[explanation_key] = generate_session_explanation(session, client)
                st.rerun()

    # 4. Diagnostic Timeline & Evidence
    st.markdown("### Adaptive Diagnostic Timeline & Evidence")
    for t in session.test_results:
        status_icon = {
            TestStatus.PASS: "🟢 PASS",
            TestStatus.FAIL: "🔴 FAIL",
            TestStatus.WARNING: "🟡 WARNING",
            TestStatus.SKIPPED: "⚪ SKIPPED",
            TestStatus.ERROR: "🟣 ERROR"
        }.get(t.status, "⚪")

        with st.expander(f"{status_icon} &bull; **{t.test_name}** — {t.human_explanation}"):
            st.markdown(f"**Stage:** `{t.stage.value}`")
            st.markdown("**Measured Observations & Evidence:**")
            for e in t.evidence:
                st.markdown(f"- `{e}`")
            if t.limitations:
                st.caption(f"Limitations: {t.limitations}")
            if t.skipped_reason:
                st.caption(f"Reason Skipped: {t.skipped_reason}")

    # 5. Actionable Remediations
    st.markdown("### Safe Actionable Remediations")
    if session.recommendations:
        for idx, rec in enumerate(session.recommendations):
            st.markdown(f"#### {idx+1}. {rec.observed_issue}")
            st.markdown(f"*{rec.why_it_helps}*")
            st.markdown("**Recommended Steps:**")
            for s in rec.steps_to_follow:
                st.markdown(f"1. {s}")
            st.markdown(f"**Expected Outcome:** {rec.expected_outcome}")
            st.markdown(f"**How to Verify:** {rec.how_to_verify}")
            st.caption(f"Caution/Risk: {rec.risks_and_limitations}")
            st.markdown("---")

    # 6. Remediation Verification
    st.markdown("### Remediation Verification Loop")
    c_verif1, c_verif2 = st.columns([2, 3])
    with c_verif1:
        if st.button("🔄 Verify Recovery (Re-run Check)", key="btn_verify"):
            with st.spinner("Re-evaluating target reachability..."):
                orchestrator = DiagnosticOrchestrator()
                new_session = orchestrator.run_investigation(
                    user_symptom=session.user_symptom,
                    target_host=session.target_host,
                    target_port=session.target_port,
                    service_type=session.service_type
                )
                prev_fail = any(t.status == TestStatus.FAIL for t in session.test_results)
                curr_fail = any(t.status == TestStatus.FAIL for t in new_session.test_results)

                if prev_fail and not curr_fail:
                    session.verification_outcome = VerificationOutcome.VERIFIED_RECOVERY
                    session.verification_notes = "All failed checks succeeded after fix."
                elif prev_fail and curr_fail:
                    session.verification_outcome = VerificationOutcome.ISSUE_PERSISTS
                    session.verification_notes = "Issue persists after attempted remediation."
                else:
                    session.verification_outcome = VerificationOutcome.PARTIAL_IMPROVEMENT
                    session.verification_notes = "Re-evaluation completed."

                save_session(session)
                st.session_state["current_session"] = session
                st.rerun()

    with c_verif2:
        if session.verification_outcome:
            st.success(f"Verification Result: {session.verification_outcome.value}")
            st.caption(session.verification_notes or "")

    # 7. Ticketing & Reports Export
    st.markdown("### 🎫 Incident Ticketing & Report Export")
    c_ticket, c_rep1, c_rep2 = st.columns(3)

    with c_ticket:
        with st.popover("🎫 Create Incident Ticket", use_container_width=True):
            ticket_sys = st.selectbox("System", ["Jira", "Generic Webhook"])
            ticket_summary = st.text_input("Summary", value=f"[Incident] {session.target_host}: {session.hypotheses[0].title if session.hypotheses else 'Network Anomaly'}")
            if st.button("Submit Ticket", type="primary"):
                if ticket_sys == "Jira":
                    jira = JiraConnector()
                    res = jira.create_incident_ticket(session, summary=ticket_summary)
                    if res.get("success"):
                        st.success(f"Ticket Created: `{res.get('ticket_id')}`")
                        if res.get("ticket_url"):
                            st.markdown(f"[Open in Jira]({res.get('ticket_url')})")
                    else:
                        st.error(res.get("message"))
                else:
                    res = GenericTicketWebhookConnector.send_incident_to_webhook(session)
                    if res.get("success"):
                        st.success(f"Webhook Dispatched: `{res.get('ticket_id')}`")
                    else:
                        st.error(res.get("message"))

    with c_rep1:
        html_data = generate_html_report(session)
        st.download_button(
            label="📄 Download HTML Report",
            data=html_data,
            file_name=f"report_{session.session_id[:8]}.html",
            mime="text/html",
            use_container_width=True
        )

    with c_rep2:
        pdf_data = generate_pdf_report(session)
        if pdf_data:
            st.download_button(
                label="📑 Download PDF Report",
                data=pdf_data,
                file_name=f"report_{session.session_id[:8]}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.button("📑 PDF Export Unavailable", disabled=True, use_container_width=True)


def _render_batch_diagnosis():
    st.subheader("Multi-Target & Batch Diagnostic Audit")
    st.caption("Diagnose multiple hosts, URLs, or CSV target lists concurrently with bounded worker pools.")

    default_batch_text = (
        "google.com,443,https,Google Search\n"
        "github.com,443,https,GitHub\n"
        "1.1.1.1,53,udp,Cloudflare DNS\n"
        "127.0.0.1,9999,tcp,Unbound Local Port"
    )

    c_input, c_opt = st.columns([3, 1])
    with c_input:
        batch_text = st.text_area(
            "Target List (One target per line or CSV: host,port,protocol,label)",
            value=default_batch_text,
            height=140
        )
        uploaded_file = st.file_uploader("Or Upload CSV Target File", type=["csv", "txt"])
        if uploaded_file is not None:
            batch_text = uploaded_file.getvalue().decode("utf-8")

    with c_opt:
        concurrency = st.slider("Concurrency Limit", min_value=1, max_value=8, value=4, help="Controls simultaneous threads.")
        audit_symptom = st.text_input("Audit Reason", value="Batch network health audit")
        run_batch_btn = st.button("🚀 Run Batch Audit", type="primary", use_container_width=True)

    if run_batch_btn:
        targets = BatchDiagnosticOrchestrator.parse_targets(batch_text)
        if not targets:
            st.error("No valid targets identified. Please verify the host format.")
            return

        st.info(f"Queued {len(targets)} targets for concurrent diagnostic audit (max {concurrency} parallel workers)...")
        prog_bar = st.progress(0)
        status_msg = st.empty()

        def on_batch_progress(completed, total, res):
            pct = min(1.0, completed / total)
            prog_bar.progress(pct)
            status_msg.text(f"Completed: {res.host} ({res.status}) — [{completed}/{total}]")

        orchestrator = BatchDiagnosticOrchestrator(max_concurrency=concurrency)
        with st.spinner("Executing concurrent network diagnostics..."):
            report = orchestrator.run_batch(
                targets=targets,
                symptom_description=audit_symptom,
                on_progress=on_batch_progress
            )

        prog_bar.progress(1.0)
        status_msg.text("Batch audit completed.")
        st.session_state["batch_report"] = report

    # Render Batch Results
    report = st.session_state.get("batch_report")
    if report:
        st.markdown("---")
        st.markdown(f"### Batch Audit Results (`{report.batch_id}`)")

        # Summary Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Targets", report.total_targets)
        m2.metric("🟢 Healthy", report.healthy_count)
        m3.metric("🟡 Degraded", report.degraded_count)
        m4.metric("🔴 Failed / Error", report.failed_count)

        # Comparison Matrix Table
        st.markdown("#### Comparison Matrix")
        df_matrix = pd.DataFrame(report.comparison_matrix)
        st.dataframe(df_matrix, use_container_width=True)

        # Ranked Problems
        if report.ranked_problems:
            st.markdown("#### 🚨 Ranked Problematic Targets (By Severity)")
            for p in report.ranked_problems:
                badge = "🔴 FAILED" if p.status in ("FAILED", "ERROR") else "🟡 DEGRADED"
                with st.expander(f"{badge} &bull; **{p.label or p.host}** ({p.host}:{p.port}) — Severity: {p.severity_score}/100"):
                    st.markdown(f"**Primary Root Cause:** {p.top_root_cause} (Confidence: `{p.confidence}`)")
                    st.markdown(f"- DNS Status: `{p.dns_status}` &bull; Port Handshake: `{p.port_status}` &bull; HTTP/TLS: `{p.http_status}`")
                    st.markdown(f"- Latency: `{p.avg_latency_ms or 'N/A'} ms` &bull; Packet Loss: `{p.packet_loss_pct}%`")
                    if p.session:
                        if st.button("Inspect Full Session", key=f"inspect_{p.target_id}"):
                            st.session_state["current_session"] = p.session
                            st.session_state["nav_selection"] = "Diagnose"
                            st.rerun()

        # CSV Export
        csv_data = df_matrix.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Comparison Matrix (CSV)",
            data=csv_data,
            file_name=f"batch_matrix_{report.batch_id}.csv",
            mime="text/csv"
        )
