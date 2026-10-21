"""LLM-Assisted Explanation & Remediation Plan Service.

Generates executive summaries, technical deep dives, and prioritized remediation
plans grounded strictly on the deterministic DiagnosticSession.
The deterministic root-cause engine remains the authoritative source of truth.
"""

from __future__ import annotations

import logging
from typing import Optional

from diagnostics.models import DiagnosticSession, TestStatus
from llm.client import LLMClient

logger = logging.getLogger(__name__)


def generate_session_explanation(
    session: DiagnosticSession,
    llm_client: Optional[LLMClient] = None
) -> str:
    """
    Generates a human-readable explanation and remediation plan.
    Uses LLM when configured, strictly grounded in the session's deterministic findings.
    Falls back gracefully to a structured deterministic summary.
    """
    if llm_client and llm_client.is_configured():
        llm_response = _generate_llm_explanation(session, llm_client)
        if llm_response:
            return llm_response

    return _generate_deterministic_explanation(session)


def _generate_llm_explanation(session: DiagnosticSession, client: LLMClient) -> Optional[str]:
    """Calls configured LLM with strict grounding in deterministic facts."""
    top_hypothesis = session.hypotheses[0] if session.hypotheses else None
    top_cause = top_hypothesis.probable_root_cause if top_hypothesis else "Inconclusive / No anomaly found"
    confidence = f"{top_hypothesis.confidence.value} ({int(top_hypothesis.confidence_score * 100)}%)" if top_hypothesis else "N/A"

    failed_tests = [
        f"{t.test_name} ({t.stage.value}): {t.human_explanation} [Evidence: {'; '.join(t.evidence[:2])}]"
        for t in session.test_results if t.status in (TestStatus.FAIL, TestStatus.ERROR)
    ]
    passed_tests = [t.test_name for t in session.test_results if t.status == TestStatus.PASS]

    system_prompt = (
        "You are an expert Network Site Reliability Engineer (SRE). "
        "A deterministic diagnostic engine has already performed rigorous network tests and determined the root cause. "
        "YOUR ROLE: Translate these deterministic findings into an articulate, professional executive explanation "
        "and actionable remediation plan. "
        "CRITICAL RULE: The deterministic engine is the ABSOLUTE SOURCE OF TRUTH. "
        "DO NOT contradict the determined root cause. DO NOT hallucinate alternative primary causes.\n"
        "Format your response in GitHub-flavored Markdown with the following sections:\n"
        "### 📋 Executive Summary\n"
        "### 🔍 Technical Root Cause Breakdown\n"
        "### 🛠️ Prioritized Remediation Action Plan\n"
        "### 🛡️ Safety & Verification Checklist\n"
    )

    user_prompt = (
        f"**User Reported Symptom:** {session.user_symptom}\n"
        f"**Target:** {session.target_host or 'N/A'}:{session.target_port or 'N/A'} (Service: {session.service_type or 'N/A'})\n"
        f"**Authoritative Root Cause:** {top_cause}\n"
        f"**Confidence Level:** {confidence}\n"
        f"**Failed Tests:**\n{chr(10).join(f'- {f}' for f in failed_tests) if failed_tests else 'None (all tests passed)'}\n"
        f"**Passed Tests:** {', '.join(passed_tests) if passed_tests else 'None'}\n"
        f"**Action Recommended by Deterministic Engine:** "
        f"{top_hypothesis.suggested_corrective_action if top_hypothesis else 'Verify service'}\n\n"
        "Write the grounded explanation now."
    )

    try:
        explanation = client.generate_completion(system_prompt, user_prompt)
        if explanation and len(explanation.strip()) > 50:
            return explanation
    except Exception as e:
        logger.warning(f"Failed to generate LLM explanation: {e}")

    return None


def _generate_deterministic_explanation(session: DiagnosticSession) -> str:
    """High-quality deterministic fallback explanation when LLM is unavailable."""
    top_h = session.hypotheses[0] if session.hypotheses else None

    lines = []
    lines.append("### 📋 Executive Summary")
    if top_h:
        lines.append(
            f"The network diagnostic investigation concluded with **{top_h.confidence.value}** confidence "
            f"({int(top_h.confidence_score * 100)}%) that the primary root cause of the incident is: "
            f"**{top_h.title}**."
        )
        lines.append(f"\n> **Diagnostic Finding:** {top_h.probable_root_cause}\n")
    else:
        lines.append("All network diagnostic stages completed within normal operational parameters. No root cause anomaly was triggered.")

    lines.append("### 🔍 Technical Root Cause Breakdown")
    if top_h and top_h.supporting_evidence:
        lines.append("**Empirical Evidence Supporting Diagnosis:**")
        for ev in top_h.supporting_evidence:
            lines.append(f"- {ev}")
    else:
        lines.append("Baseline network connectivity and transport stages functioned without error.")

    if top_h and top_h.alternative_explanations:
        lines.append("\n**Alternative Technical Considerations:**")
        for alt in top_h.alternative_explanations:
            lines.append(f"- {alt}")

    lines.append("\n### 🛠️ Prioritized Remediation Action Plan")
    if top_h:
        lines.append(f"> **Primary Recommended Action:** {top_h.suggested_corrective_action}\n")

    if session.recommendations:
        for idx, rec in enumerate(session.recommendations, 1):
            lines.append(f"**Step {idx}: {rec.observed_issue}**")
            lines.append(f"*{rec.why_it_helps}*")
            for step in rec.steps_to_follow:
                lines.append(f"1. {step}")
            lines.append(f"*Expected Outcome:* {rec.expected_outcome}")
            lines.append(f"*Caution:* {rec.risks_and_limitations}\n")
    elif top_h:
        lines.append(f"1. {top_h.suggested_corrective_action}")
        lines.append(f"2. {top_h.recommended_next_step}")
    else:
        lines.append("No remediation required. The tested target is reachable and functioning.")

    lines.append("### 🛡️ Safety & Verification Checklist")
    if top_h and top_h.verification_steps:
        for v in top_h.verification_steps:
            lines.append(f"- [ ] {v}")
    else:
        lines.append("- [ ] Re-run verification diagnostic to ensure steady-state operation.")

    return "\n".join(lines)
