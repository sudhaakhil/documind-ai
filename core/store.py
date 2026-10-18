"""Document registry (JSON) + ChromaDB vector index."""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import chromadb
from chromadb.config import Settings

from . import llm
from .config import (
    CHROMA_DIR,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    COLLECTION_NAME,
    EMBED_BATCH_SIZE,
    EMBED_MODEL,
    REGISTRY_PATH,
)
from .pdf_loader import PDFError, chunk_pages, extract_pages

ProgressFn = Callable[[float, str], None]


@dataclass
class Document:
    id: str
    filename: str
    size_bytes: int
    pages: int
    chunks: int
    uploaded_at: str
    summary: str | None = None


@dataclass
class Passage:
    n: int  # citation number shown to the model and the user
    text: str
    filename: str
    page: int
    doc_id: str
    score: float  # cosine similarity, 0..1

    def to_dict(self) -> dict:
        return asdict(self)


def read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


class DocumentStore:
    def __init__(self) -> None:
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(
            path=str(CHROMA_DIR), settings=Settings(anonymized_telemetry=False)
        )
        # Embeddings are computed with Ollama and passed in explicitly.
        self._col = client.get_or_create_collection(
            COLLECTION_NAME, metadata={"hnsw:space": "cosine"}, embedding_function=None
        )
        self._docs: dict[str, Document] = {
            d["id"]: Document(**d) for d in read_json(REGISTRY_PATH, [])
        }

    # ---- registry -------------------------------------------------------
    def _save(self) -> None:
        write_json(REGISTRY_PATH, [asdict(d) for d in self._docs.values()])

    def documents(self) -> list[Document]:
        return sorted(self._docs.values(), key=lambda d: d.uploaded_at, reverse=True)

    def get(self, doc_id: str | None) -> Document | None:
        return self._docs.get(doc_id) if doc_id else None

    def set_summary(self, doc_id: str, summary: str) -> None:
        self._docs[doc_id].summary = summary
        self._save()

    # ---- indexing -------------------------------------------------------
    def add_pdf(
        self, filename: str, data: bytes, progress: ProgressFn | None = None
    ) -> tuple[Document, bool]:
        """Index a PDF. Returns (document, created); created is False for duplicates."""
        report = progress or (lambda *_: None)
        doc_id = hashlib.sha256(data).hexdigest()[:16]
        if doc_id in self._docs:
            return self._docs[doc_id], False

        report(0.05, "Reading PDF")
        pages = extract_pages(data)
        chunks = chunk_pages(pages, CHUNK_SIZE, CHUNK_OVERLAP)
        if not chunks:
            raise PDFError(
                "No selectable text found. This looks like a scanned PDF, and OCR isn't supported yet."
            )

        embeddings: list[list[float]] = []
        for start in range(0, len(chunks), EMBED_BATCH_SIZE):
            batch = chunks[start : start + EMBED_BATCH_SIZE]
            report(0.1 + 0.85 * start / len(chunks), f"Embedding passages {start + 1}–{start + len(batch)} of {len(chunks)}")
            embeddings.extend(llm.embed([c.text for c in batch], EMBED_MODEL))

        report(0.97, "Saving to index")
        self._col.add(
            ids=[f"{doc_id}:{c.index}" for c in chunks],
            embeddings=embeddings,
            documents=[c.text for c in chunks],
            metadatas=[
                {"doc_id": doc_id, "filename": filename, "page": c.page, "chunk": c.index}
                for c in chunks
            ],
        )
        doc = Document(
            id=doc_id,
            filename=filename,
            size_bytes=len(data),
            pages=len(pages),
            chunks=len(chunks),
            uploaded_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )
        self._docs[doc_id] = doc
        self._save()
        report(1.0, "Ready")
        return doc, True

    def remove(self, doc_id: str) -> None:
        self._col.delete(where={"doc_id": doc_id})
        self._docs.pop(doc_id, None)
        self._save()

    # ---- retrieval ------------------------------------------------------
    def search(self, query: str, k: int, doc_id: str | None = None) -> list[Passage]:
        if not self._docs:
            return []
        result = self._col.query(
            query_embeddings=llm.embed([query], EMBED_MODEL),
            n_results=k,
            where={"doc_id": doc_id} if doc_id else None,
            include=["documents", "metadatas", "distances"],
        )
        return [
            Passage(
                n=i,
                text=text,
                filename=meta["filename"],
                page=int(meta["page"]),
                doc_id=meta["doc_id"],
                score=max(0.0, 1.0 - dist),
            )
            for i, (text, meta, dist) in enumerate(
                zip(result["documents"][0], result["metadatas"][0], result["distances"][0]),
                start=1,
            )
        ]

    def leading_text(self, doc_id: str, max_chars: int) -> str:
        """The document's opening text, in reading order, for summaries."""
        result = self._col.get(where={"doc_id": doc_id}, include=["documents", "metadatas"])
        ordered = sorted(
            zip(result["documents"], result["metadatas"]), key=lambda pair: pair[1]["chunk"]
        )
        text, total = [], 0
        for chunk, meta in ordered:
            if total >= max_chars:
                break
            text.append(f"[Page {meta['page']}] {chunk}")
            total += len(chunk)
        return "\n\n".join(text)
