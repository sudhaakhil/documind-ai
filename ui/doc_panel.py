"""Right-hand document panel: details, summary, cited passages."""

from __future__ import annotations

import streamlit as st

from core import rag
from core.chats import ChatStore
from core.llm import OllamaError
from core.store import DocumentStore

from . import components as ui
from . import state


def _focused_sources(chats: ChatStore) -> list[dict]:
    chat = chats.get(st.session_state.active_chat_id)
    if not chat:
        return []
    messages = chat["messages"]
    index = st.session_state.focused_msg
    if index is None or index >= len(messages):
        index = next(
            (i for i in range(len(messages) - 1, -1, -1) if messages[i]["role"] == "assistant"), None
        )
    return messages[index].get("sources", []) if index is not None else []


def render(store: DocumentStore, chats: ChatStore, ollama: dict) -> None:
    with st.container(key="doc-panel"):
        docs = store.documents()
        if not docs:
            ui.empty_state(
                "file-search",
                "No document selected",
                "Upload a PDF to see its details, a summary, and the passages behind each answer.",
            )
            return

        doc = store.get(st.session_state.selected_doc_id)
        if doc is None:
            doc = docs[0]
            st.session_state.selected_doc_id = doc.id

        ui.doc_header(doc.filename, f"PDF · {ui.human_size(doc.size_bytes)}")
        ui.info_grid(
            [
                ("Pages", str(doc.pages)),
                ("Passages", str(doc.chunks)),
                ("Added", ui.human_date(doc.uploaded_at)),
            ]
        )
        st.toggle(
            "Answer from this document only",
            key="scope_to_doc",
            help="When off, questions search every uploaded document.",
        )

        _summary(store, doc, ollama)
        _sources(chats, doc.id)

        with st.popover("Remove document", icon=":material/delete:", width="stretch"):
            st.caption("This deletes the document and its index. Chats are kept.")
            st.button(
                "Remove permanently",
                type="primary",
                key="confirm-remove",
                on_click=_remove,
                args=(store, doc.id, doc.filename),
            )


def _remove(store: DocumentStore, doc_id: str, filename: str) -> None:
    # Runs as a callback so the scope toggle's state can still be reset.
    store.remove(doc_id)
    st.session_state.selected_doc_id = None
    st.session_state.scope_to_doc = False
    state.flash("success", f"Removed {filename}")


def _summary(store: DocumentStore, doc, ollama: dict) -> None:
    ui.subheading("Summary")
    if doc.summary:
        ui.summary_text(doc.summary)
        return
    if st.button(
        "Generate summary",
        icon=":material/auto_awesome:",
        width="stretch",
        disabled=not ollama["online"],
        key="gen-summary",
    ):
        with st.spinner("Reading the document…"):
            try:
                store.set_summary(doc.id, rag.summarize(store, doc.id, st.session_state.chat_model))
            except OllamaError as exc:
                ui.callout("error", str(exc))
                return
        st.rerun()


def _sources(chats: ChatStore, doc_id: str) -> None:
    sources = _focused_sources(chats)
    ui.subheading("Cited passages")
    if not sources:
        st.caption("Ask a question to see the exact passages each answer is based on.")
        return

    pages = sorted({s["page"] for s in sources if s["doc_id"] == doc_id})
    if pages:
        st.caption("Pages referenced in this document")
        ui.page_refs(pages)

    with st.container(key="passages"):
        for source in sources:
            ui.passage_card(source)
