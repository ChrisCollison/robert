# ROBERT UI — Local Browser Interface for Diagnostics

## Overview

This is a local browser-based interface for displaying ROBERT diagnostic output. The app runs on your machine (no external servers) and provides:

- **Left panel**: ROBERT diagnostic output (markdown, HTML, structured data)
- **Right panel**: Heuristics-first chat interface for asking questions about your results
- **Security**: Your API key stays on your machine; never exposed to the browser

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_ui.txt
```

### 2. Set Your API Key

Choose one of these methods:

**Option A: Environment Variable (Recommended)**
```bash
export ROBERT_CHAT_API_KEY="sk-..."
python app.py
```

**Option B: Local Config File**
```bash
# Create config/.env in the same directory as app.py
echo 'ROBERT_CHAT_API_KEY=sk-...' > config/.env
python app.py
```

### 3. Run the App

From this directory (`agent/ui/`):

```bash
python app.py
```

The app will open in your browser at `http://localhost:8050`.

## Usage

1. **Select a run**: Use the dropdown to choose a ROBERT diagnostic run
2. **View diagnostics**: Left panel displays the diagnostic summary and metrics
3. **Ask questions**: Type a question in the chat box on the right
4. **Get answers**: Deterministic FAQ heuristics answer common questions from extracted evidence

Current chat status:
- Heuristics-first responses are implemented and run without API calls
- Optional OpenAI fallback is enabled for unanswered heuristic questions when `ROBERT_CHAT_API_KEY` is configured and the `openai` package is installed

## Configuration

### API Key Security

Your API key is:
- ✅ Loaded server-side at startup
- ✅ Never sent to your browser
- ✅ Never logged or displayed
- ✅ Only used for LLM API calls

Your API key is **NOT**:
- ❌ Hardcoded in source files
- ❌ Visible in browser console or network tab
- ❌ Stored in git repository

### Supported LLM Providers

The current fallback path uses the OpenAI Python client with server-side key handling only.

Optional environment variables:

- `ROBERT_OPENAI_MODEL` defaults to `gpt-4o-mini`
- `ROBERT_OPENAI_MAX_TOKENS` defaults to `350`

If `openai` is not installed, the UI still starts and the chat returns a clear fallback-unavailable message.

## Experimental Local Knowledge Base

This repository includes a local-only experimental knowledge indexing workflow (Phase 1).

- Place `.txt`, `.md`, and `.pdf` files in `agent/ui/knowledge/`.
- Build the index locally with the notebook `agent/ui/Build_Local_Knowledge_Index.ipynb`.
- Current default chunking is `350` words with `75` words overlap.
- Indexing and retrieval happen fully on your machine (no document upload to OpenAI).
- Full documents are not sent to OpenAI.
- In future chat integration, only retrieved chunks may be passed to optional LLM fallback.

Important workflow note:
- Rebuild the local index every time you add, remove, or modify documents in `agent/ui/knowledge/`.

Current status:
- Phase 1 includes local loading, chunking, BM25 indexing, and retrieval helpers.
- Phase 2 integration is now available as an optional local retrieval path in chat (heuristics-first remains primary).
- A future phase may include seeded local FAQ documents (question/answer notes) in `agent/ui/knowledge/`.

Optional local retrieval settings:
- `ROBERT_ENABLE_LOCAL_RAG` defaults to `true` (set to `false` to disable).
- `ROBERT_RAG_STORAGE_DIR` defaults to `agent/ui/storage`.
- `ROBERT_RAG_TOP_K` defaults to `3`.

## Development

### Directory Structure

```
agent/ui/
├── app.py                 # Main Dash application
├── components.py          # Layout components (header, panels, chat)
├── utils.py              # Helper functions (load context, format markdown)
├── config.py             # Configuration management (API keys, paths)
├── callbacks.py          # Dash callbacks (document selection, chat)
├── chat.py               # LLM integration (Phase 2)
├── robert_context.py     # Load ROBERT outputs (Phase 3)
├── .env.example          # Template for API key config (Phase 2)
├── README.md             # This file
└── __init__.py           # Package marker

agent/
├── chat_prompts.py       # LLM system prompts (Phase 2)
├── requirements_ui.txt   # Dash and UI dependencies
└── ...
```

### Running Tests

(Phase 2+)

```bash
pytest tests/test_ui.py
```

## Roadmap

**Phase 1** (Current): Document viewer + layout
**Phase 2**: Chat interface + API key handling
**Phase 3**: ROBERT integration (load diagnostics, inject context)
**Phase 4+**: Polish, export, dark mode, etc.

## Troubleshooting

### "API key not configured" Error

Set the `ROBERT_CHAT_API_KEY` environment variable or create `config/.env`:

```bash
export ROBERT_CHAT_API_KEY="your-key-here"
```

### App won't start

Check that Dash is installed:

```bash
pip install -r requirements_ui.txt
```

### API calls failing

- Verify API key is correct and has credits
- Check network connectivity
- Look for error messages in the chat interface

## Related Documentation

- `AGENTS.md` — Project governance
- `agent/run_context_schema.md` — Diagnostic data fields
- `agent/diagnose_score.ipynb` — Diagnostic rules engine
