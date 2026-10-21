"""Integration tests for FastAPI REST API Endpoints."""

import pytest
from fastapi.testclient import TestClient
from api.server import app

client = TestClient(app)


def test_health_check_endpoint():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert "scheduler_running" in data


def test_diagnose_endpoint_validation():
    # Empty symptom should fail validation
    res = client.post("/api/v1/diagnose", json={"symptom": "", "target_host": "google.com"})
    assert res.status_code == 400

    # Blocked link-local metadata IP should fail RFC validation
    res = client.post("/api/v1/diagnose", json={"symptom": "Blocked test", "target_host": "169.254.169.254"})
    assert res.status_code == 400


def test_monitoring_targets_crud():
    payload = {
        "name": "Integration Test Host",
        "host": "127.0.0.1",
        "port": 80,
        "service_type": "http",
        "interval_seconds": 60
    }
    create_res = client.post("/api/v1/monitoring/targets", json=payload)
    assert create_res.status_code == 201
    created_target = create_res.json()["target"]
    target_id = created_target["target_id"]

    # Verify listing
    list_res = client.get("/api/v1/monitoring/targets")
    assert list_res.status_code == 200
    assert any(t["target_id"] == target_id for t in list_res.json())

    # Delete
    del_res = client.delete(f"/api/v1/monitoring/targets/{target_id}")
    assert del_res.status_code == 200


def test_ticket_creation_simulated():
    # Trigger diagnosis on loopback
    diag_res = client.post("/api/v1/diagnose", json={
        "symptom": "Test incident for ticketing",
        "target_host": "127.0.0.1",
        "target_port": 80,
        "service_type": "http"
    })
    assert diag_res.status_code == 200
    session_id = diag_res.json()["session_id"]

    # Create ticket via API
    ticket_res = client.post("/api/v1/tickets/create", json={
        "session_id": session_id,
        "system": "jira"
    })
    assert ticket_res.status_code == 200
    data = ticket_res.json()
    assert data["success"] is True
    assert "ticket_id" in data
