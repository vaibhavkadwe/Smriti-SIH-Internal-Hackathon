# Companion Persona (DB-Versioned) + Text-Chat Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship persona v1.2.0 as a new `voice_companion_configs` row (never an in-place edit) and polish the mobile text-chat UI to the Monad spec, with audio explicitly out of scope.

**Architecture:** Backend task adds an idempotent `ensure_persona_v1_2_0()` seeder beside the existing `get_active_config` seed pattern, tested at service level; real-environment activation goes through the existing write path `POST /api/v1/companion/config` (clinician/admin, `activate: true`), the same path `backend/smoke_e2e.py` uses. Frontend tasks edit only `mobile/lib/screens/voice_companion_screen.dart`, reusing `MonadPillButton`, `MonadPillTag` idioms, and `Monad.patientBody` tokens.

**Tech Stack:** FastAPI + SQLAlchemy 2.0 + SQLite-in-memory pytest; Flutter (Material, `flutter_test` for existing widget tests).

**Spec:** User correction 2026-09-12 (DB-stored versioned persona; CLAUDE.md language-set check; text-chat-only frontend polish; speech-plugin flag-back as report-only).

## Global Constraints

- System prompt lives in the DB (`voice_companion_configs`), versioned — NEVER edit a version row in place; always insert a new row (version column is unique).
- New version is `1.2.0` (`1.0.0` = seed default, `1.1.0` = smoke_e2e idempotent seed — both taken).
- `system_prompt` column limit is `String(5000)` — the v1.2.0 text below is ~1500 chars, do not exceed 5000.
- Audio is OUT OF SCOPE: no listening/speaking states, no new audio dependencies.
- Conversation text floor is 20px (`Monad.patientBody` = `monoBodyLg` 20px) — do not introduce smaller conversation text.
- One primary action per screen (lakeBlue `MonadPillButton` primary); parchment canvas, no gradients on patient chrome.
- Do NOT hardcode the persona anywhere else; runtime truth stays the active DB row (`get_system_prompt` prefers it, `voice_persona.txt` remains seed + no-DB fallback only).

---

### Task 1: Phase 1 — persona v1.2.0 (new DB row, approval-gated activation)

**Files:**
- Modify: `backend/app/services/voice_companion_service.py` (add `PERSONA_V1_2_0_PROMPT` + `ensure_persona_v1_2_0`)
- Test: `backend/app/tests/test_voice_companion.py` (append content + versioning tests)

**Interfaces:**
- Consumes: `VoiceCompanionConfig` (`backend/app/models/all_models.py:270`), existing `create_config` / `activate_config` / `get_active_config` / `list_configs` semantics
- Produces: `PERSONA_V1_2_0_PROMPT: str`, `VoiceCompanionService.ensure_persona_v1_2_0(db: AsyncSession) -> VoiceCompanionConfig` (idempotent: returns existing `1.2.0` row if present, else inserts with `activate=True` which deactivates all other rows per `create_config`)

- [ ] **Step 1: Write the failing test**

```python
@pytest.mark.asyncio
async def test_persona_v1_2_0_content_and_activation(db_session):
    config = await VoiceCompanionService.ensure_persona_v1_2_0(db_session)
    assert config.version == "1.2.0"
    assert config.persona_name == "Saathi"
    assert config.is_active is True
    assert "EMOTIONAL CHECK-IN" in config.system_prompt
    assert "BOUNDARIES" in config.system_prompt
    assert "never argue" in config.system_prompt
    assert "inform your caregiver or doctor" in config.system_prompt
    assert "SAME language the patient just used" in config.system_prompt
    assert len(config.system_prompt) <= 5000
    # activating the new row retires the seed default, never edits it
    seed = await VoiceCompanionService.activate_config(db_session, "1.0.0")
    assert seed is not None and seed.system_prompt != config.system_prompt
    service = VoiceCompanionService(lang_service=MockLanguageService(), llm=LLMClient(api_key=""))
    assert await service.get_system_prompt(db=db_session) == seed.system_prompt
    # idempotent re-seed returns the same row, no duplicate
    again = await VoiceCompanionService.ensure_persona_v1_2_0(db_session)
    assert again.id == config.id


@pytest.mark.asyncio
async def test_persona_v1_2_0_duplicate_version_rejected(db_session):
    await VoiceCompanionService.ensure_persona_v1_2_0(db_session)
    with pytest.raises(ValueError):
        await VoiceCompanionService.create_config(
            db_session, version="1.2.0", system_prompt="dup", activate=True
        )
```

Note: `MockLanguageService`, `LLMClient`, and the `db_session` fixture are already imported/available in `test_voice_companion.py` (used by `test_get_system_prompt_uses_db_row`).

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest app/tests/test_voice_companion.py -q -k "v1_2_0" 2>&1 | tail -3`
Expected: FAIL with `AttributeError` / `ImportError` (`ensure_persona_v1_2_0` does not exist yet)

- [ ] **Step 3: Write minimal implementation**

```python
PERSONA_V1_2_0_PROMPT = (
    "You are 'Saathi', a warm, patient, and gentle AI companion for elderly "
    "individuals in Northeast India (Assam, Meghalaya, Manipur, Tripura, "
    "Nagaland, Mizoram, Arunachal Pradesh, Sikkim).\n\n"
    "TONE: Respectful, soft, comforting, and unhurried. Use simple, direct, "
    "short sentences — one idea at a time. Reply in the SAME language the "
    "patient just used; if they mix languages, mirror the dominant one. "
    "Never rushed, never condescending, never clinical.\n\n"
    "EMOTIONAL CHECK-IN: In every conversation, gently ask how the elder is "
    "feeling today (mood, sleep, appetite, company) before anything else. If "
    "they sound sad, lonely, worried, or tired, slow down, name the feeling "
    "kindly (\"That sounds lonely\"), and stay with it — comfort first, tasks "
    "second. Never dismiss, minimize, or rush past an emotion.\n\n"
    "MEMORY: Help the elder recall daily routines, medicines already taken, "
    "family members, happy memories, local tea traditions, and regional "
    "festivals (Bihu, Wangala, Hornbill, Chapchar Kut) with encouraging "
    "words. If they repeat a story or get slightly confused, never argue, "
    "correct harshly, or say \"you already told me that\" — validate gently "
    "and enjoy it with them again.\n\n"
    "BOUNDARIES: Never prescribe medications, adjust dosages, or give medical "
    "diagnoses. If asked about health emergencies, drug dosages, or new "
    "symptoms, gently say: \"Please let me inform your caregiver or doctor "
    "so they can help you right away.\" You are company and memory support, "
    "not a doctor."
)
```

```python
@staticmethod
async def ensure_persona_v1_2_0(db: AsyncSession) -> VoiceCompanionConfig:
    """Insert persona v1.2.0 as a NEW version row (never an in-place edit).

    Idempotent: returns the existing 1.2.0 row when present. Activation
    flips all other rows inactive via create_config(activate=True).
    """
    stmt = select(VoiceCompanionConfig).where(
        VoiceCompanionConfig.version == "1.2.0"
    )
    res = await db.execute(stmt)
    existing = res.scalars().first()
    if existing is not None:
        return existing
    return await VoiceCompanionService.create_config(
        db,
        version="1.2.0",
        system_prompt=PERSONA_V1_2_0_PROMPT,
        persona_name=DEFAULT_PERSONA,
        activate=True,
    )
```

Placement: constant beside `DEFAULT_VERSION`/`DEFAULT_PERSONA` (`voice_companion_service.py:33-34`); method after `activate_config` (`:158-173`). This constant is the insertion payload only — runtime truth remains the active DB row.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest app/tests/test_voice_companion.py -q 2>&1 | tail -2`
Expected: all PASS (existing 1.0.0/2.0.0 versioning tests untouched and green)

- [ ] **Step 5: Activation (ops, approval-gated — do NOT run before the user approves the draft text above)**

```bash
curl -X POST https://<host>/api/v1/companion/config \
  -H "Authorization: Bearer <clinician-or-admin-jwt>" \
  -H "Content-Type: application/json" \
  -d '{"version":"1.2.0","persona_name":"Saathi","activate":true,"system_prompt":"<exact PERSONA_V1_2_0_PROMPT text>"}'
```

This is the existing write path (`POST /companion/config`, 201; 409 if the version already exists). Verify with `GET /api/v1/companion/config` (newest first; `1.2.0` has `is_active: true`). Rollback is `POST /api/v1/companion/config/1.0.0/activate` (or `1.1.0`).

- [ ] **Step 6: Commit (code + tests only; activation is an ops call, not a commit)**

```bash
git add backend/app/services/voice_companion_service.py backend/app/tests/test_voice_companion.py
git commit -m "feat: add companion persona v1.2.0 seeder (new versioned row)"
```

---

### Task 2: Language-set truth check + CLAUDE.md refresh (report + 3-line doc fix)

**Files:**
- Modify: `CLAUDE.md` (3 stale lines only — read exact lines first)
- Test: none (docs-only; verify with grep)

**Interfaces:**
- Consumes: `mobile/lib/screens/voice_companion_screen.dart:35-46` (10-entry picker), `:76-97` (provider-gated disabling), backend `supported_languages` contract
- Produces: corrected CLAUDE.md language documentation

- [ ] **Step 1: Confirm the finding (report evidence, no code)**

Run: `grep -n "4-language picker\|text chat, 4 langs\|Ship with Assamese" CLAUDE.md`
Expected: three hits — (a) language-ship list naming only Assamese/Bengali/Hindi/English, (b) "companion chat has a 4-language picker (default Assamese)", (c) "voice_companion (text chat, 4 langs)". Meanwhile the built picker (`voice_companion_screen.dart:35-46`) holds TEN entries (assamese, bengali, hindi, english, mizo, meitei, khasi, bodo, garo, nepali) with provider-gated disabling (`_languageAvailable`, `:94-97`; disabled rows render "— not yet available", `:187-214`), and the screen comment (`:76-80`) already documents Khasi + Mizo exclusion. Conclusion for the user: YES, Khasi/Mizo already appear as disabled options when the active provider lacks them — the earlier session report was right, CLAUDE.md is the stale doc.

- [ ] **Step 2: Read the exact CLAUDE.md lines, then apply these three replacements**

(a) Ship-list line → append the picker reality: `Ship with Assamese, Bengali, Hindi, English (highest-coverage for NER); companion picker additionally lists Mizo, Meitei (Manipuri), Khasi, Bodo, Garo, Nepali, provider-gated (unsupported entries show "not yet available" and are disabled).`
(b) `companion chat has a 4-language picker (default Assamese)` → `companion chat has a 10-language picker (default Assamese; entries the active provider does not cover show "not yet available" and are disabled)`
(c) `voice_companion (text chat, 4 langs)` → `voice_companion (text chat, 10-lang picker, provider-gated)`

- [ ] **Step 3: Verify**

Run: `grep -n "4-language picker\|text chat, 4 langs" CLAUDE.md || echo "stale lines gone"`
Expected: `stale lines gone`

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: companion picker is 10-language provider-gated, not 4-language"
```

---

### Task 3: Frontend polish — text-chat UI to spec (no audio states)

**Files:**
- Modify: `mobile/lib/screens/voice_companion_screen.dart` (only file)
- Test: existing `mobile/test/monad_widgets_test.dart` + `flutter analyze` (no new screen test: the screen fires `/language/status` in `initState`, so a widget test would need HTTP mocking — out of proportion for a styling pass; verification is analyzer + existing suite + the visual checklist in Step 6)

**Interfaces:**
- Consumes: `MonadPillButton` (`mobile/lib/widgets/monad/monad_pill_button.dart`, `label` + `MonadPillVariant.primary` + `busy`), `Monad` colors (`parchment`, `ash`, `periwinkleMist`, `tintGold`, `offBlack`, `white`), `Monad.patientBody` (20px floor)
- Produces: spec-compliant transcript bubbles, pill send button, typing bubble, gold fallback tag

- [ ] **Step 1 (bubbles — FIX DRIFT): patient messages to parchment + ash border**

Built state drifts from spec: user bubbles are `offBlack` fill with white text and no border (`:284-292`); companion bubbles already match spec (periwinkleMist + ash border). Replace the decoration and text color:

```dart
decoration: BoxDecoration(
  color: isUser ? Monad.parchment : Monad.periwinkleMist,
  borderRadius: BorderRadius.only(
    topLeft: const Radius.circular(16),
    topRight: const Radius.circular(16),
    bottomLeft: Radius.circular(isUser ? 16 : 4),
    bottomRight: Radius.circular(isUser ? 4 : 16),
  ),
  border: Border.all(color: Monad.ash, width: 1),
),
child: Text(
  msg.content,
  style: Monad.patientBody.copyWith(
    color: Monad.offBlack,
  ),
),
```

- [ ] **Step 2 (send — FIX DRIFT): `MonadPillButton` primary instead of raw circle `IconButton`**

Built state drifts: `:378-396` is a 50px circle `IconButton` (lakeBlue) with inline spinner. Replace the whole `SizedBox(width: 50, height: 50, child: IconButton(...))` block with:

```dart
MonadPillButton(
  label: 'Send',
  variant: MonadPillVariant.primary,
  busy: _sending,
  onPressed: () => _send(_messageController.text),
),
```

and add the import:

```dart
import '../widgets/monad/monad_pill_button.dart';
```

(`MonadPillButton` already handles busy→spinner and disabled state; its min height 48 aligns with the 50px input field. The trailing "▸" on primary is per DESIGN.md — keep it.)

- [ ] **Step 3 (typing indicator — ADD): simple companion typing bubble while `_sending`**

In `build`, change the list to append one typing item while waiting:

```dart
itemCount: _messages.length + (_sending ? 1 : 0),
itemBuilder: (context, index) => index < _messages.length
    ? _messageBubble(_messages[index])
    : _typingBubble(),
```

and add (next to `_messageBubble`):

```dart
Widget _typingBubble() {
  return Padding(
    padding: const EdgeInsets.only(bottom: 12),
    child: Row(
      mainAxisAlignment: MainAxisAlignment.start,
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        _companionAvatar(),
        const SizedBox(width: 10),
        Flexible(
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: Monad.periwinkleMist,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(16),
                topRight: Radius.circular(16),
                bottomLeft: Radius.circular(4),
                bottomRight: Radius.circular(16),
              ),
              border: Border.all(color: Monad.ash, width: 1),
            ),
            child: Text('…', style: Monad.patientBody),
          ),
        ),
      ],
    ),
  );
}
```

- [ ] **Step 4 (fallback tag — FIX DRIFT): small gold tag at top instead of full-width banner**

Built state drifts: `_offlineBanner` (`:241-262`) is a full-width `tintGold` bar with wifi icon. Replace its body with a small centered gold tag (keep the same copy and the `_wasFallback` wiring in `build`):

```dart
Widget _offlineBanner() {
  return Padding(
    padding: const EdgeInsets.only(top: 8),
    child: Center(
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: ShapeDecoration(
          color: Monad.tintGold,
          shape: StadiumBorder(side: BorderSide(color: Monad.ash, width: 1)),
        ),
        child: Text(
          'OFFLINE MODE — RESPONSES SIMPLIFIED',
          style: Monad.monoBodySm.copyWith(color: Monad.offBlack),
        ),
      ),
    ),
  );
}
```

(`tintGold` is the theme's gold tint; stadium + ash border matches the `MonadPillTag` idiom. `Row`/`Icon` imports stay used elsewhere — run analyze to confirm no unused imports.)

- [ ] **Step 5 (type floor — VERIFY, no change): confirm 20px minimum on all conversation text**

Run: `grep -n "patientBody\|monoBody\b\|monoCaption" mobile/lib/screens/voice_companion_screen.dart`
Expected: bubbles (`:294-299`), input (`:353`), and typing bubble all use `Monad.patientBody` (20px via `monoBodyLg`); `monoBody` (16px)/`monoCaption` (12px) appear ONLY in the language menu, offline tag, and input hint — chrome, not conversation text. No edit needed; if any conversation `Text` uses a smaller style, switch it to `Monad.patientBody`.

- [ ] **Step 6: Verify (analyzer + existing suite + visual checklist)**

Run: `flutter analyze mobile/lib/screens/voice_companion_screen.dart` then `flutter test mobile/test/monad_widgets_test.dart`
Expected: no issues; existing tests pass. Then visually confirm on-device: patient bubble right/parchment/ash-border, companion left/periwinkleMist, Send pill primary, "…" bubble while waiting, gold tag only after a fallback reply, all conversation text ≥20px.

- [ ] **Step 7: Commit**

```bash
git add mobile/lib/screens/voice_companion_screen.dart
git commit -m "feat: companion text-chat Monad polish (bubbles, pill send, typing, fallback tag)"
```

---

### Task 4 (REPORT-ONLY, no code): speech-plugin flag-back for the demo decision

No files, no commits. Verify `mobile/pubspec.yaml` carries no audio plugins today (confirmed: deps are drift/sqlite/notifications/http — no `speech_to_text`, `flutter_tts`, `record`, or `audioplayers`; `assets/audio/` exists but unused by the companion). Report back:

- Option A (on-device voices): `speech_to_text` (mic → text) + `flutter_tts` (device TTS). Roughly 1–2 days including mic-permission UX, locale mapping per picker language, and fallback when a device lacks the voice. Loses server Saaras/Bulbul voices; Assamese/Bodo/Manipuri device support varies by handset.
- Option B (server pipeline): `record` (capture wav → base64 → existing `POST /companion/chat/voice`) + `audioplayers` (play returned base64 wav). Roughly 2–4 days: permissions, recording lifecycle, upload/playback states, error UX. Keeps Saaras STT (Assamese/Bodo/Manipuri codes accepted) — but Bulbul TTS currently beta-gates Assamese/Bodo and rejects Manipuri, so voice replies in those three would still fail server-side today.
- Recommendation for the demo: ship text-chat + document "audio pipeline complete server-side, on-device capture pending". Rationale: even a perfect on-device build cannot speak Assamese/Bodo/Manipuri until Sarvam grants TTS beta access, and mic-permission/recording UX is the riskiest pre-demo work.

---

## Self-Review

- Spec coverage: DB-versioned persona via new row + write-path activation + approval gate ✓ (Task 1); Khasi/Mizo disabled-options check + stale-doc callout ✓ (Task 2); parchment/ash + periwinkleMist bubbles ✓, MonadPillButton primary send ✓, typing indicator ✓, gold fallback tag ✓, 20px floor ✓, no audio states ✓ (Task 3); speech-plugin flag-back ✓ (Task 4, report-only).
- Placeholder scan: every step carries literal code, exact file:line anchors, literal commands with expected outputs, and the full v1.2.0 prompt text. The only deliberate deferral is Task 1 Step 5 (ops activation), which is gated on draft approval by the spec itself — not a placeholder.
- Type consistency: `ensure_persona_v1_2_0(db) -> VoiceCompanionConfig`, `PERSONA_V1_2_0_PROMPT: str`, version `"1.2.0"`, persona `"Saathi"` match across test/implementation/ops steps; Dart identifiers (`MonadPillButton`, `MonadPillVariant.primary`, `busy`, `Monad.tintGold`, `Monad.patientBody`, `Monad.monoBodySm`) match their definitions in `monad_pill_button.dart` / `monad_theme.dart`.
- Open assumptions stated, not hidden: Task 2 assumes the three grep hits are the only stale lines (Step 1 re-verifies); Task 3 assumes no screen-level widget test (justified: `initState` fires `/language/status`); "Phase 2 fallback" is read as the existing `CompanionReply.fallback` → `_wasFallback` wiring already in the screen.
