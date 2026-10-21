"""Stage 4 & 5 Diagnostic: Destination ICMP Reachability and TCP Port Availability."""

import datetime
import socket
import subprocess
import time
from typing import List, Optional
from diagnostics.models import DiagnosticStage, TestResult, TestStatus
from utils.platform import get_os_type


def check_destination_reachability(target_host: str, ping_count: int = 2, timeout_sec: int = 2) -> TestResult:
    """
    Checks destination reachability via ICMP ping if available.
    """
    start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    evidence: List[str] = []
    values = {"target_host": target_host}

    evidence.append(f"Testing ICMP reachability to destination: {target_host}")
    os_type = get_os_type()

    if os_type == "windows":
        cmd = ["ping", "-n", str(ping_count), "-w", str(timeout_sec * 1000), target_host]
    else:
        cmd = ["ping", "-c", str(ping_count), "-W", str(timeout_sec), target_host]

    success = False
    start_t = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=(ping_count * timeout_sec) + 3)
        duration = round(time.time() - start_t, 3)
        values["ping_duration_sec"] = duration

        if proc.returncode == 0:
            success = True
            evidence.append(f"Destination responded to ICMP ping in {duration}s.")
        else:
            evidence.append("ICMP ping failed or timed out.")
    except Exception as e:
        evidence.append(f"Ping execution notice: {str(e)}")

    end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

    status = TestStatus.PASS if success else TestStatus.WARNING
    explanation = (
        f"Target '{target_host}' responds to ICMP echo."
        if success
        else f"Target '{target_host}' did not respond to ICMP ping (may be blocked by firewalls)."
    )

    return TestResult(
        test_id="dest_icmp_01",
        stage=DiagnosticStage.DESTINATION,
        test_name="Destination ICMP Reachability",
        start_time=start_time,
        end_time=end_time,
        status=status,
        measured_values=values,
        human_explanation=explanation,
        evidence=evidence,
        limitations="Many cloud hosts and firewalls disable ICMP echo while accepting TCP/UDP traffic."
    )


def check_tcp_port_availability(target_host: str, port: int, timeout_sec: float = 3.0) -> TestResult:
    """
    Attempts bounded TCP three-way handshake to destination:port.
    Accurately distinguishes Connection Refused, Timeout, and Network Unreachable.
    """
    start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    evidence: List[str] = []
    values = {"target_host": target_host, "port": port, "timeout_sec": timeout_sec}

    evidence.append(f"Initiating TCP handshake to {target_host}:{port} (timeout={timeout_sec}s)")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout_sec)

    status = TestStatus.FAIL
    explanation = ""
    start_t = time.time()

    try:
        sock.connect((target_host, port))
        duration_ms = round((time.time() - start_t) * 1000, 2)
        values["handshake_duration_ms"] = duration_ms
        sock.close()

        status = TestStatus.PASS
        explanation = f"TCP port {port} is OPEN and responsive (connected in {duration_ms}ms)."
        evidence.append(f"TCP handshake completed successfully in {duration_ms}ms.")

    except socket.timeout:
        duration_ms = round((time.time() - start_t) * 1000, 2)
        values["handshake_duration_ms"] = duration_ms
        status = TestStatus.FAIL
        values["error_type"] = "TIMEOUT"
        explanation = f"TCP connection to port {port} timed out after {timeout_sec}s."
        evidence.append("Connection timed out. Packets may be dropped by firewall or target is down.")

    except ConnectionRefusedError:
        duration_ms = round((time.time() - start_t) * 1000, 2)
        values["handshake_duration_ms"] = duration_ms
        status = TestStatus.FAIL
        values["error_type"] = "CONNECTION_REFUSED"
        explanation = f"TCP port {port} is closed (Connection Refused: RST received)."
        evidence.append("Connection was actively refused by target host (TCP RST received).")

    except OSError as e:
        duration_ms = round((time.time() - start_t) * 1000, 2)
        values["handshake_duration_ms"] = duration_ms
        status = TestStatus.FAIL
        values["error_type"] = "OS_ERROR"
        values["os_errno"] = e.errno
        explanation = f"TCP connection error on port {port}: {e.strerror}"
        evidence.append(f"Socket error ({e.errno}): {e.strerror}")

    finally:
        try:
            sock.close()
        except Exception:
            pass

    end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

    return TestResult(
        test_id="tcp_port_01",
        stage=DiagnosticStage.PORT,
        test_name="TCP Port Availability & Handshake",
        start_time=start_time,
        end_time=end_time,
        status=status,
        measured_values=values,
        human_explanation=explanation,
        evidence=evidence,
        limitations="Verifies TCP layer connectivity. Does not imply application protocol readiness."
    )
