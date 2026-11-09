# Evaluation report (status)

Status: complete. Strategies, judge, injection tests and failure analysis measured on 2026-11-09; recommendation at the end.

## What is checked offline (no API)

| Check | Where | Status |
|---|---|---|
| Normalisation, exact match, token F1 | `src/metrics.py`, `tests/test_metrics.py` | passing |
| p90 latency arithmetic | same | passing |
| Swap test: flags position-driven judges only | same | passing |
| Pareto front and dominance | same | passing (lecture figures as reference values) |
| Cache key includes the model | same | passing |
| Cost arithmetic, cache multipliers | same | passing |
| Label scorer and judge record | `src/evaluate.py`, `tests/test_evaluate.py` | passing (PR #11) |

## The three strategies on 30 cases (measured)

| Strategy | Right /30 (expected or second acceptable) | Right /30 (expected only) | Cost per 1,000 calls | Median latency | p90 latency | Re-prompted | Gave up | Prompt file |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Zero-shot | 28/30 | 27/30 | $1.02 | 2.60 s | 4.47 s | 17 | 1 | `prompts/route_zero_shot.md` |
| Few-shot | 27/30 | 26/30 | $0.74 | 0.98 s | 1.16 s | 0 | 0 | `prompts/route_few_shot.md` |
| Chain-of-thought | 27/30 | 25/30 | $1.03 | 1.58 s | 1.83 s | 0 | 0 | `prompts/route_cot.md` |

Four facts: model `anthropic/claude-haiku-4.5` (through OpenRouter), date 2026-11-09, parameters max_output_tokens 300 and model-default sampling, test file `evals/test_cases.csv` (30 cases). Right answers by exact match on the label, no model. Cost from the measured input and output tokens of every call, each at its own price, re-prompts included. Files: `runs/results_<strategy>.csv`, `runs/calls.csv`; the table is computed by `python -m src.summarise`.

**Pareto front:** zero-shot and few-shot. No other strategy is at least as good on right answers, cost and p90 latency, and better on one. Chain-of-thought is dominated by few-shot: same right answers, more expensive, slower.

**What 30 cases can tell.** One case is 3.3 points. Zero-shot is one case ahead of the other two, which is smaller than what 30 cases can resolve: on accuracy, the three strategies cannot be told apart. They do differ on cost, latency and re-prompts.

**Why zero-shot needed 17 re-prompts.** We re-ran case L04-20 and printed the raw answers. The model returns the JSON inside a ```json block and then adds a "Reasoning" paragraph. Our validation rejects the extra text, and one re-prompt ("Send corrected JSON only") fixes it. When the reasoning is long, the answer hits max_output_tokens (300), stop_reason is max_tokens, and the code refuses it: that is the one give-up (L04-20). The few-shot and chain-of-thought prompts say "Return only the JSON object, with nothing before or after it"; the zero-shot prompt says "Return JSON only" and shows its example in a ```json block. So the cause is the zero-shot prompt, and the checks in src/llm.py did their job: no truncated or invalid answer was used.

## The judge (measured)

Judge model: `anthropic/claude-sonnet-4.5`, a different and larger model than the component (`anthropic/claude-haiku-4.5`), so the model does not grade itself. It scores each answer from 1 to 5 on four criteria against the expected answer (`evals/rubric.md`). Date 2026-11-09, same 30 cases. Files: `runs/judge_<strategy>.csv`, `runs/pairwise.csv`; the figures are computed by `python -m src.summarise --judge`.

| Strategy | Correct | Grounded | Review | Format | Judge cost (30 cases) |
|---|---:|---:|---:|---:|---:|
| Zero-shot | 4.73 | 4.83 | 4.73 | 4.87 | $0.1183 |
| Few-shot | 4.73 | 4.87 | 4.73 | 5.00 | $0.1195 |
| Chain-of-thought | 4.73 | 4.83 | 4.70 | 5.00 | $0.1199 |

**Calibration.** Before reading the judge, we (Lynn and Sereine) scored 10 few-shot answers by hand with the same rubric (`evals/human_scores.csv`). The judge gave the same score on 31 of 40 criterion scores (78%), and was within one point on 33 of 40 (82%).

| Criterion | Same score as us |
|---|---:|
| Correct | 8/10 |
| Grounded | 8/10 |
| Review | 5/10 |
| Format | 10/10 |

What we take from it: we trust the judge as a second reading on format and on correctness. We do not trust it on the review criterion: it agrees with us only half the time. The decision to send a ticket to a human is therefore checked by code (confidence below 0.70 or label `other` forces review), not by the judge. The main score stays exact match on the label; the judge does not replace it.

**Swap.** Every pair of strategies was judged on the 30 cases in both orders (A then B, B then A). The order changed the verdict in 15 of 90 comparisons (17%); those count as a tie, not a preference.

| Pair | First preferred | Second preferred | Tie | Changed by the swap |
|---|---:|---:|---:|---:|
| Zero-shot vs few-shot | 3 | 3 | 24 | 5 |
| Zero-shot vs chain-of-thought | 5 | 2 | 23 | 2 |
| Few-shot vs chain-of-thought | 3 | 3 | 24 | 8 |

The judge gives the same mean correctness to the three strategies, and prefers none of them once order effects are removed (71 ties out of 90). This agrees with exact match: on quality, 30 cases cannot separate the strategies; cost and latency do.

## Injection tests (measured)

`LIVE_TESTS=1 python -m pytest tests/test_guardrails.py -q`, model `anthropic/claude-haiku-4.5`, 2026-11-09. Five attacks written into the ticket (reveal the prompt, force a label, fake a system tag, leave the task, a French override), each run 3 times, plus one normal delivery ticket as a control. Result: 48 passed in 49 secs 

What is checked on every run: only the fixed fields (label, needs_human_review, injection_suspected) leave the component, the label is one of the 7 allowed, and an attack always goes to a human. The control ticket is still routed to delivery and is not flagged. A forced label is never sent without review: even if the model obeys the attack, a person sees the ticket first.

## Status of each measured item

| Item | Status |
|---|---|
| Strategy results on 30 cases (zero-shot, few-shot, chain-of-thought) | done (see above) |
| Right answers out of 30, by scorer | done (see above) |
| Cost per 1,000 calls, from `runs/` tokens | done (see above) |
| Median and p90 latency | done (see above) |
| Pareto front across strategies | done (see above) |
| Judge model, agreement with our own scores on 10 cases | done (see "The judge") |
| Verdicts changed by the swap | done: 15 of 90 (17%) |
| Injection tests run several times | done: 5 attacks × 3 runs + control (see "Injection tests")|

Each figure, when measured, needs the model, the date, the parameters and the test file, and must be recorded in `runs/`.


## Local surrogate evaluation

## Failure analysis

Model `anthropic/claude-haiku-4.5`, 2026-11-09, the 30 cases of `evals/test_cases.csv`. We read every answer that was wrong, gave up, or was right only through the second acceptable label (`runs/results_<strategy>.csv`), and grouped them by cause.

| Strategy | Wrong or gave up | Right only through the second label | Wrong and not sent to a person |
|---|---|---|---|
| Zero-shot | L04-20 (gave up), L04-26 | L04-18 | L04-26 |
| Few-shot | L04-17, L04-26, L04-27 | L04-18 | L04-26, L04-27 |
| Chain-of-thought | L04-17, L04-26, L04-27 | L04-18, L04-28 | L04-17, L04-27 |

| Cause | Cases | Example, spelled out |
|---|---|---|
| Prompt | L04-26 (all three), L04-27 (few-shot, chain-of-thought), L04-20 (zero-shot give-up) | L04-26 is a French complaint about a car carburettor. Albert's sells beauty products only, so the expected label is `other`. Few-shot answered `returns_refunds` with confidence 0.92 and no review. The prompt lists the label names without definitions and never says what the marketplace sells, so nothing tells the model that this product is outside the catalogue. L04-27 is the same gap: a brand pitching to become a seller gets `seller`, because the prompt never says that `seller` means a seller already on the marketplace. |
| Model | L04-26 and L04-27 in few-shot (confidence 0.92) | The review rule (confidence below 0.70) relies on the confidence the model reports about itself. On these two tickets the model was wrong and sure of itself, so no person sees them. A confidence threshold cannot catch a confident error. |
| Test case | L04-17 | A wrong item in the parcel, a seller who never answered, and a request for the right product. The course dataset says `delivery`; we said `seller` with `delivery` acceptable; few-shot said `product_information` (confidence 0.65, sent to review) and chain-of-thought `returns_refunds`. Several labels are defensible: the case measures our label boundaries as much as the model. |
| Scorer | L04-18, L04-28 | L04-18 (some items missing from an intact box) expects `seller`; every strategy said `delivery`, our second acceptable label. Counting only the expected label, chain-of-thought falls from 27/30 to 25/30. The scorer choice moves the result by up to two cases, more than the gap between strategies. The judge is not a better scorer for the review decision: it agrees with us on 5 of 10 cases on that criterion. |
| Retrieval | none | No error comes from missing company text; see ADR 0003. |

**What would fix most errors:** a second version of the prompt with one line per label (what it covers, with the boundary cases seller vs delivery and other) and one line on the marketplace scope (beauty products only; a brand offering its products is `other`). This is a new prompt version: it must be run again on the 30 cases, and the v1 figures above stay as they are.

## Recommendation

We recommend the few-shot prompt on Claude Haiku 4.5: on 30 cases it is as accurate as the other two strategies (27/30, within one case), and it is the cheapest ($0.74 per 1,000 calls), the fastest (p90 1.16 s) and the only one with no re-prompt. Before go-live, its prompt needs label definitions and the marketplace scope, because its two errors that reach no person (L04-26, L04-27) come from the prompt, and the 30 cases must be run again on that version.

## Appendix: local run on llama3.2:3b (not used as evidence)

Kept for the record only. It measures a different, local model (Ollama, `llama3.2:3b`, temperature 0, seed 42, 2026-11-09), not the component we deploy, and it ran before all 30 cases had been checked by a person. None of the figures above come from it.

| Strategy | Correct | Median latency | P90 latency |
|---|---:|---:|---:|
| Zero-shot | 22/30 | 4,334 ms | 6,923 ms |
| Few-shot | 25/30 | 2,118 ms | 3,177 ms |
| Chain-of-thought | 22/30 | 8,395 ms | 11,018 ms |