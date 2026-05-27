# PROJECT WORKFLOW TRACE (UPDATED)

This document explains how the ROBERT companion workflow currently operates, in plain English.

Scope note:
- This is a companion layer around ROBERT.
- ROBERT remains the authority for model scoring and report generation.
- The companion reads ROBERT outputs, organizes evidence, and helps explain the score.

Evidence basis:
- Repository files and notebook content were inspected.
- Notebook execution state was checked from notebook metadata.
- Current run archives were inspected for artifact presence.
- ROBERT core code was not modified.

## 1. Executive Summary

The workflow has five practical stages:
1. Run ROBERT and archive the outputs so they are not overwritten.
2. Extract evidence from ROBERT output files into structured companion files.
3. Build deterministic diagnosis notes from that evidence.
4. Open a local UI to view evidence and ask questions.
5. Optionally use a local knowledge index or OpenAI for explanation wording.

What matters most for collaborators:
- The ROBERT score is still ROBERT's score.
- The companion does not create a competing score.
- Chat and guided questions are safety-gated by evidence checks.
- Most archived runs are complete, but not all runs have every companion artifact.

## 2. Active Workflow

Current working sequence used by the companion:
1. `agent/robert_run_wrapper.ipynb`
- Optionally runs ROBERT from the command line.
- Archives ROBERT folders (`CURATE`, `GENERATE`, `VERIFY`, `PREDICT`) into a timestamped run folder.
- Writes a `run_manifest.json` for reproducibility.

2. `agent/extract_context.ipynb`
- Reads archived ROBERT files, especially `PREDICT_data.dat` and `VERIFY_data.dat`.
- Builds structured evidence outputs including `run_context.json` and `llm_evidence.json`.
- Reconstructs score fields using ROBERT's own scoring logic (not a new scoring system).
- Creates a portable bundle (`llm_run_bundle/`) and report assets.

3. `agent/diagnose_score.ipynb`
- Reads `run_context.json`.
- Produces `diagnosis.json` and `diagnosis_summary.md`.
- Adds deterministic interpretation observations to help explain likely reasons behind the score.

4. `agent/ui/run_ui_from_notebook.ipynb` or `start_ui.py`
- Starts the local dashboard.
- Loads run evidence and diagnosis files.
- Shows metrics, narrative, and figures.
- Enables question answering with guardrails.

5. Optional local knowledge index
- `agent/ui/Build_Local_Knowledge_Index.ipynb` can build a local search index for background reference materials.

## 3. Notebook-By-Notebook Explanation

### `agent/robert_run_wrapper.ipynb`

Purpose:
- Preserve each ROBERT run in a separate archive folder.

Why this matters:
- ROBERT outputs use fixed folder names at the project level.
- Without archiving, a new run can overwrite previous outputs.

Main outputs:
- `agent/run_archive/<timestamp>__<dataset>/outputs/...`
- `run_manifest.json`

### `agent/extract_context.ipynb`

Purpose:
- Convert archived ROBERT outputs into companion evidence files that are easier to consume.

Why this matters:
- ROBERT evidence is mostly in DAT files and report artifacts.
- The UI and chat layer need a structured, consistent context.

Main outputs:
- `run_context.json`
- `llm_evidence.json`
- `llm_run_bundle/`
- `report_assets/`
- `dataset_profile.json` (when available)

### `agent/diagnose_score.ipynb`

Purpose:
- Generate explanation-ready diagnosis notes from `run_context.json`.

Why this matters:
- Collaborators need short, interpretable observations, not raw output only.

Main outputs:
- `diagnosis.json`
- `diagnosis_summary.md`

### `agent/verify_extraction_parity.ipynb`

Purpose:
- Check whether extracted values match source DAT files.

Term definition:
- Parity means "do extracted values match the original source values?"

Current status:
- This notebook exists and defines a full parity flow.
- Notebook cells are currently unexecuted in the present notebook metadata snapshot.

### `agent/ui/run_ui_from_notebook.ipynb`

Purpose:
- Help users install dependencies and launch the local UI from a notebook.

Why this matters:
- Gives a guided startup path for non-developer workflows.

### `agent/ui/Build_Local_Knowledge_Index.ipynb`

Purpose:
- Build a local retrieval index for background documents.

Term definition:
- RAG (retrieval-augmented generation) here means: first retrieve relevant local document snippets, then use them as extra context during answering.

Important boundary:
- This local knowledge is supplemental context.
- It does not replace run-specific ROBERT evidence.

## 4. UI/App Workflow

The local app is built with Dash.

Term definition:
- Dash is a Python framework for building interactive web apps.

What happens when a run is selected:
1. The app loads `run_context.json`.
2. It loads diagnosis files and dataset profile (if present).
3. It runs a parity check against source DAT files.
4. It renders metrics, observations, narrative text, and evidence images.
5. It enables or blocks chat depending on parity status.

Term definitions:
- Callback: a function that runs automatically after a UI action (for example, changing run selection or pressing Send).
- Heuristic: a rule-based answer path that does not require an LLM call.

Current behavior summary:
- Typed chat and guided FAQ are both wired into current UI callbacks.
- Guided FAQ is active (starter questions and grouped question launcher).
- A report-summary button exists and can produce a whole-report summary via OpenAI when configured.

## 5. RAG / Knowledge-Base Workflow

The local knowledge flow is:
1. Collect supported files (`.txt`, `.md`, `.pdf`) from `agent/ui/knowledge/`.
2. Split text into chunks.
3. Build a BM25 index and save it in `agent/ui/storage/`.
4. Retrieve top matching chunks for relevant questions.

Term definition:
- JSON is a structured text format used to store data files.

Files produced by local indexing:
- `agent/ui/storage/chunks.jsonl`
- `agent/ui/storage/bm25.pkl`
- `agent/ui/storage/manifest.json`

Current-state clarification:
- Earlier notes suggested local retrieval integration was still future work.
- Current UI/chat code already uses local retrieval in supported answer paths.

## 6. JSON / Evidence Files Produced

This section explains the key outputs in collaborator language.

`run_manifest.json`
- Created during archiving.
- Records how a run was produced (dataset, command, archived modules, report references).

`run_context.json`
- Main structured evidence file used by the companion.
- Feeds diagnosis, UI display, and chat evidence packing.

`llm_evidence.json`
- LLM-facing evidence payload with policy constraints.
- Explicitly frames ROBERT outputs as source of truth.

`dataset_profile.json`
- Compact dataset context (when available), based on curated outputs and dataset files.

`diagnosis.json`
- Machine-readable interpretation observations and derived convenience values.

`diagnosis_summary.md`
- Human-readable diagnosis narrative.

`llm_run_bundle/`
- Portable package of core evidence files plus routing metadata (`bundle_index.json`).

`report_assets/`
- Archived report PDFs for viewing.

## 7. What Is Verified

Verified from current inspection:
1. Workflow stage separation is in place: wrapper -> extraction -> diagnosis -> UI.
2. ROBERT score authority remains in ROBERT logic (`calc_score` path), not companion scoring.
3. Guided FAQ is implemented and wired in current UI/chat paths.
4. Local retrieval modules are implemented and currently referenced in chat paths.
5. Runtime parity gating exists in the UI and controls chat availability.
6. Notebook execution metadata shows:
- `robert_run_wrapper.ipynb`, `extract_context.ipynb`, `diagnose_score.ipynb`, and `run_ui_from_notebook.ipynb` have executed cells.
- `verify_extraction_parity.ipynb` currently has no executed cells.
7. Current run archive counts (top-level per run):
- Total runs: 9
- `run_context.json`: 8
- `llm_evidence.json`: 8
- `diagnosis.json`: 8
- `diagnosis_summary.md`: 8
- `dataset_profile.json`: 5
- `outputs/`: 9
- `report_assets/`: 8
- `llm_run_bundle/`: 8

Interpretation of these counts:
- Most runs are companion-complete.
- One archived run appears intentionally or effectively partial/incomplete.

## 8. What Is Not Yet Verified

Not yet verified in this pass:
1. Full parity notebook execution results, because `verify_extraction_parity.ipynb` is currently unexecuted.
2. Whether every historical/future ROBERT DAT wording variant is fully covered by the extractor parser logic.
3. End-to-end PDF-to-JSON parity, because PDF parity remains a placeholder in the parity notebook.
4. Runtime stability of `start_ui.py` across all local environments, since terminal history shows intermittent non-zero exits despite successful imports and notebook-based launch paths.

## 9. Known Gaps and Uncertainties

Known gaps:
1. Artifact completeness is uneven across archived runs (especially dataset profiling artifacts).
2. Parity assurance is split across two layers:
- Notebook parity design exists but is not recently executed.
- UI runtime parity check is active.
3. Some status notes in older audit documents are now stale relative to current code (especially guided FAQ and local retrieval integration).

Uncertainty labels:
- Not determined from static inspection: complete parser robustness across all possible ROBERT output text variants.
- Not determined from static inspection: whether all collaborator environments will reproduce identical startup behavior for the UI launcher script.

## 10. Wrapper Approach vs Future ROBERT-Native JSON Export

Current wrapper approach (today):
- ROBERT runs as-is.
- Companion notebooks read ROBERT outputs after the run.
- Companion builds structured JSON evidence files in a separate layer.

Strengths of current approach:
1. No changes to ROBERT core behavior are required.
2. Companion logic remains auditable and optional.
3. Existing ROBERT users can adopt companion tools incrementally.

Limitations of current approach:
1. Parsing robustness depends on stable text patterns in DAT outputs.
2. Multiple post-processing steps are needed before UI/chat is fully enabled.
3. Archive completeness can vary run-to-run.

Potential future ROBERT-native JSON export:
- ROBERT itself could emit stable machine-readable JSON outputs directly.

Potential benefits:
1. Less parser fragility.
2. Simpler and more consistent downstream extraction.
3. Clearer contract between ROBERT and companion tools.

Boundary condition:
- This updated trace documents the current wrapper architecture only.
- No ROBERT-core change is proposed or implemented here.

---

## Short Glossary (for non-developers)

- JSON: structured text format for data files.
- Dash: Python framework for an interactive web app.
- Parity: match-check between extracted values and source files.
- Heuristic: rule-based answer path (without calling an LLM).
- Callback: code that runs in response to a UI action.
- RAG: retrieve relevant local documents first, then use them as extra context for generated answers.
