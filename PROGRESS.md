# ROBERT Agent — Development Progress Log

This file is a running narrative record of what has been built, why, and what was learned at each step.
It is intended for review at any point to understand the state of the project without reading code.

For the operational task list, see `TODO.md`.
For the append-only audit log of completed steps, see `COMPLETED_TASKS.md`.
For technical anchors from repository inspection, see `agent/REFERENCE_NOTES.md`.

---

## Project Mission

Build a companion layer for ROBERT that helps chemists understand their ROBERT scores.

The first question the agent must answer is:

> "Why did I get this ROBERT score?"

The agent reads ROBERT output folders, extracts structured evidence, applies rule-based
diagnostic flags, and produces a plain-language explanation grounded in that evidence.

The `robert/` directory is read-only. All new code lives in `agent/`.

---

## Phase 1 — Repository Inspection and Governance (2026-04-24)

**Goal:** Understand the ROBERT codebase before writing any agent code.

**What was done:**

- Inspected `robert/report_utils.py` and located `calc_score()` — the function that
  computes the ROBERT score. It reads from PREDICT and VERIFY outputs and combines
  sub-scores for CV performance, test performance, prediction stability (SD),
  CV-test agreement, flawed model tests, and sorted cross-validation.
- Confirmed that the score has two variants per run: `No PFI` (all descriptors) and
  `PFI` (only descriptors that pass the Permutation Feature Importance filter).
- Mapped the four output folders ROBERT creates: `CURATE/`, `GENERATE/`, `VERIFY/`,
  `PREDICT/` — and identified the primary parse targets as `PREDICT_data.dat` and
  `VERIFY_data.dat`.
- Established governance documentation:
  - `AGENTS.md`: rules, guardrails, and sources of truth (read-only ROBERT policy,
    no LLM in core, API keys via env vars only, notebook-first development).
  - `agent/REFERENCE_NOTES.md`: verified technical anchors from the inspection.
  - `TODO.md`: operational task list.
  - `COMPLETED_TASKS.md`: append-only audit log.

**Branch created:** `agent-score-explainer` (tracked to personal fork `ChrisCollison/robert`).

---

## Phase 2 — Schema and Planning (2026-05-13, session 1)

**Goal:** Define what the extractor must produce before writing any parsing code.

**What was done:**

- Created `agent/run_context_schema.md` documenting the full schema for `run_context.json`.
- Defined the V1 must-have subset: a focused list of fields extractable from PREDICT and
  VERIFY alone, covering prediction type, model identity, CV/test metrics, descriptor
  counts, verification test results, and data availability flags.
- Defined a parser behavior contract: null-safe (never crash on missing files or sections),
  stable output shape (all V1 keys always present even if null), and a warning list for
  conversion failures.
- Defined acceptance criteria: must pass on a complete regression run, a complete
  classification run, and an intentionally incomplete run.
- Added notebook-first development rules to `AGENTS.md`: all new implementation in
  Jupyter notebooks in `agent/`, plain-language markdown before each code cell,
  shared helpers to `agent/robert_helper.py` only.

---

## Phase 3 — Run Wrapper Notebook (2026-05-13, session 2)

**Goal:** Build a reproducible way to run ROBERT and archive its outputs per run.

**Problem being solved:** ROBERT always writes to the same fixed folder names
(`CURATE/`, `GENERATE/`, `VERIFY/`, `PREDICT/`). Without archiving, each new run
overwrites the previous one, making it impossible to compare runs or build an
extractor that reads a specific run.

**What was built:** `agent/robert_run_wrapper.ipynb`

This notebook:
1. Lets the user pick a dataset by filename or relative path (fuzzy resolution included).
2. Previews the dataset columns and suggests `names`, `y`, and `ignore` options.
3. Builds the ROBERT CLI command automatically from a `ROBERT_OPTIONS` dictionary.
4. Optionally runs ROBERT as a subprocess.
5. Archives `CURATE/`, `GENERATE/`, `VERIFY/`, `PREDICT/` into a timestamped folder
   under `agent/run_archive/<timestamp>__<dataset_name>/`.
6. Writes `run_manifest.json` recording the exact command, dataset path, return code,
   and which folders were archived.

**Key design decisions:**
- `RUN_ROBERT = False` by default — lets the user inspect the resolved command before
  committing to a run.
- `COPY_INSTEAD_OF_MOVE = False` by default — moves folders to avoid stale leftovers
  in the project root.
- Project root is inferred by walking parent directories looking for `AGENTS.md` + `robert/`,
  so the notebook works regardless of which directory the kernel started in.
- Dataset resolution does: exact match → partial stem match → fuzzy suggestion fallback.

**Databases added:** `Databases/Regression/` and `Databases/Clasification/` with example
datasets covering regression (Hvapor, ddG, barrier, solubility, logKOW, etc.) and
classification (TOF, outcome, imbalanced Ni catalysis, etc.).

**First ROBERT run completed:** Hvapor dataset (133 compounds, 5 descriptors → 3 after
curation, MVL model, regression). Archived in `agent/run_archive/20260513_160812__Hvapor/`.

---

## Phase 4 — Context Extractor Notebook (2026-05-13, session 3)

**Goal:** Parse the archived ROBERT output files and produce a structured `run_context.json`
that captures all evidence relevant to the ROBERT score.

**What was built:** `agent/extract_context.ipynb`

This notebook:
1. Accepts a run folder path (or auto-selects the most recent run).
2. Checks which `.dat` files are present and sets availability flags.
3. Parses `PREDICT_data.dat` for both the No PFI and PFI model variants, extracting:
   - model type and target property name,
   - cross-validation type (e.g. 10x 5-fold),
   - CV and test R², RMSE, MAE,
   - number of training and test points,
   - number and names of descriptors,
   - training:descriptor ratio,
   - average prediction uncertainty (SD) on the test set,
   - y-value range of the training data,
   - outlier counts (train and test),
   - y-value distribution across quartiles,
   - prediction type (regression vs classification, auto-detected from line format).
4. Parses `VERIFY_data.dat` for both variants, extracting:
   - results of the three baseline tests (y_mean, y_shuffle, onehot): PASSED/UNCLEAR/FAILED,
   - flawed model score contribution (penalty for failed/unclear tests),
   - sorted cross-validation R² and RMSE lists,
   - original CV RMSE and 15%/30% alert thresholds.
5. Parses `CURATE_data.dat` for initial/final datapoint counts and feature reduction summary.
6. Reads `run_manifest.json` for provenance (command used, dataset path).
7. Assembles all extracted values into `run_context.json` written to the run folder.

**Parser design principles:**
- All regex patterns were written against the exact line formats from a real Hvapor run
  (not inferred from code or documentation).
- Every field defaults to `null` on parse failure — no crashes on missing files or sections.
- Both `reg` and `clas` output formats are handled (R²/RMSE vs MCC).
- `parser_warnings` field collects any conversion failures for auditability.

**What `run_context.json` is used for:**
- Input to the next notebook: `agent/diagnose_score.ipynb` (not yet built).
- Provides the structured evidence layer that the diagnosis and explanation layers will read.
- The `score.no_pfi` and `score.pfi` fields are null in V1 — score reconstruction is
  deferred to the diagnosis notebook.

---

## Phase 5 — Diagnosis Notebook (2026-05-13, session 4)

**Goal:** Convert extracted evidence into deterministic, auditable diagnosis outputs.

**What was built:** `agent/diagnose_score.ipynb`

This notebook:
1. Loads a selected `run_context.json` (or auto-selects the most recent one).
2. Computes score-relevant component values for both `no_pfi` and `pfi` variants.
3. Mirrors ROBERT threshold logic from `report_utils.py` where available:
  - scaled RMSE/MCC bucket scores,
  - R2 penalty thresholds,
  - CV-test RMSE factor score,
  - SD coverage score,
  - VERIFY flawed-model and sorted-CV contributions.
4. Emits deterministic evidence-linked flags for:
  - low CV/test quality,
  - large CV-test discrepancies,
  - failed VERIFY tests,
  - high outlier fraction,
  - y-distribution imbalance,
  - missing evidence sections.
5. Writes diagnosis artifacts next to `run_context.json`:
  - `diagnosis.json`
  - `diagnosis_summary.md`

**Scope notes:**
- This is rule-based and deterministic (no LLM calls).
- This does not modify ROBERT scoring code; it is a companion diagnosis layer.
- Some classification score terms present in `report_utils.py` (for example `descp_score`) are
  referenced there but not populated in the ROBERT code path; the notebook treats these as
  unavailable evidence in V1.

---

## Next Steps

1. **Validate diagnosis on the archived Hvapor run:** execute `agent/diagnose_score.ipynb`
  and confirm `diagnosis.json` + `diagnosis_summary.md` are generated with expected flags.

2. **Validate on a classification run:** pick a dataset from `Databases/Clasification/`,
  run wrapper -> extractor -> diagnosis. Confirm MCC-oriented branches populate and RMSE-only
  logic stays null-safe.

3. **Validate on an incomplete run:** create or capture a missing-module run and confirm
  diagnosis reports evidence gaps instead of failing.

4. **Refine diagnosis thresholds where needed:** lock any agent-only thresholds with
  explicit rationale, then keep them stable for reproducible comparisons.

5. **Commit and push** diagnosis notebook plus updated tracking docs to
  `myfork/agent-score-explainer`.

---

## Phase 6 — UI Readability Execution Start (2026-05-16)

**Goal:** Make the diagnostics panel readable and evidence-driven before enabling API-backed chat.

**What was done:**

- Added an explicit mandatory plan-approval checkpoint to governance in `AGENTS.md`:
  - plan must be presented,
  - user approval must be received,
  - only then implementation begins.
- Fixed UI launch stability for root-level startup (`start_ui.py`) and script import paths (`agent/ui/callbacks.py`).
- Updated run discovery/loader behavior to match normalized archive structure:
  - context from run root or `llm_run_bundle/`,
  - diagnosis files from run root with legacy fallback.
- Reworked document rendering in UI callbacks to use structured Dash components instead of literal HTML strings:
  - metrics table,
  - markdown diagnosis narrative,
  - evidence image cards.
- Expanded metrics extraction for the interface to show core No PFI/PFI model and VERIFY evidence in one view.
- Added first-pass evidence image display using already-generated artifact image files from run outputs.

**Current status:**

- UI now starts and discovers archived runs.
- Diagnostic content is now rendered in structured form (not escaped HTML text).
- Evidence images are wired for display if run artifacts are present.

**Immediate next step:**

- Add severity-oriented styling for observations and execute readability smoke tests across both available runs.

---

## Phase 7 — Severity Styling + Heuristics-First Chat (2026-05-16)

**Goal:** Start Phase 2A implementation while preserving cost-control policy (deterministic answers first, no mandatory API usage).

**What was done:**

- Added structured observation rendering with explicit severity badges in the diagnostics panel:
  - `PASSED` -> success,
  - `info` -> neutral,
  - `warning` -> warning,
  - `failed` -> danger.
- Enabled the chat panel input/send flow and wired callback handling for user messages.
- Implemented a deterministic heuristics-first responder in `agent/ui/chat.py` for common questions:
  - why score,
  - CV/test gap,
  - VERIFY status,
  - descriptors/features,
  - outliers,
  - warnings/missing evidence.
- Added explicit source tagging for assistant responses in UI:
  - `Heuristic`,
  - `Fallback Disabled`,
  - `No API Key`.
- Live-tested the updated app behavior in local Dash run:
  - run loads,
  - severity observations render,
  - heuristic response generated without API key.

**Current status:**

- Phase 1B semantic styling item is implemented.
- Phase 2A core heuristics routing is implemented.
- Full two-run smoke checklist is now completed (see `agent/ui/PHASE1B_SMOKE_TEST_2026-05-16.md`).
- Robustness/classification validation remains pending.

**Delta from smoke execution:**

- Both archived Hvapor runs passed readability checks for metrics, observations, narrative, and image evidence refresh on run switch.
- One chat intent gap was found for phrasing `verification tests` and fixed in `agent/ui/chat.py`.
- Re-test confirmed heuristic response source for `Did any verification tests fail?` on both runs.

---

## Phase 8 — Classification + Robustness Validation (2026-05-16)

**Goal:** Execute the next validation gates after UI smoke completion: classification branch correctness and missing-file robustness.

**What was done:**

- Ran a full classification ROBERT workflow on `AQME-ROBERT_interpret_TOF_clasif.csv` (`--type clas`) and archived outputs as a new run.
- Executed `extract_context.ipynb` and `diagnose_score.ipynb` on that classification run.
- Found and fixed a parser mismatch in `extract_context.ipynb` where classification metrics were emitted by ROBERT as:
  - `Accur. = ..., F1 score = ..., MCC = ...`
  rather than MCC-first ordering.
- Extended parser logic to support both ordering styles and updated classification `pred_type` detection accordingly.
- Re-ran extraction/diagnosis and confirmed classification fields now populate correctly (`pred_type=clas`, MCC/F1/accuracy parsed for both No PFI and PFI).
- Created an intentionally incomplete run containing only `PREDICT` outputs and re-ran extraction/diagnosis.
- Confirmed null-safe behavior with explicit missing evidence representation for absent `VERIFY`, `CURATE`, and `GENERATE` sections.

**Validation artifacts:**

- `agent/validation_classification_report_2026-05-16.md`
- `agent/validation_robustness_report_2026-05-16.md`

**Current status:**

- Classification validation gate: complete.
- Missing-file robustness gate: complete.
- Remaining primary validation item: full regression validation pass and explicit report-vs-diagnosis comparison item in TODO.

---

## Architecture Summary

```
robert_run_wrapper.ipynb
    └── runs ROBERT → archives outputs → writes run_manifest.json
            │
            ▼
    agent/run_archive/<timestamp>__<dataset>/
        ├── outputs/
        │   ├── CURATE/CURATE_data.dat
        │   ├── GENERATE/GENERATE_data.dat
        │   ├── VERIFY/VERIFY_data.dat
        │   └── PREDICT/PREDICT_data.dat
        ├── run_manifest.json
        └── run_context.json   ← written by extract_context.ipynb
                │
                ▼
        extract_context.ipynb
            └── parses .dat files → writes run_context.json
                        │
                        ▼
            diagnose_score.ipynb
                └── rule-based flags → score explanation
                            │
                            ▼
                explain.ipynb  (not yet built)
                    └── plain-language report for chemists
                            │
                            ▼ (optional, disabled by default)
                    LLM translation layer
```

The `robert/` directory is never touched at any step.
