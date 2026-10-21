"""Module K: Evaluation and Performance Metrics Dashboard."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from storage.database import get_evaluation_metrics


def render_evaluation():
    st.header("Evaluation & Benchmark Metrics")
    st.caption(
        "Quantitative benchmark of diagnostic engine accuracy across controlled simulation runs. "
        "Separates controlled simulation labels from uncontrolled live runs."
    )

    metrics = get_evaluation_metrics()
    total = metrics["total_runs"]

    if total == 0:
        st.info("No simulation evaluation runs logged yet. Execute scenarios in the 'Fault Simulation Lab' to populate benchmark data.")
        return

    # Key metric tiles
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Scenarios Tested", total)
    with c2:
        st.metric("Correct Diagnoses", metrics["correct_runs"])
    with c3:
        st.metric("Diagnosis Accuracy", f"{metrics['accuracy']}%")
    with c4:
        st.metric("Avg Duration / Run", f"{metrics['avg_duration']}s")

    st.markdown("---")

    # Breakdown by category/scenario
    st.subheader("Accuracy Breakdown by Fault Scenario")
    categories = metrics["category_breakdown"]
    if categories:
        data = []
        for scen_id, stats in categories.items():
            tot = stats["total"]
            corr = stats["correct"]
            acc = round((corr / tot) * 100, 1) if tot > 0 else 0
            data.append({
                "Scenario ID": scen_id,
                "Expected Fault": stats["expected"][:30],
                "Runs": tot,
                "Correct": corr,
                "Accuracy (%)": acc
            })
        df = pd.DataFrame(data)

        # Plot bar chart with Plotly
        fig = px.bar(
            df,
            x="Scenario ID",
            y="Accuracy (%)",
            color="Accuracy (%)",
            color_continuous_scale="Viridis",
            text="Accuracy (%)",
            title="Classification Accuracy per Scenario"
        )
        fig.update_layout(
            yaxis=dict(range=[0, 105]),
            template="plotly_dark",
            plot_bgcolor="rgba(15, 23, 42, 0.45)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="'Inter', sans-serif", color="#e2e8f0")
        )
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df, use_container_width=True)

    # Confusion / Recent Records
    st.subheader("Recent Evaluation Records")
    recent = metrics.get("recent_records", [])
    if recent:
        rec_data = []
        for r in recent:
            rec_data.append({
                "Timestamp": r["timestamp"][:19],
                "Scenario": r["scenario_id"],
                "Expected Ground-Truth": r["expected_cause"],
                "Predicted Cause": r["predicted_cause"],
                "Result": "✅ Correct" if r["is_correct"] == 1 else "❌ Mismatch",
                "Duration (s)": r["duration_seconds"]
            })
        st.dataframe(pd.DataFrame(rec_data), use_container_width=True)
