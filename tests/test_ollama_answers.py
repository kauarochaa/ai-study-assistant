import io
import json
import unittest
from unittest.mock import patch
from src.ai_study_assistant.ollama_answers import OllamaAnswerGenerator
from src.ai_study_assistant.answers import AnswerError, ABSTAIN
from src.ai_study_assistant.documents import DocumentChunk
from src.ai_study_assistant.search import SearchResult


class OllamaTests(unittest.TestCase):
    def test_sources_and_no_thinking(self):
        result = SearchResult(DocumentChunk('sample.txt', None, 0, 'SaaS é software pronto.'), 1)
        body = {'done': True, 'message': {'content': json.dumps({'answer': 'Software pronto.', 'supported': True, 'citations': [1]})}}
        with patch('src.ai_study_assistant.ollama_answers.urlopen', return_value=io.BytesIO(json.dumps(body).encode())) as request:
            answer = OllamaAnswerGenerator().generate('SaaS?', [result])
            self.assertEqual(answer.sources, [result.chunk])
            self.assertFalse(json.loads(request.call_args.args[0].data)['think'])

    def test_no_context_no_call(self):
        with patch('src.ai_study_assistant.ollama_answers.urlopen') as request:
            self.assertEqual(OllamaAnswerGenerator().generate('pergunta', []).text, ABSTAIN)
            request.assert_not_called()

    def test_rejects_invalid_source(self):
        result = SearchResult(DocumentChunk('a.txt', None, 0, 'texto'), 1)
        body = {'done': True, 'message': {'content': json.dumps({'answer': 'texto', 'supported': True, 'citations': [99]})}}
        with patch('src.ai_study_assistant.ollama_answers.urlopen', return_value=io.BytesIO(json.dumps(body).encode())):
            with self.assertRaises(AnswerError):
                OllamaAnswerGenerator().generate('pergunta', [result])
