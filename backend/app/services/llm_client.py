"""Minimal LLM client shared by services (OpenRouter free tier or Anthropic).

Used by:
- Voice Companion (Phase 9): elder-facing conversational replies.
- RAG clinical answer synthesis (Phase 10): grounded answers over retrieved
  medical document chunks.

Two wire protocols are supported behind one interface (`complete()`):

- ``openrouter`` — OpenAI-compatible ``/chat/completions``; ``Authorization:
  Bearer``; the system prompt is sent as the first message; text is read from
  ``choices[0].message.content``.
- ``anthropic``  — native Messages API; ``x-api-key`` + ``anthropic-version``;
  the system prompt is a top-level field; text is read from ``content[0].text``.

The provider is auto-detected from the API key prefix (``sk-or-`` =>
OpenRouter) unless ``LLM_PROVIDER`` pins it explicitly.

**Free-tier safety.** With ``OPENROUTER_FREE_ONLY=true`` (default) any model
slug that is not suffixed ``:free`` is dropped before a request is ever made,
so a misconfigured model id can never spend money.

**Free-tier reality.** Free OpenRouter models are unreliable in two distinct
ways: the upstream provider may return an error, or it may return HTTP 200 with
``content: null`` (reasoning-only models). Both are treated as a miss and the
next model in ``model_chain`` is tried. Only if every candidate misses does
``complete()`` raise, letting callers degrade (companion -> canned reply,
RAG -> extractive summary).

The client is "enabled" only when an API key is configured.
"""

import logging
from typing import List, Dict, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

PLACEHOLDER_KEYS = {
    "",
    "mock_anthropic_key",
    "placeholder-key",
    "your_openrouter_api_key_here",
    "sk-or-v1-xxxxxxxx",
}

PROVIDER_OPENROUTER = "openrouter"
PROVIDER_ANTHROPIC = "anthropic"

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"


class LLMServiceError(Exception):
    """Raised when the LLM request fails (all candidate models exhausted)."""

    def __init__(self, message: str, provider_status: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.provider_status = provider_status


def detect_provider(api_key: str) -> str:
    """Infer the wire protocol from the key prefix. OpenRouter keys are `sk-or-`."""
    return PROVIDER_OPENROUTER if api_key.startswith("sk-or-") else PROVIDER_ANTHROPIC


class LLMClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        api_version: Optional[str] = None,
        max_tokens: Optional[int] = None,
        transport: Optional[httpx.AsyncBaseTransport] = None,
        provider: Optional[str] = None,
        fallback_models: Optional[List[str]] = None,
        free_only: Optional[bool] = None,
        base_url: Optional[str] = None,
    ):
        explicit_key = api_key is not None
        raw_key = api_key
        if raw_key is None:
            # OpenRouter first: it is the project's default provider.
            raw_key = settings.OPENROUTER_API_KEY or settings.ANTHROPIC_API_KEY
            if not raw_key:
                raw_key = __import__("os").getenv("CLAUDE_API_KEY", "")
        self.api_key = (raw_key or "").strip()

        configured = provider or settings.LLM_PROVIDER
        if configured and configured != "auto":
            self.provider = configured
        else:
            self.provider = detect_provider(self.api_key)

        self.free_only = (
            settings.OPENROUTER_FREE_ONLY if free_only is None else free_only
        )
        self.max_tokens = max_tokens or settings.LLM_MAX_TOKENS
        self.api_version = api_version or settings.ANTHROPIC_VERSION
        self.base_url = (base_url or settings.OPENROUTER_BASE_URL).rstrip("/")
        self._transport = transport
        self.enabled = bool(self.api_key) and self.api_key not in PLACEHOLDER_KEYS

        if self.provider == PROVIDER_OPENROUTER:
            primary = model or settings.OPENROUTER_MODEL
            extras = (
                fallback_models
                if fallback_models is not None
                else [
                    m.strip()
                    for m in settings.OPENROUTER_FALLBACK_MODELS.split(",")
                    if m.strip()
                ]
            )
        else:
            primary = model or settings.CLAUDE_MODEL
            extras = fallback_models or []

        chain: List[str] = []
        for candidate in [primary, *extras]:
            if candidate and candidate not in chain:
                chain.append(candidate)
        self.model_chain = self._enforce_free_only(chain)
        # `model` keeps the historical single-model attribute (first candidate).
        self.model = self.model_chain[0] if self.model_chain else primary

        if explicit_key and not self.api_key:
            # Caller deliberately constructed a disabled client (tests, no-key path).
            self.enabled = False

    def _enforce_free_only(self, chain: List[str]) -> List[str]:
        """Drop paid slugs when free-only mode is on (OpenRouter only)."""
        if not (self.free_only and self.provider == PROVIDER_OPENROUTER):
            return chain
        free = [m for m in chain if m.endswith(":free")]
        dropped = [m for m in chain if not m.endswith(":free")]
        if dropped:
            logger.warning(
                "OPENROUTER_FREE_ONLY is on; ignoring non-free model(s): %s",
                ", ".join(dropped),
            )
        if not free:
            logger.error(
                "No ':free' OpenRouter model configured; LLM calls will fail until "
                "OPENROUTER_MODEL is set to a free slug."
            )
        return free

    # ---------- wire-format adapters ----------

    def _build_request(
        self, model: str, system: str, messages: List[Dict[str, str]], max_tokens: int
    ):
        """Return (url, headers, payload) for the active provider."""
        if self.provider == PROVIDER_OPENROUTER:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                # OpenRouter attribution headers (optional but recommended).
                "HTTP-Referer": settings.OPENROUTER_APP_URL,
                "X-Title": settings.OPENROUTER_APP_TITLE,
            }
            payload = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": [{"role": "system", "content": system}, *messages],
            }
            return f"{self.base_url}/chat/completions", headers, payload

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": self.api_version,
            "content-type": "application/json",
        }
        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": messages,
        }
        return ANTHROPIC_URL, headers, payload

    def _parse_text(self, data: dict) -> str:
        """Extract reply text, or '' when the model returned no usable content."""
        if self.provider == PROVIDER_OPENROUTER:
            choices = data.get("choices") or []
            if not choices:
                return ""
            message = choices[0].get("message") or {}
            return (message.get("content") or "").strip()
        blocks = data.get("content") or []
        if not blocks:
            return ""
        return (blocks[0].get("text") or "").strip()

    # ---------- public API ----------

    async def complete(
        self,
        system: str,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
    ) -> str:
        """Single-turn completion. Tries each model in `model_chain` in order."""
        if not self.enabled:
            raise LLMServiceError(
                "LLM API key not configured. Set OPENROUTER_API_KEY "
                "(or ANTHROPIC_API_KEY for the Claude path)."
            )
        if not self.model_chain:
            raise LLMServiceError(
                "No usable LLM model configured (free-only mode filtered every "
                "candidate). Set OPENROUTER_MODEL to a ':free' slug."
            )

        limit = max_tokens or self.max_tokens
        last_error = "no attempt made"
        last_status: Optional[int] = None

        for model in self.model_chain:
            url, headers, payload = self._build_request(model, system, messages, limit)
            try:
                async with httpx.AsyncClient(
                    timeout=settings.LLM_TIMEOUT_SECONDS, transport=self._transport
                ) as client:
                    resp = await client.post(url, json=payload, headers=headers)
            except httpx.HTTPError as exc:
                last_error, last_status = f"transport error: {exc}", None
                logger.warning("LLM model %s transport error: %s", model, exc)
                continue

            if resp.status_code != 200:
                last_error = f"HTTP {resp.status_code}: {resp.text[:200]}"
                last_status = resp.status_code
                logger.warning("LLM model %s failed — %s", model, last_error)
                continue

            try:
                data = resp.json()
            except ValueError as exc:
                last_error, last_status = f"invalid JSON: {exc}", resp.status_code
                continue

            # OpenRouter reports upstream failures inside a 200 body.
            if isinstance(data, dict) and data.get("error"):
                err = data["error"]
                last_error = str(err.get("message", err))[:200]
                last_status = err.get("code") if isinstance(err, dict) else None
                logger.warning("LLM model %s upstream error — %s", model, last_error)
                continue

            text = self._parse_text(data)
            if not text:
                last_error, last_status = "empty/null content", resp.status_code
                logger.warning(
                    "LLM model %s returned no content; trying next candidate", model
                )
                continue

            if model != self.model_chain[0]:
                logger.info("LLM served by fallback model %s", model)
            return text

        raise LLMServiceError(
            f"All LLM candidates failed ({len(self.model_chain)} tried). "
            f"Last error — {last_error}",
            provider_status=last_status,
        )
