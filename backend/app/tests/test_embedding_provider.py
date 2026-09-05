"""Tests for EmbeddingProvider — determinism, registry, graceful fallback."""
import pytest

from app.config import settings
from app.services.embedding_provider import (
    EmbeddingUnavailableError,
    HeuristicEmbeddingProvider,
    get_embedding_provider,
)


def test_heuristic_is_deterministic_and_normalized():
    provider = HeuristicEmbeddingProvider()
    a = provider.embed("Amlodipine 5 mg every morning")
    b = provider.embed("Amlodipine 5 mg every morning")
    assert a == b
    # normalized (unit) vector
    norm = sum(x * x for x in a) ** 0.5
    assert abs(norm - 1.0) < 1e-6
    assert len(a) == settings.EMBEDDING_DIMENSIONS


def test_heuristic_similarity_reflects_lexical_overlap():
    provider = HeuristicEmbeddingProvider()
    v1 = provider.embed("Take Metformin twice daily with meals")
    v2 = provider.embed("Metformin twice daily dosage with meals")
    v3 = provider.embed("blood pressure target below one forty")
    sim_same = sum(x * y for x, y in zip(v1, v2))
    sim_diff = sum(x * y for x, y in zip(v1, v3))
    assert sim_same > sim_diff


def test_heuristic_stable_across_instances():
    # md5 hashing is process/instance independent -> stored vectors match a
    # fresh query vector computed in another request.
    a = HeuristicEmbeddingProvider().embed("routine pillbox morning")
    b = HeuristicEmbeddingProvider().embed("routine pillbox morning")
    assert a == b


def test_default_provider_is_heuristic():
    provider = get_embedding_provider()
    assert isinstance(provider, HeuristicEmbeddingProvider)


def test_local_provider_raises_when_package_missing(monkeypatch):
    """Intent preserved: the provider hard-fails (never silently) without the
    package. Simulated by making find_spec report absence — the package IS
    installed in this venv, so we stub the discovery instead of uninstalling."""
    import app.services.embedding_provider as ep

    monkeypatch.setattr(ep.importlib.util, "find_spec", lambda name: None)
    with pytest.raises(EmbeddingUnavailableError):
        ep.LocalSentenceTransformerProvider()


def test_registry_falls_back_to_heuristic_for_missing_backend(monkeypatch):
    # A backend that cannot be built (package/key missing) must degrade to the
    # deterministic provider — never raise. Simulated by stubbing discovery off.
    import app.services.embedding_provider as ep

    monkeypatch.setattr(ep.importlib.util, "find_spec", lambda name: None)
    monkeypatch.setattr(settings, "EMBEDDING_PROVIDER", "local")
    provider = get_embedding_provider()
    assert isinstance(provider, HeuristicEmbeddingProvider)


def test_registry_falls_back_for_unknown_name(monkeypatch):
    monkeypatch.setattr(settings, "EMBEDDING_PROVIDER", "does-not-exist")
    provider = get_embedding_provider()
    assert isinstance(provider, HeuristicEmbeddingProvider)


def test_embed_many_batches():
    provider = HeuristicEmbeddingProvider()
    vectors = provider.embed_many(["one dose", "two doses"])
    assert len(vectors) == 2
    assert len(vectors[0]) == settings.EMBEDDING_DIMENSIONS
