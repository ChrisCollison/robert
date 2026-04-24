# ROBERT Companion Agent Prototype

This project explores an optional companion layer for ROBERT, focused on helping chemists interpret ROBERT results.

The first goal is deliberately narrow:

> Explain why a user received a particular ROBERT score.

The prototype reads ROBERT output folders and extracts evidence from the same underlying files that support the ROBERT report. It then organizes that evidence into a structured summary and, optionally, uses an LLM to translate the findings into plain language.

This project is not a replacement for ROBERT. It is an exploratory add-on intended to support interpretation, transparency, and better user decision-making.

## Initial Scope

The first prototype should answer:

- Why did I get this score?
- What evidence supports that explanation?
- What are the most likely limiting factors?
- What should I try next?

## Out of Scope for v1

- automatic reruns,
- full UI,
- hosted service,
- fine-tuned model,
- changing ROBERT model selection,
- changing existing ROBERT defaults,
- parsing the PDF as the primary source of truth.

## Development Philosophy

Start with the smallest useful interpretation engine.

Build in layers:

1. Extract context from ROBERT outputs.
2. Diagnose score-limiting factors using transparent rules.
3. Generate a structured explanation.
4. Optionally translate the explanation with an LLM.
5. Only later consider UI integration.

## Ethical and Collaboration Note

ROBERT is the upstream scientific tool. This prototype should preserve attribution, respect the existing codebase, and aim to contribute useful improvements back to the ROBERT project where appropriate.