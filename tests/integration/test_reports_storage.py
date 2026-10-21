"""Integration tests for reports generation and database persistence."""

import os
import pytest
from diagnostics.models import (
    ConfidenceLevel,
    DiagnosticRecommendation,
    DiagnosticSession,
    DiagnosticStage,
    RootCauseHypothesis,
    TestResult,
    TestStatus,
    VerificationOutcome,
)
from reports.html_report import generate_html_report
from reports.pdf_report import generate_pdf_report
from storage.database import delete_session, get_session, save_session


def test_session_persistence_and_reports(tmp_path):
    test_db = str(tmp_path / "nta_test.db")

    session = DiagnosticSession(
        session_id="integration_sess_01",
        user_symptom="Website is not loading at all",
        target_host="test.org",
        target_port=443,
        service_type="https",
        test_results=[
            TestResult(
                test_id="t1",
                stage=DiagnosticStage.LOCAL_CONFIG,
                test_name="Local Config",
                status=TestStatus.PASS,
                human_explanation="Local IP active",
                evidence=["192.168.1.5 assigned"]
            ),
            TestResult(
                test_id="t2",
                stage=DiagnosticStage.DNS,
                test_name="DNS Hostname Resolution",
                status=TestStatus.PASS,
                human_explanation="Resolved to 93.184.216.34",
                evidence=["Lookup in 12ms"]
            )
        ],
        hypotheses=[
            RootCauseHypothesis(
                hypothesis_id="h1",
                title="Healthy Baseline",
                probable_root_cause="All layers operational",
                confidence=ConfidenceLevel.HIGH,
                confidence_score=0.9,
                supporting_evidence=["DNS and IP passed"],
                recommended_next_step="Inspect browser cache",
                suggested_corrective_action="No network action required"
            )
        ],
        recommendations=[
            DiagnosticRecommendation(
                id="r1",
                observed_issue="No network fault",
                why_it_helps="Confirms network is up",
                steps_to_follow=["Open in private tab"],
                expected_outcome="Loads normally",
                how_to_verify="Verify in browser",
                risks_and_limitations="None"
            )
        ],
        verification_outcome=VerificationOutcome.VERIFIED_RECOVERY
    )

    # 1. Test SQLite storage
    save_session(session, db_path=test_db)
    loaded = get_session("integration_sess_01", db_path=test_db)
    assert loaded is not None
    assert loaded.session_id == "integration_sess_01"
    assert loaded.user_symptom == "Website is not loading at all"
    assert len(loaded.test_results) == 2
    assert loaded.verification_outcome == VerificationOutcome.VERIFIED_RECOVERY

    # 2. Test HTML report generation
    html_out = generate_html_report(loaded)
    assert "<!DOCTYPE html>" in html_out
    assert "Website is not loading at all" in html_out
    assert "Healthy Baseline" in html_out
    assert "VERIFIED_RECOVERY" in html_out

    # 3. Test PDF report generation
    pdf_bytes = generate_pdf_report(loaded)
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 500  # PDF binary output produced
    assert pdf_bytes.startswith(b"%PDF")

    # 4. Test delete
    deleted = delete_session("integration_sess_01", db_path=test_db)
    assert deleted is True
    assert get_session("integration_sess_01", db_path=test_db) is None
