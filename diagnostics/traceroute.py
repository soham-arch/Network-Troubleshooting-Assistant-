"""Stage 8 Diagnostic: Cross-platform Bounded Route Traceroute."""

import datetime
import re
import subprocess
import time
from typing import List, Optional
from diagnostics.models import DiagnosticStage, TestResult, TestStatus
from utils.platform import get_os_type


def run_bounded_traceroute(target_host: str, max_hops: int = 15, timeout_sec: int = 2) -> TestResult:
    """
    Executes a bounded traceroute (max 15 hops) with tight timeouts.
    Distinguishes intermediate hops and 'No response observed' without false assumptions.
    """
    start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    evidence: List[str] = []
    values = {"target_host": target_host, "max_hops": max_hops}

    evidence.append(f"Tracing network route to {target_host} (max {max_hops} hops)...")
    os_type = get_os_type()

    if os_type == "windows":
        cmd = ["tracert", "-d", "-h", str(max_hops), "-w", str(timeout_sec * 1000), target_host]
    else:
        cmd = ["traceroute", "-n", "-m", str(max_hops), "-w", str(timeout_sec), target_host]

    hops = []
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=(max_hops * timeout_sec) + 8,
            check=False
        )
        lines = proc.stdout.splitlines()

        for line in lines:
            line = line.strip()
            # Windows tracert line example: "  1    <1 ms    <1 ms    <1 ms  192.168.1.1"
            # Linux traceroute line example: " 1  192.168.1.1  0.512 ms  0.421 ms"
            match = re.match(r"^(\d+)\s+(.+)", line)
            if match:
                hop_num = match.group(1)
                hop_rest = match.group(2)
                if "*" in hop_rest and not re.search(r"\d+\.\d+\.\d+\.\d+", hop_rest):
                    hop_desc = f"Hop {hop_num}: * * * (No response observed)"
                else:
                    hop_desc = f"Hop {hop_num}: {hop_rest}"
                hops.append(hop_desc)
                if len(hops) <= 8:  # Show first few in evidence
                    evidence.append(hop_desc)

        if len(hops) > 8:
            evidence.append(f"... and {len(hops) - 8} additional hops inspected.")

        values["hops"] = hops
        status = TestStatus.PASS if hops else TestStatus.WARNING
        explanation = f"Traceroute discovered {len(hops)} intermediate network hop(s)."

    except subprocess.TimeoutExpired:
        status = TestStatus.WARNING
        explanation = "Traceroute exceeded maximum allocated execution time."
        evidence.append("Traceroute reached bounded time limit.")
    except FileNotFoundError:
        status = TestStatus.SKIPPED
        explanation = "System traceroute utility not available on this environment."
        evidence.append("Utility 'tracert'/'traceroute' was not found.")
    except Exception as e:
        status = TestStatus.ERROR
        explanation = f"Traceroute error: {str(e)}"
        evidence.append(str(e))

    end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

    return TestResult(
        test_id="trace_01",
        stage=DiagnosticStage.TRACEROUTE,
        test_name="Bounded Route Path Trace",
        start_time=start_time,
        end_time=end_time,
        status=status,
        measured_values=values,
        human_explanation=explanation,
        evidence=evidence,
        limitations="Intermediate routers frequently deprioritize or filter ICMP/UDP TTL-exceeded responses."
    )
