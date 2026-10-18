"""DocuMind AI — intelligent PDF analysis and question answering.

Run with:  streamlit run app.py
"""

import streamlit as st

from core import llm
from core.chats import ChatStore
from core.store import DocumentStore
from ui import doc_panel, sidebar, state, theme, workspace

st.set_page_config(
    page_title="DocuMind AI",
    page_icon=":material/description:",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource(show_spinner="Opening your library…")
def get_store() -> DocumentStore:
    return DocumentStore()


@st.cache_resource
def get_chats() -> ChatStore:
    return ChatStore()


@st.cache_data(ttl=15, show_spinner=False)
def ollama_status() -> dict:
    try:
        return {"online": True, "models": llm.list_models()}
    except llm.OllamaError:
        return {"online": False, "models": []}


theme.apply()
state.init()
store, chats, ollama = get_store(), get_chats(), ollama_status()

sidebar.render(store, chats, ollama)

if st.session_state.show_panel:
    main, panel = st.columns([2, 1], gap="medium")
    with main:
        workspace.render(store, chats, ollama)
    with panel:
        doc_panel.render(store, chats, ollama)
else:
    with st.container(key="workspace-solo"):
        workspace.render(store, chats, ollama)
