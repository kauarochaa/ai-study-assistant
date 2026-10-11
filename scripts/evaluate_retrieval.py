"""Run a small reproducible search check using the actual local model, no API."""
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from fastembed import TextEmbedding
from src.ai_study_assistant.library import load_chunks
from src.ai_study_assistant.retrieval import retrieve
from src.ai_study_assistant.semantic_search import SemanticSearch, MODEL_NAME

CASES = [
    ("O que é SaaS?", "software pronto"),
    ("Qual serviço do Google permite salvar arquivos?", "Cloud Storage"),
    ("Como pagar pelo que eu utilizo?", "conforme o uso"),
    ("O que é nuvem híbrida?", "combina"),
    ("Quais serviços de máquinas virtuais existem no Azure e Google?", ("Virtual Machines", "Compute Engine")),
    ("Qual é a capital da França?", None),
    ("Como fazer um bolo de chocolate?", None),
    ("Quem venceu a Copa de 2022?", None),
]


def main():
    chunks, errors = load_chunks([ROOT / "examples" / "cloud.md"])
    if errors:
        raise SystemExit(errors[0])
    model = TextEmbedding(model_name=MODEL_NAME, cache_dir=str(ROOT / "data" / "models"), threads=2)
    base = ROOT / "data" / "test_runs"
    base.mkdir(parents=True, exist_ok=True)
    passed = 0
    with tempfile.TemporaryDirectory(dir=base) as temporary:
        search = SemanticSearch(chunks, Path(temporary), model=model)
        try:
            for question, expected in CASES:
                results = retrieve(question, chunks, search.search(question, limit=4))
                content = " ".join(result.chunk.text for result in results)
                terms = expected if isinstance(expected, tuple) else (expected,)
                ok = not results if expected is None else all(term.casefold() in content.casefold() for term in terms)
                passed += int(ok)
                print(f'{"OK" if ok else "FALHOU"}: {question} ({len(results)} trechos)')
        finally:
            search.close()
    print(f"Resultado: {passed}/{len(CASES)} exemplos. Avalia recuperação; não avalia respostas da OpenAI.")
    return 0 if passed == len(CASES) else 1


if __name__ == "__main__":
    raise SystemExit(main())
