# Learn and build together

Work by topic, not by a fixed deadline. The first two weeks can produce a baseline, not the full vision.

| Course topic | Router experiment | Deliverable |
|---|---|---|
| Setup and LLM overview | Define one task family and its success rubric | 20–50 labeled tasks |
| Tokens and embeddings | Measure input/output lengths and cost | Token/cost notebook |
| Attention and context | Compare short vs long inputs | Context-length evaluation |
| GPT implementation and generation | Compare decoding settings at fixed model | Latency/quality curves |
| Training and finetuning | Compare specialized and general models | Held-out comparison |
| Reasoning model setup and evaluation | Add a stronger baseline and verifier | Reproducible evaluation harness |
| Inference-time scaling | Compare one call, more compute, and verification | Cost per successful task |
| Distillation and RL | Investigate whether a smaller policy can replace an expensive one | Optional research experiment |

## Milestones

1. **Today:** executable structured contract and synthetic selection baseline.
2. **First real experiment:** two models, one dataset, measured cost/quality/p95 latency, held-out split. Record failures as well as successes.
3. **Baseline router:** compare fixed choices and simple rules on held-out tasks; charge for routing itself.
4. **Reasoning and tools:** treat every model/budget/tool combination as its own measured policy. Include retry and verifier costs.
5. **English to constraints:** extract requirements, expose ambiguities, validate structured output. Unsupported safety requirements require human review.
6. **Learned routing:** only after enough data, fit a selector and check calibration, distribution shift, and fallback behavior.

Later: agent loops, retrieval, hosted vs local execution, quantization, hardware, and human escalation. Physical robotics is a separate safety-critical effort.

## Next session

Pick the first text-classification domain, define the label set and acceptable errors, collect examples, and choose two models available to you. Do not assume a tiny dataset establishes a 99% accuracy guarantee.
