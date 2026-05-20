# AGENTS.md — ROBERT Companion Agent Development Guide

## Mission

We are building an optional companion layer for ROBERT that helps chemists understand and act on ROBERT results. The first supported question is:

> “Why did I get this ROBERT score?”

The goal is not to replace ROBERT, rewrite ROBERT, or change its scientific behavior. The goal is to inspect ROBERT outputs, identify evidence relevant to the score, and produce a clear explanation that helps a chemist understand what happened and what to try next.

## Core Operating Principle

The companion agent is a wrapper around ROBERT, not a competing scoring system.

The agent must:
- treat ROBERT outputs and documented ROBERT logic as the authority,
- extract, normalize, cite, and explain ROBERT-generated evidence,
- keep all deterministic evidence auditable and visible,
- clearly label any computed value as a derived convenience value.

The agent must not:
- present a separate agent score,
- override ROBERT's reported score,
- invent new score components,
- invent warning thresholds not present in ROBERT outputs or documented ROBERT logic.

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

## Mandatory Execution Checkpoint

Before any implementation work begins, the agent must:
1. present the plan to the user,
2. receive explicit user approval,
3. only then execute edits or commands.

This applies to code, notebooks, scripts, and documentation updates.

Do not make broad edits. Prefer small, reversible changes.

Do not refactor unrelated code.

Do not change existing ROBERT behavior unless explicitly requested.

Do not remove existing functionality.

Do not rename public functions, CLI arguments, folders, or output files unless explicitly approved.

Do not introduce network calls into the standard ROBERT workflow.

Any LLM/OpenAI/API functionality must be optional and disabled by default.

Any API key must be supplied by the user through an environment variable or explicit config option. Never hard-code keys.

If an API key is stored in a `.env` or config file, do not rename that file or its containing folder unless the user explicitly asks for that rename.

## Notebook-First Development Rules

1. Prefer new implementation work in Jupyter notebooks located in `agent/` whenever practical.
2. For every notebook, include clear explanations for each code cell so a chemistry expert with limited Python experience can follow what the code is doing.
3. Use short, plain-language markdown immediately before code cells to explain:
   - the purpose of the cell,
   - expected inputs,
   - expected outputs or side effects.
4. Keep reusable multi-use helper logic out of notebooks when it becomes shared across notebooks, and place it in a single helper script: `agent/robert_helper.py`.
5. Avoid creating additional helper modules unless there is a strong reason; default to the single helper script above for shared utilities.

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
4. generate evidence-linked observations grounded in ROBERT outputs,
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