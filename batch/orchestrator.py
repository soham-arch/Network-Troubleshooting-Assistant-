"""Concurrent Multi-Target & Batch Diagnostic Orchestrator.

Allows testing multiple targets (hosts, ports, URLs, CSV lists) concurrently
with bounded worker pools, computing comparison matrices and ranking problematic targets.
"""

from __future__ import annotations

import concurrent.futures
import csv
import datetime
import io
import logging
import re
import uuid
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field

from diagnostics.models import DiagnosticSession, DiagnosticStage, TestStatus
from engine.orchestrator import DiagnosticOrchestrator
from utils.validation import validate_hostname_or_ip, validate_port

logger = logging.getLogger(__name__)


class BatchTargetItem(BaseModel):
    """Specification of an individual diagnostic target in a batch."""
    target_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    host: str
    port: Optional[int] = 443
    service_type: Optional[str] = "https"
    label: Optional[str] = None


class BatchTargetResult(BaseModel):
    """Diagnostic outcome summary for an individual target in a batch."""
    target_id: str
    host: str
    port: Optional[int] = None
    service_type: Optional[str] = None
    label: Optional[str] = None
    session_id: str
    status: str  # HEALTHY, DEGRADED, FAILED, ERROR
    dns_status: str = "N/A"
    port_status: str = "N/A"
    http_status: str = "N/A"
    avg_latency_ms: Optional[float] = None
    packet_loss_pct: float = 0.0
    top_root_cause: str = "None"
    confidence: str = "LOW"
    severity_score: float = 0.0  # 0 to 100, higher means more severe
    failed_tests_count: int = 0
    duration_seconds: float = 0.0
    session: Optional[DiagnosticSession] = None


class BatchDiagnosisReport(BaseModel):
    """Aggregate report from a multi-target diagnostic run."""
    batch_id: str
    start_time: str
    end_time: str
    total_targets: int
    healthy_count: int
    degraded_count: int
    failed_count: int
    results: List[BatchTargetResult] = Field(default_factory=list)
    ranked_problems: List[BatchTargetResult] = Field(default_factory=list)
    comparison_matrix: List[Dict[str, Any]] = Field(default_factory=list)


class BatchDiagnosticOrchestrator:
    """Manages concurrent execution of diagnostics across multiple targets."""

    def __init__(self, db_path: str = "data/nta.db", max_concurrency: int = 4):
        self.db_path = db_path
        self.max_concurrency = min(max(1, max_concurrency), 8)  # Enforce 1-8 bounds

    @staticmethod
    def parse_targets(input_text_or_csv: str) -> List[BatchTargetItem]:
        """
        Parses multi-target input from raw text, CSV format, or newline-separated hosts.
        Supports:
        - google.com
        - https://github.com
        - 1.1.1.1,53,udp,Cloudflare DNS
        - api.service.internal,8080,http,Internal API
        """
        targets: List[BatchTargetItem] = []
        lines = [line.strip() for line in input_text_or_csv.strip().splitlines() if line.strip()]

        for line in lines:
            # Check if line is CSV header
            if line.lower().startswith("host") or line.lower().startswith("target"):
                continue

            host = ""
            port: Optional[int] = None
            service_type: Optional[str] = None
            label: Optional[str] = None

            # Check if line contains CSV commas
            if "," in line:
                reader = csv.reader(io.StringIO(line))
                try:
                    parts = next(reader)
                    if len(parts) >= 1:
                        host = parts[0].strip()
                    if len(parts) >= 2 and parts[1].strip():
                        try:
                            port = int(parts[1].strip())
                        except ValueError:
                            pass
                    if len(parts) >= 3 and parts[2].strip():
                        service_type = parts[2].strip().lower()
                    if len(parts) >= 4 and parts[3].strip():
                        label = parts[3].strip()
                except Exception:
                    host = line.split(",")[0].strip()
            else:
                # Plain URL or Host
                candidate = line.strip()
                if candidate.startswith("http://") or candidate.startswith("https://"):
                    m = re.match(r"(https?)://([^:/]+)(?::(\d+))?", candidate)
                    if m:
                        service_type = m.group(1).lower()
                        host = m.group(2)
                        port = int(m.group(3)) if m.group(3) else (443 if service_type == "https" else 80)
                elif ":" in candidate:
                    parts = candidate.split(":")
                    host = parts[0]
                    try:
                        port = int(parts[1])
                    except ValueError:
                        pass
                else:
                    host = candidate

            # Default port and service if omitted
            if not port:
                port = 443 if service_type == "https" else (80 if service_type == "http" else 80)
            if not service_type:
                service_type = "https" if port == 443 else "http"

            # Strict validation
            is_valid_host, clean_host, _ = validate_hostname_or_ip(host)
            is_valid_port, clean_port, _ = validate_port(port)

            if is_valid_host and is_valid_port:
                targets.append(BatchTargetItem(
                    host=clean_host,
                    port=clean_port,
                    service_type=service_type,
                    label=label or clean_host
                ))

        return targets

    def run_batch(
        self,
        targets: List[BatchTargetItem],
        symptom_description: str = "Automated batch network diagnostic check",
        on_progress: Optional[Callable[[int, int, BatchTargetResult], None]] = None
    ) -> BatchDiagnosisReport:
        """Executes diagnostics on target list using bounded thread pool."""
        start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        batch_id = str(uuid.uuid4())[:8]

        results: List[BatchTargetResult] = []
        total_targets = len(targets)
        completed_count = 0

        def diagnose_single(item: BatchTargetItem) -> BatchTargetResult:
            t_start = datetime.datetime.now()
            orchestrator = DiagnosticOrchestrator(db_path=self.db_path)
            try:
                session = orchestrator.run_investigation(
                    user_symptom=f"{symptom_description} [{item.label or item.host}]",
                    target_host=item.host,
                    target_port=item.port,
                    service_type=item.service_type,
                    run_traceroute=False
                )
                t_end = datetime.datetime.now()
                duration = round((t_end - t_start).total_seconds(), 2)
                return self._evaluate_target_result(item, session, duration)
            except Exception as e:
                logger.error(f"Batch diagnosis failed for target {item.host}: {e}")
                t_end = datetime.datetime.now()
                duration = round((t_end - t_start).total_seconds(), 2)
                return BatchTargetResult(
                    target_id=item.target_id,
                    host=item.host,
                    port=item.port,
                    service_type=item.service_type,
                    label=item.label,
                    session_id=str(uuid.uuid4()),
                    status="ERROR",
                    top_root_cause=f"Diagnostic error: {str(e)}",
                    severity_score=90.0,
                    duration_seconds=duration
                )

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrency) as executor:
            future_to_target = {executor.submit(diagnose_single, t): t for t in targets}
            for future in concurrent.futures.as_completed(future_to_target):
                res = future.result()
                results.append(res)
                completed_count += 1
                if on_progress:
                    on_progress(completed_count, total_targets, res)

        end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Compute summary counts
        healthy = sum(1 for r in results if r.status == "HEALTHY")
        degraded = sum(1 for r in results if r.status == "DEGRADED")
        failed = sum(1 for r in results if r.status in ("FAILED", "ERROR"))

        # Rank problems by severity descending
        ranked = sorted(
            [r for r in results if r.status != "HEALTHY"],
            key=lambda x: x.severity_score,
            reverse=True
        )

        # Build comparison matrix records
        matrix = []
        for r in results:
            matrix.append({
                "Target / Label": r.label or r.host,
                "Host": r.host,
                "Port": r.port,
                "Status": r.status,
                "DNS": r.dns_status,
                "Port Handshake": r.port_status,
                "HTTP/TLS": r.http_status,
                "Latency (ms)": f"{r.avg_latency_ms} ms" if r.avg_latency_ms is not None else "N/A",
                "Packet Loss": f"{r.packet_loss_pct}%",
                "Primary Finding": r.top_root_cause,
                "Severity": round(r.severity_score, 1)
            })

        return BatchDiagnosisReport(
            batch_id=batch_id,
            start_time=start_time,
            end_time=end_time,
            total_targets=total_targets,
            healthy_count=healthy,
            degraded_count=degraded,
            failed_count=failed,
            results=results,
            ranked_problems=ranked,
            comparison_matrix=matrix
        )

    def _evaluate_target_result(
        self,
        item: BatchTargetItem,
        session: DiagnosticSession,
        duration: float
    ) -> BatchTargetResult:
        """Calculates stage breakdown, overall health status, and severity score."""
        dns_status = "N/A"
        port_status = "N/A"
        http_status = "N/A"
        avg_latency = None
        packet_loss = 0.0
        failed_count = 0

        for t in session.test_results:
            if t.status in (TestStatus.FAIL, TestStatus.ERROR):
                failed_count += 1

            if t.stage == DiagnosticStage.DNS:
                dns_status = t.status.value
            elif t.stage == DiagnosticStage.PORT:
                port_status = t.status.value
            elif t.stage == DiagnosticStage.HTTP_TLS:
                http_status = t.status.value
            elif t.stage == DiagnosticStage.LATENCY:
                avg_latency = t.measured_values.get("avg_rtt_ms")
                packet_loss = float(t.measured_values.get("packet_loss_pct", 0.0))

        # Calculate severity score
        severity = 0.0
        if dns_status == "FAIL":
            severity += 40.0
        if port_status == "FAIL":
            severity += 35.0
        if http_status in ("FAIL", "ERROR"):
            severity += 25.0
        if packet_loss > 0:
            severity += min(30.0, packet_loss * 0.5)
        if avg_latency and avg_latency > 150.0:
            severity += min(20.0, (avg_latency - 150.0) * 0.1)

        severity = min(100.0, round(severity, 1))

        # Overall Status
        if failed_count > 0 or severity >= 35.0:
            status = "FAILED"
        elif severity > 10.0 or packet_loss > 0 or (avg_latency and avg_latency > 120.0):
            status = "DEGRADED"
        else:
            status = "HEALTHY"

        top_cause = session.hypotheses[0].probable_root_cause if session.hypotheses else "Normal operation"
        confidence = session.hypotheses[0].confidence.value if session.hypotheses else "HIGH"

        return BatchTargetResult(
            target_id=item.target_id,
            host=item.host,
            port=item.port,
            service_type=item.service_type,
            label=item.label,
            session_id=session.session_id,
            status=status,
            dns_status=dns_status,
            port_status=port_status,
            http_status=http_status,
            avg_latency_ms=avg_latency,
            packet_loss_pct=packet_loss,
            top_root_cause=top_cause,
            confidence=confidence,
            severity_score=severity,
            failed_tests_count=failed_count,
            duration_seconds=duration,
            session=session
        )
