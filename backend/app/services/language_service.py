"""Bhashini Multi-lingual Speech & Translation Service.

Phase 8 — real Bhashini (ULCA) integration with a pluggable provider interface:

- `LanguageServiceProvider` — abstract ASR / TTS / NMT interface.
- `BhashiniLanguageService` — real Government of India ULCA inference pipeline
  client (headers: `Authorization` = API key, `userID` = user id).
- `MockLanguageService` — deterministic local provider for tests/offline dev.
- `get_language_service()` — factory honouring `LANGUAGE_SERVICE_PROVIDER`:
  `auto`      -> Bhashini when credentials configured, otherwise Mock (logged)
  `bhashini`  -> always Bhashini (raises `LanguageServiceError` if unconfigured)
  `mock`      -> always Mock

NER language codes (ISO 639): Assamese, Bengali, Hindi, English plus
config-only additions: Manipuri (mni), Bodo (brx), Nepali (ne), Mizo (lus),
Khasi (kha). No code changes needed to add more — extend `LANG_CODES`.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# Bhashini pipeline language codes
LANG_CODES: Dict[str, str] = {
    "assamese": "as",
    "bengali": "bn",
    "hindi": "hi",
    "english": "en",
    "manipuri": "mni",
    "bodo": "brx",
    "nepali": "ne",
    "mizo": "lus",
    "khasi": "kha",
}

_PLACEHOLDER_KEYS = {"", "mock_key", "placeholder-key"}


class LanguageServiceError(Exception):
    """Raised when a language provider cannot complete a request."""

    def __init__(self, message: str, provider_status: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.provider_status = provider_status


class LanguageServiceProvider(ABC):
    """Abstract interface for speech and translation services."""

    name: str = "abstract"

    @abstractmethod
    async def speech_to_text(self, audio_base64: str, source_language: str) -> str:
        """Convert patient voice audio to recognized text."""

    @abstractmethod
    async def text_to_speech(self, text: str, target_language: str) -> str:
        """Synthesize text into spoken audio (base64 audio format)."""

    @abstractmethod
    async def translate_text(
        self, text: str, source_language: str, target_language: str
    ) -> str:
        """Translate text between NER languages and English for LLM reasoning."""

    def supported_languages(self) -> List[str]:
        return list(LANG_CODES.keys())


class BhashiniLanguageService(LanguageServiceProvider):
    """Real Government of India Bhashini (ULCA) inference pipeline client."""

    name = "bhashini"

    def __init__(
        self,
        api_key: Optional[str] = None,
        user_id: Optional[str] = None,
        endpoint: Optional[str] = None,
        transport: Optional[httpx.AsyncBaseTransport] = None,
    ):
        self.api_key = api_key if api_key is not None else settings.BHASHINI_API_KEY
        self.user_id = user_id if user_id is not None else settings.BHASHINI_USER_ID
        self.endpoint = endpoint or settings.BHASHINI_ENDPOINT
        self._transport = transport

        if not self.api_key or self.api_key.strip() in _PLACEHOLDER_KEYS:
            raise LanguageServiceError(
                "Bhashini API key not configured. Set BHASHINI_API_KEY."
            )
        if not self.user_id or not self.user_id.strip():
            raise LanguageServiceError(
                "Bhashini user id not configured. Set BHASHINI_USER_ID."
            )
        if not self.endpoint:
            raise LanguageServiceError("Bhashini endpoint not configured.")

    # ---------- internals ----------

    def _lang_code(self, language: str) -> str:
        code = LANG_CODES.get((language or "").lower())
        if not code:
            raise LanguageServiceError(
                f"Unsupported language '{language}'. Supported: {sorted(LANG_CODES)}"
            )
        return code

    async def _post(self, payload: dict) -> dict:
        headers = {
            "Authorization": self.api_key,
            "userID": self.user_id,
            "Content-Type": "application/json",
        }
        try:
            async with httpx.AsyncClient(
                timeout=20.0, transport=self._transport
            ) as client:
                resp = await client.post(self.endpoint, json=payload, headers=headers)
        except httpx.HTTPError as exc:
            raise LanguageServiceError(f"Bhashini request failed: {exc}") from exc

        if resp.status_code != 200:
            raise LanguageServiceError(
                f"Bhashini API error (HTTP {resp.status_code}): {resp.text[:300]}",
                provider_status=resp.status_code,
            )
        try:
            return resp.json()
        except ValueError as exc:
            raise LanguageServiceError("Bhashini returned non-JSON response") from exc

    @staticmethod
    def _dig(data: dict, *path):
        """Walk nested ULCA response (dicts + list indexes); None if missing."""
        cur: object = data
        for key in path:
            if isinstance(cur, dict) and key in cur:
                cur = cur[key]
            elif isinstance(cur, list) and isinstance(key, int) and 0 <= key < len(cur):
                cur = cur[key]
            else:
                return None
        return cur

    # ---------- public API ----------

    async def speech_to_text(self, audio_base64: str, source_language: str) -> str:
        code = self._lang_code(source_language)
        payload = {
            "pipelineTasks": [
                {
                    "taskType": "asr",
                    "config": {
                        "language": {"sourceLanguage": code},
                        "audioFormat": "wav",
                        "samplingRate": 16000,
                    },
                }
            ],
            "inputData": {"audio": [{"audioContent": audio_base64}]},
        }
        data = await self._post(payload)
        text = self._dig(data, "pipelineResponse", 0, "output", 0, "source")
        if text is None:
            raise LanguageServiceError("Unexpected Bhashini ASR response shape")
        return text

    async def text_to_speech(self, text: str, target_language: str) -> str:
        code = self._lang_code(target_language)
        payload = {
            "pipelineTasks": [
                {
                    "taskType": "tts",
                    "config": {"language": {"sourceLanguage": code}, "gender": "female"},
                }
            ],
            "inputData": {"input": [{"source": text}]},
        }
        data = await self._post(payload)
        audio = self._dig(data, "pipelineResponse", 0, "audio", 0, "audioContent")
        if audio is None:
            raise LanguageServiceError("Unexpected Bhashini TTS response shape")
        return audio

    async def translate_text(
        self, text: str, source_language: str, target_language: str
    ) -> str:
        src_code = self._lang_code(source_language)
        tgt_code = self._lang_code(target_language)
        if src_code == tgt_code:
            return text
        payload = {
            "pipelineTasks": [
                {
                    "taskType": "translation",
                    "config": {
                        "language": {"sourceLanguage": src_code, "targetLanguage": tgt_code}
                    },
                }
            ],
            "inputData": {"input": [{"source": text}]},
        }
        data = await self._post(payload)
        translated = self._dig(data, "pipelineResponse", 0, "output", 0, "target")
        if translated is None:
            raise LanguageServiceError("Unexpected Bhashini translation response shape")
        return translated


class MockLanguageService(LanguageServiceProvider):
    """Deterministic local language provider for testing and offline development."""

    name = "mock"

    async def speech_to_text(self, audio_base64: str, source_language: str) -> str:
        return "I took my morning medicine and had a cup of tea."

    async def text_to_speech(self, text: str, target_language: str) -> str:
        return "UklGRjIAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="

    async def translate_text(
        self, text: str, source_language: str, target_language: str
    ) -> str:
        return f"Translated to {target_language}: {text}"


def get_language_service(
    provider: Optional[str] = None,
    transport: Optional[httpx.AsyncBaseTransport] = None,
) -> LanguageServiceProvider:
    """Dependency injector for speech and language service.

    `provider` overrides `settings.LANGUAGE_SERVICE_PROVIDER` (auto | bhashini | mock).
    """
    choice = (provider or settings.LANGUAGE_SERVICE_PROVIDER or "auto").lower()

    if choice == "mock":
        return MockLanguageService()
    if choice == "bhashini":
        return BhashiniLanguageService(transport=transport)

    # auto: use the real provider only when credentials are configured
    configured = bool(settings.BHASHINI_API_KEY) and settings.BHASHINI_API_KEY.strip() not in _PLACEHOLDER_KEYS
    if configured and settings.BHASHINI_USER_ID:
        return BhashiniLanguageService(transport=transport)
    logger.warning(
        "Bhashini credentials not configured — using MockLanguageService. "
        "Set BHASHINI_API_KEY + BHASHINI_USER_ID to enable real ASR/TTS."
    )
    return MockLanguageService()
