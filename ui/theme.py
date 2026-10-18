"""Injects the design system stylesheet (ui/styles.css)."""

from pathlib import Path

import streamlit as st

_CSS = Path(__file__).with_name("styles.css")


def apply() -> None:
    # st.markdown keeps <style> tags; the element itself is hidden by styles.css.
    st.markdown(f"<style>{_CSS.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
