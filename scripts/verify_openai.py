"""One deliberate paid API smoke check after configuring credit."""
import os
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
from src.ai_study_assistant.library import load_chunks
from src.ai_study_assistant.search import KeywordSearch
from src.ai_study_assistant.answers import AnswerGenerator, AnswerError


def main():
    load_dotenv(ROOT / ".env")
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        print("Configure OPENAI_API_KEY no .env local antes de verificar.")
        return 1
    chunks, errors = load_chunks([ROOT / "examples" / "cloud.md"])
    if errors:
        print(errors[0])
        return 1
    question = "O que é SaaS?"
    results = KeywordSearch(chunks).search(question)
    generator = AnswerGenerator(key, os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip() or "gpt-4.1-mini")
    print("Esta verificação realiza uma chamada real à API com o material público de exemplo.")
    try:
        answer = generator.generate(question, results)
        if not answer.sources:
            print("A API respondeu, mas não forneceu uma resposta apoiada nas fontes. Confira antes de considerar validado.")
            return 1
        print(answer.text)
        for source in answer.sources:
            print(f"Fonte: {source.source}, trecho {source.index + 1}")
        print("API acessível e referências válidas. Confira manualmente se a explicação está correta.")
        return 0
    except AnswerError as error:
        print(str(error))
        return 1
    finally:
        generator.close()


if __name__ == "__main__":
    raise SystemExit(main())
