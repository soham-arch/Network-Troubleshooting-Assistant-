"""Unit tests for Natural Language Symptom Intake & LLM Grounded Explanations."""

import pytest
from diagnostics.models import (
    ConfidenceLevel,
    DiagnosticRecommendation,
    DiagnosticSession,
    DiagnosticStage,
    RootCauseHypothesis,
    TestResult,
    TestStatus,
)
from llm.client import LLMClient
from llm.explanation_service import generate_session_explanation
from llm.symptom_parser import parse_symptom


def test_parse_web_symptom_with_url():
    text = "The web portal https://app.corp.internal:8443 is showing 502 bad gateway"
    parsed = parse_symptom(text)
    assert parsed.target_host == "app.corp.internal"
    assert parsed.target_port == 8443
    assert parsed.service_type == "https"
    assert parsed.category == "WEB_SERVICE_FAILURE"
    assert "http_tls" in parsed.recommended_stages


def test_parse_voip_symptom():
    text = "Teams calls are dropping and stuttering with heavy lag to 10.20.30.40"
    parsed = parse_symptom(text)
    assert parsed.target_host == "10.20.30.40"
    assert parsed.category == "VOIP_REALTIME_DEGRADATION"
    assert "latency" in parsed.recommended_stages
    assert "traceroute" in parsed.recommended_stages


def test_parse_dns_symptom():
    text = "DNS name lookup failing for database.production.net"
    parsed = parse_symptom(text)
    assert parsed.target_host == "database.production.net"
    assert parsed.category == "DNS_RESOLUTION_ISSUE"
    assert "dns" in parsed.recommended_stages


def test_deterministic_explanation_grounding():
    session = DiagnosticSession(
        session_id="test-grounding-123",
        user_symptom="Can't connect to intranet",
        target_host="192.168.1.50",
        target_port=80,
        hypotheses=[
            RootCauseHypothesis(
                hypothesis_id="h1",
                title="TCP Connection Refused",
                probable_root_cause="Remote host actively refused the TCP SYN on port 80",
                confidence=ConfidenceLevel.HIGH,
                confidence_score=0.95,
                supporting_evidence=["TCP RST packet received"],
                recommended_next_step="Check web server daemon",
                suggested_corrective_action="Start the HTTP service on target"
            )
        ],
        recommendations=[
            DiagnosticRecommendation(
                id="rec1",
                observed_issue="TCP port 80 closed",
                why_it_helps="Allows web traffic",
                steps_to_follow=["Verify systemctl status nginx"],
                expected_outcome="Port 80 begins listening",
                how_to_verify="nc -zv 192.168.1.50 80",
                risks_and_limitations="None"
            )
        ]
    )

    client = LLMClient(provider="none")
    explanation = generate_session_explanation(session, client)

    # Explanation must strictly feature the authoritative hypothesis title and finding
    assert "TCP Connection Refused" in explanation
    assert "TCP RST packet received" in explanation
    assert "Start the HTTP service on target" in explanation
    assert "Executive Summary" in explanation
