"""Per-patient conversation history for the voice companion.

Seam: Redis when REDIS_URL is reachable, else an in-process dict (tests,
no-redis dev). Turn text is treated as sensitive health data — never logged,
and each patient's buffer is capped so memory cannot grow unbounded.

DPDP: stores only {role, content} turns — no identifiers, no phone numbers.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from app.config import settings

logger = logging.getLogger(__name__)

_MAX_TURNS = 20  # per patient; oldest trimmed first
_TTL_SECONDS = 7 * 24 * 3600  # one week of conversation memory


class ConversationStore:
    """Turn-taking memory keyed by patient id."""

    def __init__(self, redis_client=None, max_turns: int = _MAX_TURNS):
        self._redis = redis_client  # optional redis.asyncio client
        self._mem: Dict[str, List[Dict[str, str]]] = {}
        self.max_turns = max_turns

    # ---------- internals ----------

    def _key(self, patient_id: str) -> str:
        return f"companion:history:{patient_id}"

    async def _redis_get(self, key: str) -> List[Dict[str, str]]:
        raw = await self._redis.get(key)
        return json.loads(raw) if raw else []

    async def _redis_set(self, key: str, turns: List[Dict[str, str]]) -> None:
        await self._redis.set(key, json.dumps(turns), ex=_TTL_SECONDS)

    # ---------- public API ----------

    async def get(self, patient_id: str) -> List[Dict[str, str]]:
        try:
            if self._redis is not None:
                return await self._redis_get(self._key(patient_id))
        except Exception as exc:  # redis down -> degrade to memory
            logger.warning("Redis history read failed (%s); using in-memory", exc)
        return list(self._mem.get(patient_id, []))

    async def append(
        self,
        patient_id: str,
        user_message: str,
        assistant_reply: str,
    ) -> List[Dict[str, str]]:
        turns = await self.get(patient_id)
        turns.append({"role": "user", "content": user_message})
        turns.append({"role": "assistant", "content": assistant_reply})
        if len(turns) > self.max_turns:
            turns = turns[-self.max_turns:]
        if self._redis is not None:
            try:
                await self._redis_set(self._key(patient_id), turns)
            except Exception as exc:
                logger.warning("Redis history write failed (%s); in-memory only", exc)
        self._mem[patient_id] = turns
        return turns

    async def clear(self, patient_id: str) -> None:
        self._mem.pop(patient_id, None)
        if self._redis is not None:
            try:
                await self._redis.delete(self._key(patient_id))
            except Exception as exc:
                logger.warning("Redis history clear failed (%s)", exc)


_store: Optional[ConversationStore] = None
_redis_tried = False


async def get_conversation_store() -> ConversationStore:
    """Singleton store: Redis-backed when configured and reachable, else memory.

    ponytail: connection probe on first call only; a down Redis degrades to
    in-memory history rather than breaking chat.
    """
    global _store, _redis_tried
    if _store is not None:
        return _store
    if not _redis_tried and settings.REDIS_URL:
        _redis_tried = True
        try:
            import redis.asyncio as aioredis

            client = aioredis.from_url(
                settings.REDIS_URL, socket_connect_timeout=1, decode_responses=True
            )
            await client.ping()
            _store = ConversationStore(redis_client=client)
            logger.info("Companion history: Redis-backed")
            return _store
        except Exception as exc:
            logger.warning("Redis unavailable (%s); companion history in-memory", exc)
    _store = ConversationStore()
    return _store


def reset_conversation_store_for_tests() -> None:
    global _store, _redis_tried
    _store = None
    _redis_tried = False


# Self-check: python -m app.services.conversation_store
if __name__ == "__main__":
    import asyncio

    async def _demo():
        s = ConversationStore()
        await s.append("p1", "hi", "hello dear")
        await s.append("p1", "how are you", "I am well")
        h = await s.get("p1")
        assert len(h) == 4, h
        small = ConversationStore(max_turns=2)
        await small.append("p2", "a", "b")
        await small.append("p2", "c", "d")
        assert [t["content"] for t in await small.get("p2")] == ["c", "d"]
        await s.clear("p1")
        assert await s.get("p1") == []
        print("conversation_store: OK")

    asyncio.run(_demo())
