"""Voice Companion Service (Phase 9) — Claude API + Bhashini Speech Provider.

Features:
- Calm, elder-friendly, empathetic conversational assistant grounded in
  Northeast Indian daily routines, festivals, and family respect.
- Versioned, DB-backed system prompt (`voice_companion_configs` table),
  seeded with a sensible default on first use — editable without code changes.
- Deferral of medical diagnoses/prescriptions to caregivers/clinicians.
- End-to-end voice pipeline: Bhashini ASR -> Claude reasoning -> Bhashini TTS.
- Graceful degradation: without an API key, or when the upstream call fails,
  the companion replies with a warm canned message and flags `fallback: true`
  so the elder experience never breaks.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.all_models import VoiceCompanionConfig
from app.services.language_service import (
    LanguageServiceProvider,
    LanguageServiceError,
    get_language_service,
)
from app.services.llm_client import LLMClient, LLMServiceError

logger = logging.getLogger(__name__)

DEFAULT_VERSION = "1.0.0"
DEFAULT_PERSONA = "Saathi"

# Persona lives in a file, not code, so non-devs can tune the voice without a
# code change. DB-config rows override it; this file is the seed + fallback.
_PERSONA_FILE = Path(__file__).resolve().parent.parent / "voice_persona.txt"
_PERSONA_CACHE: Optional[str] = None


def load_persona_prompt() -> str:
    global _PERSONA_CACHE
    if _PERSONA_CACHE is None:
        try:
            _PERSONA_CACHE = _PERSONA_FILE.read_text(encoding="utf-8").strip()
        except OSError:
            logger.warning("voice_persona.txt missing; using built-in persona")
            _PERSONA_CACHE = (
                "You are a warm, patient voice companion for elderly users in "
                "Northeast India. Keep replies short and gentle. Never give "
                "medical advice; refer the patient to their caregiver or doctor."
            )
    return _PERSONA_CACHE


class CompanionServiceError(Exception):
    """Raised when the companion cannot produce a reply (and fallback is disabled)."""


class VoiceCompanionService:
    def __init__(
        self,
        lang_service: Optional[LanguageServiceProvider] = None,
        llm: Optional[LLMClient] = None,
        auto_fallback: Optional[bool] = None,
    ):
        self.lang_service = lang_service or get_language_service()
        self.llm = llm or LLMClient()
        self.auto_fallback = (
            settings.LLM_AUTO_FALLBACK if auto_fallback is None else auto_fallback
        )

    # ---------- versioned prompt management ----------

    async def get_system_prompt(self, db: Optional[AsyncSession] = None) -> str:
        """Return the active system prompt, seeding the default row when empty."""
        if db is not None:
            active = await VoiceCompanionService.get_active_config(db)
            if active is not None:
                return active.system_prompt
        return load_persona_prompt()

    @staticmethod
    async def get_active_config(
        db: AsyncSession,
    ) -> Optional[VoiceCompanionConfig]:
        """Fetch the active voice companion config, seeding defaults if none exist."""
        stmt = (
            select(VoiceCompanionConfig)
            .where(VoiceCompanionConfig.is_active == True)
            .order_by(VoiceCompanionConfig.created_at.desc())
        )
        res = await db.execute(stmt)
        active = res.scalars().first()
        if active is not None:
            return active

        # Seed the default persona on first use (idempotent per version).
        stmt = select(VoiceCompanionConfig).where(
            VoiceCompanionConfig.version == DEFAULT_VERSION
        )
        res = await db.execute(stmt)
        existing = res.scalars().first()
        if existing is None:
            existing = VoiceCompanionConfig(
                version=DEFAULT_VERSION,
                system_prompt=load_persona_prompt(),
                persona_name=DEFAULT_PERSONA,
                is_active=True,
            )
            db.add(existing)
            await db.commit()
            await db.refresh(existing)
        else:
            existing.is_active = True
            await db.commit()
        return existing

    @staticmethod
    async def list_configs(db: AsyncSession) -> List[VoiceCompanionConfig]:
        stmt = select(VoiceCompanionConfig).order_by(
            VoiceCompanionConfig.created_at.desc()
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def create_config(
        db: AsyncSession,
        version: str,
        system_prompt: str,
        persona_name: str = DEFAULT_PERSONA,
        activate: bool = True,
    ) -> VoiceCompanionConfig:
        stmt = select(VoiceCompanionConfig).where(
            VoiceCompanionConfig.version == version
        )
        res = await db.execute(stmt)
        if res.scalars().first() is not None:
            raise ValueError(f"Voice companion version '{version}' already exists")

        if activate:
            await db.execute(
                VoiceCompanionConfig.__table__.update().values(is_active=False)
            )
        config = VoiceCompanionConfig(
            version=version,
            system_prompt=system_prompt,
            persona_name=persona_name,
            is_active=activate,
        )
        db.add(config)
        await db.commit()
        await db.refresh(config)
        return config

    @staticmethod
    async def activate_config(db: AsyncSession, version: str) -> Optional[VoiceCompanionConfig]:
        stmt = select(VoiceCompanionConfig).where(
            VoiceCompanionConfig.version == version
        )
        res = await db.execute(stmt)
        config = res.scalars().first()
        if config is None:
            return None
        await db.execute(
            VoiceCompanionConfig.__table__.update().values(is_active=False)
        )
        config.is_active = True
        await db.commit()
        await db.refresh(config)
        return config

    # ---------- conversation ----------

    @staticmethod
    def _canned_reply(patient_name: str) -> str:
        return (
            f"Hello {patient_name}, it is lovely talking with you today. "
            "Have you had your warm cup of Assam tea yet?"
        )

    async def chat(
        self,
        user_message: str,
        patient_name: Optional[str] = "Grandparent",
        patient_language: str = "assamese",
        conversation_history: Optional[list] = None,
        db: Optional[AsyncSession] = None,
    ) -> Dict[str, Any]:
        """Send a message to Claude; returns a dict with reply_text + metadata."""
        system_prompt = await self.get_system_prompt(db)
        messages = list(conversation_history or [])
        messages.append(
            {
                "role": "user",
                "content": f"[Patient: {patient_name}, Preferred Language: {patient_language}]\n{user_message}",
            }
        )

        if not self.llm.enabled:
            if self.auto_fallback:
                return {
                    "reply_text": self._canned_reply(patient_name),
                    "patient_language": patient_language,
                    "fallback": True,
                    "reason": "no_api_key",
                }
            raise CompanionServiceError(
                "Claude API key not configured and auto-fallback disabled"
            )

        try:
            reply_text = await self.llm.complete(system_prompt, messages)
        except LLMServiceError as exc:
            if self.auto_fallback:
                logger.warning("Companion fallback after LLM error: %s", exc.message)
                return {
                    "reply_text": self._canned_reply(patient_name),
                    "patient_language": patient_language,
                    "fallback": True,
                    "reason": "upstream_error",
                }
            raise CompanionServiceError(exc.message) from exc

        return {
            "reply_text": reply_text,
            "patient_language": patient_language,
            "fallback": False,
        }

    async def voice_chat_pipeline(
        self,
        audio_base64: str,
        patient_name: str,
        language: str = "assamese",
        conversation_history: Optional[list] = None,
        db: Optional[AsyncSession] = None,
    ) -> Dict[str, Any]:
        """Full Voice Pipeline: Bhashini ASR -> LLM -> Bhashini TTS.

        Each stage degrades gracefully; failures are reported in `warnings`
        rather than breaking the elder-facing conversation.
        """
        warnings: List[str] = []

        # 1. Speech to Text via Bhashini
        try:
            recognized_query = await self.lang_service.speech_to_text(
                audio_base64, language
            )
        except LanguageServiceError as exc:
            recognized_query = ""
            warnings.append(f"ASR failed: {exc.message}")

        # 2. LLM Conversation Engine (with per-patient history when provided)
        if recognized_query:
            companion_result = await self.chat(
                user_message=recognized_query,
                patient_name=patient_name,
                patient_language=language,
                conversation_history=conversation_history,
                db=db,
            )
            reply_text = companion_result["reply_text"]
            if companion_result.get("fallback"):
                warnings.append("Conversation fell back to canned reply")
        else:
            reply_text = self._canned_reply(patient_name)
            warnings.append("No recognized query — used canned reply")

        # 3. Text to Speech via Bhashini
        reply_audio_base64 = ""
        try:
            reply_audio_base64 = await self.lang_service.text_to_speech(
                reply_text, language
            )
        except LanguageServiceError as exc:
            warnings.append(f"TTS failed: {exc.message}")

        return {
            "recognized_query": recognized_query,
            "reply_text": reply_text,
            "reply_audio_base64": reply_audio_base64,
            "language": language,
            "warnings": warnings,
        }
