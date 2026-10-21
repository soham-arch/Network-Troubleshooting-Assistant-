"""LLM Client Abstraction.

Supports local models via Ollama and LM Studio (OpenAI-compatible),
as well as cloud providers (OpenAI, Gemini), with deterministic safe fallback.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional
import requests

from utils.config import config

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for generating completions across local and cloud LLM providers."""

    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: int = 15
    ):
        self.provider = (provider or config.ai_provider or "none").lower()
        self.api_key = api_key if api_key is not None else config.ai_api_key
        self.base_url = base_url or getattr(config, "ai_base_url", "")
        self.model = model or getattr(config, "ai_model", "")
        self.timeout_seconds = timeout_seconds

        # Set default model & base_url per provider if not specified
        if self.provider == "ollama":
            self.base_url = self.base_url or "http://localhost:11434"
            self.model = self.model or "llama3"
        elif self.provider == "lm_studio":
            self.base_url = self.base_url or "http://localhost:1234/v1"
            self.model = self.model or "local-model"
        elif self.provider == "openai":
            self.base_url = self.base_url or "https://api.openai.com/v1"
            self.model = self.model or "gpt-4o-mini"
        elif self.provider == "gemini":
            self.base_url = self.base_url or "https://generativelanguage.googleapis.com/v1beta"
            self.model = self.model or "gemini-1.5-flash"

    def is_configured(self) -> bool:
        """Check if provider is configured and not 'none'."""
        if self.provider == "none":
            return False
        if self.provider in ("openai", "gemini") and not self.api_key:
            return False
        return True

    def generate_completion(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """Generate response text from LLM. Returns None if provider is none or errors occur."""
        if not self.is_configured():
            return None

        try:
            if self.provider == "ollama":
                return self._call_ollama(system_prompt, user_prompt)
            elif self.provider in ("lm_studio", "openai"):
                return self._call_openai_compatible(system_prompt, user_prompt)
            elif self.provider == "gemini":
                return self._call_gemini(system_prompt, user_prompt)
            else:
                logger.warning(f"Unsupported LLM provider: {self.provider}")
                return None
        except Exception as e:
            logger.error(f"LLM generation failed for provider '{self.provider}': {e}")
            return None

    def _call_ollama(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """Calls local Ollama generate or chat API."""
        endpoint = f"{self.base_url.rstrip('/')}/api/chat"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "options": {"temperature": 0.2}
        }
        res = requests.post(endpoint, json=payload, timeout=self.timeout_seconds)
        if res.status_code == 200:
            data = res.json()
            return data.get("message", {}).get("content", "").strip()
        else:
            logger.warning(f"Ollama returned HTTP {res.status_code}: {res.text}")
            return None

    def _call_openai_compatible(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """Calls LM Studio or OpenAI chat completions API."""
        base = self.base_url.rstrip("/")
        endpoint = f"{base}/chat/completions" if not base.endswith("/chat/completions") else base
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2
        }
        res = requests.post(endpoint, json=payload, headers=headers, timeout=self.timeout_seconds)
        if res.status_code == 200:
            data = res.json()
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "").strip()
            return None
        else:
            logger.warning(f"OpenAI-compatible endpoint returned HTTP {res.status_code}: {res.text}")
            return None

    def _call_gemini(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """Calls Google Gemini generateContent REST API."""
        endpoint = f"{self.base_url.rstrip('/')}/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": f"SYSTEM INSTRUCTION:\n{system_prompt}\n\nUSER REQUEST:\n{user_prompt}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2
            }
        }
        res = requests.post(endpoint, json=payload, timeout=self.timeout_seconds)
        if res.status_code == 200:
            data = res.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "").strip()
            return None
        else:
            logger.warning(f"Gemini API returned HTTP {res.status_code}: {res.text}")
            return None
