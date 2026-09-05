"""Phase 10 tests — RAG pipeline (chunking, embeddings, retrieval, answers)."""
import uuid

import pytest
import httpx

from app.services.rag_service import RAGService
from app.services.llm_client import LLMClient


# ---------- chunking ----------


def test_chunk_text_long_document_with_overlap():
    words = " ".join(f"word{i}" for i in range(200))
    chunks = RAGService.chunk_text(words, chunk_size=120, overlap=40)
    assert len(chunks) >= 2
    assert all(len(c) <= 200 for c in chunks)  # chunk + overlap caps


def test_chunk_text_short_document_single_chunk():
    assert RAGService.chunk_text("short text here") == ["short text here"]


def test_chunk_text_empty():
    assert RAGService.chunk_text("") == []
    assert RAGService.chunk_text("   ") == []


# ---------- embeddings ----------


def test_embeddings_are_deterministic_and_normalized():
    e1 = RAGService.generate_embedding("Donepezil 5mg once daily at bedtime")
    e2 = RAGService.generate_embedding("Donepezil 5mg once daily at bedtime")
    assert e1 == e2
    norm = sum(x * x for x in e1) ** 0.5
    assert abs(norm - 1.0) < 1e-6
    assert RAGService.cosine_similarity(e1, e2) == pytest.approx(1.0, abs=1e-6)


def test_embeddings_similar_text_closer_than_dissimilar():
    q = RAGService.generate_embedding("Donepezil dosage for MCI")
    same = RAGService.generate_embedding("Donepezil 5mg dose for mild cognitive impairment")
    diff = RAGService.generate_embedding("Assam tea festival Bihu celebration")
    assert RAGService.cosine_similarity(q, same) > RAGService.cosine_similarity(q, diff)


# ---------- ingest / query (SQLite-backed) ----------


@pytest.mark.asyncio
async def test_ingest_and_query_roundtrip(db_session):
    patient_id = uuid.uuid4()
    doc = await RAGService.ingest_document(
        db=db_session,
        patient_id=patient_id,
        uploaded_by=uuid.uuid4(),
        file_ref="reports/prescription_2026.pdf",
        doc_type="prescription",
        title="Prescription 2026",
        extracted_text=(
            "Patient prescribed Donepezil 5mg once daily at bedtime for mild "
            "cognitive impairment. Also advised physical exercise and a healthy diet."
        ),
    )
    assert doc.id is not None
    assert doc.embedding_status.value == "completed"

    matches = await RAGService.query_medical_context(
        db=db_session, patient_id=patient_id, query="Donepezil dosage", top_k=1
    )
    assert len(matches) == 1
    assert "Donepezil" in matches[0]["text"]
    assert matches[0]["title"] == "Prescription 2026"
    assert matches[0]["file_ref"] == "reports/prescription_2026.pdf"
    assert matches[0]["similarity"] > 0.0

    # Unrelated patient sees nothing
    other = await RAGService.query_medical_context(
        db=db_session, patient_id=uuid.uuid4(), query="Donepezil dosage"
    )
    assert other == []


@pytest.mark.asyncio
async def test_query_respects_similarity_threshold(db_session):
    patient_id = uuid.uuid4()
    await RAGService.ingest_document(
        db=db_session,
        patient_id=patient_id,
        uploaded_by=uuid.uuid4(),
        file_ref="x.pdf",
        doc_type="report",
        extracted_text="Patient reports good sleep and appetite this week.",
    )
    matches = await RAGService.query_medical_context(
        db=db_session,
        patient_id=patient_id,
        query="Donepezil dosage",
        top_k=3,
        min_similarity=0.99,  # unreachable threshold -> nothing returned
    )
    assert matches == []


# ---------- answer synthesis ----------


@pytest.mark.asyncio
async def test_answer_extractive_without_llm_key(db_session, monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "")
    patient_id = uuid.uuid4()
    await RAGService.ingest_document(
        db=db_session,
        patient_id=patient_id,
        uploaded_by=uuid.uuid4(),
        file_ref="donepezil.pdf",
        doc_type="prescription",
        extracted_text="Prescribed Donepezil 5mg once daily at bedtime for MCI.",
    )
    result = await RAGService.answer_question(
        db=db_session,
        patient_id=patient_id,
        question="What is the Donepezil dosage?",
        llm=LLMClient(api_key=""),
    )
    assert result["question"]
    assert result["synthesized"] is False
    assert len(result["citations"]) >= 1
    assert "(1)" in result["answer"]
    assert "disclaimer" in result


@pytest.mark.asyncio
async def test_answer_synthesized_with_llm(db_session):
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        import json

        captured["json"] = json.loads(request.content.decode())
        return httpx.Response(
            200, json={"content": [{"type": "text", "text": "The dosage is 5mg at bedtime [1]."}]}
        )

    patient_id = uuid.uuid4()
    await RAGService.ingest_document(
        db=db_session,
        patient_id=patient_id,
        uploaded_by=uuid.uuid4(),
        file_ref="donepezil.pdf",
        doc_type="prescription",
        extracted_text="Prescribed Donepezil 5mg once daily at bedtime for MCI.",
    )
    llm = LLMClient(api_key="sk-test", transport=httpx.MockTransport(handler))
    result = await RAGService.answer_question(
        db=db_session, patient_id=patient_id, question="What is the dosage?", llm=llm
    )
    assert result["synthesized"] is True
    assert "5mg" in result["answer"]
    assert "[1]" in captured["json"]["messages"][0]["content"]


@pytest.mark.asyncio
async def test_answer_with_no_records(db_session):
    result = await RAGService.answer_question(
        db=db_session, patient_id=uuid.uuid4(), question="Anything?", llm=LLMClient(api_key="")
    )
    assert result["citations"] == []
    assert "No relevant records" in result["answer"]
