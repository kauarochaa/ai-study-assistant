"""Delete only ordinary supported files directly in the document folder."""
from pathlib import Path
from .documents import SUPPORTED_SUFFIXES


def delete_document(directory: Path, name: str) -> None:
    if not name or name in {".", ".."} or any(c in name for c in ("/", "\\", ":")):
        raise ValueError("Selecione um documento da lista.")
    directory = directory.resolve()
    target = directory / name
    if target.is_symlink() or target.resolve().parent != directory:
        raise ValueError("Este arquivo não pode ser excluído pelo aplicativo.")
    if target.suffix.lower() not in SUPPORTED_SUFFIXES:
        raise ValueError("Este formato não pode ser excluído pelo aplicativo.")
    if not target.is_file():
        raise ValueError("O documento não está mais disponível.")
    target.unlink()
