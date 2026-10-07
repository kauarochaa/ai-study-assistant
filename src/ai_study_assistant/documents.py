"""Read study files and split their text into chunks for later retrieval."""

from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


SUPPORTED_SUFFIXES = {".pdf", ".txt", ".md"}
CHUNK_SIZE = 1_000
CHUNK_OVERLAP = 150


@dataclass(frozen=True)
class DocumentPage:
    source: str
    page: int | None
    text: str


@dataclass(frozen=True)
class DocumentChunk:
    source: str
    page: int | None
    index: int
    text: str


def read_document(path: Path) -> list[DocumentPage]:
    """Extract text from a PDF, plain-text, or Markdown file."""
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        reader = PdfReader(str(path))
        if reader.is_encrypted:
            raise ValueError("o PDF está protegido por senha")

        pages = []
        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append(DocumentPage(path.name, page_number, text.strip()))
        return pages

    if suffix in {".txt", ".md"}:
        text = path.read_text(encoding="utf-8-sig").strip()
        return [DocumentPage(path.name, None, text)] if text else []

    raise ValueError(f"formato não suportado: {suffix or '(sem extensão)'}")


def chunk_document(
    page: DocumentPage,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[DocumentChunk]:
    """Split a page or text section into overlapping, word-aligned chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size precisa ser maior que zero")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap precisa estar entre zero e chunk_size")

    text = " ".join(page.text.split())
    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            boundary = text.rfind(" ", start, end)
            if boundary > start:
                end = boundary

        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append(
                DocumentChunk(
                    source=page.source,
                    page=page.page,
                    index=len(chunks),
                    text=chunk_text,
                )
            )

        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
        if start > 0 and text[start - 1] != " " and text[start] != " ":
            boundary = text.find(" ", start, end)
            if boundary != -1:
                start = boundary
        while start < len(text) and text[start] == " ":
            start += 1

    return chunks
