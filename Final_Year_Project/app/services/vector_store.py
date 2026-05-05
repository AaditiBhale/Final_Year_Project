from __future__ import annotations

from pathlib import Path
from typing import List


class ManufacturingVectorStore:
    """
    Lightweight text retriever for local demos.
    Replace with FAISS/Chroma + embeddings for production usage.
    """

    def __init__(self, knowledge_file: str = "data/knowledge_base.md") -> None:
        base_path = Path(__file__).resolve().parents[2]
        self.knowledge_path = base_path / knowledge_file
        self.chunks = self._load_chunks()

    def _load_chunks(self) -> List[str]:
        if not self.knowledge_path.exists():
            return []
        raw = self.knowledge_path.read_text(encoding="utf-8")
        return [chunk.strip() for chunk in raw.split("\n\n") if chunk.strip()]

    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        if not self.chunks:
            return ["No local manufacturing knowledge base found."]
        query_terms = set(query.lower().split())
        scored = []
        for chunk in self.chunks:
            overlap = len(query_terms.intersection(set(chunk.lower().split())))
            scored.append((overlap, chunk))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in scored[:top_k]]
