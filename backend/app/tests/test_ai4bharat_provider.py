"""AI4Bharat (Hugging Face Inference API) provider tests — Phase 8 alternate.

Mock-transport tests verify request payloads, auth headers, response parsing,
and the Khasi/Mizo UnsupportedLanguageError contract. A live test at the
bottom calls the real translation endpoint with an Assamese phrase — it is
skipped unless RUN_LIVE_AI4BHARAT=1 and HUGGINGFACE_API_TOKEN are both set
(same opt-in pattern as the other live tests in this repo).
"""

import base64
import json
import os

import httpx
import pytest

from app.config import settings
from app.services.language_service import (
    AI4BHARAT_LANG_CODES,
    Ai4BharatLanguageService,
    BhashiniLanguageService,
    LanguageServiceError,
    MockLanguageService,
    UnsupportedLanguageError,
    get_language_service,
)

LIVE = pytest.mark.skipif(
    not (os.environ.get("RUN_LIVE_AI4BHARAT") == "1" and settings.HUGGINGFACE_API_TOKEN),
    reason="needs RUN_LIVE_AI4BHARAT=1 and HUGGINGFACE_API_TOKEN",
)


def _client(handler, token: str = "hf-test-token") -> Ai4BharatLanguageService:
    return Ai4BharatLanguageService(
        api_token=token,
        inference_base="https://router.huggingface.co/hf-inference",
        transport=httpx.MockTransport(handler),
    )


# ---------- construction ----------


def test_requires_token():
    with pytest.raises(LanguageServiceError, match="HUGGINGFACE_API_TOKEN"):
        Ai4BharatLanguageService(api_token="")


def test_supported_languages_exclude_khasi_mizo():
    langs = Ai4BharatLanguageService(api_token="t").supported_languages()
    assert set(langs) == set(AI4BHARAT_LANG_CODES)
    assert "khasi" not in langs
    assert "mizo" not in langs
    assert "assamese" in langs


# ---------- translation ----------


@pytest.mark.asyncio
async def test_translate_payload_and_parse():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["headers"] = dict(request.headers)
        captured["json"] = json.loads(request.content.decode())
        return httpx.Response(200, json=[{"translation_text": "Hello, how are you today?"}])

    client = _client(handler)
    result = await client.translate_text("নমস্কাৰ, আজি কেনে আছে?", "assamese", "english")
    assert result == "Hello, how are you today?"

    assert (
        captured["url"]
        == "https://router.huggingface.co/hf-inference/models/ai4bharat/indictrans2-indic-indic-1B"
    )
    assert captured["headers"]["authorization"] == "Bearer hf-test-token"
    assert captured["json"] == {
        "inputs": "নমস্কাৰ, আজি কেনে আছে?",
        "parameters": {"src_lang": "asm_Beng", "tgt_lang": "eng_Latn"},
    }


@pytest.mark.asyncio
async def test_translate_same_language_short_circuits():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200, json=[])

    client = _client(handler)
    assert await client.translate_text("namaskar", "assamese", "assamese") == "namaskar"
    assert calls == []  # no HTTP call for same-language translation


@pytest.mark.asyncio
async def test_translate_unsupported_language_raises():
    client = _client(lambda r: httpx.Response(200, json=[]))
    with pytest.raises(UnsupportedLanguageError, match="not yet available") as exc:
        await client.translate_text("hi", "khasi", "english")
    assert exc.value.language == "khasi"
    with pytest.raises(UnsupportedLanguageError, match="not yet available"):
        await client.translate_text("hi", "mizo", "english")


@pytest.mark.asyncio
async def test_translate_upstream_error_has_status():
    client = _client(lambda r: httpx.Response(503, text="model loading"))
    with pytest.raises(LanguageServiceError) as exc_info:
        await client.translate_text("hi", "assamese", "english")
    assert exc_info.value.provider_status == 503


# ---------- ASR ----------


@pytest.mark.asyncio
async def test_asr_payload_and_parse():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["headers"] = dict(request.headers)
        captured["body_b64"] = base64.b64encode(request.content).decode()
        return httpx.Response(200, json={"text": "I took my morning medicine."})

    client = _client(handler)
    audio = base64.b64encode(b"fake-wav-bytes").decode()
    text = await client.speech_to_text(audio, "assamese")
    assert text == "I took my morning medicine."

    assert captured["headers"]["authorization"] == "Bearer hf-test-token"
    assert captured["headers"]["content-type"] == "application/octet-stream"
    assert captured["body_b64"] == base64.b64encode(b"fake-wav-bytes").decode()


@pytest.mark.asyncio
async def test_asr_unsupported_language_raises():
    client = _client(lambda r: httpx.Response(200, json={"text": ""}))
    with pytest.raises(UnsupportedLanguageError):
        await client.speech_to_text("audio", "khasi")


# ---------- TTS ----------


@pytest.mark.asyncio
async def test_tts_binary_audio_response_parse():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["json"] = json.loads(request.content.decode())
        return httpx.Response(
            200,
            content=b"RIFF....",
            headers={"Content-Type": "audio/wav"},
        )

    client = _client(handler)
    audio_b64 = await client.text_to_speech("নমস্কাৰ", "assamese")
    assert audio_b64 == base64.b64encode(b"RIFF....").decode()
    assert captured["json"]["inputs"] == "নমস্কাৰ"
    assert captured["json"]["parameters"]["lang"] == "asm_Beng"
    assert captured["json"]["parameters"]["gender"] == "female"


@pytest.mark.asyncio
async def test_tts_unsupported_language_raises():
    client = _client(lambda r: httpx.Response(200, content=b""))
    with pytest.raises(UnsupportedLanguageError):
        await client.text_to_speech("hello", "mizo")


# ---------- factory chain ----------


@pytest.mark.asyncio
async def test_factory_auto_prefers_ai4bharat_when_token_set(monkeypatch):
    monkeypatch.setattr(settings, "SARVAM_API_KEY", "")
    monkeypatch.setattr(settings, "HUGGINGFACE_API_TOKEN", "hf-real")
    monkeypatch.setattr(settings, "BHASHINI_API_KEY", "real-key")
    monkeypatch.setattr(settings, "BHASHINI_USER_ID", "uid-1")
    service = get_language_service(provider="auto")
    assert isinstance(service, Ai4BharatLanguageService)


@pytest.mark.asyncio
async def test_factory_auto_falls_back_to_bhashini(monkeypatch):
    monkeypatch.setattr(settings, "SARVAM_API_KEY", "")
    monkeypatch.setattr(settings, "HUGGINGFACE_API_TOKEN", "")
    monkeypatch.setattr(settings, "BHASHINI_API_KEY", "real-key")
    monkeypatch.setattr(settings, "BHASHINI_USER_ID", "uid-1")
    service = get_language_service(provider="auto")
    assert isinstance(service, BhashiniLanguageService)


@pytest.mark.asyncio
async def test_factory_auto_falls_back_to_mock(monkeypatch):
    monkeypatch.setattr(settings, "SARVAM_API_KEY", "")
    monkeypatch.setattr(settings, "HUGGINGFACE_API_TOKEN", "")
    monkeypatch.setattr(settings, "BHASHINI_API_KEY", "")
    monkeypatch.setattr(settings, "BHASHINI_USER_ID", "")
    service = get_language_service(provider="auto")
    assert isinstance(service, MockLanguageService)


@pytest.mark.asyncio
async def test_factory_ai4bharat_forced_without_token_raises(monkeypatch):
    # The repo .env may carry a real token — clear it to test the guard.
    monkeypatch.setattr(settings, "HUGGINGFACE_API_TOKEN", "")
    with pytest.raises(LanguageServiceError, match="HUGGINGFACE_API_TOKEN"):
        get_language_service(provider="ai4bharat")


# ---------- live endpoint (opt-in) ----------


@LIVE
@pytest.mark.asyncio
async def test_live_translate_assamese_sane_response():
    """Calls the real Hugging Face endpoint with a sample Assamese phrase and
    confirms a sane response comes back (non-empty, differs from input).

    Skips itself when the AI4Bharat models are not currently served by the
    configured HF base (serverless platform has dropped them before — the
    "Model not supported by provider" 400). To run against a dedicated
    Inference Endpoint, set HUGGINGFACE_INFERENCE_BASE in .env.
    """
    service = Ai4BharatLanguageService()  # token from settings/env
    try:
        result = await service.translate_text(
            "নমস্কাৰ, আজি ভাল আছে নে?", "assamese", "english"
        )
    except LanguageServiceError as exc:
        if exc.provider_status == 400 and "not supported" in exc.message.lower():
            pytest.skip(
                "AI4Bharat models not served by the configured HF base — "
                "set HUGGINGFACE_INFERENCE_BASE to a dedicated Inference Endpoint"
            )
        raise
    assert isinstance(result, str)
    assert result.strip(), "empty translation returned"
    assert result.strip() != "নমস্কাৰ, আজি ভাল আছে নে?", "echoed input, not translated"
    print(f"\nLIVE IndicTrans2 result: {result!r}")
