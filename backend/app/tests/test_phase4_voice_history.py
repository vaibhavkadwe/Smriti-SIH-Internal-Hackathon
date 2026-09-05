"""P4 — persona file + Redis-backed per-patient conversation history."""
import uuid

import pytest

from app.services.conversation_store import ConversationStore, reset_conversation_store_for_tests
from app.services.voice_companion_service import load_persona_prompt

AUTH = "/api/v1/auth"
PATIENTS = "/api/v1/patients"
COMPLIANCE = "/api/v1/compliance"
COMPANION = "/api/v1/companion"


async def _patient_with_consent(client):
    r = await client.post(f"{AUTH}/register", json={
        "phone": f"+91{uuid.uuid4().int % 10**10}",
        "email": f"{uuid.uuid4().hex[:8]}@test.in",
        "password": "Passw0rd123", "role": "patient", "preferred_language": "assamese"})
    assert r.status_code == 201, r.text
    login = await client.post(f"{AUTH}/login",
        json={"phone": r.json()["phone"], "password": "Passw0rd123"})
    h = {"Authorization": f"Bearer {login.json()['access_token']}"}
    prof = await client.post(PATIENTS, json={"name": "Koka Biren", "region": "assam"}, headers=h)
    assert prof.status_code == 201, prof.text
    pid = prof.json()["id"]
    consent = await client.post(f"{COMPLIANCE}/consent", headers=h,
        json={"patient_id": pid, "consent_type": "patient_self", "scope": "voice_companion"})
    assert consent.status_code == 200, consent.text
    return h, pid


def test_persona_file_loaded_and_has_safety_rules():
    p = load_persona_prompt()
    assert "Northeast India" in p or "companion" in p.lower()
    assert "never" in p.lower() and ("medical" in p.lower() or "caregiver" in p.lower())
    assert "SAME language" in p  # respond-in-input-language rule


@pytest.mark.asyncio
async def test_store_roundtrip_and_cap():
    s = ConversationStore(max_turns=4)
    await s.append("p", "u1", "a1")
    await s.append("p", "u2", "a2")
    turns = await s.get("p")
    assert [t["content"] for t in turns] == ["u1", "a1", "u2", "a2"]
    await s.append("p", "u3", "a3")  # exceeds cap -> oldest trimmed
    assert len(await s.get("p")) == 4
    await s.clear("p")
    assert await s.get("p") == []


@pytest.mark.asyncio
async def test_text_chat_persists_history_across_requests(client):
    reset_conversation_store_for_tests()
    h, pid = await _patient_with_consent(client)
    r1 = await client.post(f"{COMPANION}/chat/text", headers=h,
        json={"patient_id": pid, "message": "Hello, I had my tea today.", "language": "english"})
    assert r1.status_code == 200, r1.text
    # canned fallback also fine — history only persists on non-fallback replies
    if r1.json().get("fallback"):
        pytest.skip("LLM key not configured; history path needs a real reply")
    r2 = await client.post(f"{COMPANION}/chat/text", headers=h,
        json={"patient_id": pid, "message": "What did I just tell you?", "language": "english"})
    assert r2.status_code == 200, r2.text
    # store now holds both exchanges for this patient
    from app.routes.voice_companion import get_conversation_store as route_store
    store = await route_store()
    turns = await store.get(pid)
    assert any("tea" in t["content"] for t in turns)
    # DPDP: store never holds identifiers beyond turn text
    assert all(set(t.keys()) == {"role", "content"} for t in turns)


@pytest.mark.asyncio
async def test_voice_chat_requires_consent_scope(client):
    """Companion consent scope is enforced before any history read."""
    h, pid = await _patient_with_consent(client)
    # revoke by consenting only to a different scope? simpler: new patient without consent
    r = await client.post(f"{AUTH}/register", json={
        "phone": f"+91{uuid.uuid4().int % 10**10}",
        "email": f"{uuid.uuid4().hex[:8]}@test.in",
        "password": "Passw0rd123", "role": "patient", "preferred_language": "assamese"})
    login = await client.post(f"{AUTH}/login",
        json={"phone": r.json()["phone"], "password": "Passw0rd123"})
    h2 = {"Authorization": f"Bearer {login.json()['access_token']}"}
    prof = await client.post(PATIENTS, json={"name": "No Consent", "region": "assam"}, headers=h2)
    no_consent_pid = prof.json()["id"]
    resp = await client.post(f"{COMPANION}/chat/text", headers=h2,
        json={"patient_id": no_consent_pid, "message": "hi", "language": "assamese"})
    assert resp.status_code == 403
