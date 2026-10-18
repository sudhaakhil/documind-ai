"""PDF text extraction and page-aware chunking."""

from __future__ import annotations

import io
import re
from dataclasses import dataclass

from pypdf import PdfReader
from pypdf.errors import PdfReadError


class PDFError(ValueError):
    """The PDF can't be indexed (corrupt, encrypted, or has no text)."""


@dataclass
class Chunk:
    text: str
    page: int  # 1-based
    index: int  # position within the document


def _normalize(text: str) -> str:
    text = re.sub(r"-\n(?=\w)", "", text)  # re-join hyphenated line breaks
    text = re.sub(r"[ \t ]+", " ", text)
    text = re.sub(r" ?\n ?", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pages(data: bytes) -> list[str]:
    """Return the text of each page (index 0 = page 1)."""
    try:
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted and not reader.decrypt(""):
            raise PDFError("This PDF is password-protected.")
        return [_normalize(page.extract_text() or "") for page in reader.pages]
    except PdfReadError as exc:
        raise PDFError("This file couldn't be read as a PDF. It may be damaged.") from exc


def _split(text: str, size: int, overlap: int) -> list[str]:
    pieces, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            # Prefer to break at a paragraph, sentence or word boundary.
            window = text[start:end]
            for sep in ("\n\n", ". ", "\n", " "):
                cut = window.rfind(sep)
                if cut > size * 0.6:
                    end = start + cut + len(sep)
                    break
        piece = text[start:end].strip()
        if piece:
            pieces.append(piece)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return pieces


def chunk_pages(pages: list[str], size: int, overlap: int) -> list[Chunk]:
    chunks: list[Chunk] = []
    for page_no, text in enumerate(pages, start=1):
        for piece in _split(text, size, overlap):
            chunks.append(Chunk(text=piece, page=page_no, index=len(chunks)))
    return chunks
