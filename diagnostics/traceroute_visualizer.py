"""Interactive Traceroute Visualization & Hop Failure Analyzer.

Parses cross-platform traceroute outputs, computes per-hop latency and packet loss,
identifies the first failing hop or latency bottleneck, and produces an interactive
Plotly network path graph.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from diagnostics.models import TestResult, DiagnosticStage


class TracerouteHop(BaseModel):
    """Structured network hop information."""
    hop_number: int
    ip: str = "Unknown"
    hostname: Optional[str] = None
    latencies_ms: List[float] = Field(default_factory=list)
    avg_latency_ms: Optional[float] = None
    min_latency_ms: Optional[float] = None
    max_latency_ms: Optional[float] = None
    loss_pct: float = 0.0
    status: str = "OK"  # OK, HIGH_LATENCY, PACKET_LOSS, TIMEOUT, FIRST_FAILURE
    raw_text: str = ""


def parse_traceroute_hops(traceroute_result: Optional[TestResult] = None, raw_hops: Optional[List[str]] = None) -> List[TracerouteHop]:
    """
    Parses hop records from either a TestResult or raw string lines.
    Handles Windows tracert and Linux/Unix traceroute formats.
    """
    lines: List[str] = []
    if traceroute_result and traceroute_result.stage == DiagnosticStage.TRACEROUTE:
        lines = traceroute_result.measured_values.get("hops", [])
        if not lines:
            lines = [e for e in traceroute_result.evidence if e.startswith("Hop ") or re.match(r"^\d+\s+", e)]
    elif raw_hops:
        lines = raw_hops

    if not lines:
        return []

    parsed: List[TracerouteHop] = []

    for line in lines:
        line_str = str(line).strip()
        # Hop prefix pattern: e.g. "Hop 1: <1 ms <1 ms <1 ms 192.168.1.1" or "1  192.168.1.1  0.5 ms"
        match_hop = re.search(r"(?:Hop\s+)?(\d+)[:\s]+(.+)", line_str, re.IGNORECASE)
        if not match_hop:
            continue

        hop_num = int(match_hop.group(1))
        content = match_hop.group(2).strip()

        # Check for complete timeout
        if "* * *" in content or "no response" in content.lower() or content.startswith("*"):
            parsed.append(TracerouteHop(
                hop_number=hop_num,
                ip="* (No response)",
                latencies_ms=[],
                loss_pct=100.0,
                status="TIMEOUT",
                raw_text=line_str
            ))
            continue

        # Extract IP address
        ip_match = re.search(r"(\d{1,3}(?:\.\d{1,3}){3})", content)
        ip = ip_match.group(1) if ip_match else "Unknown"

        # Extract hostname if present
        host_match = re.search(r"([a-zA-Z0-9\.\-_]+\.[a-zA-Z]{2,})", content)
        hostname = host_match.group(1) if host_match and host_match.group(1) != ip else None

        # Extract latencies (e.g., "<1 ms", "12.4 ms", "15 ms")
        lat_matches = re.findall(r"(?:<\s*)?(\d+(?:\.\d+)?)\s*ms", content)
        latencies = [float(l) for l in lat_matches]

        # Calculate packet loss if asterisks mixed with latencies
        total_probes = max(3, len(latencies) + content.count("*"))
        loss_pct = round((content.count("*") / total_probes) * 100, 1)

        avg_lat = round(sum(latencies) / len(latencies), 2) if latencies else None
        min_lat = min(latencies) if latencies else None
        max_lat = max(latencies) if latencies else None

        # Determine status
        if loss_pct >= 50.0:
            status = "PACKET_LOSS"
        elif avg_lat and avg_lat > 120.0:
            status = "HIGH_LATENCY"
        else:
            status = "OK"

        parsed.append(TracerouteHop(
            hop_number=hop_num,
            ip=ip,
            hostname=hostname,
            latencies_ms=latencies,
            avg_latency_ms=avg_lat,
            min_latency_ms=min_lat,
            max_latency_ms=max_lat,
            loss_pct=loss_pct,
            status=status,
            raw_text=line_str
        ))

    # Mark first failure point
    first_failure_identified = False
    for hop in parsed:
        if not first_failure_identified and hop.status in ("TIMEOUT", "PACKET_LOSS", "HIGH_LATENCY"):
            hop.status = "FIRST_FAILURE"
            first_failure_identified = True
            break

    return parsed


def find_first_failing_hop(hops: List[TracerouteHop]) -> Optional[TracerouteHop]:
    """Finds the first hop that timed out or experienced severe degradation."""
    for h in hops:
        if h.status in ("FIRST_FAILURE", "TIMEOUT", "PACKET_LOSS"):
            return h
    return None


def create_traceroute_path_figure(hops: List[TracerouteHop], target_host: str = "") -> go.Figure:
    """
    Renders an interactive Plotly diagram of network hops:
    - Path topology node diagram with color coded status (Green, Yellow, Red)
    - Latency trend overlay
    - First failing hop highlighted
    """
    if not hops:
        fig = go.Figure()
        fig.add_annotation(
            text="No traceroute hop data available",
            showarrow=False,
            font=dict(size=14, color="#94a3b8")
        )
        fig.update_layout(height=200, margin=dict(l=10, r=10, t=10, b=10))
        return fig

    hop_nums = [h.hop_number for h in hops]
    labels = [f"Hop {h.hop_number}<br><b>{h.ip}</b>" for h in hops]
    latencies = [h.avg_latency_ms if h.avg_latency_ms is not None else 0 for h in hops]

    colors = []
    marker_sizes = []
    marker_symbols = []

    for h in hops:
        if h.status == "FIRST_FAILURE":
            colors.append("#dc2626")  # Bright Red
            marker_sizes.append(22)
            marker_symbols.append("x-thin-open")
        elif h.status == "TIMEOUT":
            colors.append("#ef4444")  # Red
            marker_sizes.append(16)
            marker_symbols.append("circle")
        elif h.status == "PACKET_LOSS":
            colors.append("#f97316")  # Orange
            marker_sizes.append(16)
            marker_symbols.append("diamond")
        elif h.status == "HIGH_LATENCY":
            colors.append("#eab308")  # Yellow
            marker_sizes.append(16)
            marker_symbols.append("circle")
        else:
            colors.append("#10b981")  # Emerald Green
            marker_sizes.append(16)
            marker_symbols.append("circle")

    # Create subplots: Top is path topology, bottom is latency bar chart
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.55, 0.45],
        shared_xaxes=True,
        vertical_spacing=0.15,
        subplot_titles=("Network Route Topology & Failure Point", "Hop Latency (ms)")
    )

    # 1. Route Topology Path (Line + Scatter)
    hover_texts = []
    for h in hops:
        status_desc = {
            "FIRST_FAILURE": "🚨 FIRST BOTTLENECK / FAILING HOP",
            "TIMEOUT": "⚠️ Request Timed Out (100% Loss)",
            "PACKET_LOSS": f"⚠️ Degraded (Loss: {h.loss_pct}%)",
            "HIGH_LATENCY": f"⚠️ High Latency ({h.avg_latency_ms} ms)",
            "OK": f"✅ Healthy ({h.avg_latency_ms} ms)"
        }.get(h.status, h.status)

        hover_texts.append(
            f"<b>Hop {h.hop_number}</b><br>"
            f"IP: {h.ip}<br>"
            f"Host: {h.hostname or 'N/A'}<br>"
            f"Avg RTT: {h.avg_latency_ms or 'N/A'} ms<br>"
            f"Loss: {h.loss_pct}%<br>"
            f"Status: {status_desc}"
        )

    # Connecting backbone line
    fig.add_trace(
        go.Scatter(
            x=hop_nums,
            y=[1] * len(hop_nums),
            mode="lines",
            line=dict(color="#cbd5e1", width=3),
            hoverinfo="skip",
            showlegend=False
        ),
        row=1, col=1
    )

    # Hop Node Markers
    fig.add_trace(
        go.Scatter(
            x=hop_nums,
            y=[1] * len(hop_nums),
            mode="markers+text",
            marker=dict(
                size=marker_sizes,
                color=colors,
                line=dict(width=2, color="#ffffff")
            ),
            text=[f"H{h.hop_number}" for h in hops],
            textposition="top center",
            hovertext=hover_texts,
            hoverinfo="text",
            name="Hops",
            showlegend=False
        ),
        row=1, col=1
    )

    # Annotate first failure
    first_fail = find_first_failing_hop(hops)
    if first_fail:
        fig.add_annotation(
            x=first_fail.hop_number,
            y=1,
            text=f"🚨 Failing Hop ({first_fail.ip})",
            showarrow=True,
            arrowhead=2,
            arrowcolor="#dc2626",
            ax=0,
            ay=-45,
            font=dict(color="#dc2626", size=12, family="sans-serif"),
            bgcolor="#fee2e2",
            bordercolor="#f87171",
            borderwidth=1,
            row=1, col=1
        )

    # 2. Latency Bars
    fig.add_trace(
        go.Bar(
            x=hop_nums,
            y=latencies,
            marker_color=colors,
            name="Avg Latency (ms)",
            hovertext=[f"Hop {h.hop_number}: {h.avg_latency_ms or 0} ms" for h in hops],
            hoverinfo="text",
            showlegend=False
        ),
        row=2, col=1
    )

    fig.update_yaxes(
        showticklabels=False,
        showgrid=False,
        zeroline=False,
        row=1, col=1
    )
    fig.update_yaxes(
        title_text="ms",
        showgrid=True,
        gridcolor="rgba(255, 255, 255, 0.07)",
        color="#94a3b8",
        row=2, col=1
    )
    fig.update_xaxes(
        title_text="Hop Number",
        tickmode="linear",
        tick0=1,
        dtick=1,
        color="#94a3b8",
        row=2, col=1
    )

    fig.update_layout(
        height=380,
        margin=dict(l=40, r=40, t=40, b=40),
        plot_bgcolor="rgba(15, 23, 42, 0.45)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="'Inter', sans-serif", color="#e2e8f0")
    )

    return fig
