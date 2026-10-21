"""Adaptive Diagnostic Investigation Orchestrator.

Orchestrates test execution adapting dynamically to previous stage findings.
Supports cancellation tokens, callbacks, and deterministic flow termination.
"""

import datetime
import threading
import uuid
from typing import Callable, List, Optional

from diagnostics.connectivity import check_destination_reachability, check_tcp_port_availability
from diagnostics.dns import run_dns_resolution
from diagnostics.gateway import check_gateway_reachability
from diagnostics.http_tls import check_http_service, check_tls_certificate
from diagnostics.latency import measure_latency_and_loss
from diagnostics.local_config import run_local_config_diagnostic
from diagnostics.models import (
    DiagnosticSession,
    DiagnosticStage,
    TestResult,
    TestStatus,
)
from diagnostics.traceroute import run_bounded_traceroute
from engine.root_cause import analyze_test_results
from storage.database import save_session


class DiagnosticCancellation(Exception):
    """Raised when user cancels a running investigation."""
    pass


class DiagnosticOrchestrator:
    """
    Executes an adaptive investigation:
    1. Local config -> if failed, halt destination tests, report local failure.
    2. Gateway check -> informs local connectivity health.
    3. DNS resolution -> if failed and host is a name, test resolver; halt HTTP/TLS on unresolved host.
    4. Destination reachability & TCP handshake -> if closed/timed out, avoid TLS/HTTP failure duplication.
    5. TLS / HTTP diagnostics -> evaluate web application layer.
    6. Latency & Loss measurement.
    """

    def __init__(self, db_path: str = "data/nta.db"):
        self.db_path = db_path
        self._cancel_flag = threading.Event()

    def cancel(self) -> None:
        """Signals orchestrator to abort pending tests."""
        self._cancel_flag.set()

    def run_investigation(
        self,
        user_symptom: str,
        target_host: Optional[str] = None,
        target_port: Optional[int] = None,
        service_type: Optional[str] = None,
        is_simulated: bool = False,
        simulation_scenario_id: Optional[str] = None,
        run_traceroute: bool = False,
        on_test_complete: Optional[Callable[[TestResult, int, int], None]] = None
    ) -> DiagnosticSession:
        """
        Runs adaptive network diagnostic workflow with progress callbacks and persistent storage.
        """
        self._cancel_flag.clear()
        session_id = str(uuid.uuid4())
        start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

        session = DiagnosticSession(
            session_id=session_id,
            start_time=start_time,
            user_symptom=user_symptom,
            target_host=target_host,
            target_port=target_port,
            service_type=service_type,
            is_simulated=is_simulated,
            simulation_scenario_id=simulation_scenario_id
        )

        test_results: List[TestResult] = []
        total_estimated_steps = 7 if run_traceroute else 6
        step_idx = 0

        # Helper to record test and invoke callback
        def record_result(res: TestResult) -> None:
            nonlocal step_idx
            step_idx += 1
            test_results.append(res)
            session.test_results = test_results
            if on_test_complete:
                on_test_complete(res, step_idx, total_estimated_steps)

        # Stage 1: Local Configuration
        if self._cancel_flag.is_set():
            return self._finalize_cancelled(session)

        local_res = run_local_config_diagnostic()
        record_result(local_res)

        # Stage 2: Gateway Check
        if self._cancel_flag.is_set():
            return self._finalize_cancelled(session)

        gateway_ip = local_res.measured_values.get("default_gateway")
        gw_res = check_gateway_reachability(gateway_ip, ping_count=2, timeout_sec=2)
        record_result(gw_res)

        # Stage 3: DNS Resolution (if host specified)
        resolved_ip: Optional[str] = None
        dns_success = False

        if target_host:
            if self._cancel_flag.is_set():
                return self._finalize_cancelled(session)

            # Check if host is already an IP address
            is_ip = False
            try:
                import ipaddress
                ipaddress.ip_address(target_host)
                is_ip = True
                resolved_ip = target_host
                dns_success = True
                # Record skipped DNS
                record_result(TestResult(
                    test_id="dns_01",
                    stage=DiagnosticStage.DNS,
                    test_name="DNS Hostname Resolution",
                    status=TestStatus.SKIPPED,
                    measured_values={"target_host": target_host},
                    human_explanation="Target is an explicit IP address; DNS lookup skipped.",
                    evidence=[f"Direct IP provided: {target_host}"],
                    skipped_reason="Target is an IP address."
                ))
            except ValueError:
                pass

            if not is_ip:
                dns_res = run_dns_resolution(target_host, timeout_sec=3.0)
                record_result(dns_res)
                if dns_res.status == TestStatus.PASS:
                    dns_success = True
                    resolved_ips = dns_res.measured_values.get("resolved_ips", [])
                    resolved_ip = resolved_ips[0] if resolved_ips else None

        # Stage 4 & 5: Destination Port & Connectivity
        tcp_port = target_port
        if not tcp_port and service_type:
            if service_type.lower() == "https":
                tcp_port = 443
            elif service_type.lower() == "http":
                tcp_port = 80
        elif not tcp_port:
            tcp_port = 80  # Default to web port

        port_success = False
        if target_host and (dns_success or resolved_ip):
            if self._cancel_flag.is_set():
                return self._finalize_cancelled(session)

            # Attempt TCP Port handshake
            port_res = check_tcp_port_availability(target_host, tcp_port, timeout_sec=3.0)
            record_result(port_res)
            port_success = (port_res.status == TestStatus.PASS)

            # Stage 6: TLS and HTTP diagnostics
            if port_success and tcp_port in (80, 443, 8080, 8443) or service_type in ("http", "https"):
                if self._cancel_flag.is_set():
                    return self._finalize_cancelled(session)

                use_https = (tcp_port in (443, 8443) or service_type == "https")
                if use_https:
                    tls_res = check_tls_certificate(target_host, tcp_port, timeout_sec=4.0)
                    record_result(tls_res)

                http_res = check_http_service(target_host, tcp_port, use_https=use_https, timeout_sec=4.0)
                record_result(http_res)

            # Stage 7: Bounded Latency & Loss
            if self._cancel_flag.is_set():
                return self._finalize_cancelled(session)

            lat_res = measure_latency_and_loss(target_host, samples=4, timeout_sec=2)
            record_result(lat_res)

            # Stage 8: Bounded Route Path Trace
            if run_traceroute:
                if self._cancel_flag.is_set():
                    return self._finalize_cancelled(session)
                trace_res = run_bounded_traceroute(target_host, max_hops=12, timeout_sec=2)
                record_result(trace_res)

        elif target_host and not dns_success:
            # Skip subsequent application tests because hostname did not resolve
            record_result(TestResult(
                test_id="port_skipped",
                stage=DiagnosticStage.PORT,
                test_name="TCP Port Handshake",
                status=TestStatus.SKIPPED,
                measured_values={},
                human_explanation="TCP port handshake skipped because DNS resolution failed.",
                evidence=["Prerequisite DNS failed."],
                skipped_reason="DNS resolution failed."
            ))

        # Root Cause Analysis & Recommendations
        hypotheses, recs = analyze_test_results(
            test_results=test_results,
            target_host=target_host or "",
            target_port=tcp_port or 0
        )

        session.test_results = test_results
        session.hypotheses = hypotheses
        session.recommendations = recs
        session.end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Save to database
        save_session(session, self.db_path)

        return session

    def _finalize_cancelled(self, session: DiagnosticSession) -> DiagnosticSession:
        """Finalizes session when user cancels during execution."""
        session.end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        hypotheses, recs = analyze_test_results(
            session.test_results,
            target_host=session.target_host or "",
            target_port=session.target_port or 0
        )
        session.hypotheses = hypotheses
        session.recommendations = recs
        save_session(session, self.db_path)
        return session
