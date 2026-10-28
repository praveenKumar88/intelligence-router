# Dataset preparation

Run from the repository root with Python 3.9+ (standard library only):

```sh
python3 scripts/prepare_dataset.py
```

This downloads a revision-pinned JSONL file from [SupraLabs/Prompt-Routing-Dataset](https://huggingface.co/datasets/SupraLabs/Prompt-Routing-Dataset), verifies its SHA256, validates the schema, removes normalized duplicates, and writes stratified splits to `data/prepared/`. Generated dataset files are ignored by Git. Audit summaries and split hashes are tracked under `reports/`.

For offline reuse, supply the original downloaded JSONL:

```sh
python3 scripts/prepare_dataset.py --source /path/to/router_dataset_openai_gpt-oss-120b.jsonl
```

The revision, checksum, normalization policy, and seed are recorded in the script and report. Invalid rows, conflicting duplicate labels, or changed source bytes cause failure. Split files contain only `id`, `prompt`, and `label`. Fit feature extraction and classifiers on train only; tune on dev and evaluate on test once the approach is fixed. No classifier has been trained yet.

## Attribution and label provenance

Dataset author: SupraLabs. Dataset card metadata specifies MIT; refer to the pinned upstream card for its terms and provenance. The card attributes prompt sources to `magpie-align/Magpie-Reasoning-150K` and `HuggingFaceH4/instruction_dataset`, with generated annotations from GPT-OSS-120B via OpenRouter. This repository downloads the upstream data without checking raw examples into Git.

The routing labels encode a programmatic policy, not head-to-head measurements of specific small and large models. Use this as a bootstrap routing benchmark. Production routing needs independent evaluation of real model outcomes and representative workloads. Normalized exact duplicate detection does not detect semantic paraphrases.
