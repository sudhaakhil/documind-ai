"""Chat history persisted to a JSON file."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from .config import CHATS_PATH
from .store import read_json, write_json


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class ChatStore:
    def __init__(self) -> None:
        self._chats: dict[str, dict] = {c["id"]: c for c in read_json(CHATS_PATH, [])}

    def _save(self) -> None:
        write_json(CHATS_PATH, list(self._chats.values()))

    def recent(self, limit: int = 8) -> list[dict]:
        return sorted(self._chats.values(), key=lambda c: c["updated_at"], reverse=True)[:limit]

    def get(self, chat_id: str | None) -> dict | None:
        return self._chats.get(chat_id) if chat_id else None

    def create(self, first_question: str) -> dict:
        title = " ".join(first_question.split())
        chat = {
            "id": uuid.uuid4().hex[:12],
            "title": title if len(title) <= 48 else title[:47].rstrip() + "…",
            "created_at": _now(),
            "updated_at": _now(),
            "messages": [],
        }
        self._chats[chat["id"]] = chat
        return chat

    def append(self, chat_id: str, message: dict) -> None:
        chat = self._chats[chat_id]
        chat["messages"].append(message)
        chat["updated_at"] = _now()
        self._save()

    def delete(self, chat_id: str) -> None:
        self._chats.pop(chat_id, None)
        self._save()
