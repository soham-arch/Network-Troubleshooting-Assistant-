"""Stage 7 Diagnostic: Bounded Round-Trip Latency and Packet Loss."""

import datetime
import re
import subprocess
import time
from typing import List, Optional
from diagnostics.models import DiagnosticStage, TestResult, TestStatus
from utils.platform import get_os_type


def measure_latency_and_loss(
    target_host: str,
    samples: int = 5,
    timeout_sec: int = 2
) -> TestResult:
    """
    Performs bounded ICMP ping sample series to compute minimum, maximum,
    average latency, and exact packet loss percentage.
    """
    start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    evidence: List[str] = []
    values = {
        "target_host": target_host,
        "sample_count": samples,
        "timeout_sec": timeout_sec
    }

    evidence.append(f"Initiating latency & jitter test ({samples} probes to {target_host})")
    os_type = get_os_type()

    if os_type == "windows":
        cmd = ["ping", "-n", str(samples), "-w", str(timeout_sec * 1000), target_host]
    else:
        cmd = ["ping", "-c", str(samples), "-W", str(timeout_sec), target_host]

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=(samples * timeout_sec) + 4,
            check=False
        )
        out = proc.stdout

        # Parse loss percentage
        loss_pct = 100.0
        loss_match = re.search(r"(\d+)%\s*(?:packet\s*)?loss", out, re.IGNORECASE)
        if loss_match:
            loss_pct = float(loss_match.group(1))
        values["packet_loss_pct"] = loss_pct
        evidence.append(f"Measured packet loss: {loss_pct}%")

        # Parse latency
        min_ms, avg_ms, max_ms = None, None, None
        if os_type == "windows":
            # Minimum = 15ms, Maximum = 22ms, Average = 18ms
            times_match = re.search(
                r"Minimum\s*=\s*(\d+)ms,\s*Maximum\s*=\s*(\d+)ms,\s*Average\s*=\s*(\d+)ms",
                out,
                re.IGNORECASE
            )
            if times_match:
                min_ms = float(times_match.group(1))
                max_ms = float(times_match.group(2))
                avg_ms = float(times_match.group(3))
        else:
            # rtt min/avg/max/mdev = 15.2/18.4/22.1/2.3 ms
            rtt_match = re.search(r"=\s*([0-9.]+)/([0-9.]+)/([0-9.]+)", out)
            if rtt_match:
                min_ms = float(rtt_match.group(1))
                avg_ms = float(rtt_match.group(2))
                max_ms = float(rtt_match.group(3))

        values["min_latency_ms"] = min_ms
        values["avg_latency_ms"] = avg_ms
        values["max_latency_ms"] = max_ms

        if avg_ms is not None:
            evidence.append(f"Round-trip Latency: min={min_ms}ms, avg={avg_ms}ms, max={max_ms}ms")

        # Status determination
        if loss_pct == 100.0:
            status = TestStatus.FAIL
            explanation = f"100% packet loss to destination {target_host}."
        elif loss_pct > 0.0:
            status = TestStatus.WARNING
            explanation = f"Intermittent packet loss observed: {loss_pct}% loss to {target_host}."
        elif avg_ms and avg_ms > 200.0:
            status = TestStatus.WARNING
            explanation = f"High average network latency detected: {avg_ms}ms."
        else:
            status = TestStatus.PASS
            explanation = f"Connection latency is stable (avg {avg_ms or 0}ms, 0% loss)."

    except subprocess.TimeoutExpired:
        values["packet_loss_pct"] = 100.0
        status = TestStatus.FAIL
        explanation = f"Latency diagnostic timed out testing {target_host}."
        evidence.append("Ping command timed out completely.")
    except Exception as e:
        status = TestStatus.ERROR
        explanation = f"Error during latency measurement: {str(e)}"
        evidence.append(str(e))

    end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

    return TestResult(
        test_id="latency_01",
        stage=DiagnosticStage.LATENCY,
        test_name="Round-Trip Latency & Packet Loss Profile",
        start_time=start_time,
        end_time=end_time,
        status=status,
        measured_values=values,
        human_explanation=explanation,
        evidence=evidence,
        limitations="Small bounded sample (5 packets). Short tests may not capture sporadic long-term jitter."
    )
