"""Unit tests for input validation, security policies, and models."""

import pytest
from diagnostics.models import (
    ConfidenceLevel,
    DiagnosticSession,
    DiagnosticStage,
    TestResult,
    TestStatus,
)
from utils.validation import (
    validate_hostname_or_ip,
    validate_port,
)


def test_validate_hostname():
    # Valid hostnames
    valid, host, err = validate_hostname_or_ip("example.com")
    assert valid is True
    assert host == "example.com"
    assert err is None

    valid, host, err = validate_hostname_or_ip("sub.domain.co.uk")
    assert valid is True

    # Invalid hostnames with dangerous metacharacters
    valid, _, err = validate_hostname_or_ip("example.com; rm -rf /")
    assert valid is False
    assert "illegal characters" in err

    valid, _, err = validate_hostname_or_ip("google.com && dir")
    assert valid is False


def test_validate_ip_addresses():
    # Valid IPv4
    valid, ip, _ = validate_hostname_or_ip("192.168.1.1")
    assert valid is True
    assert ip == "192.168.1.1"

    # Cloud metadata link-local address should be blocked
    valid, _, err = validate_hostname_or_ip("169.254.169.254")
    assert valid is False
    assert "cloud metadata" in err.lower() or "prohibited" in err.lower()


def test_validate_port():
    valid, port, err = validate_port("80")
    assert valid is True
    assert port == 80

    valid, port, err = validate_port(443)
    assert valid is True
    assert port == 443

    # Out of range
    valid, _, err = validate_port("70000")
    assert valid is False
    assert "out of range" in err

    # Non-integer
    valid, _, err = validate_port("http")
    assert valid is False


def test_diagnostic_models_serialization():
    res = TestResult(
        test_id="test_01",
        stage=DiagnosticStage.DNS,
        test_name="DNS Lookup",
        status=TestStatus.PASS,
        measured_values={"ips": ["1.1.1.1"]},
        human_explanation="Lookup succeeded",
        evidence=["Resolved to 1.1.1.1"]
    )
    json_str = res.model_dump_json()
    assert "DNS Lookup" in json_str

    deserialized = TestResult.model_validate_json(json_str)
    assert deserialized.status == TestStatus.PASS
    assert deserialized.stage == DiagnosticStage.DNS
