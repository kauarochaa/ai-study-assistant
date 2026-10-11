import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

from src.ai_study_assistant.documents import SUPPORTED_SUFFIXES
from src.ai_study_assistant.search import KeywordSearch
from src.ai_study_assistant.library import list_documents, load_chunks, StudySearch
from src.ai_study_assistant.history import History
from dataclasses import asdict


PROJECT_ROOT = Path(__file__).resolve().parent
DOCUMENTS_DIR = PROJECT_ROOT / "documents"


def main() -> None:
    parser = argparse.ArgumentParser(description="Busca nos seus materiais de estudo.")
    parser.add_argument("--keywords", action="store_true", help="Usar a busca anterior por palavras.")
    parser.add_argument("--search-only", action="store_true", help="Mostrar trechos sem chamar a API de IA.")
    args = parser.parse_args()
    load_dotenv(PROJECT_ROOT / ".env", override=False)
    DOCUMENTS_DIR.mkdir(exist_ok=True)
    files = list_documents(DOCUMENTS_DIR)

    if not files:
        extensions = ", ".join(sorted(SUPPORTED_SUFFIXES))
        print(f"Coloque arquivos {extensions} na pasta documents/ para começar.")
        return

    print("AI Study Assistant - leitura de documentos\n")
    all_chunks, errors = load_chunks(files)
    for error in errors:
        print(error)
    for path in files:
        print(f"{path.name}: {sum(chunk.source == path.name for chunk in all_chunks)} trecho(s)")

    print(f"\nTotal preparado para busca: {len(all_chunks)} trecho(s).")
    if not all_chunks:
        print("Não há texto para pesquisar. Use PDFs com texto selecionável ou arquivos de texto.")
        return

    if args.keywords:
        search = KeywordSearch(all_chunks)
        print("\nBusca por palavras ativada.")
    else:
        try:
            from src.ai_study_assistant.semantic_search import SemanticSearch
            print("\nPreparando busca semântica. Na primeira execução, o modelo será baixado.")
            search = SemanticSearch(all_chunks, PROJECT_ROOT / "data")
        except ImportError:
            print("Instale as dependências: .\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt")
            raise SystemExit(1)
        except Exception:
            print("Busca semântica indisponível; usando busca por palavras nesta execução.")
            search = KeywordSearch(all_chunks)
            args.keywords = True
        if not args.keywords:
            print("Índice local reutilizado." if search.reused_index else "Embeddings criados e salvos no banco local.")
        print("Os resultados são os trechos mais próximos da pergunta; confira se respondem ao assunto.")

    print("\nDigite uma pergunta. Digite sair para encerrar.")
    generator = None
    try:
        key = os.getenv("OPENAI_API_KEY", "").strip()
        if key and not args.search_only:
            from src.ai_study_assistant.answers import AnswerGenerator
            generator = AnswerGenerator(key, os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip() or "gpt-4.1-mini")
            print("Respostas com IA ativadas: pergunta e trechos encontrados serão enviados à OpenAI.")
        elif not args.search_only:
            print("Configure OPENAI_API_KEY no .env para gerar respostas. Por enquanto, mostrarei os trechos.")
        query_search = search if args.keywords else StudySearch(all_chunks, search)
        ask_questions(query_search, generator, History(PROJECT_ROOT / "data" / "history.sqlite3"))
    finally:
        if generator is not None:
            generator.close()
        if not args.keywords:
            search.close()


def ask_questions(search, generator=None, history=None) -> None:
    while True:
        try:
            question = input("\nPergunta: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBusca encerrada.")
            break
        if question.casefold() == "sair":
            break
        if not question:
            continue

        try:
            results = search.search(question)
        except Exception as error:
            print(f"Não foi possível concluir a busca: {error}")
            continue
        if not results:
            print("Nenhum trecho contém palavras relevantes dessa pergunta. Tente outros termos.")
            continue

        if generator is not None:
            from src.ai_study_assistant.answers import AnswerError
            print("\nGerando resposta...")
            try:
                answer = generator.generate(question, results)
            except AnswerError as error:
                print(f"Não foi possível gerar a resposta: {error}")
                continue
            print(f"\nResposta: {answer.text}")
            if history is not None:
                history.add(question, answer.text, [asdict(chunk) for chunk in answer.sources], "Resposta com OpenAI")
            if answer.sources:
                print("\nFontes consultadas:")
                for chunk in answer.sources:
                    location = f", página {chunk.page}" if chunk.page is not None else ""
                    print(f"- {chunk.source}{location}, trecho {chunk.index + 1}")
            continue

        print("\nTrechos encontrados:")
        if history is not None:
            history.add(question, "Trechos encontrados. Confira se respondem à pergunta.",
                        [asdict(result.chunk) for result in results], "Somente trechos (sem custo de API)")
        for number, result in enumerate(results, start=1):
            chunk = result.chunk
            location = f", página {chunk.page}" if chunk.page is not None else ""
            print(f"\n{number}. Fonte: {chunk.source}{location}, trecho {chunk.index + 1}")
            print(chunk.text)


if __name__ == "__main__":
    main()
