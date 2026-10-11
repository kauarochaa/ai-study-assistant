import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from src.ai_study_assistant.document_management import delete_document
from src.ai_study_assistant.history import History

ROOT = Path(__file__).resolve().parents[1]


class DeleteDocumentsTests(unittest.TestCase):
    def setUp(self):
        base = ROOT / "data" / "test_runs"
        base.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=base)
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.material = self.directory / "cloud.txt"
        self.material.write_text("Cloud é computação em nuvem.", encoding="utf-8")

    def test_deletes_selected_file_and_rejects_paths_and_other_formats(self):
        protected = self.directory / ".env"
        protected.write_text("test-only", encoding="utf-8")
        for name in ("../cloud.txt", "..\\cloud.txt", str(self.material), ".env"):
            with self.assertRaises(ValueError):
                delete_document(self.directory, name)
        self.assertTrue(self.material.exists())
        self.assertTrue(protected.exists())
        delete_document(self.directory, "cloud.txt")
        self.assertFalse(self.material.exists())
        with self.assertRaises(ValueError):
            delete_document(self.directory, "cloud.txt")

    def test_interface_requires_confirmation_and_updates_document_list(self):
        # Redirect only the app document directory to disposable test files.
        real_iterdir = Path.iterdir
        def documents_iterdir(path):
            return real_iterdir(self.directory if path == ROOT / "documents" else path)
        isolated = History(self.directory / "history.sqlite3")
        with patch.object(Path, "iterdir", documents_iterdir), \
             patch("src.ai_study_assistant.history.History", return_value=isolated), \
             patch("src.ai_study_assistant.semantic_search.clear_study_index"), \
             patch("src.ai_study_assistant.document_management.delete_document", side_effect=lambda directory, name: delete_document(self.directory, name)):
            app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
            app.multiselect[0].set_value(["cloud.txt"])
            button = next(b for b in app.button if b.label == "Excluir selecionados")
            button.click().run()
            self.assertTrue(self.material.exists())
            self.assertTrue(app.warning)
            app.checkbox[0].check()
            next(b for b in app.button if b.label == "Excluir selecionados").click().run()
            self.assertFalse(app.exception)
            self.assertFalse(self.material.exists())
            self.assertTrue(app.chat_input[0].disabled)
            self.assertFalse(app.multiselect)
            self.assertEqual(app.success[0].value, "Excluído: cloud.txt")
