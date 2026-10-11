import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from src.ai_study_assistant.documents import DocumentChunk
from src.ai_study_assistant.semantic_search import SemanticSearch, clear_study_index


class ExampleEncoder:
    """Fixed vectors isolate storage behavior from model downloads."""

    def embed(self, texts):
        for text in texts:
            yield np.array([1.0, 0.0] if "custo" in text else [0.0, 1.0])


class SemanticStorageTests(unittest.TestCase):
    def setUp(self):
        test_dir = Path(__file__).resolve().parents[1] / "data" / "test_runs"
        test_dir.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=test_dir)
        self.data_dir = Path(self.temp.name)
        self.encoder_patch = patch(
            "src.ai_study_assistant.semantic_search.TextEmbedding", return_value=ExampleEncoder()
        )
        self.encoder_patch.start()
        self.addCleanup(self.encoder_patch.stop)
        self.addCleanup(self.temp.cleanup)
        self.chunks = [
            DocumentChunk("cloud.pdf", 2, 0, "custo conforme o uso"),
            DocumentChunk("cloud.pdf", 3, 0, "armazenamento de arquivos"),
        ]

    def test_search_keeps_source_and_page_and_handles_blank_question(self):
        search = SemanticSearch(self.chunks, self.data_dir)
        try:
            result = search.search("custo", limit=1)[0]
            self.assertEqual(result.chunk, self.chunks[0])
            self.assertEqual(search.search("  "), [])
            self.assertEqual(search.search("custo", limit=0), [])
        finally:
            search.close()

    def test_restart_reuses_index_without_duplicate_points(self):
        first = SemanticSearch(self.chunks, self.data_dir)
        self.assertFalse(first.reused_index)
        first.close()
        second = SemanticSearch(self.chunks, self.data_dir)
        try:
            self.assertTrue(second.reused_index)
            self.assertEqual(len(second.search("custo", limit=10)), 2)
        finally:
            second.close()

    def test_removed_or_edited_document_does_not_leak_into_current_results(self):
        first = SemanticSearch(self.chunks, self.data_dir)
        first.close()
        changed = [DocumentChunk("novo.pdf", 1, 0, "custo atualizado")]
        second = SemanticSearch(changed, self.data_dir)
        try:
            self.assertFalse(second.reused_index)
            self.assertEqual([result.chunk for result in second.search("custo")], changed)
            self.assertEqual([collection.name for collection in second.client.get_collections().collections], [second.collection])
        finally:
            second.close()

    def test_clear_index_removes_derived_text_and_can_be_rebuilt(self):
        first = SemanticSearch(self.chunks, self.data_dir)
        first.close()
        clear_study_index(self.data_dir)
        rebuilt = SemanticSearch(self.chunks, self.data_dir)
        try:
            self.assertFalse(rebuilt.reused_index)
            self.assertEqual(len(rebuilt.search("custo", limit=10)), 2)
        finally:
            rebuilt.close()


if __name__ == "__main__":
    unittest.main()
