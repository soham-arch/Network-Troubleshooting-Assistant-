"""Cross-platform network discovery and command execution adapters."""

import os
import platform
import re
import socket
import subprocess
from typing import Any, Dict, List, Optional, Tuple


def get_os_type() -> str:
    """Returns 'windows', 'darwin' (macOS), or 'linux'."""
    sys_name = platform.system().lower()
    if sys_name == "windows":
        return "windows"
    elif sys_name == "darwin":
        return "macos"
    elif sys_name == "linux":
        return "linux"
    return sys_name


def get_hostname() -> str:
    """Get machine hostname safely."""
    try:
        return socket.gethostname()
    except Exception:
        return "Unknown"


def get_default_gateway_and_dns() -> Tuple[Optional[str], List[str]]:
    """
    Cross-platform resolution for default gateway and configured DNS servers.
    Returns (gateway_ip, [dns_server_ips])
    """
    os_type = get_os_type()
    gateway: Optional[str] = None
    dns_servers: List[str] = []

    if os_type == "windows":
        try:
            # Run netsh or ipconfig safely
            result = subprocess.run(
                ["ipconfig", "/all"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False
            )
            out = result.stdout

            # Extract Default Gateway
            gw_matches = re.findall(r"Default Gateway[ .]*:\s*([0-9a-fA-F.:]+)", out)
            for gw in gw_matches:
                gw = gw.strip()
                if gw and gw != "::" and gw != "0.0.0.0":
                    gateway = gw
                    break

            # Extract DNS Servers
            dns_matches = re.findall(r"DNS Servers[ .]*:\s*([0-9a-fA-F.:]+)", out)
            for dns in dns_matches:
                dns = dns.strip()
                if dns and dns not in dns_servers:
                    dns_servers.append(dns)

        except Exception:
            pass

    elif os_type in ("linux", "macos"):
        try:
            # Check resolv.conf for DNS
            if os.path.exists("/etc/resolv.conf"):
                with open("/etc/resolv.conf", "r") as f:
                    for line in f:
                        if line.startswith("nameserver"):
                            parts = line.split()
                            if len(parts) > 1:
                                dns_servers.append(parts[1].strip())

            # Check ip route or netstat for default gateway
            res = subprocess.run(
                ["ip", "route", "show", "default"],
                capture_output=True,
                text=True,
                timeout=4,
                check=False
            )
            if res.returncode == 0:
                match = re.search(r"default via ([0-9a-fA-F.:]+)", res.stdout)
                if match:
                    gateway = match.group(1)
            elif os_type == "macos":
                res = subprocess.run(
                    ["netstat", "-nr"],
                    capture_output=True,
                    text=True,
                    timeout=4,
                    check=False
                )
                match = re.search(r"default\s+([0-9a-fA-F.:]+)", res.stdout)
                if match:
                    gateway = match.group(1)
        except Exception:
            pass

    return gateway, dns_servers


def get_local_interfaces_info() -> List[Dict[str, Any]]:
    """
    Enumerates local network interfaces with active IP addresses and status.
    Uses socket and psutil if available.
    """
    interfaces = []
    try:
        import psutil
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()

        for name, addr_list in addrs.items():
            stat = stats.get(name)
            is_up = stat.isup if stat else False
            ipv4_list = []
            ipv6_list = []

            for addr in addr_list:
                if addr.family == socket.AF_INET:
                    ipv4_list.append(addr.address)
                elif hasattr(socket, 'AF_INET6') and addr.family == socket.AF_INET6:
                    # Strip interface zone scope if present
                    clean_v6 = addr.address.split('%')[0]
                    ipv6_list.append(clean_v6)

            if ipv4_list or ipv6_list:
                interfaces.append({
                    "name": name,
                    "is_up": is_up,
                    "ipv4": ipv4_list,
                    "ipv6": ipv6_list,
                    "speed_mbps": stat.speed if stat else 0
                })
    except Exception:
        # Fallback to standard socket
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            interfaces.append({
                "name": "default",
                "is_up": True,
                "ipv4": [ip],
                "ipv6": [],
                "speed_mbps": 0
            })
        except Exception:
            pass

    return interfaces
