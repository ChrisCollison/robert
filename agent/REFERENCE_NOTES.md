# ROBERT Agent Reference Notes

Purpose
- Persistent, source-of-truth notes for key technical findings discovered during repository inspection.
- This file is auditable and should only contain verified findings tied to repository files.

Updated
- 2026-04-24

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
