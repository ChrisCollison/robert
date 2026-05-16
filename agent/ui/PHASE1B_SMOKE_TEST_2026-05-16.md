# Phase 1B UI Smoke Test Report

Date: 2026-05-16
Environment: local Dash app via `start_ui.py`
Python: `/Users/cjcscha/mambaforge/envs/robert/bin/python`
Runs tested:
- `20260515_173258__Hvapor`
- `20260513_160812__Hvapor`

## Scope

This smoke test validates Phase 1B UI readability and heuristics-first chat behavior:
- app startup and run discovery,
- diagnostics rendering (metrics, observations, narrative, images),
- chat routing/source labels,
- no-key mode behavior.

## Results

### 1. App startup and run discovery
- Status: PASS
- Evidence:
  - Server started on `http://127.0.0.1:8050`.
  - Log shows `Found 2 diagnostic runs`.
  - Run selector displayed both Hvapor runs.

### 2. Run 20260515_173258 diagnostics rendering
- Status: PASS
- Evidence:
  - Key metrics table rendered No PFI/PFI model stats and VERIFY counts.
  - Evidence-linked observations rendered with severity badges (`PASSED`, `INFO`).
  - Diagnosis markdown narrative rendered as structured headings/lists.
  - Evidence image cards rendered with valid image previews and source paths.

### 3. Run 20260513_160812 diagnostics rendering
- Status: PASS
- Evidence:
  - Switched runs via dropdown without callback errors.
  - Diagnosis timestamp updated to selected run (`2026-05-15T20:57:15Z`).
  - Evidence images updated to the selected run's output paths.

### 4. Heuristics-first chat behavior
- Status: PASS after one fix
- Test prompts and outcomes:
  - Prompt: `Why did I get this ROBERT score?`
    - Response source badge: `Heuristic`
    - Response included CV/Test and VERIFY evidence.
  - Prompt: `Did any verification tests fail?`
    - Initial behavior: returned `No API Key` fallback (intent mismatch).
    - Fix implemented: expanded matcher to include `verification` and `test+fail` phrasing.
    - Re-test behavior: `Heuristic` response returned on both runs.

### 5. No-API-key mode
- Status: PASS
- Evidence:
  - Header shows `API key: ⚠️ Not configured`.
  - App remains fully usable for diagnostics and heuristic chat.
  - No key values are rendered in UI content.

## Issues Found and Resolved During Test

1. Heuristic intent gap for phrase `verification tests`
- Root cause: matcher only recognized `verify` and `failed` tokens.
- Fix: broadened intent condition in `agent/ui/chat.py`:
  - `"verify" in q or "verification" in q or ("test" in q and "fail" in q)`
- Validation: re-tested successfully on both runs.

## Overall Outcome

Phase 1B smoke test passed for available runs after the matcher fix.

Readability and evidence presentation are in place, and heuristics-first chat works in no-key mode for tested prompts.
