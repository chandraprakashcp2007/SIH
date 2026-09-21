"""
Tests for Copilot BM25 RAG & Local Knowledge Base
"""
import pytest
from backend.app.copilot.retrieval import knowledge_retriever
from backend.app.copilot.ranking import BM25Ranker, tokenize


def test_bm25_tokenization():
    tokens = tokenize("JALA-01 ultrasonic river surge forecasting 2026!")
    assert "jala-01" in tokens
    assert "ultrasonic" in tokens
    assert "river" in tokens


def test_knowledge_base_indexing():
    knowledge_retriever.build_index(force=True)
    assert knowledge_retriever.is_ready is True
    assert len(knowledge_retriever.chunks) > 5
    assert len(knowledge_retriever.fingerprint) == 32


def test_knowledge_retrieval_jala():
    results = knowledge_retriever.retrieve("How does JALA measure water level?", top_k=3)
    assert len(results) > 0
    # Must retrieve jala or architecture doc
    top_doc = results[0]["document"].lower()
    assert "jala" in top_doc or "architecture" in top_doc or "readme" in top_doc


def test_knowledge_retrieval_sensor_trust():
    results = knowledge_retriever.retrieve("sensor trust contradiction check", top_k=3)
    assert len(results) > 0
    found_trust = any("trust" in c["content"].lower() for c in results)
    assert found_trust is True
