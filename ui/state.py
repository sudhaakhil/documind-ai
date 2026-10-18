"""Session-state keys and the small actions that change them.

Every UI module reads and writes app state through here, so the full list of
keys lives in one place.
"""

from __future__ import annotations

import streamlit as st

from core.config import DEFAULT_CHAT_MODEL, DEFAULT_TEMPERATURE, DEFAULT_TOP_K

DEFAULTS = {
    "active_chat_id": None,  # chat shown in the workspace (None = new chat)
    "selected_doc_id": None,  # document shown in the document panel
    "scope_to_doc": False,  # answer only from the selected document
    "show_panel": True,
    "focused_msg": None,  # index of the assistant message whose sources the panel shows
    "pending_question": None,  # set by suggestion cards
    "pending_uploads": [],  # [(filename, bytes)] waiting to be indexed
    "uploader_nonce": 0,  # bumped to reset file uploaders after indexing
    "flash": [],  # [(kind, message)] shown once on the next run
    # Settings (bound directly to widgets)
    "chat_model": DEFAULT_CHAT_MODEL,
    "top_k": DEFAULT_TOP_K,
    "temperature": DEFAULT_TEMPERATURE,
}


def init() -> None:
    for key, value in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = list(value) if isinstance(value, list) else value


def flash(kind: str, message: str) -> None:
    """Queue a one-shot message. kind: success | info | warning | error."""
    st.session_state.flash.append((kind, message))


def pop_flashes() -> list[tuple[str, str]]:
    items, st.session_state.flash = st.session_state.flash, []
    return items


def queue_uploads(files) -> None:
    st.session_state.pending_uploads = [(f.name, f.getvalue()) for f in files]
    st.session_state.uploader_nonce += 1


def new_chat() -> None:
    st.session_state.active_chat_id = None
    st.session_state.focused_msg = None


def open_chat(chat_id: str) -> None:
    st.session_state.active_chat_id = chat_id
    st.session_state.focused_msg = None


def select_doc(doc_id: str) -> None:
    st.session_state.selected_doc_id = doc_id
    st.session_state.show_panel = True


def ask(question: str) -> None:
    st.session_state.pending_question = question


def focus_message(index: int) -> None:
    st.session_state.focused_msg = index
    st.session_state.show_panel = True


def toggle_panel() -> None:
    st.session_state.show_panel = not st.session_state.show_panel
