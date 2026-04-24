# AGENTS.md — ROBERT Companion Agent Development Guide

## Mission

We are building an optional companion layer for ROBERT that helps chemists understand and act on ROBERT results. The first supported question is:

> “Why did I get this ROBERT score?”

The goal is not to replace ROBERT, rewrite ROBERT, or change its scientific behavior. The goal is to inspect ROBERT outputs, identify evidence relevant to the score, and produce a clear explanation that helps a chemist understand what happened and what to try next.

## CRITICAL RULES

1. The `robert/` directory is READ-ONLY.
2. Do not modify any existing ROBERT source files.
3. Do not refactor, rename, or reorganize ROBERT code.
4. All new functionality must be implemented in:
   - `agent/`
   - standalone scripts
5. Interaction with ROBERT must occur via:
   - reading output folders
   - calling CLI commands
   - reading generated files
6. Never inject LLM calls into ROBERT core functions.

If a change seems necessary, propose it first. Do not implement without approval.

## Source of Truth

The existing ROBERT codebase is the source of truth for:
- how ROBERT runs,
- how folders and output files are created,
- how reports are generated,
- how the ROBERT score is computed,
- existing command-line behavior,
- current tests and documentation.

Do not infer behavior if it can be determined from the code. Inspect the relevant files first.

## Working Rules

Before modifying code, always propose a short plan that includes:
1. files to inspect,
2. files likely to change,
3. expected behavior,
4. risks,
5. how to test the change.

Do not make broad edits. Prefer small, reversible changes.

Do not refactor unrelated code.

Do not change existing ROBERT behavior unless explicitly requested.

Do not remove existing functionality.

Do not rename public functions, CLI arguments, folders, or output files unless explicitly approved.

Do not introduce network calls into the standard ROBERT workflow.

Any LLM/OpenAI/API functionality must be optional and disabled by default.

Any API key must be supplied by the user through an environment variable or explicit config option. Never hard-code keys.

## Initial Development Target

Build the smallest useful prototype that can answer:

> “Why did I get this ROBERT score?”

The first implementation should read existing ROBERT output folders rather than parse the PDF report.

Target folders:
- `CURATE/`
- `GENERATE/`
- `VERIFY/`
- `PREDICT/`

The prototype should:
1. locate relevant output files,
2. extract metrics and diagnostic evidence,
3. create a structured `run_context.json`,
4. generate rule-based diagnostic flags,
5. optionally produce a natural-language explanation.

The first version should not:
- rerun ROBERT automatically,
- modify user data,
- change model selection,
- add a full GUI,
- require an API key,
- depend on a hosted service.

## Methodological Guardrails

The agent should not simply say whether a model is “good” or “bad.” It should explain evidence.

It should consider:
- dataset size,
- number of features before and after curation,
- split strategy,
- train/CV/test performance,
- verification tests,
- outliers,
- feature importance,
- chemical plausibility,
- possible leakage,
- possible representation mismatch.

The agent must distinguish between:
- low score because the model is poor,
- low score because the dataset is too small,
- low score because the target is noisy,
- low score because the split is difficult,
- low score because the descriptors do not capture the relevant chemistry.

## LLM Guardrails

If an LLM is used, it should only translate structured evidence into user-facing language.

The LLM must not invent:
- metrics,
- descriptor meanings,
- files,
- model behavior,
- chemical conclusions.

If evidence is missing, the output should say what is missing.

The deterministic extracted evidence should remain visible and auditable.

## Preferred Architecture

Start with a standalone helper module or script, for example:

- `robert/agent/`
- `robert/agent/extract_context.py`
- `robert/agent/diagnose_score.py`
- `robert/agent/prompts.py`

or, if keeping the first prototype outside the package:

- `agent_prototype/`

Prefer a clean separation:

1. extraction layer,
2. diagnosis/rules layer,
3. explanation layer,
4. optional LLM layer.

## First Task

Do not write code yet.

First inspect the repository and identify:
1. where the ROBERT score is computed,
2. where the PDF report is generated,
3. which files from `CURATE`, `GENERATE`, `VERIFY`, and `PREDICT` are used to build the report,
4. what output files are stable enough to parse.

Then propose a plan for building `run_context.json`.