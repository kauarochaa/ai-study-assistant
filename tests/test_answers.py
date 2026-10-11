import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import httpx2
from openai import APIConnectionError, RateLimitError

from src.ai_study_assistant.answers import ABSTAIN, AnswerError, AnswerGenerator
from src.ai_study_assistant.documents import DocumentChunk
from src.ai_study_assistant.search import SearchResult


class AnswerTests(unittest.TestCase):
    def setUp(self):
        self.client_patch = patch("src.ai_study_assistant.answers.OpenAI")
        self.client = self.client_patch.start().return_value
        self.addCleanup(self.client_patch.stop)
        self.generator = AnswerGenerator("local-test-placeholder")
        self.addCleanup(self.generator.close)
        self.results = [SearchResult(DocumentChunk("cloud.pdf", 2, 0, "Pagamento conforme o uso."), 0.7)]

    def response(self, data):
        self.client.responses.create.return_value = SimpleNamespace(status="completed", output_text=json.dumps(data))

    def test_retrieved_text_sent_and_real_source_returned(self):
        self.response({"answer": "Você paga conforme o uso.", "supported": True, "citations": [1, 1]})
        answer = self.generator.generate("Como pagar?", self.results)
        self.assertEqual(answer.sources, [self.results[0].chunk])
        request = self.client.responses.create.call_args.kwargs
        self.assertFalse(request["store"])
        self.assertIn(self.results[0].chunk.text, request["input"])
        self.assertNotIn("local-test-placeholder", request["input"])

    def test_unsupported_question_does_not_display_fabricated_answer(self):
        self.response({"answer": "Texto sem apoio.", "supported": False, "citations": []})
        self.assertEqual(self.generator.generate("Outra pergunta", self.results).text, ABSTAIN)

    def test_invalid_source_and_incomplete_response_rejected(self):
        self.response({"answer": "Resposta", "supported": True, "citations": [99]})
        with self.assertRaises(AnswerError):
            self.generator.generate("Pergunta", self.results)
        self.client.responses.create.return_value.status = "incomplete"
        with self.assertRaises(AnswerError):
            self.generator.generate("Pergunta", self.results)

    def test_no_context_makes_no_api_call_and_connection_failure_is_readable(self):
        self.assertEqual(self.generator.generate("Pergunta", []).sources, [])
        self.client.responses.create.assert_not_called()
        self.client.responses.create.side_effect = APIConnectionError(request=SimpleNamespace())
        with self.assertRaisesRegex(AnswerError, "conectar"):
            self.generator.generate("Pergunta", self.results)

    def test_quota_and_request_rate_errors_have_distinct_messages(self):
        response = httpx2.Response(429, request=httpx2.Request("POST", "https://api.openai.com/v1/responses"))
        for code, expected in [("insufficient_quota", "cota"), ("credit_balance_exhausted", "créditos"),
                               ("rate_limit_exceeded", "Aguarde"), ("project_spend_limit_exceeded", "gastos")]:
            with self.subTest(code=code):
                self.client.responses.create.side_effect = RateLimitError(
                    "Sensitive raw error text", response=response, body={"code": code}
                )
                with self.assertRaisesRegex(AnswerError, expected) as raised:
                    self.generator.generate("Pergunta", self.results)
                self.assertNotIn("Sensitive", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
