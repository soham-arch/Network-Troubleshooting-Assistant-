"""FastAPI Request and Response Models."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DiagnoseRequest(BaseModel):
    """Payload to trigger an autonomous network investigation."""
    symptom: str = Field(..., description="Natural language problem description", examples=["Cannot connect to web service"])
    target_host: Optional[str] = Field(None, description="Hostname or IP address to diagnose", examples=["google.com"])
    target_port: Optional[int] = Field(None, description="Target destination port", examples=[443])
    service_type: Optional[str] = Field(None, description="Protocol service (https, http, tcp)", examples=["https"])
    run_traceroute: bool = Field(False, description="Whether to include stage 8 route traceroute")


class BatchDiagnoseRequest(BaseModel):
    """Payload to trigger multi-target diagnostic execution."""
    targets: List[str] = Field(..., description="List of hostnames, URLs or CSV lines", examples=[["google.com", "github.com:443", "1.1.1.1"]])
    symptom: Optional[str] = Field("Batch network health audit", description="Audit description")
    concurrency: Optional[int] = Field(4, description="Concurrency limit (1-8)", ge=1, le=8)


class TicketCreateRequest(BaseModel):
    """Payload to create an incident ticket from a session."""
    session_id: str = Field(..., description="Diagnostic session ID to generate ticket for")
    system: str = Field("jira", description="'jira' or 'webhook'")
    summary: Optional[str] = Field(None, description="Optional custom ticket summary")
    issue_type: Optional[str] = Field("Bug", description="Jira issue type (e.g. Bug, Incident, Task)")
    custom_webhook_url: Optional[str] = Field(None, description="Target webhook URL if using webhook system")
