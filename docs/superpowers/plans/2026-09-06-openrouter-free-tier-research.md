# OpenRouter Free-Tier Research — SIH26003

Source check date: 2026-09-06. Ponytail full active (min change, reuse existing).

## Configured free slugs (primary sources)

- `OPENROUTER_MODEL=minimax/minimax-m3:free` [source: backend/app/config.py:72]
- Fallbacks: `nvidia/nemotron-3-ultra-550b-a55b:free,nvidia/nemotron-3-super-120b-a12b:free` [source: backend/app/config.py:73-75]
- `OPENROUTER_FREE_ONLY=true` drops any non-`:free` slug [source: backend/app/config.py:78, llm_client.py:134-150]
- Client verified 2026-09-05: `minimax-m3:free` returns clean Assamese + honours citation instructions; `nemotron-ultra` works weaker; `*-lightning` excluded (leaks chain-of-thought) [source: backend/app/config.py:67-71]

`.env.example` lines 30-42 mirror the same values [source: .env.example:32-41].

## Endpoint format

- Base URL: `https://openrouter.ai/api/v1` [source: backend/app/config.py:66]
- Endpoint: `POST {base_url}/chat/completions` [source: backend/app/services/llm_client.py:171]
- Headers: `Authorization: Bearer {OPENROUTER_API_KEY}` + optional `HTTP-Referer` / `X-Title` attribution [source: llm_client.py:159-165]
- Payload: `{"model":"...","max_tokens":...,"messages":[{"role":"system","content":"..."},...]}` (OpenAI-compatible) [source: llm_client.py:166-170]

## Rate limits

Not specified on openrouter.ai/docs (defers to FAQ `/docs/faq#how-are-rate-limits-calculated`) [source: webfetch 2026-09-06]. No numeric values returned by WebSearch/WebFetch either. Treat as undocumented — rely on graceful fallback (`LLM_AUTO_FALLBACK=true`) rather than rate-based backoff.

## What key is needed

- Only `OPENROUTER_API_KEY=sk-...` (key must start `sk-or-` for provider auto-detect; `detect_provider()` checks prefix) [source: llm_client.py:67, 90-96].
- No `OPENROUTER_MODEL=` override required — defaults are valid (`minimax/minimax-m3:free`). Override only to force a different `:free` slug.
- `LLM_PROVIDER=auto` (default) picks OpenRouter when key starts `sk-or-` [source: config.py:57, llm_client.py:92-96].
- Anthropic path (`ANTHROPIC_API_KEY`) exists but was swapped out; not needed. Bhashini (`BHASHINI_API_KEY`) deferred [source: config.py:45-52, 82-86].

## Dependencies

LLM wire uses `httpx>=0.25.0` (installed); no openai SDK dependency required [source: requirements.txt:18, llm_client.py:36].

## Recommendation (lazy)

Keep `LLM_PROVIDER=auto`, `OPENROUTER_FREE_ONLY=true`, set `OPENROUTER_API_KEY=sk-or-...`, leave `OPENROUTER_MODEL` at default `minimax/minimax-m3:free`. The fallback chain (`nemotron-3-ultra-550b:free`, `nemotron-3-super-120b:free`) activates automatically on provider errors or `null` content [source: llm_client.py:223-265]. No model override needed unless testing an alternate `:free` slug.

---
Citations: [file:line] format per instruction. 1 page, no abstraction added.
