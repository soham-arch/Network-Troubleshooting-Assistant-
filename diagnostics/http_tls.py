"""Stage 6 Diagnostic: HTTP, HTTPS, and TLS Diagnostic Checks."""

import datetime
import socket
import ssl
import time
from typing import List, Optional
import urllib.request
import urllib.error

from diagnostics.models import DiagnosticStage, TestResult, TestStatus


def check_tls_certificate(target_host: str, port: int = 443, timeout_sec: float = 4.0) -> TestResult:
    """
    Establishes TLS handshake and checks certificate validity, expiry, and SAN/CN.
    Distinguishes self-signed, expired, and hostname mismatch errors.
    """
    start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    evidence: List[str] = []
    values = {"target_host": target_host, "port": port}

    evidence.append(f"Testing TLS/SSL handshake on {target_host}:{port}")

    ctx = ssl.create_default_context()
    start_t = time.time()
    try:
        with socket.create_connection((target_host, port), timeout=timeout_sec) as sock:
            with ctx.wrap_socket(sock, server_hostname=target_host) as ssock:
                duration_ms = round((time.time() - start_t) * 1000, 2)
                values["handshake_duration_ms"] = duration_ms
                cert = ssock.getpeercert()

                values["tls_version"] = ssock.version()
                cipher = ssock.cipher()
                values["cipher_suite"] = cipher[0] if cipher else "Unknown"

                # Extract validity
                not_after = cert.get("notAfter", "")
                evidence.append(f"TLS handshake succeeded ({ssock.version()}, cipher {cipher[0] if cipher else 'N/A'}).")
                evidence.append(f"Certificate valid until: {not_after}")

                end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
                return TestResult(
                    test_id="tls_01",
                    stage=DiagnosticStage.HTTP_TLS,
                    test_name="TLS/SSL Handshake & Certificate Verification",
                    start_time=start_time,
                    end_time=end_time,
                    status=TestStatus.PASS,
                    measured_values=values,
                    human_explanation=f"Valid TLS certificate presented by '{target_host}'.",
                    evidence=evidence,
                    limitations="Standard trust store used for certificate authority chain validation."
                )

    except ssl.SSLCertVerificationError as e:
        duration_ms = round((time.time() - start_t) * 1000, 2)
        values["handshake_duration_ms"] = duration_ms
        values["ssl_error_reason"] = e.reason
        values["ssl_verify_code"] = e.verify_code
        evidence.append(f"TLS Verification Error: {e.verify_message} (reason: {e.reason})")

        end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return TestResult(
            test_id="tls_01",
            stage=DiagnosticStage.HTTP_TLS,
            test_name="TLS/SSL Handshake & Certificate Verification",
            start_time=start_time,
            end_time=end_time,
            status=TestStatus.FAIL,
            measured_values=values,
            human_explanation=f"TLS Certificate Validation Failed: {e.verify_message}",
            evidence=evidence,
            limitations="Certificate untrusted, self-signed, expired, or hostname does not match."
        )

    except Exception as e:
        duration_ms = round((time.time() - start_t) * 1000, 2)
        values["handshake_duration_ms"] = duration_ms
        evidence.append(f"TLS connection failed: {str(e)}")

        end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return TestResult(
            test_id="tls_01",
            stage=DiagnosticStage.HTTP_TLS,
            test_name="TLS/SSL Handshake & Certificate Verification",
            start_time=start_time,
            end_time=end_time,
            status=TestStatus.FAIL,
            measured_values=values,
            human_explanation=f"TLS Handshake failed: {str(e)}",
            evidence=evidence,
            limitations="Connection refused, timed out, or remote port does not speak TLS."
        )


def check_http_service(
    target_host: str,
    port: int = 80,
    use_https: bool = False,
    timeout_sec: float = 4.0
) -> TestResult:
    """
    Sends bounded HTTP HEAD/GET request to evaluate HTTP status code and response timing.
    Handles 4xx client errors, 5xx server errors, redirects, and timeouts.
    """
    start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    evidence: List[str] = []

    scheme = "https" if use_https else "http"
    url = f"{scheme}://{target_host}:{port}/" if port not in (80, 443) else f"{scheme}://{target_host}/"
    values = {"url": url, "scheme": scheme}

    evidence.append(f"Sending HTTP request to: {url}")

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "NetworkTroubleshootingAssistant/1.0", "Accept": "*/*"}
    )

    start_t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            duration_ms = round((time.time() - start_t) * 1000, 2)
            status_code = resp.status
            values["status_code"] = status_code
            values["response_duration_ms"] = duration_ms
            values["server_header"] = resp.headers.get("Server", "Unknown")

            evidence.append(f"HTTP response received: {status_code} in {duration_ms}ms")
            end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

            test_status = TestStatus.PASS if 200 <= status_code < 400 else TestStatus.WARNING
            return TestResult(
                test_id="http_01",
                stage=DiagnosticStage.HTTP_TLS,
                test_name="HTTP/HTTPS Service Health & Status",
                start_time=start_time,
                end_time=end_time,
                status=test_status,
                measured_values=values,
                human_explanation=f"HTTP service returned status {status_code} ({resp.reason}).",
                evidence=evidence,
                limitations="Root endpoint tested. Specific REST endpoints or auth routes may differ."
            )

    except urllib.error.HTTPError as e:
        duration_ms = round((time.time() - start_t) * 1000, 2)
        values["status_code"] = e.code
        values["response_duration_ms"] = duration_ms
        evidence.append(f"HTTP error response: {e.code} ({e.reason}) in {duration_ms}ms")
        end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # 5xx is server error, 4xx is client error
        test_status = TestStatus.FAIL if e.code >= 500 else TestStatus.WARNING
        return TestResult(
            test_id="http_01",
            stage=DiagnosticStage.HTTP_TLS,
            test_name="HTTP/HTTPS Service Health & Status",
            start_time=start_time,
            end_time=end_time,
            status=test_status,
            measured_values=values,
            human_explanation=f"HTTP server responded with error code {e.code} ({e.reason}).",
            evidence=evidence,
            limitations="Application layer responded with error."
        )

    except urllib.error.URLError as e:
        duration_ms = round((time.time() - start_t) * 1000, 2)
        values["response_duration_ms"] = duration_ms
        evidence.append(f"HTTP request connection error: {e.reason}")
        end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

        return TestResult(
            test_id="http_01",
            stage=DiagnosticStage.HTTP_TLS,
            test_name="HTTP/HTTPS Service Health & Status",
            start_time=start_time,
            end_time=end_time,
            status=TestStatus.FAIL,
            measured_values=values,
            human_explanation=f"Failed to communicate with HTTP service: {e.reason}",
            evidence=evidence,
            limitations="Connection refused, timeout, or protocol error."
        )
