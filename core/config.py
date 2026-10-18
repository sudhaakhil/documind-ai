"""Central configuration. Override any value with an environment variable."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("DOCUMIND_DATA_DIR", ROOT / "data"))
CHROMA_DIR = DATA_DIR / "chroma"
REGISTRY_PATH = DATA_DIR / "documents.json"
CHATS_PATH = DATA_DIR / "chats.json"

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
DEFAULT_CHAT_MODEL = os.getenv("DOCUMIND_CHAT_MODEL", "llama3.2")
# Changing the embedding model invalidates the index: delete data/ and re-upload.
EMBED_MODEL = os.getenv("DOCUMIND_EMBED_MODEL", "nomic-embed-text")

COLLECTION_NAME = "documind"
CHUNK_SIZE = 900
CHUNK_OVERLAP = 150
EMBED_BATCH_SIZE = 32

DEFAULT_TOP_K = 5
DEFAULT_TEMPERATURE = 0.2
HISTORY_TURNS = 3  # previous question/answer pairs sent for follow-up context
