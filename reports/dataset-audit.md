# Dataset audit

Source: [SupraLabs/Prompt-Routing-Dataset](https://huggingface.co/datasets/SupraLabs/Prompt-Routing-Dataset/tree/458d9f67018a350ee84bfd5e936aeca6f2522341)

Revision: `458d9f67018a350ee84bfd5e936aeca6f2522341`. Seed: `42`. License metadata: MIT (upstream card).

- Source rows: 992
- Original labels: {'big model': 744, 'small model': 248}
- Missing fields: none; invalid rows: 0
- Exact duplicate rows: 0
- Normalized duplicate rows removed: 0
- Conflicting duplicate groups: 0
- Labels differing from the published rule: 0

## Reproducible splits

| Split | Rows | Small | Big |
|---|---:|---:|---:|
| train | 696 | 174 | 522 |
| dev | 148 | 37 | 111 |
| test | 148 | 37 | 111 |

Split each label independently: floor(15%) test, floor(15%) dev, remainder train. Sort by a seeded SHA256 of the normalized prompt ID. Deduplicate before splitting; row order does not affect membership.

## What this can establish

This benchmark measures reproduction of the source routing policy. Its rule sends math, coding, or complexity >= 3 to the big model. It cannot establish cost savings or downstream answer quality. The source majority-label baseline is 75.0%; compare classifiers against it and report per-class metrics.

Only `prompt` enters the classifier; `label` is the target and `id` is bookkeeping. Answers, justifications, and annotated task attributes are deliberately excluded from split files.

## Limitations

- Labels encode a heuristic, not measured candidate model success.
- No semantic or near-duplicate detection; paraphrase leakage may remain.
- Reference answers are unverified and are excluded from model inputs.
- One public source is insufficient to establish production generalization.
