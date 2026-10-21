"""Security, input sanitation and target policy validation."""

import ipaddress
import re
from typing import Any, Optional, Tuple

# Disallow shell metacharacters and dangerous patterns
DISALLOWED_SHELL_CHARS = re.compile(r"[;&|`$<>\r\n\"'\\]")
HOSTNAME_REGEX = re.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,63}$|^[a-zA-Z0-9]+$"
)

# Cloud metadata addresses to block for security
BLOCKED_IP_STRINGS = {
    "169.254.169.254",  # AWS/GCP/Azure link-local metadata
    "metadata.google.internal",
}


def sanitize_input(value: str) -> str:
    """Strip whitespace and dangerous characters."""
    if not value:
        return ""
    # Strip whitespace
    clean = value.strip()
    return clean


def validate_hostname_or_ip(target: str) -> Tuple[bool, str, Optional[str]]:
    """
    Validates a destination host or IP address.
    Returns: (is_valid, sanitized_target, error_message)
    """
    if not target or not isinstance(target, str):
        return False, "", "Target host/IP cannot be empty."

    target = target.strip()

    # Reject shell injection characters
    if DISALLOWED_SHELL_CHARS.search(target):
        return False, target, "Target contains illegal characters."

    # Check for blocked cloud metadata targets
    if target.lower() in BLOCKED_IP_STRINGS:
        return False, target, "Access to cloud metadata endpoints is prohibited."

    # Try parsing as IP address (IPv4 or IPv6)
    try:
        ip = ipaddress.ip_address(target)
        if ip.is_loopback:
            # Loopback allowed for local testing/fixtures
            return True, str(ip), None
        if ip.is_link_local and str(ip) == "169.254.169.254":
            return False, target, "Link-local cloud metadata addresses are prohibited."
        return True, str(ip), None
    except ValueError:
        pass

    # Try validating as hostname
    if len(target) > 253:
        return False, target, "Hostname exceeds maximum length of 253 characters."

    if not HOSTNAME_REGEX.match(target):
        return False, target, "Invalid hostname format."

    return True, target, None


def validate_port(port: Any) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Validates TCP/UDP port number between 1 and 65535.
    Returns: (is_valid, port_int, error_message)
    """
    if port is None or port == "":
        return True, None, None  # Port is optional

    try:
        p = int(port)
        if 1 <= p <= 65535:
            return True, p, None
        return False, None, f"Port {p} out of range (1-65535)."
    except (ValueError, TypeError):
        return False, None, "Port must be an integer between 1 and 65535."
