# Phase 1: Dash App Scaffold + Document Viewer

**Status**: ✅ Implementation Complete (Ready for Testing)

**Date Created**: 2026-05-14

**What's Included**:
- Dash application scaffold with bootstrap theme
- Split-screen layout (left: document, right: chat placeholder)
- Run selector dropdown (lists archived runs from `agent/run_archive/`)
- Document viewer (renders `diagnosis_summary.md` as HTML)
- Metrics table (displays key statistics from `run_context.json`)
- API key status indicator (shows if key is configured)
- Configuration management (API key loading from environment/config)
- Comprehensive docstrings and type hints

**What's NOT Included** (Phase 2+):
- Chat interface (placeholder only)
- LLM integration
- API key security callbacks (stubs only)
- Session persistence

## File Structure

```
agent/
├── ui/
│   ├── app.py              # Main Dash application
│   ├── components.py       # Layout components (header, panels)
│   ├── utils.py            # Helpers (load context, format markdown)
│   ├── config.py           # Configuration (API key loading, paths)
│   ├── callbacks.py        # Dash callbacks (run selection, document loading)
│   ├── chat.py             # Chat stub (Phase 2)
│   ├── .gitignore          # Ignore config/.env (API keys)
│   ├── .env.example        # Template for API key config
│   ├── __init__.py         # Package marker
│   ├── README.md           # User setup guide
│   ├── PHASE1_SUMMARY.md   # This file
│   ├── config/
│   │   └── .gitkeep        # Placeholder for config/.env
│   └── requirements_ui.txt # Dependencies
├── chat_prompts.py         # LLM prompts template (Phase 2)
└── start_ui.py             # Quick start script
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_ui.txt
```

### 2. Run the App

From project root:
```bash
python start_ui.py
```

Or from `agent/ui/`:
```bash
python app.py
```

### 3. View in Browser

Open: http://localhost:8050

## Expected Behavior

### On Startup
- App loads available runs from `agent/run_archive/`
- If runs found: Dropdown populated, first run displayed
- If no runs found: Info message with instructions
- API key status shown (configured / not configured)

### When Selecting a Run
- Left panel updates with `diagnosis_summary.md` + metrics table
- Metrics extracted from `run_context.json` (model, R², dataset size, etc.)
- Right panel shows chat placeholder (Phase 2 message)
- No errors in console log

### Key Governance Points
- ✅ Read-only access to ROBERT outputs (no modifications)
- ✅ API key loaded server-side only (never exposed to browser)
- ✅ No modifications to `robert/` codebase
- ✅ All code in `agent/ui/` (follows AGENTS.md rules)

## Testing Checklist (Phase 1)

Before proceeding to Phase 2, verify:

- [ ] App starts without errors: `python start_ui.py`
- [ ] Browser opens to `http://localhost:8050`
- [ ] Run selector dropdown populated with runs from `agent/run_archive/`
- [ ] Selecting a run displays `diagnosis_summary.md` on left panel
- [ ] Metrics table displays correctly (Model, CV R², Test R², etc.)
- [ ] Layout responsive (resize browser, panels adjust)
- [ ] No API keys visible in browser DevTools:
  - [ ] Console tab (no logs containing key)
  - [ ] Network tab (no key in request/response)
  - [ ] Application > Storage (no key in localStorage/cookies)
- [ ] API key status indicator shows correctly (configured / not configured)
- [ ] Chat placeholder message appears on right panel
- [ ] Send button and input disabled (with note "coming in Phase 2")
- [ ] No TypeScript/JavaScript errors in console

## Architecture Notes

### Why This Structure?

1. **Separation of Concerns**:
   - `app.py`: Entry point and initialization
   - `config.py`: Configuration management (testable, reusable)
   - `utils.py`: Helper functions (can be unit tested)
   - `components.py`: UI components (layout reuse)
   - `callbacks.py`: Dash callbacks (reactive logic)
   - `chat.py`: Phase 2 stub (ready to fill in)

2. **Security Pattern**:
   - API key loaded at startup in `config.py`
   - Stored in Dash server state (not browser)
   - Callbacks receive question, not key
   - Never logged or printed to user

3. **Extensibility**:
   - Placeholders for Phase 2 (chat callbacks, LLM calls)
   - Modular design allows swapping components
   - Easy to add new panels or callbacks
   - Config-driven (easy to add more settings)

## Next Steps (Phase 2)

After Phase 1 testing is complete:
1. Implement `chat.py` LLM integration
2. Add chat callbacks to `callbacks.py`
3. Implement API key security checks
4. Add error handling for API failures
5. Test chat functionality end-to-end

## Troubleshooting Phase 1

### "No module named 'ui'"
Make sure you are running from the project root directory, not from within `agent/ui/`.

### "ModuleNotFoundError: No module named 'dash'"
Install dependencies: `pip install -r requirements_ui.txt`

### App starts but no runs appear
Runs are read from `agent/run_archive/`. Make sure you have:
1. Run `agent/robert_run_wrapper.ipynb` (creates ROBERT outputs)
2. Run `agent/extract_context.ipynb` (creates `run_context.json`)
3. Run `agent/diagnose_score.ipynb` (creates `diagnosis.json`, `diagnosis_summary.md`)

### "API key not configured" warning
This is normal for Phase 1. Chat will not work until Phase 2. To test API key loading:
1. Set environment variable: `export ROBERT_CHAT_API_KEY=test-key`
2. Restart app; status should change to "API key: test-..."

## Related Documentation

- `README.md` — User setup and usage guide
- `AGENTS.md` — Project governance (read-only robert/, API key handling rules)
- `agent/run_context_schema.md` — Field definitions for extracted context
- `agent/diagnose_score.ipynb` — Diagnostic rules engine
- `TODO.md` — Project roadmap and task tracking
- `/memories/session/ui_plan.md` — Comprehensive implementation plan
