# Router ideas to test

Research checked: October 27, 2026.

The original inspiration was [this X search](https://x.com/search?q=intelligent%20router&src=typed_query). Its results could not be read, and a search URL changes over time. The sources below were independently found; they are not claimed to be posts from those results. Add individual post URLs when available.

## 1. Learn when a cheaper model is sufficient

Source: [RouteLLM](https://github.com/lm-sys/RouteLLM).

Idea: use preference/evaluation data to learn model selection and tune the quality–cost tradeoff. Our first adaptation is much smaller: compare always-cheap, always-strong, and a simple selector on identical held-out tasks. Treat published savings as hypotheses, not expected results on our workload.

Experiment: freeze a labeled support-classification test set. Run both models on every test item, save correctness and total cost, then evaluate routing without fitting on test labels. Report selection errors where the cheaper model fails and the stronger model succeeds.

## 2. Select model AND reasoning budget

Source: [R2-Router](https://github.com/UCF-ML-Research/R2-Router).

Idea: consider quality as a function of both model and output budget. The repository describes joint model/budget prediction. We will independently implement a small grid experiment before learning any predictor.

Experiment: evaluate two models at two supported inference budgets on a verifiable task. Record actual token usage and p95 latency. Distinguish an output-token cap from a provider's reasoning-effort setting: they are not interchangeable controls. Compare smaller-with-more-compute against larger-with-less-compute.

## 3. Capability rules before learned selection

Source: [Hugging Face Chat UI routing documentation](https://github.com/huggingface/chat-ui/blob/main/docs/source/configuration/llm-router.md).

Idea: use explicit request signals such as images or enabled tools before model selection, with operational fallbacks. Our adaptation will filter unsupported capabilities before optimizing cost. The current starter only checks required tool names; it does not yet validate image support or actual tool execution.

Experiment: add requests requiring images, structured output, or tool calls. A candidate with missing capability metadata must not satisfy a required capability. An empty eligible set should request evaluation rather than silently relax a constraint.

## 4. Keep serving optimization as a later layer

Source: [llm-d Router](https://github.com/llm-d/llm-d-router).

Idea: routing to a serving endpoint can account for load and prefix cache state. That is useful after we have a measured model-selection baseline and real serving infrastructure.

Deferred experiment: compare identical model requests across endpoints with different load/cache states. Keep these measurements separate from model correctness.

## Implementation order

1. Build a per-request evaluation harness and a small labeled dataset.
2. Establish fixed-model baselines; include API failures, all tokens, tool use, retries, and router overhead.
3. Add explicit capability filters and explain rejection reasons.
4. Compare rule-based routing against fixed baselines on held-out cases.
5. Add model/budget combinations and plot the quality/cost frontier.
6. Train a router only when the measured data justifies it.

## Reuse policy

For now this is conceptual reuse with attribution; no external source code or pretrained checkpoints have been copied. Before incorporating either, inspect the exact revision's license and preserve required notices. Cite papers for the methods they introduce and repositories for implementations. Do not import a large framework before the baseline shows which capability we need.
