"""Local, single-user study interface."""
import logging
import os
import threading
from datetime import datetime
from dataclasses import asdict
from logging.handlers import RotatingFileHandler
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from fastembed import TextEmbedding
from src.ai_study_assistant.answers import AnswerError, AnswerGenerator
from src.ai_study_assistant.history import History
from src.ai_study_assistant.search import KeywordSearch
from src.ai_study_assistant.semantic_search import SemanticSearch, MODEL_NAME, clear_study_index
from src.ai_study_assistant.uploads import save_upload
from src.ai_study_assistant.retrieval import retrieve
from src.ai_study_assistant.document_management import delete_document
from src.ai_study_assistant.library import list_documents, load_chunks, clear_document_cache

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DOCUMENTS = ROOT / "documents"
DATA.mkdir(exist_ok=True)
DOCUMENTS.mkdir(exist_ok=True)
load_dotenv(ROOT / ".env")
st.set_page_config(page_title="AI Study Assistant", page_icon="📚", layout="wide")


@st.cache_resource
def resources():
    logger = logging.getLogger("study.web")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = RotatingFileHandler(DATA / "app.log", maxBytes=1_000_000, backupCount=2, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(handler)
    return threading.Lock(), logger


@st.cache_resource
def embedding_model():
    return TextEmbedding(model_name=MODEL_NAME, cache_dir=str(DATA / "models"), threads=2)


def show_sources(sources):
    for source in sources:
        label = f'{source["source"]} • página {source["page"] or "—"} • trecho {source["index"] + 1}'
        with st.expander(label):
            st.text(source["text"])


lock, logger = resources()
history = History(DATA / "history.sqlite3")
st.title("📚 AI Study Assistant")
st.write("Estude seus materiais, encontre explicações e confira as fontes.")
with st.sidebar:
    st.header("Seus materiais")
    if st.button("Adicionar material de exemplo"):
        with lock:
            saved = save_upload(DOCUMENTS, "Cloud_Demonstracao.md", (ROOT / "examples" / "cloud.md").read_bytes())
        st.success("Material de exemplo sobre Cloud adicionado.")
    uploads = st.file_uploader("Adicionar documentos", type=["pdf", "txt", "md"], accept_multiple_files=True, max_upload_size=20)
    if st.button("Salvar documentos", disabled=not uploads):
        for upload in uploads:
            try:
                with lock:
                    saved = save_upload(DOCUMENTS, upload.name, upload.getvalue())
                st.success(f"Salvo: {saved.name}")
            except ValueError as error:
                st.error(str(error))
            except OSError:
                st.error("Não foi possível salvar o arquivo. Confira o espaço e as permissões da pasta.")
    with st.expander("Excluir documentos salvos"):
        st.caption("Apaga os arquivos da pasta documents do projeto. As consultas antigas continuam no histórico com seus trechos.")
        for kind, message in st.session_state.pop("deletion_messages", []):
            getattr(st, kind)(message)
        available = [p.name for p in list_documents(DOCUMENTS)]
        if available:
            version = st.session_state.get("delete_form_version", 0)
            with st.form(f"delete_documents_{version}"):
                selected = st.multiselect("Documentos para excluir", available)
                confirmed = st.checkbox("Confirmo a exclusão permanente dos arquivos selecionados")
                submitted = st.form_submit_button("Excluir selecionados")
            if submitted:
                if not selected:
                    st.warning("Selecione pelo menos um documento.")
                elif not confirmed:
                    st.warning("Marque a confirmação antes de excluir.")
                else:
                    messages = []
                    with lock:
                        for name in selected:
                            try:
                                delete_document(DOCUMENTS, name)
                                clear_document_cache()
                                messages.append(("success", f"Excluído: {name}"))
                            except (ValueError, OSError):
                                messages.append(("error", f"Não foi possível excluir: {name}"))
                        if any(kind == "success" for kind, _ in messages):
                            for index_directory in (DATA / "web", DATA):
                                try:
                                    clear_study_index(index_directory)
                                except Exception:
                                    messages.append(("warning", "Arquivo excluído; um índice está em uso. Encerre outras execuções e consulte novamente para atualizá-lo."))
                    logger.info("document_deletion requested=%d completed=%d", len(selected), sum(kind == "success" for kind, _ in messages))
                    st.session_state["deletion_messages"] = messages
                    st.session_state["delete_form_version"] = version + 1
                    st.rerun()
        else:
            st.caption("Nenhum documento salvo para excluir.")
    mode = st.radio("Como consultar", ["Somente trechos (sem custo de API)", "Resposta com OpenAI"])
    strategy = st.selectbox("Busca", ["Semântica", "Por palavras"])
    st.caption("Com OpenAI, sua pergunta e os trechos encontrados são enviados à API. É necessário saldo na conta da API.")
    st.caption("Histórico e documentos ficam neste computador. Aplicativo pessoal, sem contas de usuários.")

files = list_documents(DOCUMENTS)
chunks, document_errors = load_chunks(files)
for error in document_errors:
    st.warning(error)
st.caption(f"{len(files)} documento(s) • {len(chunks)} trecho(s) disponíveis")
with st.expander("Ver documentos disponíveis"):
    for path in files:
        st.text(path.name)

if not chunks:
    st.info("Adicione um PDF com texto selecionável, TXT ou Markdown para começar.")
question = st.chat_input("Pergunte sobre seus documentos", max_chars=2000, disabled=not chunks)
if question:
    results = []
    try:
        with st.spinner("Buscando nos materiais…"):
            if strategy == "Semântica":
                try:
                    with lock:
                        search = SemanticSearch(chunks, DATA / "web", model=embedding_model())
                        try:
                            results = retrieve(question, chunks, search.search(question, limit=4))
                        finally:
                            search.close()
                except Exception as error:
                    logger.warning("semantic_search_unavailable error_type=%s", type(error).__name__)
                    st.warning("A busca semântica está indisponível. Nesta consulta usaremos a busca por palavras.")
                    results = KeywordSearch(chunks).search(question)
            else:
                results = KeywordSearch(chunks).search(question)
        sources = [asdict(result.chunk) for result in results]
        if not results:
            text = "Não encontrei trechos para essa pergunta. Tente reformular."
        elif mode == "Resposta com OpenAI":
            key = os.getenv("OPENAI_API_KEY", "")
            if not key:
                raise AnswerError("Configure OPENAI_API_KEY no arquivo .env antes de usar a IA.")
            with st.spinner("Gerando resposta…"):
                generator = AnswerGenerator(key, os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip() or "gpt-4.1-mini")
                try:
                    answer = generator.generate(question, results)
                finally:
                    generator.close()
            text, sources = answer.text, [asdict(source) for source in answer.sources]
        else:
            text = "Trechos encontrados abaixo. Confira se respondem à pergunta; este modo não gera uma explicação com IA."
        history.add(question, text, sources, mode)
        logger.info("consultation_completed mode=%s sources=%d", "openai" if mode == "Resposta com OpenAI" else "search", len(sources))
    except AnswerError as error:
        st.error(str(error))
        st.info("Você pode continuar com o modo Somente trechos enquanto resolve o saldo da API.")
        show_sources([asdict(result.chunk) for result in results])
        logger.warning("generation_failed")
    except Exception as error:
        st.error("Não foi possível concluir a consulta. Tente a busca Por palavras. Se continuar, reinicie o aplicativo.")
        logger.warning("consultation_failed error_type=%s", type(error).__name__)

st.subheader("Histórico recente")
st.caption("As últimas 20 consultas são exibidas, incluindo suas fontes da época da consulta.")
for entry in history.recent():
    with st.chat_message("user"):
        st.text(entry["question"])
    with st.chat_message("assistant"):
        st.write(entry["answer"])
        date_label = datetime.fromisoformat(entry["created"]).astimezone().strftime("%d/%m/%Y %H:%M")
        st.caption(f'{date_label} • {entry["mode"]}')
        show_sources(entry["sources"])
if not history.recent():
    st.info("Comece com uma pergunta, como: Qual a diferença entre IaaS, PaaS e SaaS?")
