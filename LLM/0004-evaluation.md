# 0004: Evaluation

- **Status:** draft. Figures pending a model run.
- **Author:** [member who has written least so far, to fill in, not the drafter]
- **Date:** [to fill in]

## Context

The component classifies support tickets into seven labels, with a confidence and a review flag. We need to know how often it is right, what it costs, and whether it can be trusted without a person reading every answer.

## Decision

Scorers:
- Label exact match with normalisation (`src/evaluate.py`, `src/metrics.py`): no model, tested on known pairs.
- A judge from a different model than the component's, scoring four rubric criteria (`evals/rubric.md`, `prompts/judge.md`). Both orders are judged; a preference counts only when both orders agree.

Strategy: [pending run: zero-shot, few-shot or chain-of-thought, chosen from the 30-case results].

## Evidence

Pending. For each figure, record the model, date, parameters and test file:
- Right answers out of 30, by scorer: pending run.
- Judge agreement with our own scores on ten cases: pending run.
- Verdicts changed by the swap: pending run.
- Cost per 1,000 calls from `runs/`: pending run.
- Median and p90 latency: pending run.

## Limits

- Thirty cases can tell differences of about three points, no smaller.
- The judge is calibrated only on the ten cases we scored ourselves.
- Any local model results are a surrogate, not the component under evaluation.

## Consequences

If the best strategy misses the target on the failure categories we read, we change the prompt or the model, and measure again.
