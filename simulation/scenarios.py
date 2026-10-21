"""Controlled Network Fault Simulation Lab.

Provides 10 predefined, repeatable network fault scenarios using isolated
synthetic fixtures and controlled local test servers.
Keeps ground-truth expected causes isolated from the prediction engine.
Never modifies real host network configuration.
"""

import datetime
import time
import uuid
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field

from diagnostics.models import (
    ConfidenceLevel,
    DiagnosticSession,
    DiagnosticStage,
    RootCauseHypothesis,
    TestResult,
    TestStatus,
)
from engine.root_cause import analyze_test_results
from storage.database import record_evaluation, save_session


class SimulationScenario(BaseModel):
    """Scenario descriptor with hidden ground-truth label."""
    id: str
    name: str
    category: str
    description: str
    simulated_symptom: str
    target_host: str
    target_port: int
    expected_cause: str  # Kept separate and revealed only during evaluation
    notes: str


SIMULATION_SCENARIOS: List[SimulationScenario] = [
    SimulationScenario(
        id="scen_01_dns_failure",
        name="1. DNS Resolution Failure (NXDOMAIN)",
        category="DNS",
        description="The target domain cannot be resolved by the local or upstream DNS resolvers.",
        simulated_symptom="I cannot open the website api.internal-corp.corp",
        target_host="invalid-nxdomain-target-xyz.com",
        target_port=443,
        expected_cause="DNS Resolution Failure (Name Unresolvable)",
        notes="Simulates NXDOMAIN response from DNS resolver."
    ),
    SimulationScenario(
        id="scen_02_tcp_refused",
        name="2. TCP Connection Refused (RST)",
        category="Transport Layer",
        description="Destination host is reachable, but the target application port is closed and returning TCP RST.",
        simulated_symptom="Connection refused when connecting to database service.",
        target_host="127.0.0.1",
        target_port=59999,
        expected_cause="Service Port Closed / Connection Refused (TCP RST)",
        notes="Simulates active connection refusal on unassigned local port."
    ),
    SimulationScenario(
        id="scen_03_tcp_timeout",
        name="3. TCP Connection Timeout (Firewall Drop)",
        category="Transport Layer",
        description="Target IP/Port drops TCP SYN packets without returning SYN-ACK or RST.",
        simulated_symptom="The server never responds and the browser keeps loading indefinitely.",
        target_host="192.0.2.1",  # TEST-NET-1 (RFC 5737 - unroutable)
        target_port=8080,
        expected_cause="TCP Connection Timeout / Firewall Packet Drop",
        notes="Simulates silent packet drop by firewall."
    ),
    SimulationScenario(
        id="scen_04_invalid_local_ip",
        name="4. Invalid Local IP / Interface Disconnected",
        category="Data Link / IP",
        description="Local network interface has no operational IPv4 address or DHCP lease.",
        simulated_symptom="My laptop cannot connect to any websites or local network shares.",
        target_host="example.com",
        target_port=80,
        expected_cause="Local Network Interface Disconnected or DHCP Lease Failed",
        notes="Synthetic fixture: interface in disconnected state."
    ),
    SimulationScenario(
        id="scen_05_gateway_down",
        name="5. Default Gateway Unreachable",
        category="Routing / Local LAN",
        description="Local IP is assigned, but the local default gateway fails to respond to ICMP probes.",
        simulated_symptom="Connected to Wi-Fi with 'No Internet, Secured' indicator.",
        target_host="example.com",
        target_port=80,
        expected_cause="Default Gateway Unreachable or Local Link Down",
        notes="Synthetic fixture: default gateway unreachable."
    ),
    SimulationScenario(
        id="scen_06_http_500",
        name="6. Application Server Error (HTTP 500)",
        category="Application Layer",
        description="Network path is healthy, but the web application responds with HTTP 500 Internal Server Error.",
        simulated_symptom="The website shows 'Internal Server Error' when accessing the billing page.",
        target_host="service.company.internal",
        target_port=80,
        expected_cause="Application Server Error (HTTP 500)",
        notes="Synthetic fixture: HTTP 500 Internal Server Error."
    ),
    SimulationScenario(
        id="scen_07_tls_failure",
        name="7. TLS Certificate Validation Failure",
        category="Security / TLS",
        description="HTTPS connection fails due to an untrusted self-signed or expired certificate.",
        simulated_symptom="Browser shows 'Your connection is not private' (ERR_CERT_AUTHORITY_INVALID).",
        target_host="secure-checkout.internal",
        target_port=443,
        expected_cause="TLS/SSL Certificate Verification Failure",
        notes="Synthetic fixture: TLS certificate verification error."
    ),
    SimulationScenario(
        id="scen_08_high_latency",
        name="8. Severe Network Latency (>250ms)",
        category="Performance",
        description="Connection is established but exhibits excessive round-trip latency and bufferbloat.",
        simulated_symptom="Video calls and web pages are extremely laggy and slow.",
        target_host="cloud.provider.com",
        target_port=443,
        expected_cause="Network Path Congestion / Intermittent Packet Loss",
        notes="Synthetic fixture: high round trip latency (avg 285ms)."
    ),
    SimulationScenario(
        id="scen_09_packet_loss",
        name="9. Intermittent Packet Loss (30% Loss)",
        category="Performance",
        description="Connection experiences sporadic packet drops resulting in retransmissions.",
        simulated_symptom="Connection randomly drops and reconnects constantly.",
        target_host="gateway.partner.com",
        target_port=443,
        expected_cause="Network Path Congestion / Intermittent Packet Loss",
        notes="Synthetic fixture: 30% packet loss measured."
    ),
    SimulationScenario(
        id="scen_10_healthy_baseline",
        name="10. Healthy Baseline (No Fault)",
        category="Baseline",
        description="All layers from local interface through HTTP application operate within normal parameters.",
        simulated_symptom="Verifying baseline health before deployment.",
        target_host="healthy-cluster.net",
        target_port=443,
        expected_cause="Healthy Baseline / No Network Fault Detected",
        notes="Synthetic fixture: all diagnostics report PASS."
    ),
]


def get_scenario_by_id(scenario_id: str) -> Optional[SimulationScenario]:
    for s in SIMULATION_SCENARIOS:
        if s.id == scenario_id:
            return s
    return None


class SimulationLabEngine:
    """Executes controlled simulation scenarios using deterministic fixtures."""

    def __init__(self, db_path: str = "data/nta.db"):
        self.db_path = db_path

    def run_simulation(
        self,
        scenario: SimulationScenario,
        on_progress: Optional[Callable[[TestResult, int, int], None]] = None
    ) -> DiagnosticSession:
        start_time_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        start_t = time.time()
        session_id = f"sim_{uuid.uuid4().hex[:10]}"

        test_results = self._generate_scenario_test_results(scenario)

        # Progress callbacks if provided
        for idx, res in enumerate(test_results):
            if on_progress:
                on_progress(res, idx + 1, len(test_results))
            time.sleep(0.08)  # Smooth UI visual feedback

        # Feed test results strictly into root cause analysis WITHOUT giving it the expected label
        hypotheses, recs = analyze_test_results(
            test_results=test_results,
            target_host=scenario.target_host,
            target_port=scenario.target_port
        )

        session = DiagnosticSession(
            session_id=session_id,
            start_time=start_time_iso,
            end_time=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            user_symptom=scenario.simulated_symptom,
            target_host=scenario.target_host,
            target_port=scenario.target_port,
            service_type="https" if scenario.target_port == 443 else "http",
            is_simulated=True,
            simulation_scenario_id=scenario.id,
            test_results=test_results,
            hypotheses=hypotheses,
            recommendations=recs
        )

        save_session(session, self.db_path)

        # Evaluate prediction against ground truth
        predicted_cause = hypotheses[0].probable_root_cause if hypotheses else "None"
        predicted_title = hypotheses[0].title if hypotheses else ""
        # Check if expected cause matches title or probable cause
        is_correct = (
            scenario.expected_cause.lower() in predicted_cause.lower()
            or scenario.expected_cause.lower() in predicted_title.lower()
            or predicted_title.lower() in scenario.expected_cause.lower()
        )

        duration = round(time.time() - start_t, 2)
        eval_id = f"eval_{uuid.uuid4().hex[:10]}"

        record_evaluation(
            eval_id=eval_id,
            session_id=session_id,
            scenario_id=scenario.id,
            expected_cause=scenario.expected_cause,
            predicted_cause=predicted_title or predicted_cause,
            is_correct=is_correct,
            duration_seconds=duration,
            tests_executed=len(test_results),
            timestamp=session.end_time or start_time_iso,
            db_path=self.db_path
        )

        return session

    def _generate_scenario_test_results(self, scenario: SimulationScenario) -> List[TestResult]:
        """Generates deterministic fixture test results according to the scenario."""
        results: List[TestResult] = []
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Local Config Base
        local_healthy = TestResult(
            test_id="sim_local_01",
            stage=DiagnosticStage.LOCAL_CONFIG,
            test_name="Local Network Configuration & Interface Inspection",
            start_time=now,
            end_time=now,
            status=TestStatus.PASS,
            measured_values={"hostname": "dev-workstation", "active_ipv4": ["192.168.1.105"], "default_gateway": "192.168.1.1"},
            human_explanation="Local network interface is UP with assigned IPv4 address 192.168.1.105.",
            evidence=["Active IPv4: 192.168.1.105", "Interface: Ethernet0 (Operational)", "Default Gateway: 192.168.1.1"],
            is_simulated=True
        )

        # Gateway Base
        gw_healthy = TestResult(
            test_id="sim_gw_01",
            stage=DiagnosticStage.GATEWAY,
            test_name="Default Gateway Reachability",
            start_time=now,
            end_time=now,
            status=TestStatus.PASS,
            measured_values={"gateway_ip": "192.168.1.1", "ping_duration_sec": 0.002},
            human_explanation="Default gateway (192.168.1.1) responded to ICMP probes in 2ms.",
            evidence=["ICMP echo reply received in 2ms.", "No packet loss to gateway."],
            is_simulated=True
        )

        # Scenario 4: Invalid Local IP
        if scenario.id == "scen_04_invalid_local_ip":
            local_fail = TestResult(
                test_id="sim_local_01",
                stage=DiagnosticStage.LOCAL_CONFIG,
                test_name="Local Network Configuration & Interface Inspection",
                start_time=now,
                end_time=now,
                status=TestStatus.FAIL,
                measured_values={"hostname": "dev-workstation", "active_ipv4": [], "default_gateway": None},
                human_explanation="No valid local IP address assigned. Physical link down or DHCP failed.",
                evidence=["Interfaces found: 1 (status: DOWN)", "No non-loopback IPv4 addresses detected.", "Default Gateway: None"],
                is_simulated=True
            )
            return [local_fail]

        # Scenario 5: Gateway Down
        if scenario.id == "scen_05_gateway_down":
            gw_fail = TestResult(
                test_id="sim_gw_01",
                stage=DiagnosticStage.GATEWAY,
                test_name="Default Gateway Reachability",
                start_time=now,
                end_time=now,
                status=TestStatus.FAIL,
                measured_values={"gateway_ip": "192.168.1.1"},
                human_explanation="No response from default gateway (192.168.1.1). ICMP ping timed out.",
                evidence=["Ping to 192.168.1.1 returned 'Request timed out'.", "100% packet loss to default gateway."],
                is_simulated=True
            )
            return [local_healthy, gw_fail]

        # Scenario 1: DNS Failure
        if scenario.id == "scen_01_dns_failure":
            dns_fail = TestResult(
                test_id="sim_dns_01",
                stage=DiagnosticStage.DNS,
                test_name="DNS Hostname Resolution",
                start_time=now,
                end_time=now,
                status=TestStatus.FAIL,
                measured_values={"target_host": scenario.target_host, "resolution_duration_sec": 2.1},
                human_explanation=f"Could not resolve hostname '{scenario.target_host}'. Name resolution failed: getaddrinfo failed (NXDOMAIN).",
                evidence=[f"DNS query for '{scenario.target_host}' timed out or returned NXDOMAIN.", "No IP addresses returned by configured resolver."],
                is_simulated=True
            )
            return [local_healthy, gw_healthy, dns_fail]

        # DNS Healthy Base
        dns_healthy = TestResult(
            test_id="sim_dns_01",
            stage=DiagnosticStage.DNS,
            test_name="DNS Hostname Resolution",
            start_time=now,
            end_time=now,
            status=TestStatus.PASS,
            measured_values={"target_host": scenario.target_host, "resolved_ips": ["93.184.216.34"], "resolution_duration_sec": 0.015},
            human_explanation=f"Hostname '{scenario.target_host}' resolved to 93.184.216.34 in 15ms.",
            evidence=[f"Resolved IPs: 93.184.216.34", "System resolver succeeded in 0.015s."],
            is_simulated=True
        )

        # Scenario 2: TCP Refused
        if scenario.id == "scen_02_tcp_refused":
            tcp_refused = TestResult(
                test_id="sim_tcp_01",
                stage=DiagnosticStage.PORT,
                test_name="TCP Port Availability & Handshake",
                start_time=now,
                end_time=now,
                status=TestStatus.FAIL,
                measured_values={"target_host": scenario.target_host, "port": scenario.target_port, "error_type": "CONNECTION_REFUSED", "handshake_duration_ms": 1.2},
                human_explanation=f"TCP port {scenario.target_port} is closed (Connection Refused: RST received).",
                evidence=["Connection actively refused by host.", "TCP RST packet returned immediately (1.2ms)."],
                is_simulated=True
            )
            return [local_healthy, gw_healthy, dns_healthy, tcp_refused]

        # Scenario 3: TCP Timeout
        if scenario.id == "scen_03_tcp_timeout":
            tcp_timeout = TestResult(
                test_id="sim_tcp_01",
                stage=DiagnosticStage.PORT,
                test_name="TCP Port Availability & Handshake",
                start_time=now,
                end_time=now,
                status=TestStatus.FAIL,
                measured_values={"target_host": scenario.target_host, "port": scenario.target_port, "error_type": "TIMEOUT", "handshake_duration_ms": 3000.0},
                human_explanation=f"TCP connection to port {scenario.target_port} timed out after 3.0s.",
                evidence=["TCP SYN packet sent with no response.", "Connection timed out after 3000ms. Likely firewall packet drop."],
                is_simulated=True
            )
            return [local_healthy, gw_healthy, dns_healthy, tcp_timeout]

        # TCP Healthy Base
        tcp_healthy = TestResult(
            test_id="sim_tcp_01",
            stage=DiagnosticStage.PORT,
            test_name="TCP Port Availability & Handshake",
            start_time=now,
            end_time=now,
            status=TestStatus.PASS,
            measured_values={"target_host": scenario.target_host, "port": scenario.target_port, "handshake_duration_ms": 28.5},
            human_explanation=f"TCP port {scenario.target_port} is OPEN and responsive (connected in 28.5ms).",
            evidence=["SYN-ACK received successfully.", "Handshake completed in 28.5ms."],
            is_simulated=True
        )

        # Scenario 7: TLS Failure
        if scenario.id == "scen_07_tls_failure":
            tls_fail = TestResult(
                test_id="tls_01",
                stage=DiagnosticStage.HTTP_TLS,
                test_name="TLS/SSL Handshake & Certificate Verification",
                start_time=now,
                end_time=now,
                status=TestStatus.FAIL,
                measured_values={"target_host": scenario.target_host, "port": scenario.target_port, "ssl_error_reason": "CERTIFICATE_VERIFY_FAILED"},
                human_explanation="TLS Certificate Validation Failed: self-signed certificate in certificate chain.",
                evidence=["SSL: CERTIFICATE_VERIFY_FAILED: self-signed certificate", "Issuer: Self-Signed Dev CA"],
                is_simulated=True
            )
            return [local_healthy, gw_healthy, dns_healthy, tcp_healthy, tls_fail]

        # Scenario 6: HTTP 500
        if scenario.id == "scen_06_http_500":
            http_500 = TestResult(
                test_id="http_01",
                stage=DiagnosticStage.HTTP_TLS,
                test_name="HTTP/HTTPS Service Health & Status",
                start_time=now,
                end_time=now,
                status=TestStatus.FAIL,
                measured_values={"status_code": 500, "response_duration_ms": 84.0, "url": f"http://{scenario.target_host}/"},
                human_explanation="HTTP server responded with error code 500 (Internal Server Error).",
                evidence=["HTTP 500 Internal Server Error returned by backend.", "Response time: 84ms."],
                is_simulated=True
            )
            return [local_healthy, gw_healthy, dns_healthy, tcp_healthy, http_500]

        # Scenario 8: High Latency
        if scenario.id == "scen_08_high_latency":
            lat_high = TestResult(
                test_id="latency_01",
                stage=DiagnosticStage.LATENCY,
                test_name="Round-Trip Latency & Packet Loss Profile",
                start_time=now,
                end_time=now,
                status=TestStatus.WARNING,
                measured_values={"packet_loss_pct": 0.0, "avg_latency_ms": 285.0, "min_latency_ms": 260.0, "max_latency_ms": 320.0},
                human_explanation="High average network latency detected: 285.0ms.",
                evidence=["Round-trip Latency: min=260ms, avg=285ms, max=320ms", "0% packet loss."],
                is_simulated=True
            )
            return [local_healthy, gw_healthy, dns_healthy, tcp_healthy, lat_high]

        # Scenario 9: Packet Loss
        if scenario.id == "scen_09_packet_loss":
            lat_loss = TestResult(
                test_id="latency_01",
                stage=DiagnosticStage.LATENCY,
                test_name="Round-Trip Latency & Packet Loss Profile",
                start_time=now,
                end_time=now,
                status=TestStatus.WARNING,
                measured_values={"packet_loss_pct": 30.0, "avg_latency_ms": 35.0, "min_latency_ms": 25.0, "max_latency_ms": 48.0},
                human_explanation="Intermittent packet loss observed: 30% loss to target.",
                evidence=["Measured packet loss: 30%", "2 out of 6 ICMP probe packets dropped."],
                is_simulated=True
            )
            return [local_healthy, gw_healthy, dns_healthy, tcp_healthy, lat_loss]

        # Scenario 10: Healthy Baseline
        http_200 = TestResult(
            test_id="http_01",
            stage=DiagnosticStage.HTTP_TLS,
            test_name="HTTP/HTTPS Service Health & Status",
            start_time=now,
            end_time=now,
            status=TestStatus.PASS,
            measured_values={"status_code": 200, "response_duration_ms": 35.0},
            human_explanation="HTTP service returned status 200 (OK).",
            evidence=["HTTP 200 OK received in 35ms.", "Server: cloudflare"],
            is_simulated=True
        )
        lat_clean = TestResult(
            test_id="latency_01",
            stage=DiagnosticStage.LATENCY,
            test_name="Round-Trip Latency & Packet Loss Profile",
            start_time=now,
            end_time=now,
            status=TestStatus.PASS,
            measured_values={"packet_loss_pct": 0.0, "avg_latency_ms": 18.0, "min_latency_ms": 15.0, "max_latency_ms": 22.0},
            human_explanation="Connection latency is stable (avg 18ms, 0% loss).",
            evidence=["Round-trip Latency: min=15ms, avg=18ms, max=22ms", "0% packet loss."],
            is_simulated=True
        )

        return [local_healthy, gw_healthy, dns_healthy, tcp_healthy, http_200, lat_clean]
