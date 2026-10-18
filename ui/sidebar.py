"""Left sidebar: brand, new chat, upload, documents, recent chats, settings."""

from __future__ import annotations

import streamlit as st

from core.chats import ChatStore
from core.store import DocumentStore

from . import components as ui
from . import state


def render(store: DocumentStore, chats: ChatStore, ollama: dict) -> None:
    with st.sidebar:
        ui.brand()
        st.button(
            "New chat",
            icon=":material/add:",
            type="primary",
            width="stretch",
            key="sb-new-chat",
            on_click=state.new_chat,
        )

        files = st.file_uploader(
            "Upload PDF",
            type=["pdf"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key=f"sb-upload-{st.session_state.uploader_nonce}",
        )
        if files:
            state.queue_uploads(files)
            st.rerun()

        _documents(store)
        _recent_chats(chats)
        _settings(ollama)


def _documents(store: DocumentStore) -> None:
    docs = store.documents()
    ui.section_label("Documents", len(docs))
    if not docs:
        st.caption("No documents yet. Upload a PDF to begin.")
        return
    with st.container(key="sb-docs"):
        for doc in docs:
            active = doc.id == st.session_state.selected_doc_id
            st.button(
                doc.filename,
                icon=":material/description:",
                type="tertiary",
                width="stretch",
                key=f"nav{'active' if active else ''}-doc-{doc.id}",
                help=f"{doc.pages} pages · click to view details",
                on_click=state.select_doc,
                args=(doc.id,),
            )


def _recent_chats(chats: ChatStore) -> None:
    recent = chats.recent()
    ui.section_label("Recent chats")
    if not recent:
        st.caption("Your conversations will appear here.")
        return
    with st.container(key="sb-chats"):
        for chat in recent:
            active = chat["id"] == st.session_state.active_chat_id
            st.button(
                chat["title"],
                icon=":material/chat_bubble:",
                type="tertiary",
                width="stretch",
                key=f"nav{'active' if active else ''}-chat-{chat['id']}",
                on_click=state.open_chat,
                args=(chat["id"],),
            )


def _settings(ollama: dict) -> None:
    with st.container(key="sb-settings"):
        with st.expander("Settings", icon=":material/tune:"):
            if ollama["online"]:
                count = len(ollama["models"])
                ui.status_line(True, f"Ollama connected · {count} model{'s' if count != 1 else ''}")
            else:
                ui.status_line(False, "Ollama offline")
                st.caption("Start it with `ollama serve`, then reload.")

            chat_models = [m for m in ollama["models"] if "embed" not in m]
            current = st.session_state.chat_model
            if f"{current}:latest" in chat_models:  # Ollama reports "llama3.2" as "llama3.2:latest"
                current = st.session_state.chat_model = f"{current}:latest"
            installed = current in chat_models
            options = chat_models if installed else [current, *chat_models]
            st.selectbox("Chat model", options, key="chat_model")
            if ollama["online"] and not installed:
                st.caption(f"Not installed. Run `ollama pull {current}`")

            st.slider(
                "Passages per answer", 2, 10, key="top_k",
                help="How many document passages are retrieved for each question.",
            )
            st.slider(
                "Creativity", 0.0, 1.0, step=0.1, key="temperature",
                help="Lower values keep answers closer to the source text.",
            )
