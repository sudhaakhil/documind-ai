"""Minimal Ollama HTTP client (chat streaming, embeddings, model listing)."""

from __future__ import annotations

import json
from collections.abc import Iterator

import requests

from .config import OLLAMA_URL


class OllamaError(RuntimeError):
    """A user-presentable problem talking to Ollama."""


def _raise_for_response(resp: requests.Response, model: str | None) -> None:
    if resp.ok:
        return
    try:
        detail = resp.json().get("error", resp.text)
    except ValueError:
        detail = resp.text
    if model and "not found" in str(detail).lower():
        raise OllamaError(f"Model '{model}' isn't installed. Run: ollama pull {model}")
    raise OllamaError(f"Ollama returned an error: {detail}")


def _post(path: str, payload: dict, *, stream: bool = False, timeout=120) -> requests.Response:
    try:
        resp = requests.post(f"{OLLAMA_URL}{path}", json=payload, stream=stream, timeout=timeout)
    except requests.ConnectionError as exc:
        raise OllamaError(
            f"Can't reach Ollama at {OLLAMA_URL}. Start it with: ollama serve"
        ) from exc
    except requests.Timeout as exc:
        raise OllamaError("Ollama took too long to respond. Try again or use a smaller model.") from exc
    _raise_for_response(resp, payload.get("model"))
    return resp


def list_models(timeout: float = 2.0) -> list[str]:
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=timeout)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise OllamaError(f"Can't reach Ollama at {OLLAMA_URL}. Start it with: ollama serve") from exc
    return sorted(m["name"] for m in resp.json().get("models", []))


def embed(texts: list[str], model: str) -> list[list[float]]:
    resp = _post("/api/embed", {"model": model, "input": texts})
    return resp.json()["embeddings"]


def chat_stream(messages: list[dict], model: str, temperature: float) -> Iterator[str]:
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "options": {"temperature": temperature},
    }
    with _post("/api/chat", payload, stream=True, timeout=(5, 300)) as resp:
        for line in resp.iter_lines():
            if not line:
                continue
            data = json.loads(line)
            if "error" in data:
                raise OllamaError(data["error"])
            chunk = data.get("message", {}).get("content", "")
            if chunk:
                yield chunk
            if data.get("done"):
                break


def chat(messages: list[dict], model: str, temperature: float) -> str:
    return "".join(chat_stream(messages, model, temperature))
