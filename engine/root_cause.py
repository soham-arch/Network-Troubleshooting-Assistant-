"""Intelligent Root-Cause Analysis Engine and Recommendation Generator."""

import uuid
from typing import List, Tuple
from diagnostics.models import (
    ConfidenceLevel,
    DiagnosticRecommendation,
    DiagnosticStage,
    RootCauseHypothesis,
    TestResult,
    TestStatus,
)


def analyze_test_results(
    test_results: List[TestResult],
    target_host: str = "",
    target_port: int = 0
) -> Tuple[List[RootCauseHypothesis], List[DiagnosticRecommendation]]:
    """
    Evaluates evidence collected across all executed diagnostic tests.
    Produces ranked hypotheses and concrete actionable recommendations.
    Never invents facts or claims hypotheses are 100% certainties without evidence.
    """
    hypotheses: List[RootCauseHypothesis] = []
    recommendations: List[DiagnosticRecommendation] = []

    # Map tests by stage
    stage_map = {res.stage: res for res in test_results}

    local_res = stage_map.get(DiagnosticStage.LOCAL_CONFIG)
    gw_res = stage_map.get(DiagnosticStage.GATEWAY)
    dns_res = stage_map.get(DiagnosticStage.DNS)
    dest_res = stage_map.get(DiagnosticStage.DESTINATION)
    port_res = stage_map.get(DiagnosticStage.PORT)
    http_res = stage_map.get(DiagnosticStage.HTTP_TLS)
    lat_res = stage_map.get(DiagnosticStage.LATENCY)

    # 1. Invalid or missing local IP configuration
    if local_res and local_res.status == TestStatus.FAIL:
        hypotheses.append(RootCauseHypothesis(
            hypothesis_id=str(uuid.uuid4())[:8],
            title="Local Network Interface Disconnected or DHCP Lease Failed",
            probable_root_cause="The local device has not obtained a valid IPv4 network address.",
            confidence=ConfidenceLevel.HIGH,
            confidence_score=0.95,
            supporting_evidence=local_res.evidence,
            contradicting_evidence=[],
            alternative_explanations=[
                "Ethernet cable unplugged or Wi-Fi radio disabled.",
                "DHCP server on local router exhausted or non-responsive.",
                "Virtual adapter conflict."
            ],
            recommended_next_step="Inspect physical/wireless interface status and renew DHCP lease.",
            suggested_corrective_action="Reconnect Wi-Fi/Ethernet or run 'ipconfig /renew' / 'dhclient'.",
            verification_steps=[
                "Verify an active non-APIPA (not 169.254.x.x) IP is assigned.",
                "Verify default gateway IP appears in local configuration."
            ]
        ))
        recommendations.append(DiagnosticRecommendation(
            id="rec_dhcp_01",
            observed_issue="No operational IP address found on local interfaces.",
            why_it_helps="An IP address is mandatory for any network communication.",
            steps_to_follow=[
                "Check physical network cable or Wi-Fi connection indicator.",
                "Toggle Wi-Fi / Airplane mode off and on.",
                "Open terminal and execute: ipconfig /renew (Windows) or sudo dhclient (Linux)."
            ],
            expected_outcome="Interface obtains a valid IPv4 address (e.g. 192.168.x.x or 10.x.x.x).",
            how_to_verify="Re-run Local Network Configuration check.",
            risks_and_limitations="Requires DHCP service running on the local router."
        ))

    # 2. Local Gateway unreachable
    if gw_res and gw_res.status == TestStatus.FAIL:
        hypotheses.append(RootCauseHypothesis(
            hypothesis_id=str(uuid.uuid4())[:8],
            title="Default Gateway Unreachable or Local Link Down",
            probable_root_cause="The local router/default gateway did not respond to ICMP packets.",
            confidence=ConfidenceLevel.MEDIUM,
            confidence_score=0.75,
            supporting_evidence=gw_res.evidence,
            contradicting_evidence=[],
            alternative_explanations=[
                "Router is powered off or rebooting.",
                "Local Wi-Fi access point lost upstream bridge connection.",
                "Router firmware intentionally drops ICMP echo requests for security."
            ],
            recommended_next_step="Check physical connection to router and verify router power status.",
            suggested_corrective_action="Reboot local router/modem and verify LAN cable or Wi-Fi signal.",
            verification_steps=[
                "Ping default gateway IP directly.",
                "Verify gateway MAC address in ARP cache (arp -a)."
            ]
        ))
        recommendations.append(DiagnosticRecommendation(
            id="rec_gw_01",
            observed_issue="Default gateway is not responding to ICMP probes.",
            why_it_helps="The default gateway routes all packets outside your local subnet.",
            steps_to_follow=[
                "Confirm local router/modem is powered on and LED indicators are green.",
                "Move closer to Wi-Fi access point or reseat Ethernet cable.",
                "Power cycle router if all local devices have lost connectivity."
            ],
            expected_outcome="Gateway responds with low latency (<5ms).",
            how_to_verify="Run Gateway Reachability test.",
            risks_and_limitations="Power cycling the router temporarily disconnects all users on the network."
        ))

    # 3. DNS Failure
    if dns_res and dns_res.status == TestStatus.FAIL:
        hypotheses.append(RootCauseHypothesis(
            hypothesis_id=str(uuid.uuid4())[:8],
            title="DNS Resolution Failure (Name Unresolvable)",
            probable_root_cause=f"The configured DNS resolver failed to resolve host '{target_host}'.",
            confidence=ConfidenceLevel.HIGH,
            confidence_score=0.90,
            supporting_evidence=dns_res.evidence,
            contradicting_evidence=["Local interface is up"] if local_res and local_res.status == TestStatus.PASS else [],
            alternative_explanations=[
                "The domain name is misspelled or does not exist (NXDOMAIN).",
                "Upstream DNS server (ISP/router) is offline or timing out.",
                "DNS filtering or captive portal blocking outbound port 53."
            ],
            recommended_next_step="Test resolution against a public resolver such as 1.1.1.1 or 8.8.8.8.",
            suggested_corrective_action="Check domain spelling or configure fallback DNS (e.g. 1.1.1.1).",
            verification_steps=[
                f"Execute 'nslookup {target_host} 1.1.1.1'.",
                "Flush local DNS resolver cache (ipconfig /flushdns or systemd-resolve --flush-caches)."
            ]
        ))
        recommendations.append(DiagnosticRecommendation(
            id="rec_dns_01",
            observed_issue=f"Domain '{target_host}' could not be resolved by the system DNS resolver.",
            why_it_helps="Applications cannot open connections without an IP address for the hostname.",
            steps_to_follow=[
                "Verify the domain name spelling.",
                "Flush DNS cache: Run 'ipconfig /flushdns' in Command Prompt.",
                "Test if public DNS works: 'nslookup " + str(target_host) + " 8.8.8.8'.",
                "If ISP DNS is failing, configure Cloudflare (1.1.1.1) or Google (8.8.8.8) in network adapter."
            ],
            expected_outcome="DNS lookup returns one or more valid IP addresses.",
            how_to_verify="Re-run DNS Hostname Resolution diagnostic.",
            risks_and_limitations="Changing adapter DNS requires administrative privileges."
        ))

    # 4. TCP Port Refused or Timeout
    if port_res and port_res.status == TestStatus.FAIL:
        err_type = port_res.measured_values.get("error_type", "")
        if err_type == "CONNECTION_REFUSED":
            hypotheses.append(RootCauseHypothesis(
                hypothesis_id=str(uuid.uuid4())[:8],
                title="Service Port Closed / Connection Refused (TCP RST)",
                probable_root_cause=f"The destination host is online but no process is listening on port {target_port}.",
                confidence=ConfidenceLevel.HIGH,
                confidence_score=0.92,
                supporting_evidence=port_res.evidence,
                contradicting_evidence=["Host is reachable on network layer"] if dest_res and dest_res.status == TestStatus.PASS else [],
                alternative_explanations=[
                    f"The web/application daemon on port {target_port} has crashed or stopped.",
                    "The service is bound exclusively to 127.0.0.1 on the server rather than 0.0.0.0.",
                    "Local host firewall (iptables/Windows Firewall) actively rejects the port."
                ],
                recommended_next_step=f"Inspect server daemon status on port {target_port}.",
                suggested_corrective_action="Start/restart the listening service on the destination host.",
                verification_steps=[
                    f"Run 'curl -v telnet://{target_host}:{target_port}' or netstat on server.",
                    "Verify daemon process is active (e.g. systemctl status nginx)."
                ]
            ))
            recommendations.append(DiagnosticRecommendation(
                id="rec_tcp_refused",
                observed_issue=f"Port {target_port} actively rejected connection (TCP RST received).",
                why_it_helps="Proves packets reached the server, but the service daemon is not running.",
                steps_to_follow=[
                    f"Verify server process listening on port {target_port}.",
                    "Restart the application or web service on the server.",
                    "Check server logs for recent crashes."
                ],
                expected_outcome=f"Port {target_port} accepts incoming connections.",
                how_to_verify="Re-run TCP Port Handshake test.",
                risks_and_limitations="Requires administrative access to the destination server."
            ))

        elif err_type == "TIMEOUT":
            hypotheses.append(RootCauseHypothesis(
                hypothesis_id=str(uuid.uuid4())[:8],
                title="TCP Connection Timeout / Firewall Packet Drop",
                probable_root_cause=f"Connection to {target_host}:{target_port} timed out without SYN-ACK response.",
                confidence=ConfidenceLevel.MEDIUM,
                confidence_score=0.80,
                supporting_evidence=port_res.evidence,
                contradicting_evidence=[],
                alternative_explanations=[
                    f"Intermediate firewall, cloud security group, or NAT is dropping SYN packets on port {target_port}.",
                    "The destination server is powered off or routing is broken.",
                    "ISP is throttling or filtering this specific port."
                ],
                recommended_next_step="Inspect cloud security groups (AWS SG / Azure NSG) and server firewall.",
                suggested_corrective_action="Add firewall rule allowing incoming traffic on destination port.",
                verification_steps=[
                    f"Test with traceroute to see where packets cease routing.",
                    "Check server security group ingress rules."
                ]
            ))
            recommendations.append(DiagnosticRecommendation(
                id="rec_tcp_timeout",
                observed_issue=f"TCP connection to port {target_port} timed out silently.",
                why_it_helps="Silent timeouts typically signify firewall packet drops or blackhole routing.",
                steps_to_follow=[
                    f"Check firewall / cloud security group ingress rules for port {target_port}.",
                    "Verify destination host public IP / routing.",
                    "Ensure upstream network provider does not block target port."
                ],
                expected_outcome="TCP handshake completes in <100ms.",
                how_to_verify="Re-run TCP Port test.",
                risks_and_limitations="Modifying security groups changes ingress security boundaries."
            ))

    # 5. TLS Certificate Validation Failure
    if http_res and http_res.test_id == "tls_01" and http_res.status == TestStatus.FAIL:
        hypotheses.append(RootCauseHypothesis(
            hypothesis_id=str(uuid.uuid4())[:8],
            title="TLS/SSL Certificate Verification Failure",
            probable_root_cause=f"The SSL/TLS certificate for '{target_host}' failed chain validation.",
            confidence=ConfidenceLevel.HIGH,
            confidence_score=0.92,
            supporting_evidence=http_res.evidence,
            contradicting_evidence=["TCP connection succeeded"] if port_res and port_res.status == TestStatus.PASS else [],
            alternative_explanations=[
                "Certificate expired or not yet valid (check client clock).",
                "Self-signed certificate without local root trust.",
                "Hostname mismatch between requested domain and certificate SAN.",
                "Interception proxy / SSL inspection active on network."
            ],
            recommended_next_step="Inspect certificate validity dates, subject alternative names, and client clock.",
            suggested_corrective_action="Renew SSL certificate or ensure device clock is synchronized via NTP.",
            verification_steps=[
                "Verify system date and time are synchronized with NTP.",
                f"Inspect certificate details using 'openssl s_client -connect {target_host}:443 -servername {target_host}'."
            ]
        ))
        recommendations.append(DiagnosticRecommendation(
            id="rec_tls_01",
            observed_issue="SSL/TLS certificate rejected by validation engine.",
            why_it_helps="Ensures client is communicating with authenticated server and prevents MITM attacks.",
            steps_to_follow=[
                "Verify your device system clock is set accurately.",
                "Check certificate expiration date using browser or OpenSSL.",
                "If self-signed in an internal dev environment, import root CA to system trust store."
            ],
            expected_outcome="TLS handshake completes with valid certificate chain.",
            how_to_verify="Re-run TLS/SSL Handshake diagnostic.",
            risks_and_limitations="Never disable certificate verification permanently in production."
        ))

    # 6. HTTP Server Error (5xx)
    if http_res and http_res.test_id == "http_01" and http_res.status == TestStatus.FAIL:
        status_code = http_res.measured_values.get("status_code", 0)
        if status_code >= 500:
            hypotheses.append(RootCauseHypothesis(
                hypothesis_id=str(uuid.uuid4())[:8],
                title=f"Application Server Error (HTTP {status_code})",
                probable_root_cause=f"Network connectivity is working, but the web application returned HTTP {status_code}.",
                confidence=ConfidenceLevel.HIGH,
                confidence_score=0.95,
                supporting_evidence=http_res.evidence,
                contradicting_evidence=["Network, DNS, and TCP handshake succeeded"],
                alternative_explanations=[
                    "Backend upstream service or database is down (502/504).",
                    "Application exception / unhandled crash on web server (500).",
                    "Service overloaded or undergoing maintenance (503)."
                ],
                recommended_next_step="Check server backend application logs and error reporting.",
                suggested_corrective_action="Inspect application error log (e.g. journalctl, Apache/Nginx error.log).",
                verification_steps=[
                    "Check web server error log.",
                    "Verify database and dependent microservices are running."
                ]
            ))
            recommendations.append(DiagnosticRecommendation(
                id="rec_http_5xx",
                observed_issue=f"Server returned HTTP status code {status_code}.",
                why_it_helps="Network layers (IP, DNS, TCP) are verified healthy; the failure is in the web application.",
                steps_to_follow=[
                    "Check server backend application logs for stack traces.",
                    "Verify upstream services (database, cache, reverse proxy).",
                    "Restart the web application service."
                ],
                expected_outcome="Endpoint returns HTTP 200 OK.",
                how_to_verify="Re-run HTTP Service diagnostic.",
                risks_and_limitations="Application debugging is required on server side."
            ))

    # 7. High Latency or Intermittent Packet Loss
    if lat_res and lat_res.status in (TestStatus.WARNING, TestStatus.FAIL):
        loss_pct = lat_res.measured_values.get("packet_loss_pct", 0)
        avg_lat = lat_res.measured_values.get("avg_latency_ms", 0)
        if loss_pct > 0 or (avg_lat and avg_lat > 150):
            hypotheses.append(RootCauseHypothesis(
                hypothesis_id=str(uuid.uuid4())[:8],
                title="Network Path Congestion / Intermittent Packet Loss",
                probable_root_cause=f"High latency ({avg_lat}ms) or packet loss ({loss_pct}%) observed on path to target.",
                confidence=ConfidenceLevel.MEDIUM,
                confidence_score=0.78,
                supporting_evidence=lat_res.evidence,
                contradicting_evidence=[],
                alternative_explanations=[
                    "Wi-Fi channel interference or weak signal strength.",
                    "Local bandwidth saturation (large download/backup ongoing).",
                    "Congested intermediate ISP peering point or bufferbloat."
                ],
                recommended_next_step="Inspect Wi-Fi signal or run continuous ping while monitoring router bandwidth.",
                suggested_corrective_action="Switch to 5GHz Wi-Fi or wired Ethernet; reduce background bandwidth usage.",
                verification_steps=[
                    "Run ping against local gateway to isolate local Wi-Fi vs ISP issue.",
                    "Re-measure latency with background downloads paused."
                ]
            ))
            recommendations.append(DiagnosticRecommendation(
                id="rec_lat_loss",
                observed_issue=f"Packet loss ({loss_pct}%) or elevated latency ({avg_lat}ms) detected.",
                why_it_helps="Improves connection stability for streaming, gaming, and interactive services.",
                steps_to_follow=[
                    "Switch from Wi-Fi to a wired Ethernet cable to isolate wireless interference.",
                    "Check if other household/office devices are consuming heavy bandwidth.",
                    "Reboot the modem/router if issue persists across all targets."
                ],
                expected_outcome="Packet loss drops to 0% and latency stabilizes.",
                how_to_verify="Re-run Round-Trip Latency diagnostic.",
                risks_and_limitations="ISP-level congestion may require contacting your service provider."
            ))

    # 8. All tests passed - Healthy baseline
    if not hypotheses and all(t.status in (TestStatus.PASS, TestStatus.SKIPPED) for t in test_results):
        hypotheses.append(RootCauseHypothesis(
            hypothesis_id=str(uuid.uuid4())[:8],
            title="Healthy Baseline / No Network Fault Detected",
            probable_root_cause="All diagnostic checks completed successfully. Network path is fully operational.",
            confidence=ConfidenceLevel.HIGH,
            confidence_score=0.90,
            supporting_evidence=["Local IP, Gateway, DNS, TCP port, and application layers all passed."],
            contradicting_evidence=[],
            alternative_explanations=[
                "The symptom may have been transient or resolved prior to testing.",
                "Issue may be specific to browser cache, cookies, or client extension."
            ],
            recommended_next_step="Clear browser cache or verify specific target URL paths.",
            suggested_corrective_action="No network action required. Test target in incognito window.",
            verification_steps=["Access target service in incognito window."]
        ))
        recommendations.append(DiagnosticRecommendation(
            id="rec_healthy",
            observed_issue="No network or server fault detected.",
            why_it_helps="Confirms network infrastructure and services are operating normally.",
            steps_to_follow=[
                "Clear browser cache and cookies.",
                "Test accessing the service in an Incognito/Private browser window."
            ],
            expected_outcome="Application loads normally.",
            how_to_verify="Verify web access in browser.",
            risks_and_limitations="None."
        ))

    # 9. Fallback if inconclusive
    if not hypotheses:
        hypotheses.append(RootCauseHypothesis(
            hypothesis_id=str(uuid.uuid4())[:8],
            title="Inconclusive Diagnostic Evidence",
            probable_root_cause="Collected diagnostic test data is insufficient to conclusively determine the fault.",
            confidence=ConfidenceLevel.LOW,
            confidence_score=0.30,
            supporting_evidence=[r.human_explanation for r in test_results],
            contradicting_evidence=[],
            alternative_explanations=["Target or protocol requires customized credentials or proprietary port checks."],
            recommended_next_step="Perform manual packet capture (Wireshark) or verify target endpoint details.",
            suggested_corrective_action="Verify target hostname, port, and authentication requirements.",
            verification_steps=["Run manual packet capture or curl probe."]
        ))

    # Sort hypotheses by confidence score descending
    hypotheses.sort(key=lambda h: h.confidence_score, reverse=True)

    return hypotheses, recommendations
