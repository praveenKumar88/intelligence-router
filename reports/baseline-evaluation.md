# CPU routing baseline

TF-IDF word unigrams/bigrams + logistic regression. Features and model fit on train only. Six prespecified configurations are compared on development macro F1; ties use the first configuration. Only the selected router is evaluated on the held-out test split. No refit on development examples.

Selected: C=10.0, balanced=True; dev macro F1=0.874.

| Test policy | Accuracy | Macro F1 |
|---|---:|---:|
| selected_router | 88.5% | 0.843 |
| always_big | 75.0% | 0.429 |
| always_small | 25.0% | 0.200 |

| Label | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| small_model | 0.794 | 0.730 | 0.761 | 37 |
| big_model | 0.912 | 0.937 | 0.924 | 111 |

## Confusion matrix

Rows are source labels; columns are predictions.

| Actual / predicted | Small | Big |
|---|---:|---:|
| Small | 27 | 10 |
| Big | 7 | 104 |

## Interpretation and limits

The test set contains 148 prompts. These results measure agreement with heuristic annotations, not whether either downstream model produces an acceptable answer. A big-to-small disagreement is a potential under-routing error relative to that heuristic, not a verified model failure.

No GPU or downstream model API was used. Cost savings, production latency, probability calibration, and out-of-distribution performance have not been established. Normalized exact duplicates were removed, but paraphrase leakage remains possible. Do not tune further against this test report; use dev for subsequent choices and collect a fresh independent evaluation set before production claims.

The local model is saved at `models/baseline.joblib` (ignored by Git). Only load trusted joblib files. Reproduce using `requirements-training.txt`; full trial scores and provenance are in `baseline-evaluation.json`.
