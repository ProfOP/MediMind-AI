from functools import lru_cache
from pathlib import Path

from config import CHROMA_DIR, EMBEDDING_MODEL, MODEL_CACHE_DIR

import chromadb
from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def _embedding_model() -> SentenceTransformer:
    return SentenceTransformer(
        EMBEDDING_MODEL,
        cache_folder=str(MODEL_CACHE_DIR / "sentence-transformers"),
    )


def embed_texts(texts: list[str]) -> list[list[float]]:
    try:
        vectors = _embedding_model().encode(texts, normalize_embeddings=True)
        return vectors.tolist()
    except Exception as exc:
        raise RuntimeError(
            "The local embedding model is unavailable. The first run needs internet to cache "
            "sentence-transformers/all-MiniLM-L6-v2 under this project's data/models folder."
        ) from exc


@lru_cache(maxsize=8)
def get_collection(persist_directory: str = str(CHROMA_DIR)):
    client = chromadb.PersistentClient(path=str(Path(persist_directory)))
    return client.get_or_create_collection(
        name="medical_education",
        metadata={"hnsw:space": "cosine"},
    )


def retrieve(query: str, top_k: int = 3, persist_directory: str = str(CHROMA_DIR)) -> list[dict]:
    if not query.strip():
        return []
    collection = get_collection(persist_directory)
    if collection.count() == 0:
        from rag.ingest import ingest_knowledge_base

        ingest_knowledge_base(persist_directory=persist_directory)
        collection = get_collection(persist_directory)
    query_vector = embed_texts([query])[0]
    matches = collection.query(
        query_embeddings=[query_vector],
        n_results=min(max(1, top_k), collection.count()),
        include=["documents", "metadatas", "distances"],
    )
    documents = matches.get("documents", [[]])[0]
    metadatas = matches.get("metadatas", [[]])[0]
    distances = matches.get("distances", [[]])[0]
    return [
        {
            "text": text,
            "title": metadata.get("title", "Untitled reference"),
            "category": metadata.get("category", "General"),
            "source_name": metadata.get("source_name", "Unknown source"),
            "source_url": metadata.get("source_url", ""),
            "distance": distance,
        }
        for text, metadata, distance in zip(documents, metadatas, distances)
    ]