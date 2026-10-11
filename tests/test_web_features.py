import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from src.ai_study_assistant.history import History
from src.ai_study_assistant.uploads import save_upload
from src.ai_study_assistant.documents import DocumentChunk
from src.ai_study_assistant.search import SearchResult
from src.ai_study_assistant.retrieval import retrieve
from src.ai_study_assistant.answers import AnswerError, GroundedAnswer

ROOT = Path(__file__).resolve().parents[1]


class WebFeaturesTests(unittest.TestCase):
    def setUp(self):
        base = ROOT / "data" / "test_runs"
        base.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=base)
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.material = self.directory / "cloud.txt"
        self.material.write_text(
            "Cloud é computação em nuvem. SaaS é software pronto para uso pela internet. "
            "IaaS oferece infraestrutura e PaaS oferece uma plataforma para aplicações.",
            encoding="utf-8",
        )

    def test_upload_validates_content_and_contains_paths(self):
        uploads_directory = self.directory / "uploads"
        saved = save_upload(uploads_directory, "../../CON.txt", "Cloud é computação em nuvem.".encode())
        self.assertEqual(saved.parent, uploads_directory)
        self.assertTrue(saved.name.startswith("material_"))
        self.assertEqual(save_upload(uploads_directory, "../../CON.txt", saved.read_bytes()), saved)
        with self.assertRaises(ValueError):
            save_upload(uploads_directory, "empty.txt", b" ")
        with self.assertRaises(ValueError):
            save_upload(uploads_directory, "broken.pdf", b"not a PDF")
        self.assertEqual(len(list(uploads_directory.iterdir())), 1)

    def test_history_persists_sources_and_order(self):
        path = self.directory / "history.sqlite3"
        history = History(path)
        history.add("primeira", "resposta", [{"source": "a.pdf", "page": 2}], "search")
        history.add("segunda", "outra", [], "openai")
        rows = History(path).recent()
        self.assertEqual([row["question"] for row in rows], ["primeira", "segunda"])
        self.assertEqual(rows[0]["sources"][0]["page"], 2)
        self.assertEqual(History(path).recent(1)[0]["question"], "segunda")

    def test_retrieval_completes_neighboring_context_and_keeps_sources(self):
        chunks = [DocumentChunk("a.pdf", 1, i, text) for i, text in enumerate([
            "IaaS é infraestrutura.", "PaaS é plataforma.", "SaaS é software."])]
        results = retrieve("PaaS", chunks, [SearchResult(chunks[1], 0.9)])
        self.assertEqual(results[0].chunk, chunks[1])
        self.assertEqual({result.chunk for result in results}, set(chunks))
        self.assertEqual(len(results), 3)

    def test_retrieval_rejects_weak_unrelated_semantic_matches(self):
        chunks = [
            DocumentChunk("cloud.txt", None, 0, "IaaS oferece infraestrutura em nuvem."),
            DocumentChunk("cloud.txt", None, 1, "SaaS é software disponível pela internet."),
        ]
        weak_matches = [SearchResult(chunks[0], 0.20), SearchResult(chunks[1], 0.10)]
        self.assertEqual(retrieve("Receita de bolo de chocolate", chunks, weak_matches), [])

    def test_interface_search_and_reload_without_api(self):
        isolated = History(self.directory / "web.sqlite3")
        with patch("src.ai_study_assistant.history.History", return_value=isolated), \
             patch("src.ai_study_assistant.library.list_documents", return_value=[self.material]):
            app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
            self.assertFalse(app.exception)
            app.selectbox[0].select("Por palavras").run()
            app.chat_input[0].set_value("O que é SaaS?").run()
            self.assertFalse(app.exception)
            self.assertEqual(len(isolated.recent()), 1)
            self.assertTrue(isolated.recent()[0]["sources"])
            app.run()
            self.assertFalse(app.exception)
            self.assertEqual(len(app.chat_message), 2)

    def test_interface_openai_response_and_quota_error(self):
        isolated = History(self.directory / "api.sqlite3")
        with patch("src.ai_study_assistant.history.History", return_value=isolated), \
             patch("src.ai_study_assistant.library.list_documents", return_value=[self.material]), \
             patch("src.ai_study_assistant.answers.AnswerGenerator") as factory, \
             patch.dict("os.environ", {"OPENAI_API_KEY": "test-only"}):
            factory.return_value.generate.side_effect = lambda question, results: GroundedAnswer("SaaS é software pronto para uso.", [results[0].chunk])
            app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
            app.selectbox[0].select("Por palavras").run()
            app.radio[0].set_value("Resposta com OpenAI").run()
            app.chat_input[0].set_value("O que é SaaS?").run()
            self.assertFalse(app.exception)
            self.assertEqual(isolated.recent()[0]["answer"], "SaaS é software pronto para uso.")
            self.assertEqual(len(isolated.recent()[0]["sources"]), 1)
            factory.return_value.close.assert_called_once()
            factory.return_value.generate.side_effect = AnswerError("Sem cota disponível.")
            app.chat_input[0].set_value("O que é SaaS?").run()
            self.assertFalse(app.exception)
            self.assertEqual(app.error[0].value, "Sem cota disponível.")
            self.assertEqual(len(isolated.recent()), 1)
            self.assertTrue(app.expander)


if __name__ == "__main__":
    unittest.main()
