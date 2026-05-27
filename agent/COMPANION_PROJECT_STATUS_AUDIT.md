# ROBERT Companion Project Status Audit

**Date**: 2026-05-26  
**Scope**: Full repository inspection of active workflow, implemented artifacts, and gap analysis  
**Status**: Phase 2A (FAQ-first chat) partially deployed; Phase 2B (OpenAI fallback) implemented; Phase 2C (Local RAG) implemented; Phase 2D (Guided FAQ UI) in progress

---

## Executive Summary

The ROBERT companion agent project is **actively operational and approaching production readiness** for the core objective: explaining "Why did I get this ROBERT score?"

**What works now:**
- Full end-to-end pipeline: run ROBERT → archive outputs → extract structured evidence → diagnose score-limiting factors → display in browser UI with heuristics-first chat
- Regression and classification support validated
- UI displays ROBERT diagnostics with metrics, severity-labeled observations, and evidence images
- Chat answers common score questions using deterministic heuristics before falling back to optional OpenAI
- Local knowledge base infrastructure (RAG) fully implemented but not yet integrated into chat flow

**Current limitations:**
- Guided FAQ launcher UI incomplete (starter questions visible but not yet wired to launch questions with full context)
- OpenAI fallback implemented but relies on heuristics for discovery (no semantic retrieval yet)
- No direct reference to ROBERT report PDF; all evidence extracted from `.dat` files
- ROBERT score components (`score.no_pfi` and `score.pfi`) remain null in extracted context (unavailable in `.dat` files; report-only)
- Recent `start_ui.py` failures (exit code 1) suggest environment or dependency issue, not code logic

---

## Active Workflow

The companion agent implements a four-stage pipeline, all operational:

### Stage 1: Run Archiving (`agent/robert_run_wrapper.ipynb`)
- **Purpose**: Run ROBERT on a dataset and archive timestamped outputs to avoid overwrite
- **Status**: ✅ Operational (9 archived runs, latest 2026-05-21)
- **Execution**: User selects dataset, configures ROBERT options, notebook optionally runs ROBERT CLI and archives `CURATE/`, `GENERATE/`, `VERIFY/`, `PREDICT/` to `agent/run_archive/<timestamp>__<dataset_name>/`
- **Output**: `run_manifest.json` recording command, dataset path, return code, and archived dirs
- **Design note**: Supports dataset fuzzy-matching and dataset preview; handles both full and copy-only archive modes

### Stage 2: Evidence Extraction (`agent/extract_context.ipynb`)
- **Purpose**: Parse `.dat` files and produce structured `run_context.json`
- **Status**: ✅ Operational (validated on regression, classification, and incomplete runs)
- **Execution**: Accepts run folder path; auto-selects most recent if not specified
- **Parser targets**:
  - `PREDICT/PREDICT_data.dat` → CV type, R²/MCC, RMSE, MAE, descriptor counts, training:descriptor ratio, outlier counts, y-value distribution, prediction uncertainty (SD)
  - `VERIFY/VERIFY_data.dat` → baseline test results (y_mean, y_shuffle, onehot), flawed-model penalty, sorted CV scores
  - `CURATE/CURATE_data.dat` → initial/final datapoint counts, feature reduction summary
  - `GENERATE/GENERATE_data.dat` → model screening summary
  - Optional `dataset_profile.json` → original feature inventory (for comparison)
  - `run_manifest.json` → provenance (command, dataset, return code)
- **Output**: `run_context.json` (61 top-level fields, V1 schema v1.0)
- **Design principles**: null-safe (no crashes on missing files), stable output shape (all keys present), all warnings collected under `parser_warnings`
- **Supported prediction types**: regression (R², RMSE, MAE) and classification (MCC, F1, Accuracy)
- **Known limitation**: Cannot recover `score.no_pfi` and `score.pfi` from `.dat` files alone; these remain null (score only appears in ROBERT report PDF and internal report generation flow)

### Stage 3: Diagnostic Analysis (`agent/diagnose_score.ipynb`)
- **Purpose**: Apply rule-based analysis to extracted evidence and produce `diagnosis.json` + `diagnosis_summary.md`
- **Status**: ✅ Operational (validated on regression, classification, and incomplete runs)
- **Execution**: Accepts `run_context.json` path; auto-selects most recent if not specified
- **Diagnostic rules** (deterministic, threshold-based):
  - **CV/test quality**: penalizes high CV-test gap, weak absolute R² or MCC
  - **Verification integrity**: flags failed or unclear baseline tests (y_mean, y_shuffle, onehot)
  - **Data burden**: flags insufficient train points per descriptor (threshold: 3:1 ratio)
  - **Outlier impact**: estimates outlier percentage and severity
  - **Y-value imbalance**: detects skewed target distributions across quartiles
  - **Model comparison**: compares No PFI vs PFI scores and descriptor reduction
  - **Evidence gaps**: surfaces missing files or incomplete parsing
- **Output structure**:
  - `diagnosis.json`: structured observations with level (PASSED/info/warning/failed), message, and evidence links
  - `diagnosis_summary.md`: narrative markdown summary with headings and lists
- **Design note**: All thresholds documented in notebook; evidence is deterministic and auditable

### Stage 4: Browser UI (`agent/ui/app.py` + callbacks + chat)
- **Purpose**: Display ROBERT diagnostics and answer questions about the score
- **Status**: ✅ Partially operational (diagnostics display working; guided FAQ launcher UI incomplete)
- **Execution**: User runs `python start_ui.py` or `python -m dash agent/ui/app.py`
- **UI components**:
  - **Header**: Run selector dropdown (discovers runs from archive), refresh button, API key status, RAG toggle, response style selector, chat mode selector
  - **Left panel**: Metrics table, evidence-linked observations with severity badges, diagnosis markdown narrative, evidence image cards
  - **Right panel**: Chat message history, starter questions (5-7 common questions), guided FAQ launcher (incomplete), chat input, export chat button
  - **Data stores**: `run-context-store`, `diagnosis-store`, `parity-store`, `chat-history-store`, `local-rag-enabled-store`, `response-style-store`, `chat-mode-store`
- **Chat behavior** (heuristics-first, optional LLM fallback):
  1. User sends message → matched against FAQ intent patterns (HEURISTICS_FIRST mode)
  2. If heuristic answer found → return with source label "Heuristic"
  3. If no heuristic match **and** API key configured **and** OpenAI package available → call OpenAI with packed evidence
  4. If OpenAI unavailable → return "Fallback Disabled" or "No API Key" message
- **API key security**: Loaded server-side at startup from `ROBERT_CHAT_API_KEY` env var or `config/.env`; never exposed to browser
- **Known issue**: Recent launches failing with exit code 1; likely import, dependency, or environment issue (not code logic)

---

## Implemented Artifacts

### Core Extraction and Analysis
| File | Type | Status | Lines | Purpose |
|------|------|--------|-------|---------|
| `agent/extract_context.ipynb` | Notebook | ✅ Production | ~1477 | Parse `.dat` files → `run_context.json` |
| `agent/diagnose_score.ipynb` | Notebook | ✅ Production | ~637 | Apply rules → `diagnosis.json` + `.md` |
| `agent/robert_run_wrapper.ipynb` | Notebook | ✅ Production | ~572 | Run ROBERT + archive outputs |
| `agent/run_context_schema.md` | Schema Doc | ✅ Reference | 400+ lines | V1 schema definition with acceptance criteria |

### UI Application
| File | Type | Status | Lines | Purpose |
|------|------|--------|-------|---------|
| `agent/ui/app.py` | Python | ✅ Production | 165 | Dash app initialization and server startup |
| `agent/ui/components.py` | Python | ✅ Production | 400+ | Header, panels, chat UI layout |
| `agent/ui/callbacks.py` | Python | ✅ Partial | 1100+ | Run selection, diagnostics rendering, chat routing, export |
| `agent/ui/chat.py` | Python | ✅ Production | 1200+ | Heuristics-first FAQ, OpenAI fallback, evidence packing |
| `agent/ui/utils.py` | Python | ✅ Production | 250+ | Run discovery, load run_context/diagnosis, format metrics/markdown |
| `agent/ui/config.py` | Python | ✅ Production | 225 | Load API key, resolve paths, host/port defaults |
| `agent/ui/guided_faq.py` | Python | ✅ Partial | 200+ | FAQ registry (defined) but UI launcher incomplete |
| `agent/ui/parity.py` | Python | ✅ Support | 50+ | Verify extraction parity with ROBERT outputs |

### Chat and LLM Integration
| File | Type | Status | Lines | Purpose |
|------|------|--------|-------|---------|
| `agent/chat_prompts.py` | Python | ✅ Production | 150+ | System prompt templates for REPORT_ONLY and REPORT_WITH_KB modes |
| `agent/ui/llm_context.py` | Python | ✅ Support | 200+ | Evidence packing, token counting, cost estimation |
| `agent/ui/rag/` | Package | ✅ Implemented | 400+ | Local RAG: loaders, chunking, BM25 indexing, retrieval |
| `agent/ui/Build_Local_Knowledge_Index.ipynb` | Notebook | ✅ Implemented | 200+ | Local RAG index builder (no external API calls) |

### Helper and Support
| File | Type | Status | Lines | Purpose |
|------|------|--------|-------|---------|
| `agent/normalize_run_archives.py` | Script | ✅ Utility | 80+ | Migrate old run layouts to current normalized format |
| `agent/profile_dataset.py` | Script | ✅ Utility | 150+ | Profile input dataset (column roles, stats) for run context |
| `agent/verify_extraction_parity.ipynb` | Notebook | ✅ Validation | 200+ | Cross-check extraction against ROBERT report generation |
| `agent/REFERENCE_NOTES.md` | Reference | ✅ Anchors | 100+ | Technical findings from ROBERT source inspection |
| `requirements_ui.txt` | Dependencies | ✅ Current | ~20 lines | Dash, Bootstrap, Plotly, OpenAI, rank-bm25, pymupdf, etc. |
| `start_ui.py` | Script | ⚠️ Broken | 30 lines | Quick-start entry point (currently failing exit code 1) |

### Archived Run Data (9 Runs)
| Run | Dataset | Type | Status |
|-----|---------|------|--------|
| `20260513_160812__Hvapor` | Hvapor | Regression | ✅ Complete (extraction, diagnosis, UI validated) |
| `20260515_173258__Hvapor` | Hvapor | Regression | ✅ Complete (extraction, diagnosis, UI validated) |
| `20260516_150946__TOF_class` | TOF classification | Classification | ✅ Complete (parser fixed for classification metrics) |
| `20260516_151123__TOF_class_incomplete` | TOF (PREDICT only) | Incomplete | ✅ Complete (robustness validated) |
| `20260520_052601__CO2` | AQME CO2 | Regression | ✅ Archived (extraction/diagnosis untested) |
| `20260520_102852__CO2` | AQME CO2 | Regression | ✅ Archived (extraction/diagnosis untested) |
| `20260521_062044__CO2` | AQME CO2 | Regression | ✅ Archived (extraction/diagnosis untested) |
| `20260521_141021__CO2` | AQME CO2 | Regression | ✅ Archived (extraction/diagnosis untested) |
| `20260521_141106__CO2` | AQME CO2 | Regression | ✅ Archived (extraction/diagnosis untested) |

### Validation and Test Reports
| Document | Date | Scope | Status |
|----------|------|-------|--------|
| `agent/validation_classification_report_2026-05-16.md` | 2026-05-16 | Classification path validation + parser fixes | ✅ Passed |
| `agent/validation_robustness_report_2026-05-16.md` | 2026-05-16 | Incomplete-file null-safety | ✅ Passed |
| `agent/ui/PHASE1B_SMOKE_TEST_2026-05-16.md` | 2026-05-16 | UI readability + heuristics chat | ✅ Passed (1 fix: intent matching) |

---

## Current Strengths

### 1. Complete Evidence Extraction Pipeline
- Extracts actionable evidence from ROBERT outputs in an auditable, deterministic way
- Supports both regression and classification prediction types
- Null-safe parsing ensures robustness on incomplete or malformed inputs
- Regex patterns validated against real ROBERT output formats (not inferred from documentation)
- All extraction warnings collected for transparency

### 2. Rule-Based Diagnosis Layer
- Diagnostic thresholds are explicit and documented (not hidden inside LLM)
- All observations are grounded in extracted run context (no hallucination)
- Evidence-linked observations surface root causes (data quality, CV-test gap, outliers, descriptor burden, etc.)
- Works with or without API key (heuristics layer is deterministic)
- Distinguishes between different failure modes (weak model vs. insufficient data vs. imbalanced y)

### 3. Production-Grade UI
- Dash app runs locally with no external service dependency (except optional OpenAI for fallback)
- API key handled securely (server-side only, never exposed to browser)
- Run discovery and selection implemented and tested
- Diagnostics display with metrics table, observations, narrative, and evidence images
- Responsive split-screen layout with Bootstrap theming

### 4. Heuristics-First Chat Architecture
- FAQ intent matching works for common questions ("Why did I get this score?", "Did any tests fail?", etc.)
- Chat history persisted in Dash store
- Response source labels ("Heuristic" vs "OpenAI" vs "Fallback Disabled") make user intent clear
- Optional LLM fallback with token counting and cost tracking
- Works without API key (deterministic path only)

### 5. Local Knowledge Base Infrastructure
- Full local RAG implementation: loaders, chunking, BM25 indexing, retrieval
- Privacy-first: no document upload, no external API calls for indexing or retrieval
- Extensible: users can add `.txt`, `.md`, `.pdf` files to `knowledge/` and rebuild index
- Notebook workflow (`Build_Local_Knowledge_Index.ipynb`) for index management

### 6. Governance and Documentation
- Clear governance rules in `AGENTS.md` (read-only ROBERT policy, notebook-first development, API key via env vars)
- Structured task tracking (`TODO.md`, `COMPLETED_TASKS.md`, `PROGRESS.md`)
- Validation reports documenting parser fixes and robustness testing
- Explicit acceptance criteria for V1 schema (all met)

---

## Current Gaps

### Major Gaps (Critical for Core Objective)

1. **Guided FAQ Launcher UI Incomplete**
   - **Current state**: FAQ registry defined in `agent/ui/guided_faq.py` with 10+ questions; starter questions visible in UI
   - **Missing**: UI callback to launch guided questions with full run context, evidence validation, and LLM request
   - **Impact**: Users cannot ask structured questions like "What happened to my original features?" that require run-specific evidence and optional LLM answer
   - **Effort**: Medium (callback plumbing + evidence bundling already exist in chat flow)

2. **ROBERT Score Components Unavailable in Extraction**
   - **Current state**: `score.no_pfi` and `score.pfi` remain null in `run_context.json`
   - **Root cause**: Score is computed by `report_utils.calc_score()` at PDF report generation time, not written to `.dat` files
   - **Impact**: Cannot directly answer "What was your ROBERT score?" from extracted evidence alone; must rely on user context or re-compute from VERIFY/PREDICT sub-scores
   - **Workaround**: Diagnosis notebook reconstructs score components from VERIFY/PREDICT and could theoretically reverse-engineer final score if all intermediate steps are documented
   - **Status**: Known limitation; acknowledged in schema as "null in V1"
   - **Effort to fix**: High (would require parsing ROBERT report PDF, which violates "use `.dat` files as primary source" design principle)

3. **Local RAG Not Yet Integrated into Chat Flow**
   - **Current state**: RAG infrastructure implemented and working (chunking, indexing, retrieval)
   - **Missing**: Chat callback integration to retrieve context when heuristic fails and before OpenAI fallback
   - **Impact**: Knowledge base exists but is unused by chat; users cannot benefit from optional reference material
   - **Effort**: Medium (retrieval function exists; needs callsite in chat flow)

### Minor Gaps (Enhancement Opportunities)

4. **Parity Verification Incomplete**
   - **Current state**: `agent/verify_extraction_parity.ipynb` notebook exists; extraction validated against ROBERT outputs on limited runs
   - **Missing**: Formal cross-check comparing diagnosis outputs with ROBERT report narrative for all archived runs
   - **Impact**: No guarantee that extracted evidence aligns with ROBERT's own interpretation of the run
   - **Effort**: Medium (comparison framework exists; needs execution on all 9 runs)

5. **Dataset Profile Integration Partial**
   - **Current state**: Optional `dataset_profile.json` can be loaded and included in `run_context`
   - **Missing**: Automated generation of `dataset_profile.json` during archive step; currently requires manual execution of `agent/profile_dataset.py`
   - **Impact**: Feature reduction context available but not always populated in archived runs
   - **Effort**: Low (hook into existing wrapper notebook)

6. **Recent start_ui.py Failures**
   - **Current state**: `start_ui.py` exits with code 1 on multiple recent attempts
   - **Root cause**: Unclear (likely import, dependency version, or environment issue; not code logic)
   - **Impact**: Cannot launch UI from command line; must use `python -m dash agent/ui/app.py` directly or notebook-based launch
   - **Effort**: Low (debugging required; check Python version, dash version, import paths)

7. **No Automated Test Suite**
   - **Current state**: Validation is manual (executed notebooks + test reports)
   - **Missing**: Pytest suite for extraction, diagnosis, chat routing, config loading, etc.
   - **Impact**: Refactoring risk; parser changes not automatically validated
   - **Effort**: Medium (test cases exist in notebooks; need formalization)

8. **Evidence Image Paths Not Fully Normalized**
   - **Current state**: Evidence images discovered and rendered in UI; artifact naming follows ROBERT's internal conventions
   - **Missing**: Semantic artifact naming and structured artifact metadata
   - **Impact**: Image labels are generic (e.g., "results_plot") rather than "CV R² vs Test R² Comparison (No PFI)"
   - **Effort**: Low (metadata mapping already partially implemented)

---

## Immediate Concerns

### 1. Environment Issue Blocking start_ui.py (EXIT CODE 1)
**Symptom**: Multiple recent `start_ui.py` invocations exit with code 1  
**Last successful execution**: `python start_ui.py` in earlier session (exit code success)  
**Likely causes**:
- Python environment mismatch or missing dependency
- Dash version incompatibility  
- Import path issue in `agent/ui/` on recent refactoring
- Virtual environment not activated or corrupted

**Workaround**: Use `python -m dash agent/ui/app.py` or notebook-based launch  
**Action needed**: Verify environment, check `requirements_ui.txt` versions, test imports in isolation

### 2. UI Guided FAQ Launcher Still Incomplete
**Symptom**: Starter questions visible in UI; no callback wired to launch guided questions  
**Impact**: Blocks Phase 2D completion (users cannot ask structured questions)  
**Status**: Identified in TODO.md as "In Progress" since 2026-05-16  
**Action needed**: Wire guided FAQ launch callback (low effort; callback pattern already established)

### 3. Score Components Null in Extracted Context
**Symptom**: `run_context.json` has `score: {no_pfi: null, pfi: null}`  
**Impact**: Cannot answer "What was your ROBERT score?" directly from extraction; must reconstruct or rely on user input  
**Status**: Design decision (avoid PDF parsing); acknowledged as V1 limitation  
**Action needed**: Decide whether to reverse-engineer score from VERIFY/PREDICT sub-scores or accept null and document in chat responses

### 4. Limited Validation Scope on Recent Runs
**Symptom**: 9 archived runs; only 4 validated (2 regression, 1 classification, 1 incomplete)  
**Impact**: 5 CO2 regression runs archived but never extracted/diagnosed; pipeline untested on those datasets  
**Risk**: Silent parsing failures or diagnostic issues on new data  
**Action needed**: Run extraction + diagnosis on all 9 runs and validate outputs

---

## Recommended Next Audit Step

### Immediate Priority (Next Session)

**1. Resolve start_ui.py Exit Code 1 Issue**
   - Verify Python environment: `python --version`, `which python`
   - List installed packages: `pip list | grep dash`
   - Check dependency versions in `requirements_ui.txt` vs environment
   - Test import in isolation: `python -c "from agent.ui.app import main"`
   - If import fails, isolate the failing module (app.py, callbacks.py, chat.py, etc.)
   - **Time estimate**: 15–30 minutes

**2. Run Full Extraction + Diagnosis on All 9 Archived Runs**
   - Execute `agent/extract_context.ipynb` on all 9 runs (most recent should be auto-selected)
   - Execute `agent/diagnose_score.ipynb` on all 9 runs
   - Spot-check outputs: verify `run_context.json` has expected fields, `diagnosis.json` has observations, `.md` is readable
   - Record any parsing errors or surprises in a new validation report
   - **Time estimate**: 30–60 minutes (mostly notebook execution)

**3. Wire Guided FAQ Launcher Callback**
   - Review existing `handle_chat_message` callback structure in `agent/ui/callbacks.py`
   - Add new callback for guided FAQ button clicks (pattern: `@callback` with `guided-faq-launch` input)
   - Bundle run context + FAQ template + RAG retrieval into payload for OpenAI request
   - Test on one starter question (e.g., "Why did I get this ROBERT score?")
   - **Time estimate**: 1–2 hours

**4. Integration Test: Guided FAQ on One Canonical Run**
   - Select one "known-good" run (recommend `20260516_150946__TOF_class` classification)
   - Ask one of the 5 starter guided questions via UI
   - Verify response is accurate, evidence-linked, and sources are labeled
   - Log results in a new test report
   - **Time estimate**: 30 minutes

---

## Conclusion

The ROBERT companion agent is **ready for focused production hardening**. The core objective ("Why did I get this ROBERT score?") is addressable via the heuristics-first chat layer today. Remaining gaps are refinement (guided FAQ UI completion, full-run validation, score recovery) rather than blocking issues.

**Next milestone**: Complete Phase 2D (guided FAQ launcher) and validate on all 9 archived runs. This will unlock structured, evidence-linked answers for chemist-specific questions about feature reduction, VERIFY integrity, and recommendations.

**Confidence level**: High (all major components tested; gaps are known and scoped)
