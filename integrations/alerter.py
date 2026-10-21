"""Multi-Channel Alert Dispatcher.

Dispatches network incident and degradation notifications via:
1. Slack Webhooks
2. Generic HTTP Webhooks (PagerDuty, NOC dashboards)
3. Email (SMTP / Simulation fallback)
"""

from __future__ import annotations

import datetime
import email.mime.text
import logging
import smtplib
from typing import Any, Dict, List, Optional
import requests

from monitoring.models import AlertNotification, MonitoringTarget
from utils.config import config

logger = logging.getLogger(__name__)


class MultiChannelAlerter:
    """Manages dispatching and rate-limiting network alerts across channels."""

    def __init__(self):
        # In-memory last alert timestamps to throttle repetitive alerts {target_id: timestamp}
        self._last_alert_times: Dict[str, datetime.datetime] = {}
        self.cooldown_seconds = 180  # 3 minute throttle per target for identical alerts

    def should_suppress_alert(self, target_id: str, new_status: str) -> bool:
        """Determines if alert should be throttled."""
        now = datetime.datetime.now()
        last = self._last_alert_times.get(target_id)
        if last and (now - last).total_seconds() < self.cooldown_seconds:
            return True
        self._last_alert_times[target_id] = now
        return False

    def dispatch_incident_alert(
        self,
        target: MonitoringTarget,
        status: str,
        reason: str,
        session_id: Optional[str] = None
    ) -> List[AlertNotification]:
        """Dispatches alerts across all configured channels for this target."""
        notifications: List[AlertNotification] = []
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        subject = f"🚨 Network Alert: {target.name} is {status.upper()}"
        body = (
            f"Target: {target.name} ({target.host}:{target.port})\n"
            f"Current Status: {status}\n"
            f"Observation: {reason}\n"
            f"Timestamp: {now_iso}\n"
            f"Diagnostic Session: {session_id or 'N/A'}"
        )

        # 1. Slack Webhook
        slack_url = target.alert_slack_webhook or getattr(config, "alert_slack_webhook", "")
        if slack_url:
            status_sent = self.send_slack_alert(slack_url, subject, body, target)
            notifications.append(AlertNotification(
                target_id=target.target_id,
                target_name=target.name,
                alert_channel="SLACK",
                status="SENT" if status_sent else "FAILED",
                message=reason
            ))

        # 2. Generic HTTP Webhook
        generic_url = target.alert_generic_webhook or getattr(config, "alert_generic_webhook", "")
        if generic_url:
            payload = {
                "event": "network_incident",
                "target_id": target.target_id,
                "target_name": target.name,
                "host": target.host,
                "port": target.port,
                "status": status,
                "reason": reason,
                "session_id": session_id,
                "timestamp": now_iso
            }
            status_sent = self.send_generic_webhook(generic_url, payload)
            notifications.append(AlertNotification(
                target_id=target.target_id,
                target_name=target.name,
                alert_channel="WEBHOOK",
                status="SENT" if status_sent else "FAILED",
                message=reason
            ))

        # 3. Email Alert
        recipient = target.alert_email or getattr(config, "alert_email", "")
        if recipient:
            status_sent = self.send_email_alert(recipient, subject, body)
            notifications.append(AlertNotification(
                target_id=target.target_id,
                target_name=target.name,
                alert_channel="EMAIL",
                status="SENT" if status_sent else "SIMULATED",
                message=reason
            ))

        return notifications

    def send_slack_alert(self, webhook_url: str, title: str, text: str, target: MonitoringTarget) -> bool:
        """Sends rich card payload to Slack webhook endpoint."""
        try:
            payload = {
                "text": title,
                "blocks": [
                    {
                        "type": "header",
                        "text": {"type": "plain_text", "text": title, "emoji": True}
                    },
                    {
                        "type": "section",
                        "fields": [
                            {"type": "mrkdwn", "text": f"*Target:*\n`{target.name}`"},
                            {"type": "mrkdwn", "text": f"*Endpoint:*\n`{target.host}:{target.port}`"},
                            {"type": "mrkdwn", "text": f"*Status:*\n*{target.current_status}*"},
                            {"type": "mrkdwn", "text": f"*Time:*\n{datetime.datetime.now().strftime('%H:%M:%S UTC')}"}
                        ]
                    },
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"```{text}```"}
                    }
                ]
            }
            res = requests.post(webhook_url, json=payload, timeout=5)
            return res.status_code == 200
        except Exception as e:
            logger.error(f"Failed to post Slack alert: {e}")
            return False

    def send_generic_webhook(self, webhook_url: str, payload: Dict[str, Any]) -> bool:
        """Sends JSON payload to generic HTTP webhook."""
        try:
            res = requests.post(webhook_url, json=payload, timeout=5)
            return res.status_code in (200, 201, 202, 204)
        except Exception as e:
            logger.error(f"Failed to send generic webhook alert: {e}")
            return False

    def send_email_alert(self, recipient: str, subject: str, body: str) -> bool:
        """Sends email alert via SMTP if credentials exist, otherwise logs safely."""
        smtp_host = getattr(config, "smtp_host", "")
        smtp_port = getattr(config, "smtp_port", 587)
        smtp_user = getattr(config, "smtp_user", "")
        smtp_pass = getattr(config, "smtp_password", "")
        smtp_from = getattr(config, "smtp_from", "alerts@network-assistant.local")

        if not smtp_host:
            logger.info(f"[SIMULATED EMAIL ALERT to {recipient}]: {subject}\n{body}")
            return False  # Simulated

        try:
            msg = email.mime.text.MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = smtp_from
            msg["To"] = recipient

            with smtplib.SMTP(smtp_host, smtp_port, timeout=5) as server:
                server.starttls()
                if smtp_user and smtp_pass:
                    server.login(smtp_user, smtp_pass)
                server.send_message(msg)
            return True
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False


# Global alerter instance
alerter = MultiChannelAlerter()
