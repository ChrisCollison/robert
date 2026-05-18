# ROBERT Agent Reference Notes

Purpose
- Persistent, source-of-truth notes for key technical findings discovered during repository inspection.
- This file is auditable and should only contain verified findings tied to repository files.

Updated
- 2026-04-24

## 2026-05-16 Phase 4 Notes

### UI Ground Truth Safeguard
- UI chat gating now depends on DAT-file parity status computed from `run_context.json` vs ROBERT evidence files.
- Deterministic primary checks:
  - `outputs/PREDICT/PREDICT_data.dat` -> `run_context.predict.*`
  - `outputs/VERIFY/VERIFY_data.dat` -> `run_context.verify.*`
- Status semantics for UI:
  - `pass`: enable chat normally
  - `incomplete`: enable chat with warning (limited evidence)
  - `fail`: disable chat and show parity-block message

### Future PDF Verification (Optional)
- PDF parity is documented as an extension path in `agent/verify_extraction_parity.ipynb`.
- A placeholder parser contract is defined there (`parse_pdf_report_placeholder`) to keep future work isolated.
- Current governance remains unchanged: DAT-based parity is the authoritative safeguard for UI readiness.

## Key Findings

### Where ROBERT score is computed
- Primary score logic is in robert/report_utils.py, function calc_score.
- calc_score combines:
  - predictive contributions from get_predict_scores (PREDICT inputs), and
  - verification contributions from get_verify_scores (VERIFY inputs).
- print_score in robert/report.py calls calc_score and renders the score section.

### Where the PDF report is generated
- Report orchestration is in robert/report.py, class report.
- PDF writing occurs through report_utils.make_report and report_utils.make_pdf.
- Output filename is ROBERT_report.pdf in the working directory.

### Which module outputs feed the report and score
- PREDICT/PREDICT_data.dat is directly parsed in multiple report sections.
- VERIFY/VERIFY_data.dat is used for score components via calc_score.
- CURATE/CURATE_data.dat and GENERATE/GENERATE_data.dat are consumed in reproducibility metadata gathering.
- GENERATE/Best_model/{No_PFI,PFI} parameter CSVs are used in transparency sections.

### Safest initial parse targets for run_context.json
- PREDICT/PREDICT_data.dat
- VERIFY/VERIFY_data.dat
- CURATE/CURATE_data.dat (supplementary provenance)
- GENERATE/GENERATE_data.dat (supplementary provenance)
- GENERATE/Best_model/{No_PFI,PFI}/*.csv (model metadata)

## Notes on alignment
- AGENTS.md and README_AGENT.md are aligned on mission, constraints, and v1 scope.
- One naming inconsistency exists in AGENTS.md examples (mentions robert/agent path), while project constraints currently prefer agent/ for new wrapper files.

## Change Policy for This File
- Append verified findings only.
- Prefer concise bullets.
- Include exact file/function anchors in future updates.
