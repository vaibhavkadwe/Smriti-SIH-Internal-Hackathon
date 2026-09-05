"""Phase 8 tests — Bhashini provider & factory selection."""
import pytest
import httpx

from app.config import settings
from app.services.language_service import (
    BhashiniLanguageService,
    MockLanguageService,
    LanguageServiceError,
    get_language_service,
)


def _handler_for(json_body: dict, status_code: int = 200):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json=json_body)

    return handler


def _transport(handler) -> httpx.MockTransport:
    return httpx.MockTransport(handler)


# ---------- factory selection ----------


@pytest.mark.asyncio
async def test_factory_auto_returns_mock_without_credentials(monkeypatch):
    monkeypatch.setattr(settings, "BHASHINI_API_KEY", "")
    monkeypatch.setattr(settings, "BHASHINI_USER_ID", "")
    service = get_language_service(provider="auto")
    assert isinstance(service, MockLanguageService)


@pytest.mark.asyncio
async def test_factory_mock_forced(monkeypatch):
    monkeypatch.setattr(settings, "BHASHINI_API_KEY", "real-key")
    service = get_language_service(provider="mock")
    assert isinstance(service, MockLanguageService)


@pytest.mark.asyncio
async def test_factory_bhashini_without_credentials_raises():
    with pytest.raises(LanguageServiceError):
        get_language_service(provider="bhashini")


@pytest.mark.asyncio
async def test_factory_auto_uses_bhashini_when_configured(monkeypatch):
    monkeypatch.setattr(settings, "BHASHINI_API_KEY", "real-key")
    monkeypatch.setattr(settings, "BHASHINI_USER_ID", "uid-1")
    service = get_language_service(provider="auto")
    assert isinstance(service, BhashiniLanguageService)


# ---------- real client behavior ----------


def _client(handler) -> BhashiniLanguageService:
    return BhashiniLanguageService(
        api_key="test-key",
        user_id="test-user",
        endpoint="https://dhruva-api.bhashini.gov.in/services/inference/pipeline",
        transport=_transport(handler),
    )


@pytest.mark.asyncio
async def test_asr_payload_and_parse():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["json"] = request.content.decode()
        captured["headers"] = dict(request.headers)
        return httpx.Response(
            200,
            json={"pipelineResponse": [{"output": [{"source": "Acknowledged medication."}]}]},
        )

    client = _client(handler)
    text = await client.speech_to_text("base64audio==", "assamese")
    assert text == "Acknowledged medication."

    import json

    payload = json.loads(captured["json"])
    assert payload["pipelineTasks"][0]["taskType"] == "asr"
    assert payload["pipelineTasks"][0]["config"]["language"]["sourceLanguage"] == "as"
    assert payload["inputData"]["audio"][0]["audioContent"] == "base64audio=="
    assert captured["headers"]["authorization"] == "test-key"
    assert captured["headers"]["userid"] == "test-user"


@pytest.mark.asyncio
async def test_tts_payload_and_parse():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["json"] = request.content.decode()
        return httpx.Response(
            200, json={"pipelineResponse": [{"audio": [{"audioContent": "audio-b64"}]}]}
        )

    client = _client(handler)
    audio = await client.text_to_speech("নমস্কাৰ", "assamese")
    assert audio == "audio-b64"

    import json

    payload = json.loads(captured["json"])
    assert payload["pipelineTasks"][0]["taskType"] == "tts"
    assert payload["inputData"]["input"][0]["source"] == "নমস্কাৰ"


@pytest.mark.asyncio
async def test_translation_payload_and_parse():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["json"] = request.content.decode()
        return httpx.Response(
            200, json={"pipelineResponse": [{"output": [{"target": "Hello"}]}]}
        )

    client = _client(handler)
    result = await client.translate_text("নমস্কাৰ", "assamese", "english")
    assert result == "Hello"

    import json

    payload = json.loads(captured["json"])
    config = payload["pipelineTasks"][0]["config"]["language"]
    assert config == {"sourceLanguage": "as", "targetLanguage": "en"}


@pytest.mark.asyncio
async def test_same_language_translation_short_circuits():
    captured = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(200, json={})

    client = _client(handler)
    result = await client.translate_text("namaskar", "assamese", "assamese")
    assert result == "namaskar"
    assert captured == []  # no HTTP call made


@pytest.mark.asyncio
async def test_unsupported_language_raises():
    client = _client(handler=lambda r: httpx.Response(200, json={}))
    with pytest.raises(LanguageServiceError, match="Unsupported language"):
        await client.speech_to_text("audio", "klingon")


@pytest.mark.asyncio
async def test_upstream_error_raises_with_status():
    client = _client(handler=lambda r: httpx.Response(500, text="boom"))
    with pytest.raises(LanguageServiceError) as exc_info:
        await client.speech_to_text("audio", "assamese")
    assert exc_info.value.provider_status == 500


@pytest.mark.asyncio
async def test_unexpected_response_shape_raises():
    client = _client(handler=lambda r: httpx.Response(200, json={"unexpected": True}))
    with pytest.raises(LanguageServiceError, match="response shape"):
        await client.speech_to_text("audio", "assamese")


@pytest.mark.asyncio
async def test_mock_provider_deterministic():
    mock = MockLanguageService()
    assert await mock.speech_to_text("x", "assamese") == "I took my morning medicine and had a cup of tea."
    assert mock.name == "mock"
    assert "mizo" in mock.supported_languages()
