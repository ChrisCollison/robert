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

## Next Steps

1. **Run `agent/extract_context.ipynb`** on the archived Hvapor run and verify that
   `run_context.json` is fully populated with no unexpected nulls.

2. **Validate on a classification run:** pick a dataset from `Databases/Clasification/`,
   run it through the wrapper, then run the extractor. Confirm RMSE fields are null and
   MCC fields are populated.

3. **Validate on an incomplete run:** create a run folder with only CURATE outputs
   present (or deliberately stop ROBERT early) and confirm the extractor sets
   `available.*` correctly and does not crash.

4. **Build `agent/diagnose_score.ipynb`:** apply rule-based flags to the extracted
   context. Rules should cover:
   - Small dataset (N < 50, N < 100)
   - Low CV R² / high RMSE relative to y range
   - CV vs test discrepancy (possible overfitting or data leakage)
   - Failed VERIFY baseline tests
   - Poor extrapolation (sorted CV performance)
   - Skewed y distribution (quartile imbalance)
   - High outlier fraction

5. **Commit and push** the extractor notebook and this progress log to
   `myfork/agent-score-explainer`.

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
            diagnose_score.ipynb  (not yet built)
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
