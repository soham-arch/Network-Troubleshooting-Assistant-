"""Stage 1 Diagnostic: Local Network Configuration and Interface Inspection."""

import datetime
from typing import List
from diagnostics.models import DiagnosticStage, TestResult, TestStatus
from utils.platform import (
    get_default_gateway_and_dns,
    get_hostname,
    get_local_interfaces_info,
    get_os_type,
)


def run_local_config_diagnostic() -> TestResult:
    """
    Checks machine interfaces, assigned IP addresses, default gateway, and DNS configuration.
    Produces structured TestResult with evidence and status.
    """
    start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    evidence: List[str] = []
    values = {}

    hostname = get_hostname()
    os_type = get_os_type()
    values["hostname"] = hostname
    values["os"] = os_type
    evidence.append(f"Operating System: {os_type.capitalize()}")
    evidence.append(f"Host Name: {hostname}")

    interfaces = get_local_interfaces_info()
    values["interfaces"] = interfaces

    active_ips = []
    up_interfaces = []
    for iface in interfaces:
        if iface.get("is_up"):
            up_interfaces.append(iface["name"])
        for ip in iface.get("ipv4", []):
            if ip != "127.0.0.1" and not ip.startswith("169.254."):
                active_ips.append(ip)

    values["active_ipv4"] = active_ips
    evidence.append(f"Found {len(interfaces)} network interfaces ({len(up_interfaces)} operational).")
    if active_ips:
        evidence.append(f"Active IPv4 addresses: {', '.join(active_ips)}")
    else:
        evidence.append("No active non-loopback IPv4 addresses detected.")

    gateway, dns_servers = get_default_gateway_and_dns()
    values["default_gateway"] = gateway
    values["dns_servers"] = dns_servers

    if gateway:
        evidence.append(f"Configured Default Gateway: {gateway}")
    else:
        evidence.append("Default Gateway: None or undiscoverable.")

    if dns_servers:
        evidence.append(f"Configured DNS Servers: {', '.join(dns_servers)}")
    else:
        evidence.append("Configured DNS Servers: None or undiscoverable.")

    # Status evaluation
    status = TestStatus.PASS
    explanation = "Local network configuration is healthy with active IP addresses and discovered default gateway."

    if not active_ips:
        status = TestStatus.FAIL
        explanation = "No valid local IP address found. Machine may be disconnected from Wi-Fi/Ethernet or DHCP failed."
    elif not gateway and not dns_servers:
        status = TestStatus.WARNING
        explanation = "Local IP address is assigned, but default gateway and DNS servers could not be discovered."
    elif not gateway:
        status = TestStatus.WARNING
        explanation = "Local IP address is assigned, but default gateway is not configured."

    end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

    return TestResult(
        test_id="local_config_01",
        stage=DiagnosticStage.LOCAL_CONFIG,
        test_name="Local Network Configuration & Interface Inspection",
        start_time=start_time,
        end_time=end_time,
        status=status,
        measured_values=values,
        human_explanation=explanation,
        evidence=evidence,
        limitations="Checks local interface configuration and OS routing tables. Does not verify physical cable condition."
    )
