# Intelligence Router

Learn how intelligence works. Measure where to spend it.

Goal: accept a task and its constraints, then select the lowest-cost execution configuration supported by evaluation evidence. Eventually the configuration can include model, reasoning budget, tools, retrieval, agent strategy, and escalation.

## Start here

Python 3.9+; no dependencies or API keys needed.

```sh
python3 router.py examples/task.json --benchmarks examples/benchmarks.synthetic.json
python3 -m unittest discover -s tests -v
```

This first milestone selects the cheapest feasible configuration from **synthetic benchmark summaries** for one task family. It does not call models, parse natural-language requirements, or demonstrate real performance. Unknown task families and infeasible constraints return `needs_evaluation`, never an invented recommendation. JSON output is the first machine-readable Intelligence Configuration.

Read [the research ideas](docs/RESEARCH.md), [the roadmap](docs/ROADMAP.md) and keep [a learning journal](docs/LEARNING_LOG.md). Build one small experiment after each course topic. Course exercises belong under `learning/`; router experiments stay separate so this remains usable while you learn.

## Build one commit at a time

Follow the [commit-by-commit learning plan](docs/COMMIT_PLAN.md), starting with the dataset and rubric. Each step names the concept, implementation, and completion check.

## Learning resources

- [Build a Large Language Model (From Scratch)](https://sebastianraschka.com/llms-from-scratch/) · [official code](https://github.com/rasbt/LLMs-from-scratch)
- [Build a Reasoning Model (From Scratch)](https://sebastianraschka.com/reasoning-from-scratch/) · [official code](https://github.com/rasbt/reasoning-from-scratch)
- [Raschka course hub and video playlists](https://sebastianraschka.com/from-scratch/)
- [RouteLLM](https://github.com/lm-sys/RouteLLM): a reference for model routing and evaluation; this project explores broader execution configurations.

## Evaluation contract

A benchmark row describes a complete configuration evaluated on a particular task family. Quality and reliability are separate metrics: quality is task correctness; reliability is successful execution without operational failure. Latency uses p95. Cost is dollars per attempted task, including tools and retries when real evaluation is added. The current objective minimizes that cost subject to all three constraints and explicit required tools. Synthetic rows are teaching fixtures, not model claims. Results do not certify safety or production suitability.

Real evaluation must record model/version, dataset split, sample size, date, token counts, prices, actual tool costs, and uncertainty. Keep training and held-out evaluation tasks separate. Compare against always-cheap and always-strong baselines, including router overhead. Never use model self-confidence as calibrated correctness.

## Next milestone

Create 20–50 labeled tasks in one narrow domain (start with text classification), run two actual models on the same held-out cases, and replace the synthetic fixtures with measured results. Then test whether routing improves cost at the required quality. Natural-language extraction comes after the structured contract works, with user review of ambiguous requirements.

## Repository

Public repository: [praveenKumar88/intelligence-router](https://github.com/praveenKumar88/intelligence-router).

```sh
git clone https://github.com/praveenKumar88/intelligence-router.git
cd intelligence-router
python3 -m unittest discover -s tests -v
```

Do not put API keys, private prompts, or datasets in commits. Store credentials in your environment. No license has been selected yet.
