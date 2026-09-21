"""
PRAHARI Local Documentation Retrieval Engine (RAG)
Zero-dependency, high-speed local knowledge base with markdown chunking and fingerprint caching.
"""
import os
import hashlib
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from backend.app.copilot.ranking import BM25Ranker

INDEXED_DOC_PATHS = [
    "README.md",
    "docs/project-overview.md",
    "docs/architecture.md",
    "docs/SOFTWARE-ARCHITECTURE.md",
    "docs/AI-ENGINE.md",
    "docs/jala.md",
    "docs/agni.md",
    "docs/bhumi.md",
    "docs/risk-engine.md",
    "docs/gateway-protocol.md",
    "docs/deployment.md",
    "docs/demo-guide.md",
    "docs/safety-limitations.md",
    "docs/testing.md",
]


class DocumentChunk:
    def __init__(self, doc_path: str, section: str, content: str, chunk_index: int):
        self.doc_path = doc_path
        self.section = section
        self.content = content.strip()
        self.chunk_index = chunk_index

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document": self.doc_path,
            "section": self.section,
            "content": self.content,
            "chunk_index": self.chunk_index
        }


class LocalKnowledgeRetriever:
    """Manages document chunking, fingerprint verification, and BM25 search."""

    def __init__(self, workspace_root: Optional[str] = None):
        if workspace_root is None:
            # Navigate 4 levels up from backend/app/copilot/retrieval.py to SIH root
            self.root = Path(__file__).resolve().parent.parent.parent.parent
        else:
            self.root = Path(workspace_root)

        self.chunks: List[DocumentChunk] = []
        self.ranker = BM25Ranker()
        self.fingerprint: str = ""
        self.is_ready: bool = False

    def _compute_fingerprint(self) -> str:
        """Computes combined MD5 hash of target documentation files."""
        hasher = hashlib.md5()
        found_any = False
        for rel_path in INDEXED_DOC_PATHS:
            p = self.root / rel_path
            if p.exists() and p.is_file():
                found_any = True
                mtime = os.path.getmtime(p)
                size = os.path.getsize(p)
                hasher.update(f"{rel_path}:{mtime}:{size}".encode("utf-8"))
        return hasher.hexdigest() if found_any else "empty"

    def _chunk_markdown(self, doc_path: str, text: str) -> List[DocumentChunk]:
        """Intelligently splits markdown by header boundaries."""
        chunks: List[DocumentChunk] = []
        sections = re.split(r'\n(?=#{1,3}\s)', text)
        for idx, sec in enumerate(sections):
            lines = sec.strip().split("\n")
            if not lines or not lines[0].strip():
                continue
            first_line = lines[0].strip()
            section_title = first_line.lstrip("#").strip() if first_line.startswith("#") else "Overview"
            content = sec.strip()
            if len(content) > 30:  # Skip tiny headers
                chunks.append(DocumentChunk(
                    doc_path=doc_path,
                    section=section_title,
                    content=content,
                    chunk_index=idx
                ))
        return chunks

    def build_index(self, force: bool = False):
        """Indexes documents if fingerprint changed or if forced."""
        current_fp = self._compute_fingerprint()
        if not force and self.is_ready and current_fp == self.fingerprint:
            return  # Fingerprint matches, skip redundant work

        all_chunks: List[DocumentChunk] = []
        for rel_path in INDEXED_DOC_PATHS:
            p = self.root / rel_path
            if p.exists() and p.is_file():
                try:
                    with open(p, "r", encoding="utf-8", errors="ignore") as f:
                        text = f.read()
                    doc_chunks = self._chunk_markdown(rel_path, text)
                    all_chunks.extend(doc_chunks)
                except Exception as e:
                    pass

        self.chunks = all_chunks
        # Index provenance alongside the body so a dedicated hazard document
        # outranks a generic guide that happens to repeat the same vocabulary.
        corpus = [f"{c.doc_path} {c.doc_path} {c.section} {c.content}" for c in self.chunks]
        self.ranker.fit(corpus)
        self.fingerprint = current_fp
        self.is_ready = True

    def retrieve(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """Retrieves top_k relevant documentation chunks."""
        if not self.is_ready or not self.chunks:
            self.build_index()

        ranked = self.ranker.score(query)
        query_terms = set(re.findall(r'[a-z0-9_-]+', query.lower()))
        # Domain documents such as docs/jala.md are authoritative for explicit
        # entity queries. Apply a transparent provenance bonus after BM25.
        reranked = []
        for doc_idx, score in ranked:
            stem = Path(self.chunks[doc_idx].doc_path).stem.lower()
            provenance_bonus = 5.0 if stem in query_terms else 0.0
            reranked.append((doc_idx, score + provenance_bonus))
        ranked = sorted(reranked, key=lambda item: item[1], reverse=True)
        results: List[Dict[str, Any]] = []
        for doc_idx, score in ranked[:top_k]:
            chunk = self.chunks[doc_idx]
            c_dict = chunk.to_dict()
            c_dict["relevance_score"] = round(score, 3)
            results.append(c_dict)
        return results


knowledge_retriever = LocalKnowledgeRetriever()
