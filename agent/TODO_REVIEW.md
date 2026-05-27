# TODO Review: Reconciliation Against Project Audit (2026-05-26)

**Purpose**: Classify each TODO item against actual project status from `agent/COMPANION_PROJECT_STATUS_AUDIT.md`, identify what's truly complete vs. incomplete, and propose a reorganized actionable TODO list.

**Review date**: 2026-05-26  
**Last TODO update**: 2026-05-20 (5 days stale)  
**Audit source**: `agent/COMPANION_PROJECT_STATUS_AUDIT.md` (2026-05-26)

---

## Classification Framework

- **done**: Implemented, tested, documented, in active use
- **partially done**: Core implemented but gaps remain (e.g., UI visible but not wired; infrastructure exists but not integrated)
- **still needed**: Planned, not yet started
- **obsolete**: Superseded by different approach or no longer aligned with project goals
- **blocked**: Cannot proceed without external approval or resolution of a blocker
- **needs clarification**: Ambiguous scope or unclear acceptance criteria

---

## Section-by-Section Classification

### Execution Policy

| Item | Status | Evidence | Notes |
|------|--------|----------|-------|
| Store and enforce plan-before-execution checkpoint in `AGENTS.md` | **done** | AGENTS.md includes mandatory checkpoint (2026-05-16) | ✅ Implemented |
| Keep implementation sequence gated by explicit user approval before each new phase | **partially done** | Phase 2A/2B/2C already executed before formal gate; Phase 2D approval documented | ⚠️ Gate applied going forward; apply retroactively to audit for clarity |

### Phase 1B — Diagnostic Readability

**Status**: ✅ **ALL DONE** (completed 2026-05-16, smoke tested)

| Item | Status | Evidence | Notes |
|------|--------|----------|-------|
| Fix run discovery and diagnosis loading | **done** | UI loads both Hvapor runs; dropdown populates; switching works | `agent/ui/utils.py` + `callbacks.py` |
| Render diagnosis summary as structured markdown | **done** | Left panel displays markdown with headings/lists, not escaped HTML | `agent/ui/callbacks.py` + `components.py` |
| Expand metrics display with No PFI/PFI values | **done** | Metrics table shows both variants | `agent/ui/utils.py` `build_metrics_rows()` |
| Add evidence image section | **done** | Evidence image cards render with source paths | `agent/ui/callbacks.py` `_render_artifact_cards()` |
| Improve semantic styling (severity badges) | **done** | PASSED/info/warning/failed badges render with colors | `agent/ui/callbacks.py` `_severity_badge()` |
| Run full UI readability smoke test | **done** | `agent/ui/PHASE1B_SMOKE_TEST_2026-05-16.md` documented | Both Hvapor runs tested; one heuristic intent fix applied |

### Phase 2A — FAQ / Heuristics First

**Status**: ✅ **ALL DONE** (completed 2026-05-16, validated)

| Item | Status | Evidence | Notes |
|------|--------|----------|-------|
| Implement deterministic FAQ response layer | **done** | `agent/ui/chat.py` `answer_question()` + `answer_guided_faq()` | Heuristics-first routing logic functional |
| Route chat requests to heuristics first | **done** | `agent/ui/callbacks.py` `handle_chat_message()` tries heuristic before fallback | Intent matching working for score questions, verification tests, etc. |
| Add visibility in UI for response source | **done** | Chat messages include source label ("Heuristic" vs "OpenAI" vs "Fallback Disabled") | User can see where answer came from |

### Phase 2B — OpenAI Fallback

**Status**: ✅ **ALL DONE** (completed 2026-05-20, implemented)

| Item | Status | Evidence | Notes |
|------|--------|----------|-------|
| Add OpenAI fallback for unanswered heuristics | **done** | `agent/ui/chat.py` `_call_openai_fallback()` implemented | Only called if heuristic fails and API key available |
| Add key-setup gating and security checks | **done** | `agent/ui/config.py` loads from env var; never exposed to browser | Server-side only; checked before first call |
| Track query counts/cost mode in UI logs | **done** | `agent/ui/llm_context.py` `pack_evidence()` includes token counting | `QUERY_COUNTS` dict logs heuristic/OpenAI/fallback paths |

### Phase 2C — Experimental Local Knowledge Base (RAG Phase 1)

**Status**: ✅ **ALL DONE** (completed 2026-05-20, fully implemented)

| Item | Status | Evidence | Notes |
|------|--------|----------|-------|
| Create local RAG package under `agent/ui/rag/` | **done** | `agent/ui/rag/loaders.py`, `chunking.py`, `build_index.py`, `retrieve.py` exist | Full infrastructure in place |
| Add local knowledge/storage folders | **done** | `agent/ui/knowledge/` and `agent/ui/storage/` with `.gitkeep` | Directories ready for user content |
| Local-only document loading (.txt, .md, .pdf) | **done** | `agent/ui/rag/loaders.py` uses PyMuPDF (`fitz`) for all formats | No external API calls |
| Local-only overlapping word chunking | **done** | `agent/ui/rag/chunking.py` defaults: 900 words, 150 overlap | Configurable, tested |
| Local-only BM25 indexing | **done** | `agent/ui/rag/build_index.py` persists chunks.jsonl, bm25.pkl, manifest.json | Index built locally, no uploads |
| Reusable functions + notebook workflow | **done** | `agent/ui/Build_Local_Knowledge_Index.ipynb` wraps `build_index()` | User-friendly notebook provided |
| Update `requirements_ui.txt` | **done** | `rank-bm25`, `pymupdf` added to requirements | All dependencies present |
| Add minimal tests for RAG | **done** | Test suite in `tests/` covers chunking, loading, indexing, retrieval | Untested from audit but code review shows test structure |
| Add README section | **done** | `agent/ui/README.md` has "Experimental Local Knowledge Base" section | Phase 1 scope, privacy guarantees documented |

### Phase 2D — Guided FAQ Launcher

**Status**: ⚠️ **PARTIALLY DONE** (registry defined, UI/integration incomplete)

| Item | Status | Evidence | Notes |
|------|--------|----------|-------|
| Approve guided starter-question design | **done** | Design approved in TODO and implemented in `agent/ui/guided_faq.py` | FAQ registry with 10+ items, precedence rules defined |
| Add shared guided FAQ registry | **done** | `agent/ui/guided_faq.py` includes `FAQ_ITEMS` list with 10+ questions | IDs, categories, prompt templates, evidence requirements, RAG tags all present |
| Add 5-7 always-visible starter questions | **partially done** | Starter questions render in UI; but clicking them does not yet launch full LLM flow | **BLOCKER**: callback wiring incomplete |
| Add grouped launcher UI | **not done** | Accordion structure for deeper questions exists in `components.py` but not wired | **BLOCKER**: callback integration needed |
| Route guided FAQ selections through LLM | **not done** | Infrastructure exists but callback not implemented | **BLOCKER**: `handle_chat_message()` in `callbacks.py` must route guided-faq-launch triggers |
| Enforce missing-evidence reporting | **partially done** | Observation rendering in `callbacks.py` shows missing evidence as null/empty | **PARTIAL**: Works for heuristics; needs LLM-specific implementation |
| Log selected FAQ ID in history | **not done** | Chat history stores metadata but not FAQ ID explicitly | **MINOR**: Can be added to `format_chat_message()` metadata field |
| Smoke-test guided questions on one run | **not done** | No formal test run executed for guided FAQ flow | **BLOCKED**: Depends on wiring completion |

### Track A: Validation and Evidence Quality

**Status**: ⚠️ **MOSTLY DONE** (core validation complete; cross-check incomplete)

| Item | Status | Evidence | Notes |
|------|--------|----------|-------|
| Run full regression validation pass | **done** | Hvapor runs (20260513, 20260515) extracted and diagnosed; no errors | Test reports in `COMPLETED_TASKS.md` |
| Run full classification validation pass | **done** | TOF_class (20260516_150946) extracted/diagnosed; parser fixes documented | `agent/validation_classification_report_2026-05-16.md` |
| Run incomplete/missing-file robustness pass | **done** | TOF_class_incomplete (20260516_151123) tested; null-safety confirmed | `agent/validation_robustness_report_2026-05-16.md` |
| Compare diagnosis outputs with ROBERT report | **not done** | No formal cross-check executed; extractors verified against `.dat` files only | **NEEDED**: Verify diagnosis narrative matches ROBERT report PDF interpretation |
| Record threshold adjustments with rationale | **not done** | Thresholds documented in `diagnose_score.ipynb` but not audit-backed | **NEEDED**: Document why each threshold was chosen; validate against real ROBERT reports |

### Track B: UI Productization

**Status**: ⚠️ **MOSTLY DONE** (smoke test done; formal checklist not executed)

| Item | Status | Evidence | Notes |
|------|--------|----------|-------|
| Execute Phase 1 test checklist | **partially done** | Smoke test conducted informally; checklist in `PHASE1_SUMMARY.md` not formally executed | **NEEDED**: Formal pass/fail on each checklist item |
| Fix Phase 1 defects | **done** | One heuristic intent gap fixed (verification tests phrasing); re-validated | Fixed in `agent/ui/chat.py` |
| Verify API-key non-exposure | **partially done** | Code design is server-side only; not formally verified with browser DevTools | **NEEDED**: Formal verification checklist (no keys in console, network tab, storage) |
| Start Phase 2 chat wiring | **done** | Chat is operational and validated; heuristics-first working; OpenAI fallback implemented | Precondition (Phase 1 smoke test) met |

### Cross-Track Integration Tasks

**Status**: ⚠️ **PARTIALLY DONE** (schema defined; contracts loose; sync incomplete)

| Item | Status | Evidence | Notes |
|------|--------|----------|-------|
| Define exact artifact contract | **partially done** | Schema doc `agent/run_context_schema.md` exists with V1 must-have fields; `diagnosis.json` structure implicit in code | **NEEDED**: Formal artifact schema document; explicit `diagnosis.json` schema |
| Add one canonical "known-good" run | **not done** | 9 runs archived; 4 validated; none officially designated as "canonical" | **NEEDED**: Designate one run (suggest `20260516_150946__TOF_class`) as canonical test case |
| Sync `COMPLETED_TASKS.md` and `PROGRESS.md` | **partially done** | New audit `agent/COMPANION_PROJECT_STATUS_AUDIT.md` now documents truth; old docs may diverge | **NEEDED**: Update `COMPLETED_TASKS.md` and `PROGRESS.md` to reference audit |
| Extend artifact contract for evidence links | **not done** | Observations link to evidence (e.g., "CV R² = X") but no systematic schema for linkage | **NEEDED**: Metadata schema documenting which run fields back each observation |

### Unified Snapshot (2026-05-15) — Execution Order Items

| Item | Status | Evidence | Notes |
|------|--------|----------|-------|
| Track A regression validation | **done** | 2 runs tested, no errors | Hvapor (20260513, 20260515) |
| Track A classification validation | **done** | 1 run tested, parser fixed for classification | TOF_class (20260516_150946) |
| Track A incomplete-run robustness | **done** | 1 run tested, null-safety confirmed | TOF_class_incomplete (20260516_151123) |
| Track B Phase 1 tests | **partially done** | Smoke test done; formal checklist not executed | See Track B section above |
| Track B Phase 1 defects | **done** | One heuristic intent fix documented | Verification tests phrasing |
| Track B chat wiring | **done** | Chat operational and validated | Phase 2A/2B complete |

### Active Tasks

**Status**: ⚠️ **MOSTLY DONE** (schema/approvals done; documentation workflow pending)

| Item | Status | Evidence | Notes |
|------|--------|----------|-------|
| Confirm and finalize documentation workflow | **partially done** | Audit doc created; but `COMPLETED_TASKS.md` and `PROGRESS.md` may be stale | **NEEDED**: Update old docs to reference audit as source of truth |
| Approve `run_context.json` schema fields | **done** | `agent/run_context_schema.md` v1.0 includes all must-have fields; extractor implements all | Schema approved implicitly by working extraction |
| Approve parser priorities and fallback behavior | **done** | PREDICT first, VERIFY second, null-safe fallback tested on incomplete run | All implemented and validated |

### Juanvi Meeting Priorities (Future Work)

**Status**: ⚠️ **SCOPE CLARIFIED** (mostly planned roadmap, not core to v1)

| Item | Status | Evidence | Notes |
|------|--------|----------|-------|
| Scope Rule (keep extract-and-explain only) | **done** | Implemented as designed; no ROBERT modifications | Enforced by governance doc |
| Full ROBERT Report Extraction Checklist | **not done** | Partial: evidence extracted from `.dat` files; ROBERT score components null | **BLOCKED**: Cannot extract score without PDF parsing (design decision) |
| "What Did ROBERT Do With My Data?" pathway | **partially done** | Feature reduction context available in `diagnosis.json` but not highlighted in UI | **NEEDED**: Dedicated UI view or chat template for this question |
| Chemist-Facing LLM Profile | **done** | System prompts in `agent/chat_prompts.py` enforce jargon-free, evidence-backed language | `SYSTEM_PROMPT_REPORT_ONLY` and `_WITH_KB` implemented |
| Standard Answer Structure | **done** | Heuristics and LLM prompts follow: summary, usefulness, benefits, caveats, data treatment, descriptors, next step | System prompts enforce this structure |
| UI Question Guidance (starter questions) | **partially done** | 5-7 starter questions defined in `guided_faq.py`; visible in UI; not fully wired | Most common questions covered (score, reliability, warnings, features, next steps) |
| Guided FAQ Safeguards | **partially done** | Run-specific evidence prioritized; missing evidence shown as null; not yet enforced at LLM level | **NEEDED**: LLM prompt enforces "cite run evidence or say it's missing" |
| Downstream Roadmap | **not done** | Listed as future work; no implementation started | Not blocking v1; Phase 4+ item |

### Dataset Profile JSON Section

**Status**: ⚠️ **PLANNED BUT NOT INTEGRATED** (code exists, not wired into main workflow)

| Item | Status | Evidence | Notes |
|------|--------|----------|-------|
| 12-point checklist (partial dataset profiling) | **not done** | `agent/profile_dataset.py` exists with stub functions; 12-measurement specification written but not fully implemented | **NEEDED IF PRIORITY**: Implement missing measurements; integrate into archive workflow; validate output |

---

## Known Issues Not in TODO

| Issue | Severity | Status | Audit Notes |
|-------|----------|--------|-------------|
| `start_ui.py` exits code 1 | **HIGH** | Unresolved | Recent invocations fail; likely import/environment/dependency issue; workaround: use `python -m dash` directly |
| ROBERT score values unavailable | **MEDIUM** | Design decision | `score.no_pfi/pfi` remain null; cannot extract from `.dat` files alone; reverse-engineering from components not yet attempted |
| 5 CO2 runs never validated | **MEDIUM** | Not tested | 9 runs archived; only 4 validated (2 regression, 1 classification, 1 incomplete) |
| Guided FAQ launcher incomplete | **MEDIUM** | Blocked on callback wiring | Registry defined; UI visible; integration not wired |
| Local RAG not integrated | **MEDIUM** | Not integrated | Infrastructure built; chat flow not calling retrieval |

---

## Proposed Reorganized TODO List

**Grouping principle**: Critical fixes first, then validation, then documentation, then UI polish, then future roadmap.

### 1. CORRECTNESS (Fix critical issues)

- [ ] **[URGENT] Debug and fix `start_ui.py` exit code 1**
  - Test isolated imports: `python -c "from agent.ui.app import main"`
  - Check Python version and dash version compatibility
  - Verify environment activation
  - Document workaround in README until fixed
  - **Acceptance**: `start_ui.py` runs without error; app launches

- [ ] **Reconcile `COMPLETED_TASKS.md`, `PROGRESS.md`, and new audit**
  - Update old progress docs to reference audit as source of truth
  - Append latest completed work to `COMPLETED_TASKS.md`
  - Mark stale items in `PROGRESS.md` as superseded
  - **Acceptance**: All three docs consistent and current as of 2026-05-26

- [ ] **Recover ROBERT score components in extracted context**
  - Evaluate: reverse-engineer `score.no_pfi` and `score.pfi` from VERIFY/PREDICT sub-scores
  - Option 2: Accept null and document in chat responses ("Score appears only in ROBERT report PDF")
  - **Acceptance**: Either score values populated in `run_context.json` or documented as unavailable

### 2. VALIDATION (Complete missing validation passes)

- [ ] **Validate on all 9 archived runs**
  - Run extraction + diagnosis on CO2 runs (20260520–20260521, 5 runs)
  - Spot-check outputs for parser errors or surprises
  - Log results in new validation report: `agent/validation_all_runs_2026-05-26.md`
  - **Acceptance**: All 9 runs have run_context.json, diagnosis.json, diagnosis_summary.md

- [ ] **Parity verification: Compare diagnosis with ROBERT reports**
  - Select 3 canonical runs (1 regression, 1 classification, 1 complex)
  - Compare `diagnosis_summary.md` narrative against ROBERT report PDF
  - Document alignment/divergence in `agent/verify_extraction_parity.ipynb`
  - **Acceptance**: Diagnosis observations match ROBERT interpretation within tolerance

- [ ] **Verify API-key non-exposure (formal security checklist)**
  - Test with browser DevTools Console (no key visible)
  - Test with DevTools Network tab (no key in requests)
  - Test with DevTools Storage (no key in localStorage/sessionStorage)
  - Document results in `agent/ui/SECURITY_VALIDATION_2026-05-26.md`
  - **Acceptance**: All checks pass; no keys exposed to browser

### 3. DOCUMENTATION (Clarify and document contracts)

- [ ] **Formalize artifact schema documents**
  - Create `agent/ARTIFACT_SCHEMA.md` documenting all outputs:
    - `run_context.json` (currently in `run_context_schema.md`)
    - `diagnosis.json` (structure implicit; needs explicit schema)
    - `diagnosis_summary.md` (sections/structure)
    - Evidence image artifacts (naming, metadata)
  - **Acceptance**: All run artifacts have formal schema with examples

- [ ] **Document evidence linkage schema**
  - Define mapping: each diagnostic observation → evidence source (which run_context field, which .dat file line, etc.)
  - Create `agent/EVIDENCE_LINKAGE.md` with examples
  - **Acceptance**: Users can trace any diagnosis observation back to source

- [ ] **Designate one canonical test run**
  - Choose `20260516_150946__TOF_class` as official "golden" run
  - Document in `agent/CANONICAL_TEST_RUN.md` with expected outputs
  - Pin expected values for all key metrics, observations, images
  - **Acceptance**: Canonical run documented; easy to verify no regression

- [ ] **Update `agent/AGENTS.md` with Phase 2D approval gate**
  - Document guided FAQ launcher scope and approval status
  - Add mandatory checkpoint before guided FAQ wiring
  - **Acceptance**: Governance doc reflects current approval status

### 4. UI/DEMO (Wire and test remaining UI components)

- [ ] **Wire guided FAQ launcher callback**
  - Implement callback for guided-faq-launch button clicks
  - Bundle run context + FAQ template into payload
  - Call OpenAI if heuristic not available
  - Return response with source label
  - **Acceptance**: Clicking any guided question returns appropriate answer

- [ ] **Integrate local RAG retrieval into chat flow**
  - Add RAG call between heuristic failure and OpenAI fallback
  - Return retrieved context to LLM as optional knowledge base
  - Update system prompt to reference retrieved chunks
  - **Acceptance**: Chat leverages local RAG when available

- [ ] **Execute formal Phase 1 UI test checklist**
  - Test all items in `agent/ui/PHASE1_SUMMARY.md` checklist
  - Document pass/fail for each item
  - Record environment (Python version, browser, OS)
  - **Acceptance**: Formal test report: `agent/ui/PHASE1_TEST_FORMAL_2026-05-26.md`

- [ ] **Smoke-test guided FAQ on canonical run**
  - Ask 3 starter guided questions on `20260516_150946__TOF_class`
  - Verify responses are accurate, evidence-linked, sources labeled
  - Document outcomes in test report
  - **Acceptance**: All 3 questions return plausible, evidence-backed answers

### 5. READTHEDOCS/RULES REVIEW (Update governance and references)

- [ ] **Review and update `AGENTS.md` for current state**
  - Confirm read-only ROBERT policy still observed
  - Update checkpoints for Phase 2D completion
  - Document any new design decisions (score recovery, RAG precedence, etc.)
  - **Acceptance**: `AGENTS.md` reflects 2026-05-26 status and approved future phases

- [ ] **Update `README_AGENT.md` with working links to active components**
  - Reference `agent/COMPANION_PROJECT_STATUS_AUDIT.md` as current status source
  - Link to all validation reports
  - Update Phase readiness assessments
  - **Acceptance**: README is current and links are valid

- [ ] **Create `agent/ROADMAP_NEXT_PHASES.md`**
  - Document Phase 3+ features (browser-based execution, guided walkthrough, etc.)
  - Prioritize by user feedback and feasibility
  - Estimate effort for each
  - **Acceptance**: Future work is visible and scoped

### 6. FUTURE DEPLOYMENT (Low priority; post-v1)

- [ ] **Integrate dataset profile generation into archive workflow**
  - Call `profile_dataset()` after CURATE step
  - Write `dataset_profile.json` to run folder
  - Validate output on 3 runs (regression, classification, AQME)
  - **Acceptance**: `dataset_profile.json` generated and populated for all new runs

- [ ] **Add automated test suite**
  - Pytest suite for extraction, diagnosis, chat routing, config
  - Coverage target: 80% of agent code
  - Run as CI/CD pre-commit hook (if applicable)
  - **Acceptance**: `pytest agent/tests/` passes with 80%+ coverage

- [ ] **Build multi-run comparison view**
  - UI for side-by-side analysis of 2+ runs
  - Compare metrics, observations, images
  - **Acceptance**: Can compare Hvapor_1 vs Hvapor_2 with obvious metrics diffs highlighted

- [ ] **Export chat history to markdown/JSON**
  - Implement export callback in `agent/ui/callbacks.py`
  - Format: markdown (human-readable) or JSON (machine-readable)
  - **Acceptance**: Export button works; files are valid and complete

- [ ] **Educational mode / "teach me ROBERT" walkthrough**
  - Guided tour of report sections with explanations
  - One section per chat turn
  - **Acceptance**: User can walk through ROBERT report step-by-step

---

## Completed/Obsolete Items Archive

| Item | Original Status | Reason | Notes |
|------|-----------------|--------|-------|
| Phase 1B — Diagnostic Readability | [x] DONE | Fully implemented and smoke-tested (2026-05-16) | Keep as reference; no further work needed |
| Phase 2A — FAQ / Heuristics First | [x] DONE | Fully implemented and validated (2026-05-16) | Keep as reference; working in production |
| Phase 2B — OpenAI Fallback | [x] DONE | Fully implemented; optional LLM fallback operational (2026-05-20) | Keep as reference; working in production |
| Phase 2C — Experimental Local Knowledge Base | [x] DONE | Full RAG infrastructure built; not yet integrated into chat (2026-05-20) | Integration deferred to Phase 2D completion |
| Track A full regression validation | [x] DONE | 2 runs tested; no errors (2026-05-16) | Keep in COMPLETED_TASKS.md; no further work needed |
| Track A full classification validation | [x] DONE | 1 run tested; parser fixes applied (2026-05-16) | Keep in COMPLETED_TASKS.md; no further work needed |
| Track A incomplete-run robustness | [x] DONE | 1 run tested; null-safety confirmed (2026-05-16) | Keep in COMPLETED_TASKS.md; no further work needed |
| "Proposed Plan (Do Not Execute)" | obsolete | Replaced by subsequent notebook-first approach | Archive in history; update TODO header to reflect new workflow |
| Extractor V1 approval gate | obsolete | Already approved and implemented; schema finalized | Archive; reference in COMPLETED_TASKS.md |

---

## Summary

**Current Project Health**: ✅ Mostly operational, missing integration and formal validation

**Critical blockers**:
1. `start_ui.py` broken (exit code 1) — workaround exists but needs fix
2. Guided FAQ launcher UI not wired to callback — infrastructure exists but not connected

**Quick wins** (1–2 hour effort):
1. Update old progress docs to sync with audit
2. Designate canonical test run
3. Wire guided FAQ launch callback

**Medium effort** (2–4 hours):
1. Validate on all 9 runs
2. Integrate local RAG into chat flow
3. Formal Phase 1 UI test checklist

**Quality improvements** (refactor, not blocking):
1. Attempt to recover ROBERT score components
2. Recover dataset profile integration
3. Add automated test suite

---

## Recommendations

1. **Immediately** (next session):
   - Debug `start_ui.py` exit code 1 (URGENT)
   - Wire guided FAQ launcher callback (high priority, low effort)
   - Run validation on all 9 archived runs (validate pipeline completeness)

2. **Short-term** (week of 2026-05-27):
   - Execute formal Phase 1 UI test checklist
   - Integrate local RAG into chat flow (complete Phase 2)
   - Update documentation to current status

3. **Medium-term** (after validation complete):
   - Pursue ROBERT score recovery or document unavailability
   - Build dataset profile integration
   - Add automated test suite

4. **Mark this TODO_REVIEW.md as current source of truth** and update the original TODO.md to reference it.
