"""Natural Language Symptom Intake & Structured Target Parser.

Parses free-text user symptoms into structured diagnostic targets (host, port, service)
and recommends prioritized diagnostic stages.
Uses deterministic heuristics with regex and keyword mapping, augmented by LLM if enabled.
"""

from __future__ import annotations

import json
import logging
import re
from typing import List, Optional
from pydantic import BaseModel, Field

from llm.client import LLMClient

logger = logging.getLogger(__name__)


class ParsedSymptom(BaseModel):
    """Structured representation of a parsed user symptom."""
    original_text: str
    target_host: Optional[str] = None
    target_port: Optional[int] = None
    service_type: Optional[str] = None
    recommended_stages: List[str] = Field(default_factory=lambda: [
        "local_config", "gateway", "dns", "destination", "port", "http_tls", "latency"
    ])
    category: str = "GENERIC_CONNECTIVITY"
    confidence: float = 0.8
    reasoning: str = ""


# Keywords associated with specific diagnostic domains
_VOIP_KEYWORDS = ["teams", "zoom", "meet", "call", "audio", "video dropping", "lag", "jitter", "packet loss", "latency", "stutter"]
_WEB_KEYWORDS = ["website", "web", "http", "https", "page", "browser", "404", "500", "502", "ssl", "certificate", "portal", "dashboard"]
_DNS_KEYWORDS = ["dns", "resolve", "domain", "nxdomain", "hostname", "name lookup", "url cannot be found"]
_PORT_KEYWORDS = ["port", "handshake", "refused", "ssh", "rdp", "database", "mysql", "postgres", "redis", "socket"]
_ROUTING_KEYWORDS = ["route", "hops", "traceroute", "carrier", "isp", "vpn", "gateway"]


def parse_symptom(text: str, llm_client: Optional[LLMClient] = None) -> ParsedSymptom:
    """
    Parses a free-text symptom into structured diagnostic parameters.
    Combines robust regex & deterministic keyword logic with optional LLM refinement.
    """
    clean_text = text.strip()
    if not clean_text:
        return ParsedSymptom(
            original_text="",
            category="EMPTY",
            confidence=0.0,
            reasoning="No symptom text provided."
        )

    # 1. Deterministic Extraction
    deterministic = _parse_deterministic(clean_text)

    # 2. If LLM is configured and confidence is moderate, attempt LLM refinement
    if llm_client and llm_client.is_configured():
        llm_parsed = _parse_with_llm(clean_text, llm_client, fallback=deterministic)
        if llm_parsed:
            return llm_parsed

    return deterministic


def _parse_deterministic(text: str) -> ParsedSymptom:
    """Deterministic extractor using regex and network heuristics."""
    text_lower = text.lower()
    target_host: Optional[str] = None
    target_port: Optional[int] = None
    service_type: Optional[str] = None
    category = "GENERIC_CONNECTIVITY"
    recommended_stages = ["local_config", "gateway"]
    reasoning_parts = []

    # Extract URL if present
    url_match = re.search(r"https?://([a-zA-Z0-9\.\-]+)(?::(\d+))?", text)
    if url_match:
        target_host = url_match.group(1)
        if url_match.group(2):
            target_port = int(url_match.group(2))
        elif text.startswith("https://") or "https://" in text:
            target_port = 443
            service_type = "https"
        else:
            target_port = 80
            service_type = "http"
        reasoning_parts.append(f"Extracted URL target: {target_host}")

    # Extract IP address if not found via URL
    if not target_host:
        ip_match = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text)
        if ip_match:
            target_host = ip_match.group(0)
            reasoning_parts.append(f"Extracted IP target: {target_host}")

    # Extract domain name if still not found
    if not target_host:
        domain_match = re.search(r"\b((?:[a-zA-Z0-9\-]+\.)+(?:com|org|net|io|edu|gov|internal|local|corp|co|in|dev|app))\b", text, re.IGNORECASE)
        if domain_match:
            target_host = domain_match.group(1).lower()
            reasoning_parts.append(f"Extracted domain: {target_host}")

    # Extract Port if mentioned (e.g. "port 8080", ":3306")
    if not target_port:
        port_match = re.search(r"(?:port\s+|:)(\d{2,5})\b", text_lower)
        if port_match:
            try:
                p = int(port_match.group(1))
                if 1 <= p <= 65535:
                    target_port = p
                    reasoning_parts.append(f"Extracted target port: {p}")
            except ValueError:
                pass

    # Protocol & Category detection
    if any(k in text_lower for k in _VOIP_KEYWORDS):
        category = "VOIP_REALTIME_DEGRADATION"
        recommended_stages.extend(["dns", "destination", "latency", "traceroute"])
        if not service_type:
            service_type = "udp_or_rtp"
        reasoning_parts.append("Detected VoIP / Real-time call quality symptom; prioritized latency, jitter, loss & route traceroute.")
    elif any(k in text_lower for k in _WEB_KEYWORDS):
        category = "WEB_SERVICE_FAILURE"
        recommended_stages.extend(["dns", "destination", "port", "http_tls", "latency"])
        if not service_type:
            service_type = "https" if target_port == 443 or "https" in text_lower else "http"
        if not target_port:
            target_port = 443 if service_type == "https" else 80
        reasoning_parts.append("Detected Web Application symptom; prioritized DNS, TCP handshake, and HTTP/TLS diagnostics.")
    elif any(k in text_lower for k in _DNS_KEYWORDS):
        category = "DNS_RESOLUTION_ISSUE"
        recommended_stages.extend(["dns"])
        reasoning_parts.append("Detected DNS name resolution symptom; prioritized local resolver check.")
    elif any(k in text_lower for k in _PORT_KEYWORDS):
        category = "PORT_CONNECTIVITY_ISSUE"
        recommended_stages.extend(["dns", "destination", "port"])
        # Check standard ports
        if "ssh" in text_lower and not target_port:
            target_port = 22
        elif "mysql" in text_lower and not target_port:
            target_port = 3306
        elif "postgres" in text_lower and not target_port:
            target_port = 5432
        elif "redis" in text_lower and not target_port:
            target_port = 6379
        reasoning_parts.append(f"Detected Port/Service connectivity issue (target port: {target_port or 'not specified'}).")
    elif any(k in text_lower for k in _ROUTING_KEYWORDS):
        category = "ROUTING_PATH_ISSUE"
        recommended_stages.extend(["dns", "destination", "latency", "traceroute"])
        reasoning_parts.append("Detected Routing/Path symptom; prioritized latency and traceroute.")
    else:
        recommended_stages.extend(["dns", "destination", "port", "http_tls", "latency", "traceroute"])
        reasoning_parts.append("Generic symptom: running comprehensive multi-stage diagnostic suite.")

    if not service_type:
        if target_port == 443:
            service_type = "https"
        elif target_port == 80:
            service_type = "http"
        elif target_port:
            service_type = "tcp"

    # Deduplicate stages while preserving order
    deduped_stages = []
    for s in recommended_stages:
        if s not in deduped_stages:
            deduped_stages.append(s)

    return ParsedSymptom(
        original_text=text,
        target_host=target_host,
        target_port=target_port,
        service_type=service_type,
        recommended_stages=deduped_stages,
        category=category,
        confidence=0.85 if target_host else 0.65,
        reasoning="; ".join(reasoning_parts)
    )


def _parse_with_llm(text: str, client: LLMClient, fallback: ParsedSymptom) -> Optional[ParsedSymptom]:
    """Uses LLM to extract JSON target parameters from free-text."""
    system_prompt = (
        "You are an expert network engineer assisting a diagnostic tool. "
        "Extract the user's network problem into a JSON object matching this schema:\n"
        "{\n"
        '  "target_host": string or null,\n'
        '  "target_port": integer or null,\n'
        '  "service_type": "https" | "http" | "tcp" | null,\n'
        '  "category": "WEB_SERVICE_FAILURE" | "VOIP_REALTIME_DEGRADATION" | "DNS_RESOLUTION_ISSUE" | "PORT_CONNECTIVITY_ISSUE" | "GENERIC_CONNECTIVITY",\n'
        '  "recommended_stages": ["local_config", "gateway", "dns", "destination", "port", "http_tls", "latency", "traceroute"],\n'
        '  "reasoning": string\n'
        "}\n"
        "Return ONLY the valid JSON object without markdown fences or extraneous text."
    )
    user_prompt = f"Analyze this network symptom: '{text}'"

    raw = client.generate_completion(system_prompt, user_prompt)
    if not raw:
        return None

    try:
        # Strip potential markdown code block fences
        cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r"```$", "", cleaned.strip(), flags=re.MULTILINE)
        data = json.loads(cleaned)

        return ParsedSymptom(
            original_text=text,
            target_host=data.get("target_host") or fallback.target_host,
            target_port=data.get("target_port") or fallback.target_port,
            service_type=data.get("service_type") or fallback.service_type,
            recommended_stages=data.get("recommended_stages") or fallback.recommended_stages,
            category=data.get("category") or fallback.category,
            confidence=0.95,
            reasoning=data.get("reasoning") or fallback.reasoning
        )
    except Exception as e:
        logger.debug(f"Failed to parse LLM symptom response as JSON: {e}")
        return None
