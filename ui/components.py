"""Reusable presentational components.

Each function renders one piece of HTML with `render_html()`. All dynamic text
goes through `esc()`. Styling lives in `styles.css` under the matching `dm-` class.
"""

from __future__ import annotations

import re
from datetime import datetime
from html import escape as esc

import streamlit as st

from .icons import icon, logo

_CALLOUT_ICONS = {"success": "check", "info": "info", "warning": "alert", "error": "alert"}


def render_html(markup: str, target=None) -> None:
    """Render trusted HTML (st.html would strip the SVG icons).

    Lines are joined so Markdown never sees indentation (code blocks) or blank
    lines (which would end the raw-HTML block).
    """
    flat = " ".join(line.strip() for line in markup.splitlines() if line.strip())
    (target or st).markdown(flat, unsafe_allow_html=True)


def human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def human_date(iso: str) -> str:
    return datetime.fromisoformat(iso).astimezone().strftime("%b %d, %Y")


# ---- layout pieces ----------------------------------------------------------
def brand() -> None:
    render_html(
        f"""<div class="dm-brand">{logo(32)}
        <div><div class="dm-brand-name">DocuMind <span>AI</span></div>
        <div class="dm-brand-tag">Document intelligence</div></div></div>"""
    )


def section_label(text: str, count: int | None = None) -> None:
    badge = f'<span class="dm-count">{count}</span>' if count is not None else ""
    render_html(f'<div class="dm-section-label">{esc(text)}{badge}</div>')


def hero() -> None:
    render_html(
        f"""<div class="dm-hero">
        <div class="dm-pill">{icon("shield", 14)} Runs locally with Ollama · your files stay on this machine</div>
        <div class="dm-hero-title" role="heading" aria-level="1">Your documents. <span>Smarter answers.</span></div>
        <p>Upload, explore, and understand your documents with AI.</p></div>"""
    )


def topbar_title(title: str, subtitle: str) -> None:
    render_html(
        f'<div class="dm-topbar-title"><div class="dm-title">{esc(title)}</div>'
        f'<div class="dm-subtitle">{icon("search", 13)} {esc(subtitle)}</div></div>'
    )


def subheading(text: str) -> None:
    render_html(f'<div class="dm-subheading">{esc(text)}</div>')


def _inline_code(text: str) -> str:
    """Escape text, then render `backticks` as <code>."""
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", esc(text))


def callout(kind: str, message: str, title: str | None = None) -> None:
    head = f"<strong>{esc(title)}</strong> " if title else ""
    render_html(
        f'<div class="dm-callout dm-callout-{kind}" role="{"alert" if kind == "error" else "status"}">'
        f"{icon(_CALLOUT_ICONS[kind], 18)}<div>{head}<span>{_inline_code(message)}</span></div></div>"
    )


def empty_state(icon_name: str, title: str, body: str) -> None:
    render_html(
        f'<div class="dm-empty"><div class="dm-empty-icon">{icon(icon_name, 22)}</div>'
        f"<div class=\"dm-empty-title\">{esc(title)}</div><p>{esc(body)}</p></div>"
    )


def status_line(online: bool, text: str) -> None:
    render_html(
        f'<div class="dm-status {"is-online" if online else "is-offline"}">'
        f'<span class="dm-dot"></span>{esc(text)}</div>'
    )


# ---- chat pieces ------------------------------------------------------------
def message_header(role: str) -> None:
    if role == "assistant":
        render_html(f'<div class="dm-msg-head">{logo(22)}<span>DocuMind</span></div>')
    else:
        render_html('<div class="dm-msg-head dm-msg-head-user"><span>You</span></div>')


def thinking(label: str = "Reading the relevant passages") -> str:
    return (
        f'<div class="dm-thinking"><span class="dm-dots"><i></i><i></i><i></i></span>{esc(label)}…</div>'
    )


def source_chips(sources: list[dict]) -> None:
    chips = "".join(
        f'<span class="dm-chip" title="{esc(s["filename"])}, page {s["page"]}">'
        f'<b>{s["n"]}</b>{icon("file-text", 13)}<span class="dm-chip-name">{esc(s["filename"])}</span>'
        f'<span class="dm-chip-page">p. {s["page"]}</span></span>'
        for s in sources
    )
    render_html(f'<div class="dm-chips"><span class="dm-chips-label">Sources</span>{chips}</div>')


# ---- document panel pieces --------------------------------------------------
def doc_header(filename: str, meta: str) -> None:
    render_html(
        f'<div class="dm-doc-head"><div class="dm-doc-icon">{icon("file-text", 20)}</div>'
        f'<div class="dm-doc-title"><div title="{esc(filename)}">{esc(filename)}</div>'
        f"<span>{esc(meta)}</span></div></div>"
    )


def info_grid(rows: list[tuple[str, str]]) -> None:
    cells = "".join(f"<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>" for k, v in rows)
    render_html(f'<dl class="dm-info">{cells}</dl>')


def page_refs(pages: list[int]) -> None:
    chips = "".join(f'<span class="dm-page">p. {p}</span>' for p in pages)
    render_html(f'<div class="dm-pages">{chips}</div>')


def passage_card(source: dict, max_chars: int = 320) -> None:
    text = source["text"]
    if len(text) > max_chars:
        text = text[:max_chars].rsplit(" ", 1)[0] + "…"
    render_html(
        f"""<div class="dm-passage">
        <div class="dm-passage-head"><b>{source["n"]}</b>
        <span class="dm-passage-name" title="{esc(source["filename"])}">{esc(source["filename"])}</span>
        <span class="dm-page">p. {source["page"]}</span></div>
        <p>{esc(text)}</p>
        <div class="dm-passage-foot">{round(source["score"] * 100)}% match</div></div>"""
    )


def summary_text(text: str) -> None:
    render_html(f'<div class="dm-summary">{icon("sparkles", 14)}<p>{esc(text)}</p></div>')
