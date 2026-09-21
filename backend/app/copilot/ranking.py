"""
PRAHARI BM25 Scoring & Ranking Algorithm
Pure-Python ultra-fast BM25 implementation for local edge documentation retrieval.
"""
import math
import re
from typing import List, Dict, Any, Tuple

# Simple regex-based tokenizer with stopword filtering
STOPWORDS = {
    "a", "an", "the", "and", "or", "in", "on", "at", "to", "for", "with", "by", "of",
    "is", "are", "was", "were", "be", "been", "that", "which", "this", "these", "it"
}


def tokenize(text: str) -> List[str]:
    tokens = re.findall(r'[a-zA-Z0-9_\-\.]+', text.lower())
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]


class BM25Ranker:
    """Okapi BM25 implementation with document length normalization."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size: int = 0
        self.avg_doc_len: float = 0.0
        self.doc_lengths: List[int] = []
        self.doc_freqs: Dict[str, int] = {}
        self.term_freqs: List[Dict[str, int]] = []
        self.idf: Dict[str, float] = {}

    def fit(self, documents: List[str]):
        """Index tokenized documents."""
        self.corpus_size = len(documents)
        if self.corpus_size == 0:
            return

        self.doc_lengths = []
        self.term_freqs = []
        self.doc_freqs = {}

        total_tokens = 0
        for doc in documents:
            tokens = tokenize(doc)
            doc_len = len(tokens)
            self.doc_lengths.append(doc_len)
            total_tokens += doc_len

            tf: Dict[str, int] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            self.term_freqs.append(tf)

            for t in set(tokens):
                self.doc_freqs[t] = self.doc_freqs.get(t, 0) + 1

        self.avg_doc_len = total_tokens / max(1, self.corpus_size)

        # Precompute IDF
        self.idf = {}
        for term, freq in self.doc_freqs.items():
            # Standard BM25 IDF formulation
            self.idf[term] = math.log(1.0 + (self.corpus_size - freq + 0.5) / (freq + 0.5))

    def score(self, query: str) -> List[Tuple[int, float]]:
        """Scores each document against query tokens. Returns list of (doc_index, score) sorted descending."""
        if self.corpus_size == 0:
            return []

        q_tokens = tokenize(query)
        if not q_tokens:
            return []

        scores: List[float] = [0.0] * self.corpus_size

        for term in q_tokens:
            if term not in self.idf:
                continue
            idf_val = self.idf[term]

            for doc_idx, tf_dict in enumerate(self.term_freqs):
                if term in tf_dict:
                    freq = tf_dict[term]
                    doc_len = self.doc_lengths[doc_idx]
                    denom = freq + self.k1 * (1.0 - self.b + self.b * (doc_len / max(1.0, self.avg_doc_len)))
                    scores[doc_idx] += idf_val * (freq * (self.k1 + 1.0)) / max(0.001, denom)

        ranked = [(idx, score) for idx, score in enumerate(scores) if score > 0.0]
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked
