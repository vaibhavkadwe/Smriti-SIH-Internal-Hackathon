"""Test configuration and fixtures for FastAPI Elder-Care Cognitive Platform."""

import os

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("ENABLE_BACKGROUND_JOBS", "false")
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")
# Test isolation: force LLM keys empty so no test ever makes a live network call,
# even when a real OPENROUTER_API_KEY is present in .env. Tests exercise the
# real vs fallback paths by constructing LLMClient with explicit keys/transports.
os.environ["OPENROUTER_API_KEY"] = ""
os.environ["ANTHROPIC_API_KEY"] = ""
os.environ["CLAUDE_API_KEY"] = ""
# Tests pin the deterministic embedder: no torch import, no model download,
# fast + offline in CI. Semantic-provider behavior is covered by unit tests of
# the provider registry with a stubbed backend.
os.environ["EMBEDDING_PROVIDER"] = "heuristic"
# Pin the language provider to mock: no test makes a live ASR/TTS/NMT call even
# when a real HUGGINGFACE_API_TOKEN / BHASHINI creds exist in .env. The
# ai4bharat/bhashini providers are covered by unit tests with a stubbed
# (httpx.MockTransport) backend — same isolation pattern as the embedder/LLM.
os.environ["LANGUAGE_SERVICE_PROVIDER"] = "mock"

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
# expire_on_commit=False mirrors backend/app/database.py (prod): commit does
# not expire ORM attributes, so response serialization after an audited read
# never triggers a lazy load outside the request greenlet.
TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine,
    class_=AsyncSession, expire_on_commit=False,
)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
