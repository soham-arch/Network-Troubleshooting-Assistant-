"""Unit tests for Traceroute Output Parser & Interactive Visualizer."""

import pytest
from diagnostics.models import DiagnosticStage, TestResult, TestStatus
from diagnostics.traceroute_visualizer import (
    create_traceroute_path_figure,
    find_first_failing_hop,
    parse_traceroute_hops,
)


def test_parse_windows_tracert():
    raw_lines = [
        "Hop 1: <1 ms <1 ms <1 ms 192.168.1.1",
        "Hop 2: 12 ms 11 ms 14 ms 10.0.0.1",
        "Hop 3: * * * (No response observed)",
        "Hop 4: 25 ms 24 ms 26 ms 8.8.8.8"
    ]
    hops = parse_traceroute_hops(raw_hops=raw_lines)
    assert len(hops) == 4
    assert hops[0].hop_number == 1
    assert hops[0].ip == "192.168.1.1"
    assert hops[0].status == "OK"

    # Hop 3 is a timeout
    assert hops[2].hop_number == 3
    assert hops[2].status in ("FIRST_FAILURE", "TIMEOUT")

    first_fail = find_first_failing_hop(hops)
    assert first_fail is not None
    assert first_fail.hop_number == 3


def test_figure_generation():
    raw_lines = [
        "Hop 1: 1 ms 1 ms 1 ms 192.168.1.1",
        "Hop 2: 45 ms 40 ms 42 ms 172.16.0.1"
    ]
    hops = parse_traceroute_hops(raw_hops=raw_lines)
    fig = create_traceroute_path_figure(hops, target_host="172.16.0.1")
    assert fig is not None
    assert len(fig.data) >= 2  # line + scatter + bar
