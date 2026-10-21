"""Monitoring and Alerting Data Models."""

from __future__ import annotations

import datetime
import uuid
from typing import Optional
from pydantic import BaseModel, Field


class MonitoringTarget(BaseModel):
    """Specification of an actively monitored network target."""
    target_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str
    host: str
    port: int = 443
    service_type: str = "https"
    interval_seconds: int = 60
    enabled: bool = True
    latency_threshold_ms: float = 150.0
    packet_loss_threshold_pct: float = 5.0
    alert_email: Optional[str] = None
    alert_slack_webhook: Optional[str] = None
    alert_generic_webhook: Optional[str] = None
    last_run: Optional[str] = None
    current_status: str = "UNKNOWN"  # HEALTHY, DEGRADED, DOWN, UNKNOWN


class MonitoringCheckRecord(BaseModel):
    """Execution telemetry record for an individual monitoring check."""
    check_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    target_id: str
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    status: str  # HEALTHY, DEGRADED, DOWN
    latency_ms: Optional[float] = None
    packet_loss_pct: float = 0.0
    session_id: Optional[str] = None
    summary: str = ""


class AlertNotification(BaseModel):
    """Log record of an alert dispatch."""
    alert_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    target_id: str
    target_name: str
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    alert_channel: str  # EMAIL, SLACK, WEBHOOK
    status: str  # SENT, FAILED, SIMULATED
    message: str = ""
