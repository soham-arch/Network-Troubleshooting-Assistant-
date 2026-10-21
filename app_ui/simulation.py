"""Module G: Controlled Fault Simulation Lab Interface."""

import streamlit as st
import time

from diagnostics.models import DiagnosticSession, TestStatus
from reports.html_report import generate_html_report
from reports.pdf_report import generate_pdf_report
from simulation.scenarios import (
    SIMULATION_SCENARIOS,
    SimulationLabEngine,
    get_scenario_by_id,
)


def render_simulation_lab():
    st.header("Controlled Network Fault Simulation Lab")
    st.caption(
        "Demonstrate and evaluate the diagnostic engine against 10 isolated, reproducible "
        "network fault scenarios. Safe: Never alters real host configuration."
    )

    scenario_names = [f"{s.name} ({s.category})" for s in SIMULATION_SCENARIOS]
    selected_idx = st.selectbox("Select Predefined Simulation Scenario:", range(len(scenario_names)), format_func=lambda i: scenario_names[i])
    current_scenario = SIMULATION_SCENARIOS[selected_idx]

    # Scenario details card
    with st.container():
        st.markdown(f"### Scenario: {current_scenario.name}")
        st.write(current_scenario.description)

        c1, c2, c3 = st.columns(3)
        c1.markdown(f"**Target Host:** `{current_scenario.target_host}`")
        c2.markdown(f"**Target Port:** `{current_scenario.target_port}`")
        c3.markdown(f"**Category:** `{current_scenario.category}`")

        st.info(f"**Simulated User Symptom:** \"{current_scenario.simulated_symptom}\"")

    c_run, c_reset = st.columns([2, 1])
    with c_run:
        run_sim = st.button("▶️ Execute Controlled Simulation", type="primary", use_container_width=True)
    with c_reset:
        reset_sim = st.button("🔄 Reset Lab State", use_container_width=True)

    if reset_sim:
        st.session_state["sim_session"] = None
        st.success("Simulation lab state reset to initial baseline.")
        st.rerun()

    if run_sim:
        engine = SimulationLabEngine()
        prog_bar = st.progress(0)
        status_box = st.empty()

        def on_sim_progress(res, cur_step, total):
            prog_bar.progress(cur_step / total)
            status_box.text(f"Simulation test: {res.test_name} -> {res.status.value}")

        sim_session = engine.run_simulation(current_scenario, on_progress=on_sim_progress)
        prog_bar.progress(1.0)
        status_box.text("Simulation analysis completed.")
        st.session_state["sim_session"] = sim_session

    # Display simulation session results and compare with hidden expected fault
    sim_session: DiagnosticSession = st.session_state.get("sim_session")
    if sim_session and sim_session.is_simulated:
        st.markdown("---")
        st.subheader("Simulation Results & Evidence")

        # 1. Prediction vs Ground Truth Comparison
        top_h = sim_session.hypotheses[0] if sim_session.hypotheses else None
        predicted_cause = top_h.title if top_h else "Inconclusive"
        expected_cause = current_scenario.expected_cause

        is_match = (
            expected_cause.lower() in predicted_cause.lower()
            or predicted_cause.lower() in expected_cause.lower()
        )

        st.markdown("### 🎯 Ground-Truth Evaluation Comparison")
        cmp_col1, cmp_col2, cmp_col3 = st.columns(3)
        with cmp_col1:
            st.markdown("**Expected Ground-Truth Fault**")
            st.info(f"**{expected_cause}**")
        with cmp_col2:
            st.markdown("**Engine Predicted Root Cause**")
            st.warning(f"**{predicted_cause}**")
        with cmp_col3:
            st.markdown("**Outcome Verification**")
            if is_match:
                st.success("✅ CORRECT MATCH (100% Accuracy)")
            else:
                st.error("❌ MISMATCH")

        # 2. Evidence timeline
        st.markdown("### Synthetic Diagnostic Timeline")
        for t in sim_session.test_results:
            icon = "🟢" if t.status == TestStatus.PASS else "🔴" if t.status == TestStatus.FAIL else "🟡"
            with st.expander(f"{icon} **{t.test_name}** ({t.status.value})"):
                st.write(t.human_explanation)
                for e in t.evidence:
                    st.write(f"- `{e}`")

        # 3. Recommendations
        st.markdown("### Advisory Remediation")
        for r in sim_session.recommendations:
            st.write(f"- **{r.observed_issue}**: {r.steps_to_follow[0]}")

        # 4. Reports Export
        col_rep1, col_rep2 = st.columns(2)
        with col_rep1:
            html_data = generate_html_report(sim_session)
            st.download_button(
                label="📄 Download HTML Simulation Report",
                data=html_data,
                file_name=f"sim_report_{sim_session.session_id[:8]}.html",
                mime="text/html",
                use_container_width=True
            )
        with col_rep2:
            pdf_data = generate_pdf_report(sim_session)
            if pdf_data:
                st.download_button(
                    label="📑 Download PDF Simulation Report",
                    data=pdf_data,
                    file_name=f"sim_report_{sim_session.session_id[:8]}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
