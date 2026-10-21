"""Unit tests for deterministic root cause analysis engine."""

import pytest
from diagnostics.models import (
    ConfidenceLevel,
    DiagnosticStage,
    TestResult,
    TestStatus,
)
from engine.root_cause import analyze_test_results


def test_dns_failure_analysis():
    results = [
        TestResult(
            test_id="local_01",
            stage=DiagnosticStage.LOCAL_CONFIG,
            test_name="Local Config",
            status=TestStatus.PASS,
            human_explanation="IP assigned",
            evidence=["192.168.1.100 assigned"]
        ),
        TestResult(
            test_id="dns_01",
            stage=DiagnosticStage.DNS,
            test_name="DNS Lookup",
            status=TestStatus.FAIL,
            human_explanation="NXDOMAIN error",
            evidence=["Resolution failed: getaddrinfo failed"]
        )
    ]
    hypotheses, recs = analyze_test_results(results, target_host="unresolved.internal")
    assert len(hypotheses) > 0
    top = hypotheses[0]
    assert "DNS" in top.title
    assert top.confidence in (ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM)
    assert len(recs) > 0
    assert any("DNS" in r.observed_issue for r in recs)


def test_tcp_refused_analysis():
    results = [
        TestResult(
            test_id="local_01",
            stage=DiagnosticStage.LOCAL_CONFIG,
            test_name="Local Config",
            status=TestStatus.PASS,
            human_explanation="Interface up",
            evidence=[]
        ),
        TestResult(
            test_id="tcp_01",
            stage=DiagnosticStage.PORT,
            test_name="TCP Port",
            status=TestStatus.FAIL,
            measured_values={"error_type": "CONNECTION_REFUSED"},
            human_explanation="Connection refused",
            evidence=["TCP RST received"]
        )
    ]
    hypotheses, recs = analyze_test_results(results, target_host="127.0.0.1", target_port=9999)
    assert len(hypotheses) > 0
    top = hypotheses[0]
    assert "Refused" in top.title or "Closed" in top.title


def test_http_500_analysis():
    results = [
        TestResult(
            test_id="local_01",
            stage=DiagnosticStage.LOCAL_CONFIG,
            test_name="Local Config",
            status=TestStatus.PASS,
            human_explanation="Interface up",
            evidence=[]
        ),
        TestResult(
            test_id="http_01",
            stage=DiagnosticStage.HTTP_TLS,
            test_name="HTTP Health",
            status=TestStatus.FAIL,
            measured_values={"status_code": 500},
            human_explanation="Server 500 error",
            evidence=["HTTP 500 Internal Server Error"]
        )
    ]
    hypotheses, recs = analyze_test_results(results, target_host="api.corp.internal", target_port=80)
    assert len(hypotheses) > 0
    top = hypotheses[0]
    assert "HTTP 500" in top.title or "Application Server Error" in top.title
