"""Ticketing Connectors: Jira and Generic ITSM Webhooks.

Translates DiagnosticSession findings and root-cause analysis into structured incident tickets.
"""

from __future__ import annotations

import base64
import json
import logging
from typing import Any, Dict, Optional
import requests

from diagnostics.models import DiagnosticSession
from utils.config import config

logger = logging.getLogger(__name__)


class JiraConnector:
    """Connects to Jira Cloud or Server REST API to create network incident tickets."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        email: Optional[str] = None,
        api_token: Optional[str] = None,
        project_key: Optional[str] = None
    ):
        self.base_url = (base_url or getattr(config, "jira_base_url", "")).rstrip("/")
        self.email = email or getattr(config, "jira_email", "")
        self.api_token = api_token or getattr(config, "jira_api_token", "")
        self.project_key = project_key or getattr(config, "jira_project_key", "IT")

    def is_configured(self) -> bool:
        """Checks if Jira connection credentials are fully populated."""
        return bool(self.base_url and self.email and self.api_token)

    def create_incident_ticket(
        self,
        session: DiagnosticSession,
        summary: Optional[str] = None,
        issue_type: str = "Bug"
    ) -> Dict[str, Any]:
        """Creates an incident ticket in Jira. Falls back to simulated response if unconfigured."""
        top_h = session.hypotheses[0] if session.hypotheses else None
        target = f"{session.target_host or 'Local Network'}:{session.target_port or ''}"
        issue_summary = summary or f"[Network Incident] {target} — {top_h.title if top_h else 'Investigation'}"

        description_lines = [
            f"*User Reported Symptom:* {session.user_symptom}",
            f"*Target Endpoint:* {target}",
            f"*Session ID:* {session.session_id}",
            "",
            "h3. Deterministic Root Cause Findings",
            f"*Probable Cause:* {top_h.probable_root_cause if top_h else 'None'}",
            f"*Confidence:* {top_h.confidence.value if top_h else 'LOW'} ({int(top_h.confidence_score*100) if top_h else 0}%)",
            "",
            "h3. Key Evidence",
        ]
        if top_h and top_h.supporting_evidence:
            for ev in top_h.supporting_evidence:
                description_lines.append(f"* {ev}")

        description_lines.extend([
            "",
            "h3. Recommended Next Steps",
            f"{top_h.suggested_corrective_action if top_h else 'Verify target'}"
        ])
        description_text = "\n".join(description_lines)

        if not self.is_configured():
            logger.info("Jira not configured; generating simulated incident ticket.")
            mock_key = f"{self.project_key}-INC-{session.session_id[:6].upper()}"
            return {
                "success": True,
                "simulated": True,
                "ticket_id": mock_key,
                "ticket_url": f"https://mock-jira.internal/browse/{mock_key}",
                "message": "Simulated ticket generated (configure JIRA_* env vars for live dispatch)."
            }

        endpoint = f"{self.base_url}/rest/api/2/issue"
        auth_str = f"{self.email}:{self.api_token}"
        auth_header = base64.b64encode(auth_str.encode()).decode()

        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/json"
        }
        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": issue_summary,
                "description": description_text,
                "issuetype": {"name": issue_type}
            }
        }

        try:
            res = requests.post(endpoint, json=payload, headers=headers, timeout=10)
            if res.status_code in (200, 201):
                data = res.json()
                key = data.get("key", "UNKNOWN")
                return {
                    "success": True,
                    "simulated": False,
                    "ticket_id": key,
                    "ticket_url": f"{self.base_url}/browse/{key}",
                    "message": "Ticket created successfully in Jira."
                }
            else:
                logger.error(f"Jira API error {res.status_code}: {res.text}")
                return {
                    "success": False,
                    "simulated": False,
                    "ticket_id": None,
                    "message": f"Jira API error ({res.status_code}): {res.text}"
                }
        except Exception as e:
            logger.error(f"Failed to communicate with Jira API: {e}")
            return {
                "success": False,
                "simulated": False,
                "ticket_id": None,
                "message": f"Connection error: {str(e)}"
            }


class GenericTicketWebhookConnector:
    """Dispatches complete structured incident reports to any ITSM or NOC webhook endpoint."""

    @staticmethod
    def send_incident_to_webhook(
        session: DiagnosticSession,
        webhook_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Posts structured JSON ticket payload to an external webhook."""
        url = webhook_url or getattr(config, "ticketing_webhook_url", "")
        if not url:
            mock_id = f"WH-TICKET-{session.session_id[:8]}"
            return {
                "success": True,
                "simulated": True,
                "ticket_id": mock_id,
                "message": "Simulated webhook ticket generated (no webhook URL specified)."
            }

        top_h = session.hypotheses[0] if session.hypotheses else None
        payload = {
            "event_type": "network_incident_ticket",
            "session_id": session.session_id,
            "timestamp": session.start_time,
            "target_host": session.target_host,
            "target_port": session.target_port,
            "user_symptom": session.user_symptom,
            "root_cause_analysis": {
                "title": top_h.title if top_h else "Inconclusive",
                "probable_cause": top_h.probable_root_cause if top_h else "None",
                "confidence": top_h.confidence.value if top_h else "LOW",
                "confidence_score": top_h.confidence_score if top_h else 0.0,
                "action": top_h.suggested_corrective_action if top_h else "Verify service"
            },
            "failed_tests_count": sum(1 for t in session.test_results if t.status.value in ("FAIL", "ERROR")),
            "test_summary": [
                {"test": t.test_name, "stage": t.stage.value, "status": t.status.value, "explanation": t.human_explanation}
                for t in session.test_results
            ]
        }

        try:
            res = requests.post(url, json=payload, timeout=8)
            success = res.status_code in (200, 201, 202, 204)
            return {
                "success": success,
                "simulated": False,
                "ticket_id": f"WH-{session.session_id[:8]}",
                "message": f"Webhook returned status HTTP {res.status_code}"
            }
        except Exception as e:
            return {
                "success": False,
                "simulated": False,
                "ticket_id": None,
                "message": f"Webhook request failed: {str(e)}"
            }
