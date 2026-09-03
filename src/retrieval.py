"""In-memory RAG: sentence-transformers embeddings + brute-force cosine search.

For one lesson's worth of chunks (dozens, not millions) an exhaustive cosine
scan is instant and exact, so there is no vector-DB service to install or debug.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

import config
from src.ingestion import Chunk

_ENCODER = None


def _encoder():
    global _ENCODER
    if _ENCODER is None:
        from sentence_transformers import SentenceTransformer

        _ENCODER = SentenceTransformer(config.EMBED_MODEL)
    return _ENCODER


def _embed(texts: list[str]) -> np.ndarray:
    vecs = _encoder().encode(
        texts, normalize_embeddings=True, show_progress_bar=False
    )
    return np.asarray(vecs, dtype=np.float32)


@dataclass
class Hit:
    chunk: Chunk
    score: float


class Retriever:
    """Holds chunk embeddings for one lesson and answers top-k queries."""

    def __init__(self, chunks: list[Chunk]):
        self.chunks = list(chunks)
        self._matrix = (
            _embed([c.text for c in self.chunks])
            if self.chunks
            else np.zeros((0, 384), dtype=np.float32)
        )

    def __len__(self) -> int:
        return len(self.chunks)

    def retrieve(self, query: str, k: int = 5) -> list[Hit]:
        if not self.chunks:
            return []
        q = _embed([query])[0]
        sims = self._matrix @ q                      # cosine (vectors are unit-norm)
        order = np.argsort(-sims)[: max(1, k)]
        return [Hit(self.chunks[i], float(sims[i])) for i in order]

    def search(self, query: str, top_k: int = 5) -> list[tuple[Chunk, float]]:
        """Convenience alias returning list of (chunk, score) tuples."""
        return [(h.chunk, h.score) for h in self.retrieve(query, k=top_k)]

    def context_block(self, query: str, k: int = 5) -> str:
        """Formatted, citation-tagged context for prompting the LLM."""
        lines = []
        for h in self.retrieve(query, k):
            lines.append(f"{h.chunk.citation()} {h.chunk.text}")
        return "\n\n".join(lines)


def build_retriever(chunks: list[Chunk]) -> Retriever:
    return Retriever(chunks)
