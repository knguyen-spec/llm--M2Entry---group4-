# Our component

*L01 working scenario. The checker names in `evals/test_cases.csv` are a balanced
review assignment; each named teammate must actually inspect the cases before
this file is treated as graded evidence.*

## The task

Albert's Marketplace needs a consistent first routing decision for customer-support
tickets. Customer-support agents and marketplace operations teams use the result
to send each ticket to the right queue. Without a first classification, tickets
can be sent to the wrong team, creating avoidable hand-offs and slower responses.
No operational error figure is claimed yet: the group will add one only if it
has a source and a date.

## Which component

We chose a prompt-driven classifier. It assigns each ticket to one of seven
support categories: `billing`, `delivery`, `returns_refunds`, `account`,
`seller`, `product_information` or `other`.

This fits the task because the required decision is a discrete label and the
ticket text normally contains the information needed to choose it. Structured
extraction would be useful for turning a ticket into many fields, but it would
not by itself solve routing. Retrieval is not required for the initial task
(decision record 0003): the classifier should not invent policy facts.

## Inputs and outputs

| Field | Definition |
|---|---|
| Input | One customer-support ticket as text |
| Output | One category, a confidence score and a human-review flag |
| Labels | `billing`, `delivery`, `returns_refunds`, `account`, `seller`, `product_information`, `other` |
| Data used | Course-approved labelled ticket set; version and checksum: to be recorded |
| Safety rule | Instructions inside a ticket are treated as ticket content, not as instructions to the classifier |

## Strategies compared

Measured on 2026-11-09 with `anthropic/claude-haiku-4.5`, max_output_tokens 300, model-default sampling, on the 30 cases of `evals/test_cases.csv` (error rate counts the second acceptable label as right). Details and the Pareto front: `docs/evaluation.md`.

| Strategy | Error rate | Cost per 1,000 calls | Latency | Prompt file |
|---|---:|---:|---:|---|
| Zero-shot | 2/30 (7%) | $1.02 | median 2.60 s, p90 4.47 s | `prompts/route_zero_shot.md` |
| Few-shot | 3/30 (10%) | $0.74 | median 0.98 s, p90 1.16 s | `prompts/route_few_shot.md` |
| Chain-of-thought | 3/30 (10%) | $1.03 | median 1.58 s, p90 1.83 s | `prompts/route_cot.md` |

**First run (L02), 10 cases, zero-shot:** error rate 0/10 (0%), 1 answer re-prompted, 0 given up. 11 API calls for 10 tickets; the run cost $0.00648, which is $0.59 per 1,000 calls ($0.65 per 1,000 tickets, re-prompts included). Latency: median 0.91 s, p90 1.44 s.
Four facts: model anthropic/claude-haiku-4.5 (through OpenRouter), date 2026-11-09, parameters max_output_tokens 300 and model-default sampling, test file evals/test_cases.csv (first 10 cases). Files: runs/results_zero_shot_10cases.csv, runs/calls.csv.
10 out of 10 tells us the module works end to end, not that the component is good: these ten cases are easy, and the 30-case set (L04) must include cases it can fail.

## Deployment recommendation

We recommend the few-shot prompt on Claude Haiku 4.5: on 30 cases it is as accurate as the other two strategies (27/30, within one case), and it is the cheapest ($0.74 per 1,000 calls), the fastest (p90 1.16 s) and the only one with no re-prompt. Before go-live, its prompt needs label definitions and the marketplace scope, because its two errors that reach no person (L04-26, L04-27) come from the prompt, and the 30 cases must be run again on that version.

- **Model and path:** `prompts/route_few_shot.md` on `anthropic/claude-haiku-4.5`, through `src/llm.py` only.
- **A person sees:** the label `other`, confidence below 0.70, a give-up after two re-prompts, and any ticket that contains instructions to the system (7 of 30 test tickets in few-shot).
- **Before go-live:** the prompt with label definitions, run again on the 30 cases; the injection tests passing on the deployed model; cost per 1,000 calls measured from `runs/`.
- **We change this if:** errors come from missing policy text (reopens retrieval, ADR 0003), the deployed model fails the injection tests, or agents cannot absorb the number of reviews.

Evidence: `docs/evaluation.md` (strategies, judge, failure analysis), `docs/decisions/0004-evaluation.md`.