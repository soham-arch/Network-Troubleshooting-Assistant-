"""Stage 2 Diagnostic: Default Gateway Reachability."""

import datetime
import subprocess
import time
from typing import List, Optional
from diagnostics.models import DiagnosticStage, TestResult, TestStatus
from utils.platform import get_os_type


def check_gateway_reachability(gateway_ip: Optional[str], ping_count: int = 3, timeout_sec: int = 2) -> TestResult:
    """
    Performs bounded ICMP ping checks against default gateway.
    Handles ICMP blocking gracefully without declaring gateway dead prematurely.
    """
    start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    evidence: List[str] = []
    values = {"gateway_ip": gateway_ip, "ping_count": ping_count}

    if not gateway_ip:
        end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return TestResult(
            test_id="gateway_01",
            stage=DiagnosticStage.GATEWAY,
            test_name="Default Gateway Reachability",
            start_time=start_time,
            end_time=end_time,
            status=TestStatus.SKIPPED,
            measured_values={"gateway_ip": None},
            human_explanation="Default gateway address was not discovered from local configuration. Test skipped.",
            evidence=["Default gateway IP is missing."],
            skipped_reason="No gateway discovered."
        )

    evidence.append(f"Testing reachability to default gateway: {gateway_ip}")
    os_type = get_os_type()

    if os_type == "windows":
        cmd = ["ping", "-n", str(ping_count), "-w", str(timeout_sec * 1000), gateway_ip]
    else:
        cmd = ["ping", "-c", str(ping_count), "-W", str(timeout_sec), gateway_ip]

    success = False
    stdout = ""
    start_t = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=(ping_count * timeout_sec) + 3)
        stdout = proc.stdout
        duration = round(time.time() - start_t, 3)
        values["ping_duration_sec"] = duration

        if proc.returncode == 0:
            success = True
            evidence.append(f"Gateway responded successfully to ICMP ping in {duration}s.")
        else:
            evidence.append("Gateway ping command exited with non-zero status.")
            if "Request timed out" in stdout or "Destination host unreachable" in stdout or "100% packet loss" in stdout:
                evidence.append("ICMP echo requests timed out or were unreachable.")
    except subprocess.TimeoutExpired:
        evidence.append("Gateway ping test timed out.")
    except Exception as e:
        evidence.append(f"Error executing ping: {str(e)}")

    end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if success:
        return TestResult(
            test_id="gateway_01",
            stage=DiagnosticStage.GATEWAY,
            test_name="Default Gateway Reachability",
            start_time=start_time,
            end_time=end_time,
            status=TestStatus.PASS,
            measured_values=values,
            human_explanation=f"Default gateway ({gateway_ip}) is responsive.",
            evidence=evidence,
            limitations="ICMP response indicates local link layer and router stack are functional."
        )
    else:
        # Failure or ICMP filter
        return TestResult(
            test_id="gateway_01",
            stage=DiagnosticStage.GATEWAY,
            test_name="Default Gateway Reachability",
            start_time=start_time,
            end_time=end_time,
            status=TestStatus.FAIL,
            measured_values=values,
            human_explanation=f"No response from default gateway ({gateway_ip}).",
            evidence=evidence,
            limitations="Note: Some security appliances/routers drop ICMP echo requests intentionally."
        )
