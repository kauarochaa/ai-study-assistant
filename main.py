from pathlib import Path

from src.ai_study_assistant.documents import SUPPORTED_SUFFIXES, chunk_document, read_document
from src.ai_study_assistant.search import KeywordSearch


PROJECT_ROOT = Path(__file__).resolve().parent
DOCUMENTS_DIR = PROJECT_ROOT / "documents"


def main() -> None:
    DOCUMENTS_DIR.mkdir(exist_ok=True)
    files = sorted(
        path
        for path in DOCUMENTS_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
    )

    if not files:
        extensions = ", ".join(sorted(SUPPORTED_SUFFIXES))
        print(f"Coloque arquivos {extensions} na pasta documents/ para começar.")
        return

    all_chunks = []
    print("AI Study Assistant - leitura de documentos\n")

    for path in files:
        try:
            pages = read_document(path)
            chunks = [chunk for page in pages for chunk in chunk_document(page)]
        except (OSError, ValueError) as error:
            print(f"Não foi possível ler {path.name}: {error}")
            continue

        all_chunks.extend(chunks)
        print(f"{path.name}: {len(pages)} página(s)/seção(ões), {len(chunks)} trecho(s)")
        if chunks:
            preview = chunks[0].text.replace("\n", " ")
            print(f"  Prévia: {preview[:180]}{'...' if len(preview) > 180 else ''}")

    print(f"\nTotal preparado para busca: {len(all_chunks)} trecho(s).")
    if not all_chunks:
        print("Não há texto para pesquisar. Use PDFs com texto selecionável ou arquivos de texto.")
        return

    search = KeywordSearch(all_chunks)
    print("\nDigite uma pergunta para buscar por palavras nos documentos. Digite sair para encerrar.")
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

        results = search.search(question)
        if not results:
            print("Nenhum trecho contém palavras relevantes dessa pergunta. Tente outros termos.")
            continue

        print("\nTrechos encontrados:")
        for number, result in enumerate(results, start=1):
            chunk = result.chunk
            location = f", página {chunk.page}" if chunk.page is not None else ""
            print(f"\n{number}. Fonte: {chunk.source}{location}, trecho {chunk.index + 1}")
            print(chunk.text)


if __name__ == "__main__":
    main()
