# Decision 0004: evaluation and recommendation

- **Status:** proposed
- **Author:** Kelsy Nguyen
- **Date:** 2026-11-09

## Context

The classifier must be compared on the same 30 checked support-ticket cases. The comparison should separate exact label scoring from human judgement and should expose failures rather than reward a test set that is too easy.

## Decision

We compare zero-shot, few-shot and structured-reasoning prompts. A deterministic label scorer is used wherever the expected label is known. The judge is used only for cases that cannot be scored field by field, and its prompt contains at least four criteria: correctness, completeness, grounding in the ticket, and output-format compliance. Ten cases are scored by people before using the judge for calibration. Pairwise comparisons are run in both orders.

Because no valid personal provider key is currently available, live provider error rate, token usage, latency and cost remain explicitly pending. A local model may be used as a clearly labelled surrogate for prompt and guardrail testing, but its results will not be presented as production-provider evidence.

## Consequences

- The three strategies remain comparable because they use the same cases and scoring rules.
- Local measurements can show prompt sensitivity and code behaviour without exposing a key.
- The production recommendation cannot be final until a supervised provider run supplies measured tokens, latency and cost.
- The test cases remain provisional until the named reviewers confirm them.

## What would change the decision

A valid supervised run using the intended provider model, fixed parameters and the final 30-case file would replace the pending fields and could change the recommended strategy.
