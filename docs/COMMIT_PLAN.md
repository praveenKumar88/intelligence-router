# Build the Intelligence Router, one commit at a time

## What we are building

A Python system that chooses an execution policy for an AI request, executes it, and records whether that choice was worth its cost. A policy is initially a model; later it includes inference budget and tools.

Example first workload: classify a support message into billing, account_access, technical_issue, or other. The application supplies a quality target and latency limit. The router chooses among policies based on held-out evidence. It returns the label, policy used, explanation of selection, measured latency, token usage, and cost.

There are two distinct decisions:

1. Offline configuration selection: which policies meet this workload's requirements? The current synthetic starter demonstrates this.
2. Online request routing: which eligible policy should handle this particular request? This is what we will build and evaluate next.

Quality is estimated over a dataset. A 95% accuracy target does not guarantee that an individual response is correct. If evidence is insufficient or constraints cannot be met, return that explicitly.

## Target workflow

Labeled examples → run candidate policies → measure outcomes → choose/tune router on development data → evaluate on untouched test data.

Incoming request + structured requirements → capability filter → router → chosen model/budget/tools → output and execution record.

Natural-language descriptions of requirements become an optional input layer after this works.

## Commit sequence

Each row is a proposed future commit, not a completed feature. Keep commits small enough to explain and demonstrate in one learning session. Split a row if implementation needs several sessions.

| # | Proposed commit | Concepts learned | Done when |
|---|---|---|---|
| 1 | `feat: define support classification dataset and rubric` | Task definition, labels, ambiguous cases, train/dev/test splits | Versioned examples have unique IDs, labels, split assignments, and a written labeling rubric; start with 40–60 examples for plumbing, then expand before performance claims |
| 2 | `feat: add model adapter and execution records` | Prompts, inference, provider interfaces, structured output, errors | One configurable model returns a validated label and records model version, tokens, elapsed time, and errors; a fake adapter supports offline development |
| 3 | `feat: evaluate fixed model baselines` | Accuracy, operational reliability, p95 latency, token pricing | Both models run on identical examples; report always-cheap and always-strong results; costs include failed requests when billed |
| 4 | `feat: filter policies by required capabilities` | Schemas, context limits, tool/image support, hard constraints | Unsupported or unknown required capabilities are excluded and every rejection has a reason |
| 5 | `feat: add a simple request routing baseline` | Features, decision rules, prediction versus observation | A rule chosen on development data routes requests; an untouched test split compares it against both fixed baselines including routing overhead |
| 6 | `feat: compare embedding based routing` | Tokens, embeddings, similarity, nearest neighbors, data leakage | Training examples alone supply neighbors; tune on dev, evaluate on test; report whether embeddings justify their cost |
| 7 | `feat: learn a model selection threshold` | Supervised learning, probability calibration, thresholds, constrained optimization | A simple classifier predicts cheap-model success; sweep thresholds on dev and report held-out quality/cost with uncertainty |
| 8 | `feat: benchmark model and inference budget combinations` | Reasoning, inference-time scaling, token caps versus reasoning effort | On a separate verifiable reasoning dataset, compare supported model/budget combinations and record actual total compute cost |
| 9 | `feat: add verification and bounded escalation` | Verifiers, cascades, false acceptance, retries | A cheaper attempt can escalate after a failed check; record verifier errors and charge for every attempt; enforce a total budget |
| 10 | `feat: compare tool assisted execution policies` | Tool calling, orchestration, deterministic checks | Compare model-only and calculator-assisted policies on arithmetic cases, measuring end-to-end correctness and cost |
| 11 | `feat: extract reviewed requirements from task descriptions` | Structured extraction, validation, ambiguity | English descriptions produce editable structured requirements; unknown values are surfaced instead of guessed |
| 12 | `docs: publish reproducible routing experiment` | Reproducibility, tradeoff curves, limitations | A saved run produces a report with dataset/version, policies, split sizes, quality, cost, p95, uncertainty, and failure examples |

## How the two courses connect

### LLMs from Scratch

- Tokens and tokenization → input length, model context limits, and inference cost.
- Embeddings → similarity-based routing features.
- Attention and transformer architecture → how context is processed and why long inputs change compute requirements.
- Generation and decoding → output length, sampling, reproducibility, and latency.
- Training and finetuning → understanding specialized models and supervised learning. Router training is a separate, smaller learning problem.

### Reasoning Models from Scratch

- Evaluation → verifiable tasks and trustworthy success measurements.
- Inference-time scaling → choosing how much compute a request receives.
- Verification and multiple candidates → test whether extra attempts improve results enough to justify cost.
- Distillation and reinforcement learning → optional later experiments once a measured baseline exists; not prerequisites for the first router.

### Additional engineering we learn through the project

Git, Python interfaces, JSON schemas, dataset management, provider APIs, instrumentation, statistics, regression/classification, and reproducible experiments. The courses supply model intuition; the project supplies routing and systems practice.

## Commit routine

1. State one hypothesis in the learning journal.
2. Implement the smallest runnable change.
3. Run the relevant check or experiment.
4. Record what happened, including a result that did not improve performance.
5. Commit the code, instructions, and non-sensitive result together.

For course exercises, use `learning/llm/` and `learning/reasoning/`; reference upstream exercises and retain required attribution for any copied material. Use `feat:`, `test:`, `experiment:`, or `docs:` to make history readable. Keep credentials and private request logs out of Git.

## Current status

Completed locally: synthetic configuration selector, four tests, CI definition, learning roadmap, and attributed research notes. No real provider calls or measured model comparison yet. Published at [praveenKumar88/intelligence-router](https://github.com/praveenKumar88/intelligence-router).

## Updated first milestone

The initial support-classification dataset proposal is superseded by the user-selected SupraLabs prompt-routing dataset. Completed: revision-pinned download, checksum verification, schema audit, normalized deduplication, deterministic stratified splits, and audit report. See `data/README.md`.

Next implementation: TF-IDF + logistic regression on prompt text, predicting the source small/big routing label. Fit preprocessing on train only; tune on dev; report held-out per-class metrics against the majority baseline. This measures policy imitation. Real model outcome evaluation remains required before production claims.
