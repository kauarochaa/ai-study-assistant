"""Shared document loading and retrieval for the browser and terminal."""
from pathlib import Path
from functools import lru_cache
from .documents import SUPPORTED_SUFFIXES, chunk_document, read_document
from .retrieval import retrieve


def list_documents(directory: Path) -> list[Path]:
    return sorted(path for path in directory.iterdir()
                  if path.is_file() and not path.is_symlink()
                  and path.suffix.lower() in SUPPORTED_SUFFIXES)


def load_chunks(paths):
    chunks, errors = [], []
    for path in paths:
        try:
            stat = path.stat()
            current = _read_chunks(str(path), stat.st_mtime_ns, stat.st_size)
            if not current:
                errors.append(f"{path.name}: não contém texto legível; PDFs digitalizados precisam de OCR.")
            chunks.extend(current)
        except Exception:
            errors.append(f"{path.name}: não foi possível ler o arquivo; confira seu formato e conteúdo.")
    return chunks, errors


@lru_cache(maxsize=32)
def _read_chunks(path: str, modified: int, size: int):
    # File metadata invalidates the cache when material changes.
    return tuple(chunk for page in read_document(Path(path)) for chunk in chunk_document(page))


def clear_document_cache():
    _read_chunks.cache_clear()


class StudySearch:
    """Apply the same relevance filter and context expansion in both interfaces."""
    def __init__(self, chunks, engine):
        self.chunks = chunks
        self.engine = engine

    def search(self, question, limit=8):
        return retrieve(question, self.chunks, self.engine.search(question, limit=4), limit=limit)
