# TODO

Purpose
- Source-of-truth list of planned and in-progress work.
- Keep this operational and concrete.

Updated
- 2026-05-15 (Unified snapshot across validation + UI tracks)
- 2026-05-16 (Readability + FAQ-first execution plan approved)
- 2026-05-19 (Juanvi chemist-facing interpretation priorities added)
- 2026-05-20 (Dataset Profile JSON plan added — verified against ROBERT source)
- 2026-05-20 (Guided FAQ launcher approved for run-specific LLM answers)

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
- [x] Run full UI readability smoke test on both available runs and log outcomes (`agent/ui/PHASE1B_SMOKE_TEST_2026-05-16.md`).

Phase 2A — FAQ / Heuristics First (Next)
- [x] Implement deterministic FAQ response layer grounded in `run_context.json` + `diagnosis.json`.
- [x] Route chat requests to heuristics first and avoid API calls when a rule answer exists.
- [x] Add visibility in UI indicating whether response came from heuristic vs LLM fallback.

Phase 2B — OpenAI Fallback (After 2A)
- [x] Add OpenAI fallback only for unanswered heuristic questions.
- [x] Add key-setup gating and security checks before first API call.
- [x] Track query counts/cost mode in UI logs for budget awareness.

Phase 2C — Experimental Local Knowledge Base (RAG, Phase 1)
- [x] Create local RAG package under `agent/ui/rag/` with `loaders.py`, `chunking.py`, `build_index.py`, and `retrieve.py`.
- [x] Add local knowledge and storage folders (`agent/ui/knowledge/`, `agent/ui/storage/`) with gitkeep placeholders.
- [x] Implement local-only document loading for `.txt`, `.md`, and `.pdf` (PyMuPDF/`fitz` for PDF extraction).
- [x] Implement local-only overlapping word chunking (defaults: chunk size 900 words, overlap 150 words).
- [x] Implement local-only BM25 indexing (`rank-bm25`) and persist artifacts to `agent/ui/storage/`:
  - [x] `chunks.jsonl`
  - [x] `bm25.pkl`
  - [x] `manifest.json`
- [x] Implement `build_local_index(...)` reusable function and summary return payload in `agent/ui/rag/build_index.py`.
- [x] Implement local retrieval and context formatting in `agent/ui/rag/retrieve.py` with helpful missing-index/empty-knowledge errors.
- [x] Add beginner notebook workflow `agent/ui/Build_Local_Knowledge_Index.ipynb` that wraps reusable functions (no duplicated logic).
- [x] Update `requirements_ui.txt` with local RAG dependencies if missing (`rank-bm25`, `pymupdf`; keep `python-dotenv` aligned with current usage).
- [x] Add minimal tests for chunking, loading, index build, and retrieval in existing test structure.
- [x] Add README section: "Experimental Local Knowledge Base" with local-first privacy guarantees and Phase 1 scope.

Phase 2D — Guided FAQ Launcher (In Progress)
- [x] Approve guided starter-question design with run evidence -> dataset profile -> RAG background precedence.
- [ ] Add shared guided FAQ registry with IDs, categories, prompt templates, evidence requirements, and RAG tags.
- [ ] Add 5-7 always-visible starter questions in the chat panel.
- [ ] Add grouped launcher UI for deeper questions by report section.
- [ ] Route guided FAQ selections through a dedicated LLM path that uses selected-run evidence first.
- [ ] Enforce missing-evidence reporting so guided answers do not collapse into generic FAQ text.
- [ ] Log selected FAQ ID, category, and evidence manifest in chat history/export payload.
- [ ] Smoke-test guided questions on one canonical archived run and record pass/fail behavior.

## Unified Snapshot (2026-05-15)

Goal
- Re-align parallel workstreams into one execution order so validation and UI progress do not drift.

Current Reality
- Validation pipeline notebook stack exists: wrapper -> extractor -> diagnosis.
- UI Phase 1 scaffold exists and is documented as implemented.
- Main gap is end-to-end validation evidence across run types and a single source of current priorities.

Track A: Validation and Evidence Quality (Primary)
- [x] Run full regression validation pass on latest archived run and log outcomes.
- [x] Run full classification validation pass (wrapper -> extractor -> diagnosis) and log outcomes (`agent/validation_classification_report_2026-05-16.md`).
- [x] Run incomplete/missing-file robustness pass and confirm null-safe behavior + warnings (`agent/validation_robustness_report_2026-05-16.md`).
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
- [ ] Extend the artifact contract so every surfaced warning, metric, score component, outlier, descriptor, and report callout links back to a concrete evidence source.

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

## Juanvi Meeting Priorities (Future Work)

Scope Rule
- [ ] Keep the companion agent strictly extract-and-explain only.
- [ ] Do not rebuild ROBERT or duplicate its ML logic.
- [ ] Keep `robert/` read-only unless explicit approval is given for a separate change.

Full ROBERT Report Extraction Checklist
- [ ] Surface all warnings, caveats, score components, VERIFY results, PREDICT metrics, outliers, feature importance, curation details, and report/PDF evidence.
- [ ] Ensure each surfaced item links back to a concrete evidence source such as `run_context.json`, `diagnosis.json`, `PREDICT_data.dat`, `VERIFY_data.dat`, `CURATE_data.dat`, `GENERATE_data.dat`, model parameter CSVs, or report artifacts.

"What Did ROBERT Do With My Data?" Explanation Pathway
- [ ] Explain how the original CSV becomes the curated feature set.
- [ ] Track original feature count, removed descriptors, retained descriptors, and final model descriptors.
- [ ] Make clear that feature reduction may be expected rather than a problem.
- [ ] Support chemist-facing examples such as "26 data points, 39 features, final model uses 3 descriptors."

Chemist-Facing LLM Profile
- [ ] Keep responses jargon-free and written for chemists.
- [ ] When ML terms are necessary, explain them in plain language.
- [ ] Require the LLM to translate extracted evidence rather than invent reasoning.

Standard Answer Structure
- [ ] Plain-language summary.
- [ ] Is the model useful?
- [ ] Main benefits.
- [ ] Caveats / warnings.
- [ ] What ROBERT did with the data.
- [ ] Important descriptors or outliers.
- [ ] Suggested next step.

UI Question Guidance
- [ ] Add clickable starter questions for:
  - [ ] Why did I get this ROBERT score?
  - [ ] Is this model reliable enough to use?
  - [ ] What did ROBERT remove from my dataset?
  - [ ] Which descriptors matter most?
  - [ ] Are there warnings I should pay attention to?
  - [ ] What should I try next?
  - [ ] Can you explain this without machine-learning jargon?
  - [ ] What did ROBERT do with my original CSV?
- [ ] Add automatic next-question suggestions so each response proposes one or two useful follow-up questions based on the current run context.

Guided FAQ Safeguards
- [ ] Ensure generic FAQ/RAG background is explanatory only and never overrides run-specific ROBERT evidence.
- [ ] Block or explicitly downgrade guided answers when required run evidence is missing.
- [ ] Warn explicitly when test-set size is very small.
- [ ] Keep descriptor explanations tentative unless a reliable definition source is available.

Downstream Roadmap
- [ ] Browser-based ROBERT execution from uploaded CSV.
- [ ] Educational mode / "teach me what ROBERT is doing."
- [ ] Guided report walkthrough, one section at a time.
- [ ] Simplified notebooks: each section should have a plain-language description followed by one simple function call.

## Next Up (Small Chunks)
- [ ] Add explicit run_context.json schema draft.

---

## Dataset Profile JSON for ROBERT Companion Bot

### Overview

**Goal:** Generate a single machine-readable `dataset_profile.json` per run that summarizes the original input CSV.  
The companion bot uses this to explain dataset-level context without needing the full raw CSV.

**Constraint:** All profiling code lives in `agent/`. No modifications to `robert/` scripts.  
**Strategy:** Parse `CURATE_data.dat` and `CURATE_options.csv` for measurements already logged by ROBERT;  
load the original CSV (path stored in `CURATE_options.csv`) to compute the rest.

**Why the original CSV?** ROBERT stores the original CSV path in `CURATE_options.csv` → `csv_name`.
The archived curated CSVs (`*_CURATE.csv`) preserve all remaining rows and can serve as fallback,
but they have columns removed and rows sorted — they are NOT identical to the input.
The profiler should attempt the original CSV path first and fall back to `*_CURATE.csv` if unavailable.

**Where generated:** After CURATE outputs are archived by the normalizer, before or during
`extract_context.ipynb`. The profiler is a lightweight read-only utility in `agent/robert_helper.py`
or a standalone `agent/profile_dataset.py`.

**Redundancy note:** Measurements 8, 9, and 10 are already computed and logged by ROBERT CURATE.
For those, the profiler should parse the existing `CURATE_data.dat` text rather than recompute.
Only measurements not logged by ROBERT (5, 6, 7, 11, 12) require loading the CSV directly.

**Priority note:** Measurement 12 (SMILES validity/element summary) is currently low priority and deferred.
Keep the `smiles_summary` field in the schema, but leave it `null` in v1 unless needed for AQME-focused runs.

---

### Proposed `dataset_profile.json` v1 Schema

```json
{
  "version": "1.0",
  "generated_at": "<ISO-8601 UTC>",
  "source_csv": "Hvapor.csv",
  "source_csv_path": "<absolute path recorded at CURATE time>",
  "row_count": 133,
  "column_count": 7,
  "column_headings": ["Name", "IF", "g3", "SS", "SGBP", "Hardness", "Hvapor"],
  "column_roles": {
    "target": "Hvapor",
    "names": "Name",
    "smiles": null,
    "ignored": ["Name"],
    "discarded": [],
    "candidate_descriptors": ["IF", "g3", "SS", "SGBP", "Hardness"]
  },
  "candidate_descriptor_count": 5,
  "missingness": {
    "IF": 0,
    "g3": 0,
    "SS": 0,
    "SGBP": 0,
    "Hardness": 0
  },
  "target_summary": {
    "type": "reg",
    "min": 38.1,
    "max": 104.2,
    "mean": 71.3,
    "median": 70.8,
    "std": 12.4,
    "range": 66.1,
    "class_counts": null
  },
  "target_imbalance": {
    "class_ratio": null,
    "minority_class_pct": null
  },
  "constant_columns": ["IF", "SS"],
  "near_constant_columns": [],
  "non_numeric_descriptors": [],
  "highly_correlated_pairs": [
    {"removed": "IF", "correlated_with": "SGBP", "r2": 1.0},
    {"removed": "SS", "correlated_with": "SGBP", "r2": 1.0}
  ],
  "top_descriptor_target_correlations": [
    {"descriptor": "SGBP", "r2_with_target": 0.72},
    {"descriptor": "Hardness", "r2_with_target": 0.61},
    {"descriptor": "g3", "r2_with_target": 0.44}
  ],
  "smiles_summary": null
}
```

---

### Checklist

- [ ] **1. Row count and column count**
  - Proposed JSON location: `row_count`, `column_count`
  - Current status: Already available in stable output
  - Evidence in repo: `CURATE_data.dat` logs "133 datapoints" and "5 accepted descriptors".
    `load_database()` in `utils.py` lines ~1238-1242 writes these counts to the log.
  - Existing function/file: `robert/utils.py` → `load_database()` (read-only reference)
  - Needed action: Parse `CURATE_data.dat` for these log lines in `agent/`. No ROBERT modification needed.
  - Notes / risks: Log text format is stable. Column count requires summing accepted + ignored + 1 (y).

- [ ] **2. Column headings**
  - Proposed JSON location: `column_headings`
  - Current status: Already available in stable output
  - Evidence in repo: Original CSV path is stored in `CURATE_options.csv` → `csv_name` column.
    Headings are the first row of that CSV.
  - Existing function/file: `CURATE_options.csv` (stable artifact)
  - Needed action: Load original CSV from path in `CURATE_options.csv`; read header row only.
    Fall back to `*_CURATE.csv` column list if original CSV is missing.
  - Notes / risks: Absolute path in `CURATE_options.csv` may break if run folder is moved.
    Resolve relative to run archive or accept null gracefully.

- [ ] **3. Column role classification**
  - Proposed JSON location: `column_roles`
  - Current status: Partially available
  - Evidence in repo: `CURATE_options.csv` stores `y`, `names`, `ignore`.
    `discard` columns are not saved anywhere — they are dropped before CURATE output is written.
    SMILES detection is not flagged for standard (non-AQME) CURATE runs.
  - Existing function/file: `CURATE_options.csv` (stable); `robert/curate.py` → `save_curate()` for what is saved.
  - Needed action: Read `CURATE_options.csv` for y/names/ignore. Infer candidate descriptors as
    (all original columns) − y − names − ignored − discarded. Detect SMILES by scanning original CSV
    for a column whose name starts with "smiles" (case-insensitive), matching AQME convention.
  - Notes / risks: `discard` is NOT saved. If the original CSV is unavailable, candidate descriptor
    list must be reconstructed from the curated CSV (already excludes discarded columns).

- [ ] **4. Candidate descriptor count**
  - Proposed JSON location: `candidate_descriptor_count`
  - Current status: Already available in stable output
  - Evidence in repo: `CURATE_data.dat` logs "5 accepted descriptors" (pre-correlation-filter count).
    `load_database()` in `utils.py` computes `accepted_descs`.
  - Existing function/file: `robert/utils.py` → `load_database()`
  - Needed action: Parse `CURATE_data.dat` for the "accepted descriptors" log line.
  - Notes / risks: This is the pre-filter count, not the post-filter count. Both are useful; post-filter
    count is derivable from the curated CSV column list.

- [ ] **5. Missingness per column**
  - Proposed JSON location: `missingness`
  - Current status: Computed internally but not saved
  - Evidence in repo: `load_database()` removes columns with <90% data and logs only the aggregate count
    ("Removed N column(s) with <90% data"). Per-column NaN counts are not logged.
  - Existing function/file: `robert/utils.py` → `load_database()` (internal only)
  - Needed action: Load original CSV and compute `df[descriptor_cols].isna().sum()` per column.
    This is a lightweight pandas operation on the raw CSV; no modeling logic required.
  - Notes / risks: Must be computed before ROBERT's imputer runs, so use the original CSV, not the
    curated CSV (imputed values will show zero missingness).

- [ ] **6. Target-property summary**
  - Proposed JSON location: `target_summary`
  - Current status: Not currently collected
  - Evidence in repo: ROBERT does NOT compute or log regression target stats (min, max, mean, std).
    For classification, `check_clas_problem()` in `utils.py` validates class counts but does not save them.
    `CURATE_data.dat` has no target summary section.
  - Existing function/file: None
  - Needed action: Load original CSV (or `*_CURATE.csv`), select the y column, compute descriptive stats.
    For classification, compute `value_counts()` for class distribution.
    This is entirely read-only pandas logic in `agent/`.
  - Notes / risks: Must determine problem type (reg/clas) from `CURATE_options.csv` or `run_context.json`.

- [ ] **7. Target distribution / imbalance summary**
  - Proposed JSON location: `target_imbalance`
  - Current status: Not currently collected
  - Evidence in repo: For classification, `check_clas_problem()` validates minimum class size (≥5)
    but does not save class ratios. For regression, no distribution metrics are computed anywhere.
  - Existing function/file: `robert/utils.py` → `check_clas_problem()` (read-only reference for logic)
  - Needed action: For classification, compute class counts and minority class percent from target column.
    For regression, compute a simple histogram or leave as null (histogram is optional in schema).
  - Notes / risks: Imbalance metrics only meaningful for classification. Keep null for regression.

- [ ] **8. Constant and near-constant descriptor columns**
  - Proposed JSON location: `constant_columns`, `near_constant_columns`
  - Current status: Already available in stable output
  - Evidence in repo: `correlation_filter()` in `utils.py` logs "- COLNAME: all the values are the same"
    to `CURATE_data.dat` for exact constant columns. Near-constant columns are NOT separately flagged.
  - Existing function/file: `robert/utils.py` → `correlation_filter()` (log text is stable)
  - Needed action: Parse `CURATE_data.dat` for "all the values are the same" lines.
    Near-constant columns can optionally be computed by the agent from the curated CSV
    (e.g., variance < threshold), but this adds no ROBERT-defined threshold to reference.
    Leave `near_constant_columns` as empty list for v1.
  - Notes / risks: Parsing the dat file text is the correct approach here — do not recompute.

- [ ] **9. Non-numeric descriptor columns**
  - Proposed JSON location: `non_numeric_descriptors`
  - Current status: Already available in stable output
  - Evidence in repo: `categorical_transform()` logs detected categorical (string) columns to `CURATE_data.dat`:
    "Initial descriptors: COL1, COL2 ... Generated descriptors: ..." or
    "No categorical variables were found".
  - Existing function/file: `robert/utils.py` → `categorical_transform()` (log text is stable)
  - Needed action: Parse `CURATE_data.dat` for the categorical variables section.
  - Notes / risks: After categorical transform, original string columns no longer exist in the curated CSV.
    Log parsing is the only way to recover the original column names.

- [ ] **10. Highly correlated descriptor summary**
  - Proposed JSON location: `highly_correlated_pairs`
  - Current status: Already available in stable output
  - Evidence in repo: `correlation_filter()` logs "- COLNAME removed (R2 = X.XX with OTHER)" to `CURATE_data.dat`.
    This is the most useful correlation evidence for the companion bot.
  - Existing function/file: `robert/utils.py` → `correlation_filter()` (log text is stable)
  - Needed action: Parse `CURATE_data.dat` for the correlation filter section.
    Extract removed column name, R² value, and kept column name as structured fields.
  - Notes / risks: Do NOT recompute the correlation matrix. The log is the canonical source.
    ROBERT's reproducibility guarantees mean the log is deterministic.

- [ ] **11. Top simple descriptor-target correlations**
  - Proposed JSON location: `top_descriptor_target_correlations`
  - Current status: Computed internally but not saved
  - Evidence in repo: `correlation_filter()` computes `r2_with_y` dict for every descriptor, but uses it
    only to decide which of a correlated pair to keep. The values are NOT logged for retained descriptors.
    Only dropped descriptors appear in the log ("R2 = X with y values" for corr_filter_y case, not the default).
  - Existing function/file: `robert/utils.py` → `correlation_filter()` (internal dict, not logged)
  - Needed action: Load the `*_CURATE.csv` (post-filter curated database, archived in run)
    and compute `scipy.stats.linregress(col, y).rvalue**2` for each remaining descriptor column.
    This exactly replicates ROBERT's own calculation without modifying any ROBERT file.
  - Notes / risks: Use the curated (post-filter) CSV, not the original. Correlations on the full
    original descriptor set are less meaningful because ROBERT already filtered them.
    This is one of the few cases where duplicating a few lines of ROBERT logic is justified.

- [ ] **12. Basic SMILES validity and element summary**
  - Proposed JSON location: `smiles_summary`
  - Current status: Not currently collected
  - Evidence in repo: Standard CURATE does not parse or validate SMILES. SMILES columns appear in the
    `ignore` list and pass through unchanged. AQME module handles SMILES validation separately.
    No SMILES validity metrics are saved in any stable CURATE output.
  - Existing function/file: None for standard runs. AQME module has separate logic.
  - Needed action: If a SMILES column is detected (column name starts with "smiles", case-insensitive),
    use RDKit (already a ROBERT dependency) to validate each SMILES and collect unique elements.
    Set `smiles_summary` to null if no SMILES column is detected.
  - Notes / risks: RDKit is available in the robert conda environment. Do not attempt element parsing
    without RDKit — regex-based element extraction from SMILES strings is unreliable.
    This measurement is low priority for non-AQME runs.

---

### Implementation Plan (Approved)

**Approved constraint:** All code in `agent/`. No modifications to `robert/`.

**Where generated:**
After the CURATE step completes and its outputs are archived, the profiler is called once.
Entry point: add a `profile_dataset(run_archive_dir)` function to `agent/robert_helper.py`.

**Execution order:**
1. Open `CURATE/CURATE_options.csv` → get y, names, ignore, csv_name (original CSV path).
2. Parse `CURATE/CURATE_data.dat` → extract logged measurements (1, 4, 8, 9, 10).
3. Load original CSV from path in step 1 (or fall back to `CURATE/*_CURATE.csv`).
4. Compute remaining measurements (2, 3, 5, 6, 7) from original CSV + options.
5. Load `CURATE/*_CURATE.csv` → compute measurement 11 (descriptor-target correlations).
6. If SMILES column detected in step 3 → compute measurement 12 using RDKit.
7. Write `dataset_profile.json` to the run archive alongside `run_context.json`.

**Proposed file:** `agent/run_archive/<run_id>/dataset_profile.json`

**How the companion bot uses this:**
- Load alongside `run_context.json` at chat startup.
- Provides context for questions about the original dataset without needing the raw CSV.
- Enables comparisons like "you started with 133 rows and 5 descriptors; ROBERT retained 3."

**How to test:**
Run `profile_dataset()` on the existing `20260515_173258__Hvapor` archive.
Verify: row_count=133, candidate_descriptor_count=5, constant_columns includes "IF" and "SS",
highly_correlated_pairs shows IF→SGBP and SS→SGBP with R²=1.0.

**Compatibility / privacy risks:**
- Only summary statistics and column names are stored. No raw data, no SMILES strings, no identifiers.
- The original CSV absolute path is stored in `source_csv_path` for provenance only. This is already
  stored in `CURATE_options.csv`, so no new privacy exposure.
- If the original CSV is on a shared or network drive, the path string reveals that. Acceptable for
  a local research tool.


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
- [ ] Add clickable starter questions for the chemist-facing interpretation workflows.
- [ ] Add automatic follow-up question suggestions based on the current run context.
- [ ] Enforce the standard answer structure and plain-language chemist-facing tone.
- [ ] **Test**: Chat works, API key not visible in DevTools network tab, graceful error messages

### Phase 3: ROBERT Integration (Weeks 3–4)
- [ ] Create `agent/ui/robert_context.py` (load run_context.json + diagnosis.json)
- [ ] Enhance chat prompts (inject diagnostic evidence into LLM context)
- [ ] Implement run selector (choose from archived runs, update left panel)
- [ ] Add a dedicated "What did ROBERT do with my data?" explanation view from original CSV through curation to final descriptor set.
- [ ] Surface original feature count, removed descriptors, retained descriptors, and final model descriptors with provenance.
- [ ] **Test**: Load different runs, verify chat context switches, spot-check LLM responses reference actual metrics

### Phase 4: Polish & Extensibility (Weeks 4+, Optional)
- [ ] Export chat history to markdown or JSON
- [ ] Dark mode / light mode toggle
- [ ] Session persistence (store chat history locally)
- [ ] Multi-run comparison (side-by-side analysis)
- [ ] Share diagnostic results (generate shareable HTML report)
- [ ] Guided report walkthrough, one section at a time.
- [ ] Educational mode / "teach me what ROBERT is doing."
- [ ] Simplified notebooks so each section starts with a plain-language description followed by one simple function call.
- [ ] Browser-based ROBERT execution from uploaded CSV as a separate future phase.
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
