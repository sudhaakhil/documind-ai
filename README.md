# DocuMind AI

An intelligent PDF analysis and question-answering assistant. Upload PDFs, ask questions in plain language, and get answers with page-level citations. Everything runs locally: **Streamlit** for the interface, **ChromaDB** for vector search, and **Ollama** for embeddings and the language model.

## Features

- Drag-and-drop PDF upload, multiple files at once, de-duplicated by content
- Page-aware chunking and semantic search with ChromaDB
- Streaming answers with numbered citations and source cards (filename + page)
- Document panel: file details, one-click AI summary, the exact passages behind each answer
- Search all documents, or limit answers to the selected one
- Saved chat history, model and retrieval settings
- Clear loading, empty, success and error states (Ollama offline, model missing, scanned PDFs)

## Quick start

1. Install [Ollama](https://ollama.com) and pull the two models:

   ```bash
   ollama pull llama3.2
   ollama pull nomic-embed-text
   ```

2. Install the Python dependencies (Python 3.10+):

   ```bash
   python -m venv .venv
   .venv\Scripts\activate        # macOS/Linux: source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   streamlit run app.py
   ```

Open http://localhost:8501. If Ollama isn't running, the app tells you so in the sidebar and on the welcome screen.

## Project structure

```
documind-ai/
├── app.py                  # Entry point: page config, layout (sidebar | workspace | panel)
├── .streamlit/config.toml  # Streamlit theme: colours, Inter font, radius, sidebar palette
├── core/                   # Back end, no Streamlit imports
│   ├── config.py           # Paths, model names, chunk sizes (env-var overridable)
│   ├── llm.py              # Ollama client: chat streaming, embeddings, model list
│   ├── pdf_loader.py       # Text extraction + page-aware chunking
│   ├── store.py            # Document registry + ChromaDB index and search
│   ├── rag.py              # Prompts, grounded answers, summaries, citation parsing
│   └── chats.py            # Chat history persistence
├── ui/                     # Interface
│   ├── styles.css          # Design tokens and all custom styling
│   ├── theme.py            # Injects styles.css
│   ├── icons.py            # Inline SVG icons + logo
│   ├── components.py       # Reusable HTML components (cards, chips, callouts…)
│   ├── state.py            # Session-state keys and actions
│   ├── sidebar.py          # Left sidebar
│   ├── workspace.py        # Welcome screen, conversation, chat input
│   └── doc_panel.py        # Right document panel
├── data/                   # Created at runtime: chroma/, documents.json, chats.json
└── DESIGN.md               # Design concept, tokens, wireframes, component specs
```

## Configuration

Set environment variables before `streamlit run`:

| Variable | Default | Purpose |
|---|---|---|
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server |
| `DOCUMIND_CHAT_MODEL` | `llama3.2` | Default chat model (also selectable in Settings) |
| `DOCUMIND_EMBED_MODEL` | `nomic-embed-text` | Embedding model. If you change it, delete `data/` and re-upload |
| `DOCUMIND_DATA_DIR` | `./data` | Where the index and history are stored |

Chunk size, overlap and history length are in `core/config.py`.

## Customising the design

- **Colours:** change the tokens at the top of `ui/styles.css` (`--dm-primary`, `--dm-sidebar`, …) and the matching values in `.streamlit/config.toml`. The TOML file colours Streamlit's built-in widgets; the CSS colours everything custom.
- **Font:** edit `font` in `.streamlit/config.toml` (any Google Fonts URL works).
- **Corner radius / shadows:** `--dm-radius*` and `--dm-shadow*` tokens.
- **Suggested questions:** the `SUGGESTIONS` list in `ui/workspace.py`.
- **Hero text:** `hero()` in `ui/components.py`.
- **Panel width:** the `[2, 1]` column ratio in `app.py`.

Custom styles target Streamlit's `data-testid` attributes and keyed containers (`st.container(key="x")` renders the class `.st-key-x`). If a future Streamlit release renames a test id, adjust the selector in `styles.css`; the app keeps working with default styling meanwhile.

## How it works

1. **Ingest:** `pypdf` extracts text per page, which is split into ~900-character chunks with 150-character overlap. Breaks prefer paragraph and sentence boundaries, and every chunk keeps its page number.
2. **Embed and store:** chunks are embedded with `nomic-embed-text` through Ollama and stored in a persistent ChromaDB collection (cosine distance) with filename and page metadata.
3. **Retrieve:** the question is embedded and the top-k passages are fetched (optionally filtered to one document).
4. **Answer:** the passages are numbered and sent to the chat model with instructions to cite them as `[n]`. The UI parses those citations to show exactly which sources were used.

## Limitations

- Scanned (image-only) PDFs need OCR, which isn't included.
- Answers can only be as good as the local model. Larger models such as `llama3.1:8b` or `qwen2.5` give better results than small ones.
