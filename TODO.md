# TODO

Purpose
- Source-of-truth list of planned and in-progress work.
- Keep this operational and concrete.

Updated
- 2026-04-24

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

## Next Up (Small Chunks)
- [ ] Add explicit run_context.json schema draft.
- [ ] Add parsing regex/token rules for PREDICT and VERIFY sections.
- [ ] Add deterministic diagnostics rubric for score limitations.
