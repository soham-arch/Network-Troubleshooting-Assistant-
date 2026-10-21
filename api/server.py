"""FastAPI REST API Server for Network Troubleshooting Assistant.

Exposes programmatic endpoints for running investigations, querying history,
launching batch audits, managing continuous monitoring targets, and ticketing.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from api.models import BatchDiagnoseRequest, DiagnoseRequest, TicketCreateRequest
from batch.orchestrator import BatchDiagnosticOrchestrator, BatchTargetItem
from diagnostics.models import DiagnosticSession
from engine.orchestrator import DiagnosticOrchestrator
from integrations.ticketing import GenericTicketWebhookConnector, JiraConnector
from monitoring.models import MonitoringTarget
from monitoring.scheduler import monitoring_scheduler
from storage.database import (
    delete_monitoring_target,
    get_monitoring_history,
    get_monitoring_targets,
    get_session,
    list_sessions,
    save_monitoring_target,
)
from utils.validation import validate_hostname_or_ip, validate_port

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Network Troubleshooting Assistant API",
    description="Autonomous network diagnostic, monitoring, and root-cause analysis REST API.",
    version="2.0.0"
)

# Enable CORS for web integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health", tags=["System"])
def health_check() -> Dict[str, Any]:
    """Returns service health status and scheduler state."""
    return {
        "status": "online",
        "service": "Network Troubleshooting Assistant",
        "scheduler_running": monitoring_scheduler.is_running()
    }


@app.post("/api/v1/diagnose", response_model=Dict[str, Any], tags=["Diagnostics"])
def trigger_diagnosis(req: DiagnoseRequest) -> Dict[str, Any]:
    """Triggers an adaptive multi-stage network investigation on a target."""
    if not req.symptom.strip():
        raise HTTPException(status_code=400, detail="Problem symptom description is required.")

    clean_host = None
    if req.target_host and req.target_host.strip():
        is_valid, clean_host, err = validate_hostname_or_ip(req.target_host.strip())
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid target host: {err}")

    clean_port = None
    if req.target_port is not None:
        is_valid, clean_port, err = validate_port(req.target_port)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid target port: {err}")

    orchestrator = DiagnosticOrchestrator()
    session = orchestrator.run_investigation(
        user_symptom=req.symptom,
        target_host=clean_host,
        target_port=clean_port,
        service_type=req.service_type,
        run_traceroute=req.run_traceroute
    )

    return session.model_dump()


@app.get("/api/v1/sessions", tags=["Sessions"])
def get_sessions(
    limit: int = Query(50, ge=1, le=200),
    is_simulated: Optional[bool] = None,
    search: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Lists historical diagnostic sessions."""
    return list_sessions(limit=limit, is_simulated=is_simulated, search_query=search)


@app.get("/api/v1/sessions/{session_id}", tags=["Sessions"])
def get_session_by_id(session_id: str) -> Dict[str, Any]:
    """Retrieves full investigation telemetry and findings for a specific session."""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    return session.model_dump()


@app.post("/api/v1/batch-diagnose", tags=["Batch"])
def trigger_batch_diagnose(req: BatchDiagnoseRequest) -> Dict[str, Any]:
    """Executes multi-target diagnosis in parallel with bounded concurrency."""
    raw_lines = "\n".join(req.targets)
    targets = BatchDiagnosticOrchestrator.parse_targets(raw_lines)
    if not targets:
        raise HTTPException(status_code=400, detail="No valid target hosts found in request payload.")

    batch_orchestrator = BatchDiagnosticOrchestrator(max_concurrency=req.concurrency or 4)
    report = batch_orchestrator.run_batch(
        targets=targets,
        symptom_description=req.symptom or "Batch network health audit"
    )

    return report.model_dump()


@app.get("/api/v1/monitoring/targets", tags=["Monitoring"])
def list_monitoring_targets() -> List[Dict[str, Any]]:
    """Returns all configured continuous monitoring targets."""
    targets = get_monitoring_targets()
    return [t.model_dump() for t in targets]


@app.post("/api/v1/monitoring/targets", status_code=status.HTTP_201_CREATED, tags=["Monitoring"])
def add_monitoring_target(target: MonitoringTarget) -> Dict[str, Any]:
    """Registers or updates a continuous monitoring target."""
    is_valid_host, clean_host, err = validate_hostname_or_ip(target.host)
    if not is_valid_host:
        raise HTTPException(status_code=400, detail=f"Invalid target host: {err}")

    is_valid_port, clean_port, err = validate_port(target.port)
    if not is_valid_port:
        raise HTTPException(status_code=400, detail=f"Invalid target port: {err}")

    target.host = clean_host
    target.port = clean_port
    save_monitoring_target(target)
    return {"message": "Monitoring target saved successfully.", "target": target.model_dump()}


@app.delete("/api/v1/monitoring/targets/{target_id}", tags=["Monitoring"])
def remove_monitoring_target(target_id: str) -> Dict[str, Any]:
    """Deletes a continuous monitoring target."""
    deleted = delete_monitoring_target(target_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Target not found.")
    return {"message": "Target deleted successfully."}


@app.post("/api/v1/monitoring/targets/{target_id}/check-now", tags=["Monitoring"])
def check_target_on_demand(target_id: str) -> Dict[str, Any]:
    """Runs an immediate on-demand diagnostic probe for a target."""
    targets = [t for t in get_monitoring_targets() if t.target_id == target_id]
    if not targets:
        raise HTTPException(status_code=404, detail="Target not found.")

    res = monitoring_scheduler.execute_check(targets[0])
    return res.model_dump()


@app.get("/api/v1/monitoring/history", tags=["Monitoring"])
def get_monitoring_telemetry(
    target_id: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500)
) -> List[Dict[str, Any]]:
    """Retrieves check telemetry records."""
    return get_monitoring_history(target_id=target_id, limit=limit)


@app.post("/api/v1/tickets/create", tags=["Ticketing"])
def create_incident_ticket(req: TicketCreateRequest) -> Dict[str, Any]:
    """Generates an incident ticket in Jira or posts to an ITSM webhook."""
    session = get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{req.session_id}' not found.")

    if req.system.lower() == "jira":
        connector = JiraConnector()
        res = connector.create_incident_ticket(session, summary=req.summary, issue_type=req.issue_type or "Bug")
        return res
    elif req.system.lower() == "webhook":
        res = GenericTicketWebhookConnector.send_incident_to_webhook(session, webhook_url=req.custom_webhook_url)
        return res
    else:
        raise HTTPException(status_code=400, detail="Invalid ticketing system. Must be 'jira' or 'webhook'.")
