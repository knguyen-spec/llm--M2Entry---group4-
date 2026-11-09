# Ten-minute defence outline

## 1. Problem and users — 1 minute

Support agents need consistent routing of customer tickets. The component predicts one support category and flags uncertain or unusual cases for human review.

## 2. Why a classifier — 1 minute

The task has a fixed label set, labelled examples and a measurable outcome. Retrieval was rejected because the ticket text itself is sufficient for routing; policy questions would change that decision.

## 3. Design — 2 minutes

Show the path: ticket → prompt → one API boundary → structured Pydantic record → cross-field validation → human-review flag. Mention bounded validation re-prompts, one retry layer and `stop_reason` checks.

## 4. Evaluation — 2 minutes

Show the 30-case table for zero-shot, few-shot and structured reasoning. State which figures are local-surrogate results and which live provider figures remain pending.

## 5. Failures and guardrails — 2 minutes

Show one misclassification and one prompt-injection ticket. Explain that ticket text is data, not instructions, and that the output is validated before being returned.

## 6. Recommendation — 1 minute

Recommend the strategy only conditionally on measured accuracy, latency and cost. State what a supervised provider run could change.

## 7. Review and limitations — 1 minute

Mention the review gap honestly, the corrective reviewed PR, the unavailable API key, and the difference between local evidence and production evidence.
