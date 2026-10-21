"""Module I: Incident History View."""

import streamlit as st
from reports.html_report import generate_html_report
from reports.pdf_report import generate_pdf_report
from storage.database import clear_all_sessions, delete_session, get_session, list_sessions


def render_history():
    st.header("Incident History & Session Archive")
    st.caption("Inspect, filter, export, and manage past diagnostic and simulation investigations.")

    c_filter, c_search, c_clear = st.columns([2, 3, 2])
    with c_filter:
        mode_filter = st.selectbox("Filter Mode", ["All Sessions", "Live Only", "Simulated Only"])
    with c_search:
        search_query = st.text_input("Search (Symptom, Host, Cause)", "")
    with c_clear:
        st.write("")
        st.write("")
        if st.button("🗑️ Clear All History", type="secondary"):
            clear_all_sessions()
            st.success("History cleared.")
            st.rerun()

    is_sim = None
    if mode_filter == "Live Only":
        is_sim = False
    elif mode_filter == "Simulated Only":
        is_sim = True

    sessions = list_sessions(limit=50, is_simulated=is_sim, search_query=search_query)

    if not sessions:
        st.info("No recorded incidents found matching the filter.")
        return

    st.markdown(f"**Found {len(sessions)} records**")

    for s in sessions:
        sess_id = s["session_id"]
        is_simulated = s["is_simulated"]
        mode_badge = "🧪 SIMULATED" if is_simulated else "🌐 LIVE"
        top_cause = s["top_hypothesis"] or "No fault"
        conf = s["top_confidence"] or "LOW"

        with st.expander(f"{mode_badge} &bull; **{s['start_time'][:19]}** &bull; Target: `{s['target_host'] or 'Local'}` &bull; {top_cause[:45]}"):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**Symptom:** {s['user_symptom']}")
                st.markdown(f"**Diagnosis:** `{top_cause}` (Confidence: {conf})")
                if s["verification_outcome"]:
                    st.markdown(f"**Verification Outcome:** `{s['verification_outcome']}`")
            with c2:
                if st.button("Delete Session", key=f"del_{sess_id}"):
                    delete_session(sess_id)
                    st.success("Deleted session.")
                    st.rerun()

            # Load full session for download
            full_session = get_session(sess_id)
            if full_session:
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    html_content = generate_html_report(full_session)
                    st.download_button(
                        label="📄 Download HTML Report",
                        data=html_content,
                        file_name=f"report_{sess_id[:8]}.html",
                        mime="text/html",
                        key=f"dl_html_{sess_id}"
                    )
                with col_d2:
                    pdf_content = generate_pdf_report(full_session)
                    if pdf_content:
                        st.download_button(
                            label="📑 Download PDF Report",
                            data=pdf_content,
                            file_name=f"report_{sess_id[:8]}.pdf",
                            mime="application/pdf",
                            key=f"dl_pdf_{sess_id}"
                        )
