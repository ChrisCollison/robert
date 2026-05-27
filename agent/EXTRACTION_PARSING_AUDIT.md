# Extraction Parsing Audit

Date: 2026-05-26
Scope: Parsing correctness and fragility audit for [agent/extract_context.ipynb](agent/extract_context.ipynb) with cross-checks against sample archived outputs and schema docs.

## Source-to-Parser Mapping

| Source file | Parser function | Pattern/logic used | Fields extracted | Failure behavior | Risk level |
|---|---|---|---|---|---|
| PREDICT/PREDICT_data.dat | read_dat + split_into_blocks + parse_predict_block | Section split by literal markers: Starting model with all variables (No PFI), Starting model with PFI filter. Regex matches for model metadata, descriptor list, CV/test metrics (regression and classification variants), SD/y-range, outlier lines, quartiles, warning lines, and artifact path lines. Pred type inferred by global regex search on CV line content. | run_context.pred_type, run_context.ml_model, run_context.available.predict, run_context.available.pfi, run_context.available.test_set, run_context.predict.no_pfi.*, run_context.predict.pfi.* including metrics, counts, outliers, quartiles, artifacts, warnings. Also contributes inputs for score reconstruction in run_context.score.* and llm_evidence.json. | If file missing/unreadable: read_dat returns None, available.predict false, predict blocks replaced by null/empty defaults. If pattern misses: field remains null (often silently). If conversion fails: safe_float/safe_int appends parser warning and returns null. If pred type not detected: pred_type null with warning. | High |
| VERIFY/VERIFY_data.dat | read_dat + split_into_blocks + parse_verify_block | Section split by same literal markers. Regex for original metric and thresholds line (Original RMSE or MCC ... 15% and 30% threshold), compiled regex for baseline tests (y_mean, y_shuffle, onehot), regex for sorted CV list blocks (RMSE, R2, MAE, MCC), warning line capture by WARNING or x-prefix. | run_context.available.verify, run_context.verify.no_pfi.*, run_context.verify.pfi.* including passed/unclear/failed counts, test_outcomes/test_results, flawed_mod_score, sorted_cv arrays, thresholds and warnings. Also contributes score reconstruction inputs. | If file missing/unreadable: available.verify false and verify branches filled from null/empty template. If baseline test pattern not found: parser forces zero counts and flawed_mod_score 0 (not null). If list parse fails: warning added and list field stays null. | Medium-High |
| CURATE/CURATE_data.dat | read_dat + parse_curate_dat | Regex and line scans: first Database ... loaded successfully window, datapoints/accepted/ignored descriptors counts, Total: N descriptors removed due to high correlation, No datapoints were removed, dropped datapoints via regex (excluded/removed/discarded), warnings via WARNING or x-prefix. | run_context.available.curate, run_context.curate.n_initial, n_final, n_dropped, n_features_initial, n_features_final, n_features_removed, ignored_descriptors, warnings. Included in llm_evidence.json. | If file missing/unreadable: available.curate false with null/empty curate defaults. If key patterns miss: values remain null, with limited explicit warnings unless numeric conversion fails. | Medium |
| GENERATE/GENERATE_data.dat | read_dat + parse_generate_dat | Line-by-line regex for model screening summaries: Best combined (RMSE or MCC) ... for MODEL ... VALUE, fallback Combined (RMSE or MCC) ... for MODEL ... VALUE. Captures warning lines via WARNING or x-prefix. | run_context.available.generate, run_context.generate.model_screening_summary list of metric/model/value/raw, run_context.generate.warnings. Included in llm_evidence.json. | If file missing/unreadable: available.generate false with empty generate defaults. If regex does not match alternate ROBERT phrasing: model_screening_summary remains empty with no explicit parser warning for miss. | Medium-High |
| run_manifest.json | json.loads in availability/provenance cell | Direct JSON load if file exists. No regex. Reads keys dataset_csv, robert_command, robert_version. Falls back to parsing version/command from .dat headers if absent. | run_context.dataset_csv, robert_command, robert_version; report PDF discovery uses dataset_csv manifest value for naming tags. | If missing: manifest_data stays None, values backfilled from .dat header parsers where possible. If malformed JSON: warning printed to notebook output (not always persisted to parser_warnings). | Low |
| agent/run_context_schema.md | Documentation only (no parser function) | Markdown schema contract (V1 and broader field catalog). No runtime enforcement in notebook. | Intended contract for run_context keys and null-safe behavior. | Drift risk: notebook schema_version is 1.2 and includes extra fields (report_assets, llm artifacts), while doc is still framed as V1 and references extract_context.py naming. | Medium |

## File Presence and Missing-File Behavior

- File reading uses read_dat(path):
  - Missing path or unreadable file returns None.
  - Availability flags are set from None checks.
  - Downstream branch logic creates stable dict shapes with null/empty defaults.

- Current behavior by source:
  - PREDICT missing: predict branches still emitted with null metrics and empty arrays.
  - VERIFY missing: verify branches emitted from empty_verify template with null values.
  - CURATE missing: curate block emitted with null counts.
  - GENERATE missing: generate block emitted with empty model_screening_summary.
  - Manifest missing: provenance values may still be recovered from .dat header lines.

- Sample archived incomplete run confirms this behavior:
  - [agent/run_archive/20260516_151123__TOF_class_incomplete/run_context.json](agent/run_archive/20260516_151123__TOF_class_incomplete/run_context.json)
  - available.verify/curate/generate are false and corresponding blocks are null/empty shaped.

## Pattern-Failure Behavior

Observed behavior when a pattern does not match:

1. Common path: field remains null or empty, often without explicit warning.
2. Numeric conversion path: safe_float/safe_int records warning text in parser_warnings.
3. PREDICT pred_type detection miss: explicit warning added.
4. VERIFY baseline test miss: parser sets passed/unclear/failed to zero and flawed_mod_score to 0 (this can look like a true pass state rather than missing evidence).
5. GENERATE miss: model_screening_summary silently empty unless a warning line is present in source text.

## CURATE and GENERATE Parsing Coverage

- CURATE is parsed when available:
  - parse_curate_dat is called under avail_curate true.
  - Fields are written to run_context.curate.

- GENERATE is parsed when available:
  - parse_generate_dat is called under avail_generate true.
  - Fields are written to run_context.generate.

- Documentation clarity in notebook markdown:
  - Intro markdown states PREDICT and VERIFY, and optionally CURATE, but does not mention GENERATE.
  - Cell guide title says Parse CURATE_data.dat and run_manifest.json; code in that cell also parses GENERATE.
  - Therefore CURATE is documented, GENERATE parsing is implemented but under-documented.

## Highest-Risk Parsing Assumptions

1. Literal section marker dependency for block splitting:
   - Any wording change in marker text can collapse No PFI/PFI splitting and silently misroute lines.

2. Highly specific metric-line regexes:
   - PREDICT and VERIFY regexes assume exact punctuation and token order.
   - Small ROBERT output formatting updates can produce nulls without obvious failures.

3. Artifact path mapping via positional Graph in lines:
   - First Graph in assigned to results_plot, second to cv_variability_plot based on encounter order.
   - If order changes, fields can swap semantically.

4. VERIFY no-match default to zeros:
   - Missing baseline-test matches are coerced to pass-like counts (0 failed, 0 unclear, flawed_mod_score 0), which can mask parser failure.

5. CURATE initial window slicing:
   - Uses a fixed 400-char substring after Database ... loaded successfully to parse datapoints/descriptors.
   - Additional text inserted upstream can move key lines out of the window.

6. GENERATE narrow pattern set:
   - Only two phrasing families parsed for model screening summary.
   - Alternate ROBERT report text yields empty summaries silently.

## Missing Documentation

1. Intro markdown does not state GENERATE_data.dat parsing, although code parses it.
2. Cell 12 guide title mentions CURATE and manifest only, but cell also parses GENERATE.
3. Pattern-failure semantics are not fully documented:
   - Which misses are silent nulls vs warning-backed nulls vs forced zero defaults.
4. Schema drift is not explicitly documented:
   - Notebook emits schema_version 1.2 and extra fields beyond V1 schema narrative.

## Recommended Fixes (Do Not Implement Yet)

1. Add explicit parser audit counters:
   - For each source block, count expected pattern families matched vs missed.
   - Emit structured parser_health section in run_context.

2. Replace forced-zero VERIFY fallback with explicit unknown state:
   - If baseline test pattern not found, keep counts as null and append a high-severity parser warning.

3. Harden block splitting:
   - Support alternate marker aliases and defensive detection with regex normalization.

4. Decouple artifact mapping from order:
   - Use label-aware regex rules for each artifact type instead of first/second Graph in assumptions.

5. Expand GENERATE pattern coverage:
   - Add alternate templates and capture unmatched candidate lines into generate.unparsed_lines for transparency.

6. Improve CURATE parsing resilience:
   - Parse line-by-line around labels instead of fixed 400-char window.

7. Align documentation and schema:
   - Update notebook markdown guides to explicitly include GENERATE parsing.
   - Reconcile run_context_schema.md with notebook output version and fields.

8. Add parser contract tests from real fixtures:
   - Regression run, classification run, and incomplete run should each assert key fields and warning behavior.

## Evidence Cross-Checked

- [agent/extract_context.ipynb](agent/extract_context.ipynb)
- [agent/run_context_schema.md](agent/run_context_schema.md)
- [agent/run_archive/20260516_150946__TOF_class/outputs/PREDICT/PREDICT_data.dat](agent/run_archive/20260516_150946__TOF_class/outputs/PREDICT/PREDICT_data.dat)
- [agent/run_archive/20260516_150946__TOF_class/outputs/VERIFY/VERIFY_data.dat](agent/run_archive/20260516_150946__TOF_class/outputs/VERIFY/VERIFY_data.dat)
- [agent/run_archive/20260516_150946__TOF_class/outputs/CURATE/CURATE_data.dat](agent/run_archive/20260516_150946__TOF_class/outputs/CURATE/CURATE_data.dat)
- [agent/run_archive/20260516_150946__TOF_class/outputs/GENERATE/GENERATE_data.dat](agent/run_archive/20260516_150946__TOF_class/outputs/GENERATE/GENERATE_data.dat)
- [agent/run_archive/20260516_150946__TOF_class/run_manifest.json](agent/run_archive/20260516_150946__TOF_class/run_manifest.json)
- [agent/run_archive/20260516_151123__TOF_class_incomplete/run_context.json](agent/run_archive/20260516_151123__TOF_class_incomplete/run_context.json)
