"""Application Settings & Diagnostics Configuration."""

from __future__ import annotations

import os
import streamlit as st
from utils.config import config


def render_settings():
    st.header("Application Settings & Integration Policy")
    st.caption("Configure diagnostic thresholds, execution timeouts, target safety policies, LLM providers, alerts, and ticketing.")

    with st.form("settings_form"):
        st.subheader("1. Diagnostic Timeouts & Thresholds")
        c1, c2 = st.columns(2)
        with c1:
            ping_count = st.number_input("Ping Probe Count", min_value=1, max_value=10, value=config.ping_count)
            dns_timeout = st.number_input("DNS Lookup Timeout (seconds)", min_value=1, max_value=15, value=config.dns_timeout_seconds)
        with c2:
            tcp_timeout = st.number_input("TCP Handshake Timeout (seconds)", min_value=1, max_value=15, value=config.tcp_timeout_seconds)
            http_timeout = st.number_input("HTTP Request Timeout (seconds)", min_value=1, max_value=30, value=config.http_timeout_seconds)

        st.subheader("2. Security & Access Policy")
        allow_private = st.checkbox("Allow RFC 1918 Private IPs in Diagnostic Targets", value=config.allow_private_ips_in_local_tests)
        st.caption("Prohibits AWS/GCP/Azure link-local cloud metadata (169.254.169.254) regardless of this setting.")

        st.subheader("3. AI Explanation & Symptom Parsing Layer")
        st.caption("Autonomous root-cause engine operates deterministically. LLM is an additive explanation layer.")
        provider_options = ["none", "ollama", "lm_studio", "openai", "gemini"]
        current_p_idx = provider_options.index(config.ai_provider) if config.ai_provider in provider_options else 0
        ai_provider = st.selectbox("AI Provider", provider_options, index=current_p_idx)

        c_llm1, c_llm2 = st.columns(2)
        with c_llm1:
            ai_base_url = st.text_input("Base URL (e.g. http://localhost:11434 for Ollama, http://localhost:1234/v1 for LM Studio)", value=config.ai_base_url)
            ai_model = st.text_input("Model Identifier (e.g. llama3, mistral, gpt-4o-mini)", value=config.ai_model)
        with c_llm2:
            ai_key = st.text_input("AI Provider API Key", value=config.ai_api_key, type="password", help="Stored only in memory or environment.")

        st.subheader("4. Default Alert Channels")
        c_alt1, c_alt2 = st.columns(2)
        with c_alt1:
            alert_slack = st.text_input("Default Slack Webhook URL", value=config.alert_slack_webhook)
            alert_email = st.text_input("Default Alert Email", value=config.alert_email)
        with c_alt2:
            alert_generic = st.text_input("Default Generic HTTP Webhook URL", value=config.alert_generic_webhook)

        st.subheader("5. Incident Ticketing Connectors (Jira / Webhook)")
        c_j1, c_j2 = st.columns(2)
        with c_j1:
            jira_url = st.text_input("Jira Base URL (e.g. https://your-domain.atlassian.net)", value=config.jira_base_url)
            jira_email = st.text_input("Jira User Email", value=config.jira_email)
            jira_key = st.text_input("Jira Project Key", value=config.jira_project_key)
        with c_j2:
            jira_token = st.text_input("Jira API Token", value=config.jira_api_token, type="password")
            ticket_webhook = st.text_input("ITSM Ticket Webhook URL", value=config.ticketing_webhook_url)

        saved = st.form_submit_button("Save All Settings", type="primary", use_container_width=True)

    if saved:
        config.ping_count = int(ping_count)
        config.dns_timeout_seconds = int(dns_timeout)
        config.tcp_timeout_seconds = int(tcp_timeout)
        config.http_timeout_seconds = int(http_timeout)
        config.allow_private_ips_in_local_tests = allow_private

        config.ai_provider = ai_provider
        config.ai_base_url = ai_base_url.strip()
        config.ai_model = ai_model.strip()
        config.ai_api_key = ai_key.strip()

        config.alert_slack_webhook = alert_slack.strip()
        config.alert_email = alert_email.strip()
        config.alert_generic_webhook = alert_generic.strip()

        config.jira_base_url = jira_url.strip()
        config.jira_email = jira_email.strip()
        config.jira_project_key = jira_key.strip()
        config.jira_api_token = jira_token.strip()
        config.ticketing_webhook_url = ticket_webhook.strip()

        st.success("Configuration updated successfully.")
