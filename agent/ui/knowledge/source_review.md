# Review of the three combined source text files

## Recommendation
Do not index the combined `.txt` files directly. They contain useful material, but also repeated navigation menus, page headers, page footers, image placeholders, source-file markers, and API index material. BM25 retrieval works better when the indexed documents are clean, topic-focused, and written in natural user language.

## Better approach
Use the combined `.txt` files as raw source material. Convert the useful sections into curated Markdown knowledge cards.

## What was preserved conceptually
The curated files preserve and reorganize material related to:

- ROBERT score purpose and score components.
- VERIFY tests: y-mean, y-shuffle, one-hot.
- PREDICT outputs: metrics, predictions, outliers, SHAP, PFI.
- GENERATE and CURATE ideas: model screening, feature pruning, descriptor selection.
- CV/test comparison, uncertainty, and sorted CV/extrapolation.
- Common chemist-facing interpretation questions.

## What was intentionally removed
The curated files do not include:

- Repeated sidebar/navigation menus.
- Previous/next documentation links.
- Copyright/footer boilerplate.
- Image placeholders that do not carry usable text.
- Long API index lists unless they support explanation.
- Version history details not needed for score interpretation.

## Why Markdown is preferred
Markdown headings give the chunker cleaner structure than raw scraped documentation text. The headings and repeated natural-language questions also improve BM25 matching.

## Suggested next improvement
After the first retrieval tests, add more targeted cards if needed:

- `07_aqme_smiles_workflow.md`
- `08_robert_output_files.md`
- `09_score_component_thresholds.md`
- `10_troubleshooting_low_scores.md`
