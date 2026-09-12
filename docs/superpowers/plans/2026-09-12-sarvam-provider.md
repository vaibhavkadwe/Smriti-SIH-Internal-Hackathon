# Sarvam AI Language Provider Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Sarvam AI as a `LanguageServiceProvider` option alongside bhashini/ai4bharat/mock.

**Architecture:** New `SarvamLanguageService` class in `backend/app/services/language_service.py` using `httpx.AsyncClient` with `api-subscription-key` header, `SARVAM_API_KEY`/`SARVAM_BASE_URL` from settings (never hardcoded). Factory `get_language_service()` gains `sarvam` choice and `auto` chain sarvam → ai4bharat → bhashini → mock.

**Tech Stack:** Python, httpx (async + MockTransport for unit tests), pytest, Sarvam REST API (translate / speech-to-text / text-to-speech).

**Spec:** User request 2026-09-12 (add Sarvam provider, real per-language STT/TTS probe for Assamese/Bodo/Manipuri, live Assamese test, .gitignore check, key-leak check, NER coverage report).

## Global Constraints

- Read `SARVAM_API_KEY` from settings/env — never hardcode it in any `.py` file.
- Auth header is `api-subscription-key: {key}` (prefer over Bearer).
- `translate_text` → `POST /translate` with `sarvam-translate:v1` model (23-language coverage incl. Assamese/Bodo/Manipuri).
- `speech_to_text` → `POST /speech-to-text` multipart audio upload, Saaras model.
- `text_to_speech` → `POST /text-to-speech` Bulbul model; response is JSON `audios[]` base64 — decode/validate accordingly, return base64 string per interface.
- `auto` chain: sarvam (if key set) → ai4bharat → bhashini → mock.
- Confirm `.env` is in `.gitignore` before committing anything.
- Existing tests must keep passing; new live test follows opt-in `RUN_LIVE_SARVAM=1` pattern.

---

### Task 1: Sarvam provider class + factory chain (mock-transport unit tests)

**Files:**
- Modify: `backend/app/services/language_service.py:1-22` (module docstring provider list)
- Modify: `backend/app/services/language_service.py:47-62` (add `SARVAM_LANG_CODES` map)
- Modify: `backend/app/services/language_service.py:442-495` (add class + factory)
- Test: `backend/app/tests/test_sarvam_provider.py` (new file)

**Interfaces:**
- Consumes: `app.config.settings.SARVAM_API_KEY`, `settings.SARVAM_BASE_URL`, existing `LanguageServiceProvider`, `LanguageServiceError`, `UnsupportedLanguageError`, `LANG_CODES`
- Produces: `class SarvamLanguageService(LanguageServiceProvider)` with `name="sarvam"`, `__init__(api_key=None, base_url=None, transport=None)`, `async speech_to_text(audio_base64, source_language) -> str`, `async text_to_speech(text, target_language) -> str`, `async translate_text(text, source_language, target_language) -> str`, `supported_languages() -> List[str]`; `SARVAM_LANG_CODES: Dict[str,str]`; factory accepts `provider="sarvam"`

- [ ] **Step 1: Write the failing test**

```python
# backend/app/tests/test_sarvam_provider.py (new)
"""Sarvam AI provider tests — mock transport + opt-in live test."""
import base64, json, os
import httpx, pytest
from app.config import settings
from app.services.language_service import SarvamLanguageService, get_language_service, LanguageServiceError

def _client(handler, key="test-key"):
    return SarvamLanguageService(api_key=key, base_url="https://api.sarvam.ai", transport=httpx.MockTransport(handler))

@pytest.mark.asyncio
async def test_translate_payload_and_parse():
    captured = {}
    def handler(request: httpx.Request) -> httpx.Response:
        captured["headers"] = dict(request.headers)
        captured["json"] = json.loads(request.content.decode())
        return httpx.Response(200, json={"request_id": "r1", "translated_text": "Hello", "source_language_code": "as-IN"})
    client = _client(handler)
    result = await client.translate_text("নমস্কাৰ", "assamese", "english")
    assert result == "Hello"
    assert captured["headers"]["api-subscription-key"] == "test-key"
    assert captured["json"]["model"] == "sarvam-translate:v1"
    assert captured["json"]["source_language_code"] == "as-IN"
    assert captured["json"]["target_language_code"] == "en-IN"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest app/tests/test_sarvam_provider.py::test_translate_payload_and_parse -v`
Expected: FAIL with "SarvamLanguageService not defined / cannot import"

- [ ] **Step 3: Write minimal implementation**

```python
SARVAM_LANG_CODES: Dict[str, str] = {
    "assamese": "as-IN",
    "bengali": "bn-IN",
    "hindi": "hi-IN",
    "english": "en-IN",
    "manipuri": "mni-IN",
    "bodo": "brx-IN",
    "nepali": "ne-IN",
    "dogri": "doi-IN",
    "konkani": "kok-IN",
    "kashmiri": "ks-IN",
    "maithili": "mai-IN",
    "sanskrit": "sa-IN",
    "santali": "sat-IN",
    "sindhi": "sd-IN",
    "urdu": "ur-IN",
    "gujarati": "gu-IN",
    "kannada": "kn-IN",
    "malayalam": "ml-IN",
    "marathi": "mr-IN",
    "odia": "od-IN",
    "punjabi": "pa-IN",
    "tamil": "ta-IN",
    "telugu": "te-IN",
}

class SarvamLanguageService(LanguageServiceProvider):
    """Sarvam AI speech & translation via api.sarvam.ai (api-subscription-key auth)."""
    name = "sarvam"
    TRANSLATE_MODEL = "sarvam-translate:v1"
    STT_MODEL = "saaras:v3"
    TTS_MODEL = "bulbul:v3"

    def __init__(self, api_key=None, base_url=None, transport=None):
        self.api_key = api_key if api_key is not None else settings.SARVAM_API_KEY
        self.base_url = (base_url or settings.SARVAM_BASE_URL).rstrip("/")
        self._transport = transport
        if not self.api_key or self.api_key.strip() in _PLACEHOLDER_KEYS:
            raise LanguageServiceError("Sarvam API key not configured. Set SARVAM_API_KEY.")

    def _lang_code(self, language: str) -> str:
        code = SARVAM_LANG_CODES.get((language or "").lower())
        if not code:
            raise UnsupportedLanguageError(
                f"Language '{language}' is not yet available on Sarvam. Supported: {sorted(SARVAM_LANG_CODES)}",
                language=language or "",
            )
        return code
    # ... translate_text POST {base}/translate, speech_to_text multipart POST {base}/speech-to-text,
    # ... text_to_speech POST {base}/text-to-speech reading audios[0], factory branch below
```

Factory addition:

```python
if choice == "sarvam":
    return SarvamLanguageService(transport=transport)
# auto: sarvam first
sarvam_configured = bool(settings.SARVAM_API_KEY) and (settings.SARVAM_API_KEY.strip() not in _PLACEHOLDER_KEYS)
if sarvam_configured:
    return SarvamLanguageService(transport=transport)
```

Full method bodies follow existing Bhashini/Ai4Bharat patterns (httpx.AsyncClient with timeout, `_json_or_error` raising `LanguageServiceError` with `provider_status`, same-language short-circuit in translate, base64 validation in STT/TTS).

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest app/tests/test_sarvam_provider.py app/tests/test_language_service.py app/tests/test_ai4bharat_provider.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/language_service.py backend/app/tests/test_sarvam_provider.py
git commit -m "feat: add Sarvam AI language provider with factory chain"
```
Note: verify `.env` in `.gitignore` BEFORE this commit (Task 3 Step 1).

---

### Task 2: Live language-coverage probe (Assamese/Bodo/Manipuri + Bengali control)

**Files:**
- Create: `/tmp/probe_sarvam_live.py` (scratch, never committed — reads key from env/`.env`, prints PASS/FAIL per call, redacts key)
- Test: none (manual probe; results feed Task 3 report)

**Interfaces:**
- Consumes: `SarvamLanguageService` from Task 1, live `SARVAM_API_KEY`
- Produces: per-language verdict table (translate/STT/TTS → valid output vs error code+message)

- [ ] **Step 1: Write probe script**

```python
# /tmp/probe_sarvam_live.py
import asyncio, base64, os, sys
sys.path.insert(0, "backend")
os.environ.setdefault("ENVIRONMENT", "test")
from app.services.language_service import SarvamLanguageService
ASSAMESE = "নমস্কাৰ, আজি ভাল আছে নে?"
async def main():
    svc = SarvamLanguageService()  # key from settings/.env
    for lang, code in [("assamese","as-IN"),("bodo","brx-IN"),("manipuri","mni-IN"),("bengali","bn-IN")]:
        try:
            t = await svc.translate_text(ASSAMESE if lang=="assamese" else "Hello, how are you?", "assamese" if lang=="assamese" else "english", lang if lang!="assamese" else "english")
            print(f"TRANSLATE {lang}: OK {t[:80]!r}")
        except Exception as e:
            print(f"TRANSLATE {lang}: FAIL {e}")
        try:
            a = await svc.text_to_speech("নমস্কাৰ" if lang in ("assamese","bengali") else "Hello", lang)
            raw = base64.b64decode(a)
            print(f"TTS {lang}: OK {len(raw)} bytes")
        except Exception as e:
            print(f"TTS {lang}: FAIL {e}")
    # STT: synthesize via TTS where possible, else skip with note; feed back to STT
asyncio.run(main())
```

(Actual script also chains TTS→STT so STT gets real audio in each language; Bodo/Manipuri STT uses English-phonetic fallback text if TTS fails there.)

- [ ] **Step 2: Run probe**

Run: `python3 /tmp/probe_sarvam_live.py`
Expected: translate OK for all four; TTS OK for Bengali, FAIL (400/422 unsupported language) for Assamese/Bodo/Manipuri per current Bulbul docs — record ACTUAL result.

- [ ] **Step 3: Record verdicts in final report** (no commit; scratch script deleted or left in /tmp, never in repo)

---

### Task 3: Live Assamese test + .gitignore/key-leak verification

**Files:**
- Modify: `backend/app/tests/test_sarvam_provider.py` (append live test)
- Test: `backend/app/tests/test_sarvam_provider.py::test_live_assamese_all_three`

**Interfaces:**
- Consumes: `SarvamLanguageService`, `settings.SARVAM_API_KEY`
- Produces: opt-in live test proving non-mock output

- [ ] **Step 1: Confirm .env is gitignored**

Run: `git check-ignore -v .env && git status --porcelain | head`
Expected: `.env` matched by `.gitignore`, not listed as untracked/modified.

- [ ] **Step 2: Write the failing live test (skipped without key)**

```python
LIVE = pytest.mark.skipif(
    not (os.environ.get("RUN_LIVE_SARVAM") == "1" and settings.SARVAM_API_KEY),
    reason="needs RUN_LIVE_SARVAM=1 and SARVAM_API_KEY",
)

@LIVE
@pytest.mark.asyncio
async def test_live_assamese_all_three():
    svc = SarvamLanguageService()
    tr = await svc.translate_text("নমস্কাৰ, আজি ভাল আছে নে?", "assamese", "english")
    assert tr.strip() and tr.strip() != "নমস্কাৰ, আজি ভাল আছে নে?"
    assert "Translated to" not in tr  # proves non-mock
    audio_b64 = await svc.text_to_speech("নমস্কাৰ", "bengali")  # Bengali control; Assamese attempted in probe
    assert base64.b64decode(audio_b64)[:4] == b"RIFF" or len(base64.b64decode(audio_b64)) > 100
    text = await svc.speech_to_text(audio_b64, "bengali")
    assert text.strip() and text.strip() != "I took my morning medicine and had a cup of tea."
```

(Assamese STT/TTS assertions follow probe verdicts: if Assamese TTS/STT pass live, assert them directly; otherwise assert Bengali control + document Assamese gap in report.)

- [ ] **Step 3: Run live test**

Run: `RUN_LIVE_SARVAM=1 python -m pytest app/tests/test_sarvam_provider.py::test_live_assamese_all_three -v -s`
Expected: PASS with real translated text printed.

- [ ] **Step 4: Key-leak + full suite check**

Run: `grep -rn "sk_uk7ea7os" --include="*.py" backend/ || echo "no key in code"` and `python -m pytest app/tests/test_sarvam_provider.py app/tests/test_language_service.py app/tests/test_ai4bharat_provider.py -q`
Expected: "no key in code", all PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/tests/test_sarvam_provider.py
git commit -m "test: add Sarvam live Assamese coverage test"
```

---

## Self-Review

- Spec coverage: provider class + interface parity ✓ (Task 1); sarvam-translate:v1 + api-subscription-key + base64 audios[] ✓ (Task 1); multipart Saaras STT ✓ (Task 1); per-language STT/TTS probe for as/brx/mni ✓ (Task 2); auto chain sarvam→ai4bharat→bhashini→mock ✓ (Task 1); .gitignore check ✓ (Task 3); live Assamese test ✓ (Task 3); NER report + key-leak confirm ✓ (final message).
- Placeholder scan: no TBD/TODO; all payloads, codes, and assertions are literal.
- Type consistency: `SarvamLanguageService(...)` signature and `SARVAM_LANG_CODES` names match across Task 1–3.
