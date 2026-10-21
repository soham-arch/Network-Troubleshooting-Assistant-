"""Unit tests for Multi-Target Batch Orchestrator."""

import pytest
from batch.orchestrator import BatchDiagnosticOrchestrator, BatchTargetItem


def test_parse_targets_csv_and_plain():
    raw = (
        "google.com,443,https,Google Search\n"
        "https://github.com\n"
        "1.1.1.1\n"
        "invalid..hostname@@"
    )
    targets = BatchDiagnosticOrchestrator.parse_targets(raw)
    # 3 valid targets, 1 invalid filtered out by RFC validation
    assert len(targets) == 3

    assert targets[0].host == "google.com"
    assert targets[0].port == 443
    assert targets[0].label == "Google Search"

    assert targets[1].host == "github.com"
    assert targets[1].port == 443

    assert targets[2].host == "1.1.1.1"


def test_batch_execution_mock():
    orchestrator = BatchDiagnosticOrchestrator(max_concurrency=2)
    targets = [
        BatchTargetItem(host="127.0.0.1", port=65500, service_type="tcp", label="Unused Port")
    ]
    report = orchestrator.run_batch(targets, symptom_description="Unit test audit")
    assert report.total_targets == 1
    assert len(report.results) == 1
    assert len(report.comparison_matrix) == 1
    # Port 65500 should be closed on loopback
    res = report.results[0]
    assert res.status in ("FAILED", "DEGRADED")
    assert len(report.ranked_problems) == 1
