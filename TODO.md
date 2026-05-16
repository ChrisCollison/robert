# TODO

Purpose
- Source-of-truth list of planned and in-progress work.
- Keep this operational and concrete.

Updated
- 2026-05-15 (Unified snapshot across validation + UI tracks)
- 2026-05-16 (Readability + FAQ-first execution plan approved)

## Approved Near-Term Plan (2026-05-16)

Execution Policy
- [x] Store and enforce plan-before-execution checkpoint in `AGENTS.md`.
- [ ] Keep implementation sequence gated by explicit user approval before each new phase.

Phase 1B — Diagnostic Readability (In Progress)
- [x] Fix run discovery and diagnosis loading for normalized run archives.
- [x] Render diagnosis summary as structured markdown in the UI (instead of escaped HTML text blocks).
- [x] Expand metrics display with key PREDICT/VERIFY values for both No PFI and PFI variants.
- [x] Add evidence image section that surfaces existing run artifact images for interpretation.
- [x] Improve semantic styling for observation severity (PASSED/info/warning/failure badges).
- [ ] Run full UI readability smoke test on both available runs and log outcomes.

Phase 2A — FAQ / Heuristics First (Next)
- [x] Implement deterministic FAQ response layer grounded in `run_context.json` + `diagnosis.json`.
- [x] Route chat requests to heuristics first and avoid API calls when a rule answer exists.
- [x] Add visibility in UI indicating whether response came from heuristic vs LLM fallback.

Phase 2B — OpenAI Fallback (After 2A)
- [ ] Add OpenAI fallback only for unanswered heuristic questions.
- [ ] Add key-setup gating and security checks before first API call.
- [ ] Track query counts/cost mode in UI logs for budget awareness.

## Unified Snapshot (2026-05-15)

Goal
- Re-align parallel workstreams into one execution order so validation and UI progress do not drift.

Current Reality
- Validation pipeline notebook stack exists: wrapper -> extractor -> diagnosis.
- UI Phase 1 scaffold exists and is documented as implemented.
- Main gap is end-to-end validation evidence across run types and a single source of current priorities.

Track A: Validation and Evidence Quality (Primary)
- [ ] Run full regression validation pass on latest archived run and log outcomes.
- [ ] Run full classification validation pass (wrapper -> extractor -> diagnosis) and log outcomes.
- [ ] Run incomplete/missing-file robustness pass and confirm null-safe behavior + warnings.
- [ ] Compare diagnosis outputs with ROBERT report expectations for at least one run.
- [ ] Record threshold adjustments (if any) with rationale in progress docs.

Track B: UI Productization (Secondary, in parallel after A1)
- [ ] Execute Phase 1 test checklist and document pass/fail details.
- [ ] Fix Phase 1 defects found during testing.
- [ ] Verify API-key non-exposure in browser tooling and logs.
- [ ] Start Phase 2 chat wiring only after Phase 1 tests pass.

Cross-Track Integration Tasks
- [ ] Define exact artifact contract consumed by UI (`run_context.json`, `diagnosis.json`, `diagnosis_summary.md`).
- [ ] Add one canonical "known-good" archived run for repeatable UI and parser testing.
- [ ] Ensure `COMPLETED_TASKS.md` and `PROGRESS.md` reflect the same status after each milestone.

Execution Order (Recommended)
1. Complete Track A regression validation pass.
2. Complete Track A classification validation pass.
3. Complete Track A incomplete-run robustness pass.
4. Execute UI Phase 1 tests and fixes.
5. Begin UI Phase 2 chat integration with validated evidence artifacts.

## Proposed Plan (Do Not Execute Without Approval)
1. Build agent/extract_context.py to parse CURATE, GENERATE, VERIFY, and PREDICT outputs into run_context.json.
2. Build agent/diagnose_score.py with transparent rule-based flags tied to extracted evidence.
3. Build agent/explain.py to create deterministic human-readable explanations from evidence + flags.
4. Build agent/run_agent.py as a CLI wrapper entry point for extract -> diagnose -> explain.
5. Add parser and rules tests focused on regression/classification branches and missing-file robustness.

## Active Tasks
- [ ] Confirm and finalize documentation workflow (reference notes + TODO + completed log + tex sync).
- [ ] Approve run_context.json schema fields and required evidence map.
- [ ] Approve parser priorities and safe fallback behavior.

## Next Up (Small Chunks)
- [ ] Add explicit run_context.json schema draft.
- [ ] Add parsing regex/token rules for PREDICT and VERIFY sections.
- [ ] Add deterministic diagnostics rubric for score limitations.

## Extractor V1 Approval Gate (Before Coding)
- [ ] Approve V1 must-have fields in `agent/run_context_schema.md`.
- [ ] Approve parser behavior contract (null-safe, never crash on missing files/sections).
- [ ] Approve initial parse priority: PREDICT first, VERIFY second.
- [ ] Approve three-run test set: regression complete, classification complete, incomplete/missing-file run.

## Immediate Start After Approval
- [ ] Implement `agent/extract_context.py` for PREDICT-only thin slice.
- [ ] Extend extractor with VERIFY parsing.
- [ ] Emit stable `run_context.json` shape with all V1 required keys.
- [ ] Validate extractor on the three-run test set and log outcomes in `COMPLETED_TASKS.md`.

## Future: Local Browser UI for ROBERT Diagnostics

**Status**: Roadmap item. Does not block current extraction/diagnosis work. Start after Phase A validation is complete.

**Mission**: Build a local browser-based UI that displays ROBERT diagnostic output alongside a chat interface. User provides their own API key; it is handled securely (backend-only, never exposed to frontend).

### Framework Research & Decision
- [x] Research Python UI frameworks (Streamlit, Gradio, NiceGUI, Panel, Dash, FastAPI+Frontend)
- [x] Recommendation: **Dash (Plotly)** for split-screen layout, API key security, Python integration
  - Split-screen: 5/5 (native flexbox/grid)
  - API key security: 4/5 (server-side callbacks)
  - Local execution: 5/5 (dev server built-in)
  - Python integration: 4/5 (callbacks are Python functions)
  - Learning curve: 3/5 (steeper than Streamlit, well-documented)
- [ ] Alternative path if scaling: FastAPI + Vue 3 (requires JavaScript expertise; maximum flexibility)

### Phase 1: Dash App Scaffold + Document Viewer (Weeks 1–2)
- [x] Create `agent/ui/` directory structure
- [x] Create `agent/ui/app.py` (main Dash application entry point)
- [x] Create `agent/ui/components.py` (reusable layout components)
- [x] Create `agent/ui/utils.py` (helper functions for loading/formatting)
- [x] Create `agent/ui/config.py` (configuration, paths, API key loading stub)
- [x] Create `agent/ui/callbacks.py` (Dash callbacks for document selection)
- [x] Create `agent/ui/README.md` (setup instructions)
- [x] Create `agent/ui/PHASE1_SUMMARY.md` (Phase 1 documentation)
- [x] Create `requirements_ui.txt` (Dash dependencies)
- [x] Create `agent/ui/.env.example` (API key template)
- [x] Create `agent/ui/.gitignore` (protect API key config)
- [x] Create `start_ui.py` (quick start script)
- [x] Implement document selector dropdown (lists runs from `agent/run_archive/`)
- [x] Implement left-side document viewer (render `diagnosis_summary.md` as HTML)
- [x] Implement metrics table (display key stats from `run_context.json`)
- [x] Implement responsive split-screen layout (left panel: document, right panel: placeholder)
- [ ] **Test Phase 1**: App starts, document loads, layout responsive, no API keys visible in browser
- [ ] Fix any issues found during Phase 1 testing

### Phase 2: Chat Interface + API Key Handling (Weeks 2–3)
- [ ] Create `agent/ui/chat.py` (LLM integration, chat logic)
- [ ] Create `agent/ui/.env.example` (template for local config, no actual keys)
- [ ] Create `agent/chat_prompts.py` (system prompts, context injection)
- [ ] Implement chat callback (receive question, call LLM, return response)
- [ ] Implement API key loading (environment variable primary, `.env` fallback)
- [ ] Implement error handling (missing key, API failures)
- [ ] **Test**: Chat works, API key not visible in DevTools network tab, graceful error messages

### Phase 3: ROBERT Integration (Weeks 3–4)
- [ ] Create `agent/ui/robert_context.py` (load run_context.json + diagnosis.json)
- [ ] Enhance chat prompts (inject diagnostic evidence into LLM context)
- [ ] Implement run selector (choose from archived runs, update left panel)
- [ ] **Test**: Load different runs, verify chat context switches, spot-check LLM responses reference actual metrics

### Phase 4: Polish & Extensibility (Weeks 4+, Optional)
- [ ] Export chat history to markdown or JSON
- [ ] Dark mode / light mode toggle
- [ ] Session persistence (store chat history locally)
- [ ] Multi-run comparison (side-by-side analysis)
- [ ] Share diagnostic results (generate shareable HTML report)
- [ ] [Additional features TBD based on feedback]

### API Key Security (All Phases)
- [ ] Load API key from `ROBERT_CHAT_API_KEY` environment variable at startup
- [ ] Fallback: read from `config/.env` (git-ignored local override)
- [ ] **Critical**: Key never sent to browser; callbacks execute server-side
- [ ] Verify: Key not visible in browser console, network tab, or storage
- [ ] Error message: "API key not configured. Please set ROBERT_CHAT_API_KEY environment variable."
- [ ] Logging: Never log API key to console or user-facing output
- [ ] Documentation: Add setup instructions to UI README

### Related Documentation
- Framework research details: `/memories/session/ui_framework_research.md`
- Complete implementation plan: `/memories/session/ui_plan.md`
- Project governance: `AGENTS.md` (read-only robert/, LLM optional, env var API keys)
- Diagnostic output spec: `agent/run_context_schema.md`

### Dependencies
- Framework: `dash`, `dash-bootstrap-components`
- Optional: `pdf2image` (for PDF rendering in Phase 3)
- LLM: `openai` or equivalent (loaded server-side only)
- Do NOT: Add to requirements.txt (keep separate in requirements_ui.txt)
