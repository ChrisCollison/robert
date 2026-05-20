# User Instructions: Run ROBERT, Extract Diagnostics, and Use the UI

Purpose:
This guide is the required workflow for using the ROBERT diagnostics UI.
The UI is designed for extracted diagnostic runs, not raw ROBERT output folders.

## Workflow Overview

Run notebooks in this order:
1. `agent/robert_run_wrapper.ipynb`
2. `agent/extract_context.ipynb`
3. `agent/diagnose_score.ipynb`
4. `agent/ui/run_ui_from_notebook.ipynb`

If you skip steps 2 or 3, the run will not appear as a usable diagnostic run in the UI.

## Step 1: Run ROBERT and Archive Outputs

Notebook:
- `agent/robert_run_wrapper.ipynb`

What to set:
- `DATASET_RELATIVE`: dataset path or filename under `Databases/`
- `ROBERT_OPTIONS`: at minimum set the dataset ID column (`names`) and target column (`y`)
- `RUN_ROBERT = True`

What to execute:
- Run the notebook top to bottom.

What success looks like:
- A new folder is created under `agent/run_archive/`, for example:
  - `agent/run_archive/<timestamp>__<dataset_name>/`
- `run_manifest.json` exists in that folder.
- `outputs/CURATE`, `outputs/GENERATE`, `outputs/VERIFY`, `outputs/PREDICT` are archived.

## Step 2: Extract Structured Context

Notebook:
- `agent/extract_context.ipynb`

What to set:
- `RUN_FOLDER`: point it to the run folder created in Step 1.
- **Default behavior**: if `RUN_FOLDER = None` (the default), the notebook automatically
  selects the most recent archived run. If you just completed a ROBERT run in Step 1,
  you can run `extract_context.ipynb` end to end without changing any settings.

What to execute:
- Run the notebook cells in order.

What success looks like:
- `run_context.json` is created in the run folder (or bundle path used by the notebook).
- Extraction warnings (if any) are printed, but the notebook completes.

## Step 3: Generate Diagnosis Files

Notebook:
- `agent/diagnose_score.ipynb`

What to set:
- `RUN_CONTEXT_PATH`: point it to the `run_context.json` generated in Step 2.

- **Default behavior**: if `RUN_CONTEXT_PATH = None` (the default), the notebook automatically
  selects the most recent archived run. If you just completed a ROBERT run in Step 1,
  you can run `diagnose_score.ipynb` end to end without changing any settings.

What to execute:
- Run the notebook cells in order.

What success looks like:
- `diagnosis.json` is created.
- `diagnosis_summary.md` is created.

## Step 4: Launch the UI

Notebook:
- `agent/ui/run_ui_from_notebook.ipynb`

What to execute:
1. Run Step 1 cell (path/config check)
2. Run Step 2 cell (dependencies, if needed)
3. Optional Step 3 cell (API key/model checks)
4. Run Step 4 cell (start server)
5. Run Step 5 cell (open browser)

Expected URL:
- `http://127.0.0.1:8050`

## Step 5: Refresh Runs in UI

In the UI header:
- Click `Refresh Runs` after generating a new extracted/diagnosed run.

Then:
- Select the new run in `Select a run:`.

## Required Files for UI Availability

A run is considered UI-ready only when these exist for the same run folder:
- `run_context.json`
- `diagnosis.json`
- `diagnosis_summary.md`

Raw run folders with only `run_manifest.json` and archived module outputs are not sufficient.

## Common Issue: "My new run is not in the dropdown"

Cause:
- Step 2 and/or Step 3 was skipped.

Fix:
1. Run `agent/extract_context.ipynb` for that run.
2. Run `agent/diagnose_score.ipynb` for that run.
3. In the UI, click `Refresh Runs`.

## Recommended Fast Checklist

Before opening the UI, verify all three are true:
1. `agent/run_archive/<run>/run_context.json` exists
2. `agent/run_archive/<run>/diagnosis.json` exists
3. `agent/run_archive/<run>/diagnosis_summary.md` exists

If all are present, the run should be selectable and usable in the UI.
