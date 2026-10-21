"""Stage 3 Diagnostic: DNS Hostname Resolution."""

import datetime
import socket
import time
from typing import List, Optional
from diagnostics.models import DiagnosticStage, TestResult, TestStatus


def run_dns_resolution(target_host: str, timeout_sec: float = 3.0) -> TestResult:
    """
    Resolves hostname to IP addresses using system resolver.
    Records duration, returned IPs, and errors.
    """
    start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    evidence: List[str] = []
    values = {"target_host": target_host}

    evidence.append(f"Attempting system DNS lookup for host: {target_host}")

    resolved_ips: List[str] = []
    start_t = time.time()
    err_str = None

    # Set default socket timeout for lookup
    old_timeout = socket.getdefaulttimeout()
    try:
        socket.setdefaulttimeout(timeout_sec)
        # getaddrinfo performs lookup across IPv4 and IPv6
        addr_info = socket.getaddrinfo(target_host, None)
        duration = round(time.time() - start_t, 4)
        values["resolution_duration_sec"] = duration

        for item in addr_info:
            sockaddr = item[4]
            ip_str = sockaddr[0]
            if ip_str not in resolved_ips:
                resolved_ips.append(ip_str)

        values["resolved_ips"] = resolved_ips
        evidence.append(f"Lookup resolved in {duration}s to {len(resolved_ips)} IP(s): {', '.join(resolved_ips)}")

    except socket.gaierror as e:
        duration = round(time.time() - start_t, 4)
        values["resolution_duration_sec"] = duration
        err_str = f"Name resolution failed: {e.strerror} (code {e.errno})"
        evidence.append(err_str)
    except socket.timeout:
        duration = round(time.time() - start_t, 4)
        values["resolution_duration_sec"] = duration
        err_str = f"DNS lookup timed out after {timeout_sec}s."
        evidence.append(err_str)
    except Exception as e:
        duration = round(time.time() - start_t, 4)
        values["resolution_duration_sec"] = duration
        err_str = f"DNS resolution error: {str(e)}"
        evidence.append(err_str)
    finally:
        socket.setdefaulttimeout(old_timeout)

    end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if resolved_ips:
        return TestResult(
            test_id="dns_01",
            stage=DiagnosticStage.DNS,
            test_name="DNS Hostname Resolution",
            start_time=start_time,
            end_time=end_time,
            status=TestStatus.PASS,
            measured_values=values,
            human_explanation=f"Hostname '{target_host}' successfully resolved to {len(resolved_ips)} IP address(es).",
            evidence=evidence,
            limitations="Using system configured resolver. Caching by OS resolver or local stub may apply."
        )
    else:
        return TestResult(
            test_id="dns_01",
            stage=DiagnosticStage.DNS,
            test_name="DNS Hostname Resolution",
            start_time=start_time,
            end_time=end_time,
            status=TestStatus.FAIL,
            measured_values=values,
            human_explanation=f"Could not resolve hostname '{target_host}'. {err_str}",
            evidence=evidence,
            limitations="Failure could indicate non-existent domain (NXDOMAIN), unreachable DNS server, or network isolation."
        )
