# Curated ROBERT RAG knowledge base

This folder contains Markdown knowledge cards prepared from the combined ROBERT documentation text files. The goal is not to mirror the official documentation page-by-page. The goal is to create short, retrieval-friendly explanatory files for a ROBERT companion agent.

## Recommended use
Place these `.md` files in:

```text
agent/ui/knowledge/
```

Then rebuild the local BM25 index using the existing index-building notebook or `build_index.py`.

## Design principles

1. The official ROBERT documentation is treated as raw source material.
2. The RAG knowledge base is rewritten as plain-English explanatory guidance.
3. Each file focuses on one concept area.
4. Each file includes common user question phrasings to improve BM25 retrieval.
5. Specific ROBERT run values should always come from parsed run outputs, not from these general documents.

## Files

- `01_robert_score.md`: score meaning, score components, reliability interpretation.
- `02_verify_tests.md`: y-mean, y-shuffle, one-hot, pass/unclear/fail interpretation.
- `03_predict_metrics_and_outputs.md`: PREDICT outputs, metrics, outliers, SHAP, PFI.
- `04_cv_test_gap_and_uncertainty.md`: CV vs test, uncertainty, sorted CV, extrapolation.
- `05_feature_selection_and_importance.md`: CURATE, descriptor pruning, RFECV, PFI, SHAP, chemical plausibility.
- `06_common_questions_for_chemists.md`: broad FAQ for natural-language retrieval.

## Recommended retrieval test questions

After indexing, test these queries and inspect the top retrieved chunks:

```text
Why did I get this ROBERT score?
What does y-shuffle mean?
Why did my VERIFY test fail?
Why is my test RMSE worse than CV?
What does a CV/test gap mean?
Why did ROBERT remove so many descriptors?
What is PFI?
What does SHAP tell me?
Why are there outliers?
Can I trust a model with a score of 6?
```

## Important limitation
These files are explanatory background. They do not contain the user's specific ROBERT results. The companion agent should combine these files with parsed run-specific evidence such as `run_context.json`, `diagnosis.json`, `PREDICT/PREDICT_data.dat`, and `VERIFY/VERIFY_data.dat`.
