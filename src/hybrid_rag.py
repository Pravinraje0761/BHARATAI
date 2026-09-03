"""Hybrid Retrieval Engine (Dense Semantic MiniLM + Sparse BM25 Keyword) for BHARATGURU.

Combines exact semantic vector similarity with token-level lexical overlap
using Reciprocal Rank Fusion (RRF) for retrieval precision.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any

from src.ingestion import Chunk
from src.retrieval import Retriever


class BM25Index:
    """Lightweight in-memory BM25 tokenizer and ranker with zero extra dependencies."""

    def __init__(self, chunks: list[Chunk], k1: float = 1.5, b: float = 0.75):
        self.chunks = chunks
        self.k1 = k1
        self.b = b
        self.doc_lens = [len(self._tokenize(c.text)) for c in chunks]
        self.avg_len = sum(self.doc_lens) / max(1, len(self.doc_lens))
        self.doc_freqs: dict[str, int] = Counter()
        self.doc_token_counts = []

        for c in chunks:
            tokens = self._tokenize(c.text)
            counts = Counter(tokens)
            self.doc_token_counts.append(counts)
            for t in counts:
                self.doc_freqs[t] += 1

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return re.findall(r"\w+", text.lower())

    def score(self, query: str) -> list[float]:
        q_tokens = self._tokenize(query)
        n_docs = len(self.chunks)
        scores = [0.0] * n_docs

        for q in q_tokens:
            df = self.doc_freqs.get(q, 0)
            if not df:
                continue
            # IDF with Robertson-Spärck Jones weighting
            idf = math.log((n_docs - df + 0.5) / (df + 0.5) + 1.0)
            for idx, counts in enumerate(self.doc_token_counts):
                tf = counts.get(q, 0)
                if tf == 0:
                    continue
                num = tf * (self.k1 + 1)
                denom = tf + self.k1 * (1 - self.b + self.b * (self.doc_lens[idx] / self.avg_len))
                scores[idx] += idf * (num / denom)

        return scores


class HybridRetriever:
    """Combines Dense MiniLM cosine similarities with Sparse BM25 via Reciprocal Rank Fusion."""

    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        self.dense_store = Retriever(chunks) if chunks else None
        self.bm25_index = BM25Index(chunks) if chunks else None

    def search(self, query: str, top_k: int = 4) -> list[tuple[Chunk, float]]:
        if not self.chunks:
            return []

        # 1. Dense Semantic Ranks
        dense_results = self.dense_store.retrieve(query, k=min(len(self.chunks), 15))
        dense_rank = {hit.chunk.text: rank + 1 for rank, hit in enumerate(dense_results)}

        # 2. Sparse BM25 Ranks
        bm25_scores = self.bm25_index.score(query)
        sorted_bm25_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)
        bm25_rank = {self.chunks[i].text: rank + 1 for rank, i in enumerate(sorted_bm25_indices[:15])}

        # 3. Reciprocal Rank Fusion (RRF constant k=60)
        rrf_scores = []
        chunk_map = {c.text: c for c in self.chunks}
        for text, chunk in chunk_map.items():
            d_r = dense_rank.get(text, 100)
            b_r = bm25_rank.get(text, 100)
            score = (1.0 / (60.0 + d_r)) + (1.0 / (60.0 + b_r))
            rrf_scores.append((chunk, score))

        rrf_scores.sort(key=lambda x: x[1], reverse=True)
        return rrf_scores[:top_k]
