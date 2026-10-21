"""Diagnostic Models and Data Structures.

Provides immutable, typed, well-documented schemas for all stages of network investigation,
test evidence, findings, recommendations, and session histories.
"""

from __future__ import annotations

import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TestStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"


class ConfidenceLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class DiagnosticStage(str, Enum):
    LOCAL_CONFIG = "local_config"
    GATEWAY = "gateway"
    DNS = "dns"
    DESTINATION = "destination"
    PORT = "port"
    HTTP_TLS = "http_tls"
    LATENCY = "latency"
    TRACEROUTE = "traceroute"


class TestResult(BaseModel):
    """Represents the structured output of an individual diagnostic check."""
    test_id: str
    stage: DiagnosticStage
    test_name: str
    start_time: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    end_time: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    status: TestStatus
    measured_values: Dict[str, Any] = Field(default_factory=dict)
    human_explanation: str
    evidence: List[str] = Field(default_factory=list)
    limitations: Optional[str] = None
    is_simulated: bool = False
    skipped_reason: Optional[str] = None


class RootCauseHypothesis(BaseModel):
    """Ranked root-cause prediction backed by concrete evidence."""
    hypothesis_id: str
    title: str
    probable_root_cause: str
    confidence: ConfidenceLevel
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    supporting_evidence: List[str] = Field(default_factory=list)
    contradicting_evidence: List[str] = Field(default_factory=list)
    alternative_explanations: List[str] = Field(default_factory=list)
    recommended_next_step: str
    suggested_corrective_action: str
    verification_steps: List[str] = Field(default_factory=list)


class DiagnosticRecommendation(BaseModel):
    """Safe, actionable advisory recommendation."""
    id: str
    observed_issue: str
    why_it_helps: str
    steps_to_follow: List[str]
    expected_outcome: str
    how_to_verify: str
    risks_and_limitations: str
    is_advisory_only: bool = True


class VerificationOutcome(str, Enum):
    VERIFIED_RECOVERY = "VERIFIED_RECOVERY"
    PARTIAL_IMPROVEMENT = "PARTIAL_IMPROVEMENT"
    ISSUE_PERSISTS = "ISSUE_PERSISTS"
    INCONCLUSIVE = "INCONCLUSIVE"


class DiagnosticSession(BaseModel):
    """Complete diagnostic investigation record."""
    session_id: str
    start_time: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    end_time: Optional[str] = None
    user_symptom: str
    target_host: Optional[str] = None
    target_port: Optional[int] = None
    service_type: Optional[str] = None
    is_simulated: bool = False
    simulation_scenario_id: Optional[str] = None
    test_results: List[TestResult] = Field(default_factory=list)
    hypotheses: List[RootCauseHypothesis] = Field(default_factory=list)
    recommendations: List[DiagnosticRecommendation] = Field(default_factory=list)
    verification_outcome: Optional[VerificationOutcome] = None
    verification_notes: Optional[str] = None
    schema_version: str = "1.0.0"
