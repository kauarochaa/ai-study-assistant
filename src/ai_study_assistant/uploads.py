"""Validate uploads before publishing them to the document folder."""
import hashlib
import re
import tempfile
from pathlib import Path
from .documents import SUPPORTED_SUFFIXES, read_document


def save_upload(directory: Path, name: str, content: bytes) -> Path:
    suffix = Path(name).suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise ValueError("Use PDF, TXT ou Markdown.")
    if not content or len(content) > 20 * 1024 * 1024:
        raise ValueError("O arquivo deve ter conteúdo e no máximo 20 MB.")
    directory.mkdir(parents=True, exist_ok=True)
    # A fixed prefix avoids Windows reserved names; no supplied path is trusted.
    stem = re.sub(r"[^\w-]+", "_", name.replace("\\", "/").split("/")[-1].rsplit(".", 1)[0])[:60]
    destination = directory / f"material_{stem}_{hashlib.sha256(content).hexdigest()[:12]}{suffix}"
    with tempfile.TemporaryDirectory(dir=directory) as temporary:
        candidate = Path(temporary) / destination.name
        candidate.write_bytes(content)
        try:
            pages = read_document(candidate)
        except Exception:
            raise ValueError("Não foi possível ler este arquivo. Use texto UTF-8 ou PDF com texto selecionável.") from None
        if not any(page.text.strip() for page in pages):
            raise ValueError("O arquivo não contém texto legível. PDFs digitalizados precisam de OCR.")
        if not destination.exists():
            candidate.replace(destination)
    return destination
