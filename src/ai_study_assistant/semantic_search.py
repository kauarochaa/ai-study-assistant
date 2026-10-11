"""Multilingual embeddings and a persistent local Qdrant index."""

import hashlib
import json
import re
from dataclasses import asdict
from pathlib import Path

from fastembed import TextEmbedding
from qdrant_client import QdrantClient, models

from .documents import DocumentChunk
from .search import SearchResult

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def _delete_local_collection(client, name: str, data_dir: Path):
    if not re.fullmatch(r"study_[0-9a-f]{24}", name):
        return
    collections_dir = (data_dir / "qdrant" / "collection").resolve()
    target = (collections_dir / name).resolve()
    if target.parent != collections_dir:
        raise ValueError("Caminho de índice inválido.")
    # qdrant-client 1.19.1 local deletion does not close SQLite first.
    # This version-specific adapter prevents locked files on Windows.
    local_collection = client._client.collections.get(name)
    if local_collection is not None:
        local_collection.close()
    client.delete_collection(name)


def clear_study_index(data_dir: Path):
    if not (data_dir / "qdrant").exists():
        return
    client = QdrantClient(path=str(data_dir / "qdrant"))
    try:
        for collection in client.get_collections().collections:
            _delete_local_collection(client, collection.name, data_dir)
    finally:
        client.close()


class SemanticSearch:
    def __init__(self, chunks: list[DocumentChunk], data_dir: Path, model=None) -> None:
        if not chunks:
            raise ValueError("Não há trechos para indexar.")
        data_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir = data_dir
        self.model = model if model is not None else TextEmbedding(model_name=MODEL_NAME, cache_dir=str(data_dir / "models"), threads=2)
        fingerprint = hashlib.sha256(json.dumps(
            {"model": MODEL_NAME, "chunks": [asdict(chunk) for chunk in chunks]},
            ensure_ascii=False, sort_keys=True,
        ).encode("utf-8")).hexdigest()[:24]
        # A new document set gets its own collection, excluding stale results.
        self.collection = f"study_{fingerprint}"
        self.client = QdrantClient(path=str(data_dir / "qdrant"))
        try:
            self.reused_index = self.client.collection_exists(self.collection)
            if self.reused_index:
                self.reused_index = self.client.count(self.collection, exact=True).count == len(chunks)
            if not self.reused_index:
                vectors = list(self.model.embed([chunk.text for chunk in chunks]))
                if len(vectors) != len(chunks):
                    raise ValueError("Não foi possível gerar todos os embeddings.")
                if self.client.collection_exists(self.collection):
                    self._delete_collection(self.collection)
                self.client.create_collection(
                    collection_name=self.collection,
                    vectors_config=models.VectorParams(size=len(vectors[0]), distance=models.Distance.COSINE),
                )
                self.client.upload_points(
                    collection_name=self.collection,
                    points=[models.PointStruct(id=i, vector=vector.tolist(), payload=asdict(chunk))
                            for i, (chunk, vector) in enumerate(zip(chunks, vectors))],
                    wait=True,
                )
            # Keep only the current derived index: removed material should not
            # remain as searchable payload in abandoned collections.
            for collection in self.client.get_collections().collections:
                if collection.name.startswith("study_") and collection.name != self.collection:
                    self._delete_collection(collection.name)
        except Exception:
            self.client.close()
            raise

    def search(self, question: str, limit: int = 3) -> list[SearchResult]:
        if not question.strip() or limit <= 0:
            return []
        vector = next(self.model.embed([question.strip()]))
        points = self.client.query_points(
            collection_name=self.collection, query=vector.tolist(), limit=limit, with_payload=True,
        ).points
        return [SearchResult(chunk=DocumentChunk(**point.payload), score=point.score)
                for point in points if point.payload]

    def close(self) -> None:
        self.client.close()

    def _delete_collection(self, name: str) -> None:
        _delete_local_collection(self.client, name, self.data_dir)
