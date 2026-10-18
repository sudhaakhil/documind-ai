"""Prompt construction for grounded answers and document summaries."""

from __future__ import annotations

import re
from collections.abc import Iterator

from . import llm
from .config import HISTORY_TURNS
from .store import DocumentStore, Passage

SYSTEM_PROMPT = """You are DocuMind, an assistant that answers questions using only the document excerpts provided.

Rules:
- Base every statement on the excerpts. Cite them inline with their numbers, like [1] or [2][3].
- If the excerpts don't contain the answer, say so plainly and suggest a better question.
- Be concise and well structured: short paragraphs, and bullet points where they help.
- Never invent page numbers, figures or quotes."""

SUMMARY_PROMPT = """Summarise the document below in 3-4 sentences for someone deciding whether to read it.
State what it is, its main topics, and any key conclusions. Plain prose, no headings, no preamble.

Document "{filename}":
{text}"""


def _context_block(passages: list[Passage]) -> str:
    return "\n\n".join(
        f"[{p.n}] {p.filename}, page {p.page}:\n{p.text}" for p in passages
    )


def build_messages(question: str, passages: list[Passage], history: list[dict]) -> list[dict]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history[-HISTORY_TURNS * 2 :]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append(
        {
            "role": "user",
            "content": f"Document excerpts:\n\n{_context_block(passages)}\n\nQuestion: {question}",
        }
    )
    return messages


def answer_stream(
    question: str, passages: list[Passage], history: list[dict], model: str, temperature: float
) -> Iterator[str]:
    return llm.chat_stream(build_messages(question, passages, history), model, temperature)


def cited_numbers(answer: str, passages: list[dict]) -> set[int]:
    valid = {p["n"] for p in passages}
    return {int(n) for n in re.findall(r"\[(\d+)\]", answer)} & valid


def summarize(store: DocumentStore, doc_id: str, model: str) -> str:
    doc = store.get(doc_id)
    text = store.leading_text(doc_id, max_chars=6000)
    prompt = SUMMARY_PROMPT.format(filename=doc.filename, text=text)
    return llm.chat([{"role": "user", "content": prompt}], model, temperature=0.2).strip()
