import json
import re
from pathlib import Path

from config import CHROMA_DIR, KNOWLEDGE_DIR
from rag.retriever import embed_texts, get_collection


def load_documents(knowledge_dir: str | Path = KNOWLEDGE_DIR) -> list[dict]:
    documents = []
    for path in sorted(Path(knowledge_dir).glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError(f"Knowledge file must contain a JSON list: {path.name}")
        for item in payload:
            required = ("id", "title", "category", "description", "content", "source")
            if any(not item.get(key) for key in required):
                raise ValueError(f"Knowledge document in {path.name} is missing required fields.")
            documents.append(item)
    return documents


def chunk_text(text: str, chunk_words: int = 160, overlap_words: int = 30) -> list[str]:
    words = re.sub(r"\s+", " ", text).strip().split(" ")
    if not words or words == [""]:
        return []
    if chunk_words < 1 or overlap_words < 0 or overlap_words >= chunk_words:
        raise ValueError("Chunk size must be positive and overlap must be smaller than the chunk.")
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_words, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = end - overlap_words
    return chunks


def ingest_knowledge_base(
    knowledge_dir: str | Path = KNOWLEDGE_DIR,
    persist_directory: str | Path = CHROMA_DIR,
) -> int:
    records = load_documents(knowledge_dir)
    chunks = []
    metadata = []
    identifiers = []
    for record in records:
        text = f"{record['title']}. {record['description']} {record['content']}"
        for index, chunk in enumerate(chunk_text(text)):
            chunks.append(chunk)
            metadata.append(
                {
                    "title": record["title"],
                    "category": record["category"],
                    "source_name": record["source"].get("name", "Unknown source"),
                    "source_url": record["source"].get("url", ""),
                    "document_id": record["id"],
                    "chunk_index": index,
                }
            )
            identifiers.append(f"{record['id']}-{index}")
    if not chunks:
        raise ValueError("The local knowledge base contains no searchable content.")

    collection = get_collection(str(Path(persist_directory)))
    existing_ids = collection.get(include=["metadatas"]).get("ids", [])
    if existing_ids:
        collection.delete(ids=existing_ids)
    collection.add(
        ids=identifiers,
        documents=chunks,
        metadatas=metadata,
        embeddings=embed_texts(chunks),
    )
    return len(chunks)