"""OpenRouter free-tier LLM adapter — provider detection, free-only guard,
request shape, response parsing, and the free-tier fallback chain."""
import json
import pytest
import httpx

from app.services.llm_client import (
    LLMClient,
    LLMServiceError,
    detect_provider,
    PROVIDER_OPENROUTER,
    PROVIDER_ANTHROPIC,
)


def _transport(handler):
    return httpx.MockTransport(handler)


# ---------- provider detection ----------


def test_detect_provider_from_key_prefix():
    assert detect_provider("sk-or-v1-abc") == PROVIDER_OPENROUTER
    assert detect_provider("sk-ant-abc") == PROVIDER_ANTHROPIC
    assert detect_provider("sk-test") == PROVIDER_ANTHROPIC


def test_openrouter_key_selects_openrouter_provider():
    client = LLMClient(api_key="sk-or-v1-xyz", model="minimax/minimax-m3:free")
    assert client.provider == PROVIDER_OPENROUTER
    assert client.enabled is True


def test_explicit_empty_key_is_disabled():
    client = LLMClient(api_key="")
    assert client.enabled is False


# ---------- free-only guard ----------


def test_free_only_drops_paid_models():
    client = LLMClient(
        api_key="sk-or-v1-xyz",
        model="anthropic/claude-3-opus",  # paid slug
        fallback_models=["minimax/minimax-m3:free", "openai/gpt-4o"],
        free_only=True,
    )
    assert client.model_chain == ["minimax/minimax-m3:free"]


def test_free_only_off_keeps_all_models():
    client = LLMClient(
        api_key="sk-or-v1-xyz",
        model="openai/gpt-4o",
        fallback_models=["minimax/minimax-m3:free"],
        free_only=False,
    )
    assert client.model_chain == ["openai/gpt-4o", "minimax/minimax-m3:free"]


@pytest.mark.asyncio
async def test_complete_raises_when_free_only_filters_everything():
    client = LLMClient(
        api_key="sk-or-v1-xyz", model="openai/gpt-4o", fallback_models=[], free_only=True
    )
    assert client.model_chain == []
    with pytest.raises(LLMServiceError):
        await client.complete("sys", [{"role": "user", "content": "hi"}])


# ---------- OpenRouter request shape + parsing ----------


@pytest.mark.asyncio
async def test_openrouter_request_shape_and_parse():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["headers"] = dict(request.headers)
        captured["json"] = json.loads(request.content.decode())
        return httpx.Response(
            200,
            json={"choices": [{"message": {"role": "assistant", "content": "নমস্কাৰ"}}]},
        )

    client = LLMClient(
        api_key="sk-or-v1-xyz",
        model="minimax/minimax-m3:free",
        transport=_transport(handler),
    )
    out = await client.complete("Be warm.", [{"role": "user", "content": "hi"}])

    assert out == "নমস্কাৰ"
    assert captured["url"].endswith("/chat/completions")
    assert captured["headers"]["authorization"] == "Bearer sk-or-v1-xyz"
    assert captured["json"]["model"] == "minimax/minimax-m3:free"
    # system prompt is sent as the first message (OpenAI format)
    assert captured["json"]["messages"][0] == {"role": "system", "content": "Be warm."}
    assert captured["json"]["messages"][-1]["content"] == "hi"


# ---------- free-tier fallback chain ----------


@pytest.mark.asyncio
async def test_fallback_chain_skips_error_body_then_null_then_succeeds():
    """Model 1: 200 with error body. Model 2: 200 null content. Model 3: OK."""
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        model = json.loads(request.content.decode())["model"]
        calls.append(model)
        if model == "m1:free":
            return httpx.Response(200, json={"error": {"message": "provider down", "code": 502}})
        if model == "m2:free":
            return httpx.Response(200, json={"choices": [{"message": {"content": None}}]})
        return httpx.Response(200, json={"choices": [{"message": {"content": "answered"}}]})

    client = LLMClient(
        api_key="sk-or-v1-xyz",
        model="m1:free",
        fallback_models=["m2:free", "m3:free"],
        transport=_transport(handler),
    )
    out = await client.complete("sys", [{"role": "user", "content": "q"}])
    assert out == "answered"
    assert calls == ["m1:free", "m2:free", "m3:free"]


@pytest.mark.asyncio
async def test_all_models_fail_raises():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, text="rate limited")

    client = LLMClient(
        api_key="sk-or-v1-xyz",
        model="m1:free",
        fallback_models=["m2:free"],
        transport=_transport(handler),
    )
    with pytest.raises(LLMServiceError) as exc:
        await client.complete("sys", [{"role": "user", "content": "q"}])
    assert exc.value.provider_status == 429


# ---------- anthropic path preserved ----------


@pytest.mark.asyncio
async def test_anthropic_path_still_works():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["headers"] = dict(request.headers)
        captured["json"] = json.loads(request.content.decode())
        return httpx.Response(200, json={"content": [{"type": "text", "text": "hello"}]})

    client = LLMClient(api_key="sk-test", model="claude-3-haiku", transport=_transport(handler))
    assert client.provider == PROVIDER_ANTHROPIC
    out = await client.complete("System prompt", [{"role": "user", "content": "hi"}])

    assert out == "hello"
    assert "api.anthropic.com" in captured["url"]
    assert captured["headers"]["x-api-key"] == "sk-test"
    assert captured["json"]["system"] == "System prompt"
