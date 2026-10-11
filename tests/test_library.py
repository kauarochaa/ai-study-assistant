import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from src.ai_study_assistant.library import list_documents, load_chunks, clear_document_cache, StudySearch
from src.ai_study_assistant.documents import DocumentChunk
from src.ai_study_assistant.search import SearchResult

ROOT = Path(__file__).resolve().parents[1]


class LibraryTests(unittest.TestCase):
    def test_invalid_pdf_does_not_block_other_documents_and_edit_refreshes(self):
        base = ROOT / "data" / "test_runs"
        base.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as temporary:
            directory = Path(temporary)
            text = directory / "study.txt"
            text.write_text("primeiro material", encoding="utf-8")
            (directory / "broken.pdf").write_bytes(b"not a PDF")
            (directory / ".env").write_text("test-only", encoding="utf-8")
            chunks, errors = load_chunks(list_documents(directory))
            self.assertEqual(len(chunks), 1)
            self.assertEqual(len(errors), 1)
            text.write_text("segundo material atualizado", encoding="utf-8")
            updated, _ = load_chunks([text])
            self.assertIn("atualizado", updated[0].text)
        clear_document_cache()

    def test_shared_search_rejects_weak_results_without_keyword_support(self):
        chunk = DocumentChunk("cloud.txt", None, 0, "SaaS fornece software pela internet.")
        engine = unittest.mock.Mock()
        engine.search.return_value = [SearchResult(chunk, 0.1)]
        search = StudySearch([chunk], engine)
        self.assertEqual(search.search("Quem venceu a Copa?"), [])
