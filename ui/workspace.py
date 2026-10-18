"""Main workspace: top bar, welcome screen, conversation and input."""

from __future__ import annotations

import streamlit as st

from core import rag
from core.chats import ChatStore
from core.llm import OllamaError
from core.pdf_loader import PDFError
from core.store import DocumentStore

from . import components as ui
from . import state

SUGGESTIONS = [
    (":material/summarize:", "Summarize the key points", "Summarize the key points of this document."),
    (":material/lightbulb:", "What are the main conclusions?", "What are the main findings or conclusions?"),
    (":material/event:", "List important dates and numbers", "List the important dates, figures and deadlines mentioned."),
    (":material/school:", "Explain the core ideas simply", "Explain the core concepts in simple terms."),
]


def render(store: DocumentStore, chats: ChatStore, ollama: dict) -> None:
    chat = chats.get(st.session_state.active_chat_id)
    docs = store.documents()
    _topbar(store, chats, chat, len(docs))

    for kind, message in state.pop_flashes():
        if kind == "success":
            st.toast(message, icon=":material/check_circle:")
        else:
            ui.callout(kind, message)

    if st.session_state.pending_uploads:
        _index_uploads(store)

    body = st.container()
    with st.container(key="composer"):
        typed = st.chat_input(
            "Ask anything about your documents…" if docs else "Upload a PDF to start asking questions",
            disabled=not docs,
            key="composer-input",
        )
    question = typed or st.session_state.pending_question
    st.session_state.pending_question = None

    with body:
        if chat or question:
            _conversation(store, chats, chat, question)
        else:
            _welcome(docs, ollama)


# ---- top bar ----------------------------------------------------------------
def _scope_text(store: DocumentStore, n_docs: int) -> str:
    doc = store.get(st.session_state.selected_doc_id)
    if st.session_state.scope_to_doc and doc:
        return f"Answering from {doc.filename} only"
    if n_docs == 0:
        return "No documents indexed yet"
    return f"Answering from all {n_docs} document{'s' if n_docs != 1 else ''}"


def _topbar(store: DocumentStore, chats: ChatStore, chat: dict | None, n_docs: int) -> None:
    with st.container(key="topbar", horizontal=True, vertical_alignment="center"):
        ui.topbar_title(chat["title"] if chat else "New chat", _scope_text(store, n_docs))
        if chat:
            with st.popover("", icon=":material/more_horiz:", help="Chat options"):
                if st.button("Delete this chat", icon=":material/delete:", type="tertiary", key="delete-chat"):
                    chats.delete(chat["id"])
                    state.new_chat()
                    st.rerun()
        showing = st.session_state.show_panel
        st.button(
            "",
            icon=":material/right_panel_close:" if showing else ":material/right_panel_open:",
            help="Hide document panel" if showing else "Show document panel",
            type="tertiary",
            key="toggle-panel",
            on_click=state.toggle_panel,
        )


# ---- uploads ----------------------------------------------------------------
def _index_uploads(store: DocumentStore) -> None:
    uploads, st.session_state.pending_uploads = st.session_state.pending_uploads, []
    for name, data in uploads:
        with st.status(f"Indexing {name}", expanded=True) as status:
            bar = st.progress(0.0, text="Starting")
            try:
                doc, created = store.add_pdf(name, data, lambda f, msg: bar.progress(f, text=msg))
            except (PDFError, OllamaError) as exc:
                status.update(label=f"Couldn't index {name}", state="error", expanded=False)
                state.flash("error", f"{name}: {exc}")
                continue
            status.update(label=f"{name} is ready", state="complete", expanded=False)
        state.select_doc(doc.id)
        if created:
            state.flash("success", f"{name} indexed · {doc.pages} pages, {doc.chunks} passages")
        else:
            state.flash("info", f"{name} is already in your library.")
    st.rerun()


# ---- welcome ----------------------------------------------------------------
def _welcome(docs: list, ollama: dict) -> None:
    ui.hero()
    if not ollama["online"]:
        ui.callout(
            "warning",
            "Start Ollama with `ollama serve` to index documents and get answers.",
            title="Ollama isn't running.",
        )

    with st.container(key="dropzone"):
        files = st.file_uploader(
            "Upload PDF documents",
            type=["pdf"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key=f"main-upload-{st.session_state.uploader_nonce}",
        )
        if files:
            state.queue_uploads(files)
            st.rerun()

    if docs:
        ui.callout(
            "success",
            f"{len(docs)} document{'s are' if len(docs) != 1 else ' is'} indexed and ready for questions.",
        )

    ui.subheading("Try asking")
    with st.container(key="suggestions"):
        for row in (SUGGESTIONS[:2], SUGGESTIONS[2:]):
            for col, (icon, label, prompt) in zip(st.columns(2), row):
                with col:
                    st.button(
                        label,
                        icon=icon,
                        width="stretch",
                        disabled=not docs,
                        key=f"suggest-{label}",
                        on_click=state.ask,
                        args=(prompt,),
                    )


# ---- conversation -----------------------------------------------------------
def _message(i: int, msg: dict) -> None:
    role = msg["role"]
    with st.container(key=f"msg-{'user' if role == 'user' else 'ai'}-{i}"):
        ui.message_header(role)
        st.markdown(msg["content"])
        if role == "assistant" and msg.get("sources"):
            ui.source_chips(msg["sources"])
            if st.session_state.focused_msg != i:
                st.button(
                    "View passages",
                    icon=":material/menu_book:",
                    type="tertiary",
                    key=f"focus-{i}",
                    on_click=state.focus_message,
                    args=(i,),
                )


def _conversation(store: DocumentStore, chats: ChatStore, chat: dict | None, question: str | None) -> None:
    messages = chat["messages"] if chat else []
    for i, msg in enumerate(messages):
        _message(i, msg)
    if question:
        _answer(store, chats, chat, question)


def _answer(store: DocumentStore, chats: ChatStore, chat: dict | None, question: str) -> None:
    # Nothing is saved until the answer succeeds, so failed attempts don't
    # leave unanswered questions in the history.
    history = list(chat["messages"]) if chat else []
    user_msg = {"role": "user", "content": question}
    _message(len(history), user_msg)

    with st.container(key="msg-ai-live"):
        ui.message_header("assistant")
        placeholder = st.empty()
        ui.render_html(ui.thinking("Searching your documents"), placeholder)
        scope = st.session_state.selected_doc_id if st.session_state.scope_to_doc else None
        try:
            passages = store.search(question, st.session_state.top_k, scope)
            if not passages:
                placeholder.empty()
                ui.callout("info", "No matching passages were found. Try rephrasing the question.")
                return
            ui.render_html(ui.thinking(), placeholder)

            def stream():
                first = True
                for token in rag.answer_stream(
                    question, passages, history,
                    st.session_state.chat_model, st.session_state.temperature,
                ):
                    if first:
                        placeholder.empty()
                        first = False
                    yield token

            answer = st.write_stream(stream())
        except OllamaError as exc:
            placeholder.empty()
            ui.callout("error", str(exc), title="Couldn't generate an answer.")
            return

    sources = [p.to_dict() for p in passages]
    cited = rag.cited_numbers(answer, sources)
    shown = [s for s in sources if s["n"] in cited] or sources
    if chat is None:
        chat = chats.create(question)
        st.session_state.active_chat_id = chat["id"]
    chats.append(chat["id"], user_msg)
    chats.append(chat["id"], {"role": "assistant", "content": answer, "sources": shown})
    st.session_state.focused_msg = len(history) + 1
    st.rerun()
