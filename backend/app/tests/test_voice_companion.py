"""Phase 9 tests — Claude voice companion & prompt version management."""
import pytest
import httpx

from app.config import settings
from app.models.all_models import VoiceCompanionConfig
from app.services.llm_client import LLMClient
from app.services.voice_companion_service import (
    VoiceCompanionService,
    CompanionServiceError,
    load_persona_prompt,
)

# The persona now lives in app/voice_persona.txt (DB-configurable; file is seed).
DEFAULT_ELDER_CARE_SYSTEM_PROMPT = load_persona_prompt()
from app.services.language_service import MockLanguageService


def _transport(handler) -> httpx.MockTransport:
    return httpx.MockTransport(handler)


# ---------- no-key fallback ----------


@pytest.mark.asyncio
async def test_chat_falls_back_without_api_key(monkeypatch):
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "")
    service = VoiceCompanionService(
        lang_service=MockLanguageService(), llm=LLMClient(api_key="")
    )
    result = await service.chat("Good morning", patient_name="Biren", patient_language="assamese")
    assert "reply_text" in result
    assert result["fallback"] is True
    assert result["reason"] == "no_api_key"
    assert "Biren" in result["reply_text"]


@pytest.mark.asyncio
async def test_chat_raises_when_fallback_disabled(monkeypatch):
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "")
    service = VoiceCompanionService(
        lang_service=MockLanguageService(),
        llm=LLMClient(api_key=""),
        auto_fallback=False,
    )
    with pytest.raises(CompanionServiceError):
        await service.chat("Hello", patient_name="Biren")


# ---------- real Claude path ----------


@pytest.mark.asyncio
async def test_chat_real_request_shape_and_parse(monkeypatch):
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        import json

        captured["json"] = json.loads(request.content.decode())
        captured["headers"] = dict(request.headers)
        return httpx.Response(
            200, json={"content": [{"type": "text", "text": "How are you today?"}]}
        )
    llm = LLMClient(api_key="sk-test", transport=_transport(handler))
    service = VoiceCompanionService(lang_service=MockLanguageService(), llm=llm)

    result = await service.chat(
        "I forgot where my glasses are.",
        patient_name="Biren",
        patient_language="assamese",
    )
    assert result["reply_text"] == "How are you today?"
    assert result["fallback"] is False

    assert captured["headers"]["x-api-key"] == "sk-test"
    assert captured["headers"]["anthropic-version"] == settings.ANTHROPIC_VERSION
    assert captured["json"]["model"] == settings.CLAUDE_MODEL
    assert captured["json"]["system"] == DEFAULT_ELDER_CARE_SYSTEM_PROMPT
    assert "Biren" in captured["json"]["messages"][-1]["content"]


@pytest.mark.asyncio
async def test_chat_upstream_error_graceful_and_strict(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, text="rate limited")

    # graceful (default)
    service = VoiceCompanionService(
        lang_service=MockLanguageService(),
        llm=LLMClient(api_key="sk-test", transport=_transport(handler)),
        auto_fallback=True,
    )
    result = await service.chat("Hello", patient_name="Biren")
    assert result["fallback"] is True
    assert result["reason"] == "upstream_error"

    # strict
    strict = VoiceCompanionService(
        lang_service=MockLanguageService(),
        llm=LLMClient(api_key="sk-test", transport=_transport(handler)),
        auto_fallback=False,
    )
    with pytest.raises(CompanionServiceError):
        await strict.chat("Hello", patient_name="Biren")


@pytest.mark.asyncio
async def test_voice_pipeline_with_mock_stages(monkeypatch):
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "")
    service = VoiceCompanionService(
        lang_service=MockLanguageService(), llm=LLMClient(api_key="")
    )
    result = await service.voice_chat_pipeline(
        audio_base64="audio", patient_name="Rupali", language="assamese"
    )
    assert result["recognized_query"]
    assert result["reply_text"]
    assert result["reply_audio_base64"]
    assert isinstance(result["warnings"], list)


# ---------- versioned prompt config ----------


@pytest.mark.asyncio
async def test_active_config_seeded_default(db_session):
    config = await VoiceCompanionService.get_active_config(db_session)
    assert config is not None
    assert config.version == "1.0.0"
    assert config.system_prompt == DEFAULT_ELDER_CARE_SYSTEM_PROMPT
    assert config.is_active is True

    # second call reuses the seeded row
    again = await VoiceCompanionService.get_active_config(db_session)
    assert again.id == config.id


@pytest.mark.asyncio
async def test_get_system_prompt_uses_db_row(db_session):
    # Seed the default persona first so 1.0.0 exists as a version.
    await VoiceCompanionService.get_active_config(db_session)
    await VoiceCompanionService.create_config(
        db_session,
        version="2.0.0",
        system_prompt="Custom prompt v2",
        persona_name="Aai",
        activate=True,
    )
    service = VoiceCompanionService(lang_service=MockLanguageService(), llm=LLMClient(api_key=""))
    prompt = await service.get_system_prompt(db=db_session)
    assert prompt == "Custom prompt v2"

    # activating an older version switches the prompt
    await VoiceCompanionService.activate_config(db_session, "1.0.0")
    prompt = await service.get_system_prompt(db=db_session)
    assert prompt == DEFAULT_ELDER_CARE_SYSTEM_PROMPT


@pytest.mark.asyncio
async def test_create_config_duplicate_rejected(db_session):
    await VoiceCompanionService.create_config(
        db_session, version="2.0.0", system_prompt="v2 prompt", activate=True
    )
    with pytest.raises(ValueError):
        await VoiceCompanionService.create_config(
            db_session, version="2.0.0", system_prompt="dup", activate=True
        )


@pytest.mark.asyncio
async def test_activate_unknown_version_returns_none(db_session):
    assert await VoiceCompanionService.activate_config(db_session, "nope") is None


@pytest.mark.asyncio
async def test_list_configs_returns_all(db_session):
    await VoiceCompanionService.get_active_config(db_session)  # seed default
    await VoiceCompanionService.create_config(
        db_session, version="2.0.0", system_prompt="v2 prompt", activate=True
    )
    configs = await VoiceCompanionService.list_configs(db_session)
    versions = {c.version for c in configs}
    assert versions == {"1.0.0", "2.0.0"}
    assert all(isinstance(c, VoiceCompanionConfig) for c in configs)
