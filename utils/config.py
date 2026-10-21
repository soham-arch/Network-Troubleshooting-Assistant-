"""Application configuration management with environment variable overrides."""

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables from .env file if present
load_dotenv()


class AppConfig(BaseModel):
    env: str = Field(default="development")
    log_level: str = Field(default="INFO")
    db_path: str = Field(default="data/nta.db")
    max_diagnostic_timeout_seconds: int = Field(default=15)
    ping_count: int = Field(default=3)
    ping_timeout_seconds: int = Field(default=2)
    dns_timeout_seconds: int = Field(default=3)
    tcp_timeout_seconds: int = Field(default=3)
    http_timeout_seconds: int = Field(default=5)
    allow_private_ips_in_local_tests: bool = Field(default=True)

    # LLM Settings (Ollama, LM Studio, OpenAI, Gemini)
    ai_provider: str = Field(default="none")
    ai_api_key: str = Field(default="")
    ai_base_url: str = Field(default="")
    ai_model: str = Field(default="")

    # Continuous Monitoring & Alerting
    monitoring_interval_default_seconds: int = Field(default=60)
    alert_email: str = Field(default="")
    alert_slack_webhook: str = Field(default="")
    alert_generic_webhook: str = Field(default="")

    # SMTP Configuration
    smtp_host: str = Field(default="")
    smtp_port: int = Field(default=587)
    smtp_user: str = Field(default="")
    smtp_password: str = Field(default="")
    smtp_from: str = Field(default="alerts@network-assistant.local")

    # Ticketing (Jira / Webhook)
    jira_base_url: str = Field(default="")
    jira_email: str = Field(default="")
    jira_api_token: str = Field(default="")
    jira_project_key: str = Field(default="IT")
    ticketing_webhook_url: str = Field(default="")

    @classmethod
    def load(cls) -> "AppConfig":
        return cls(
            env=os.getenv("APP_ENV", "development"),
            log_level=os.getenv("APP_LOG_LEVEL", "INFO"),
            db_path=os.getenv("DB_PATH", "data/nta.db"),
            max_diagnostic_timeout_seconds=int(os.getenv("MAX_DIAGNOSTIC_TIMEOUT_SECONDS", "15")),
            ping_count=int(os.getenv("PING_COUNT", "3")),
            ping_timeout_seconds=int(os.getenv("PING_TIMEOUT_SECONDS", "2")),
            dns_timeout_seconds=int(os.getenv("DNS_TIMEOUT_SECONDS", "3")),
            tcp_timeout_seconds=int(os.getenv("TCP_TIMEOUT_SECONDS", "3")),
            http_timeout_seconds=int(os.getenv("HTTP_TIMEOUT_SECONDS", "5")),
            allow_private_ips_in_local_tests=os.getenv("ALLOW_PRIVATE_IPS_IN_LOCAL_TESTS", "true").lower() == "true",
            ai_provider=os.getenv("AI_PROVIDER", "none"),
            ai_api_key=os.getenv("AI_API_KEY", ""),
            ai_base_url=os.getenv("AI_BASE_URL", ""),
            ai_model=os.getenv("AI_MODEL", ""),
            monitoring_interval_default_seconds=int(os.getenv("MONITORING_INTERVAL_DEFAULT_SECONDS", "60")),
            alert_email=os.getenv("ALERT_EMAIL", ""),
            alert_slack_webhook=os.getenv("ALERT_SLACK_WEBHOOK", ""),
            alert_generic_webhook=os.getenv("ALERT_GENERIC_WEBHOOK", ""),
            smtp_host=os.getenv("SMTP_HOST", ""),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            smtp_user=os.getenv("SMTP_USER", ""),
            smtp_password=os.getenv("SMTP_PASSWORD", ""),
            smtp_from=os.getenv("SMTP_FROM", "alerts@network-assistant.local"),
            jira_base_url=os.getenv("JIRA_BASE_URL", ""),
            jira_email=os.getenv("JIRA_EMAIL", ""),
            jira_api_token=os.getenv("JIRA_API_TOKEN", ""),
            jira_project_key=os.getenv("JIRA_PROJECT_KEY", "IT"),
            ticketing_webhook_url=os.getenv("TICKETING_WEBHOOK_URL", "")
        )


# Global default configuration instance
config = AppConfig.load()
