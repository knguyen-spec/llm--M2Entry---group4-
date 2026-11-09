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

The L04 comparison uses zero-shot, few-shot and chain-of-thought strategies
on the same 30 human-checked cases. The figures are pending; they must come
from a recorded run (`docs/evaluation.md`).

| Strategy | Error rate | Cost per 1,000 calls | Latency | Prompt file |
|---|---:|---:|---:|---|
| Zero-shot | pending run | pending | pending | `prompts/route_zero_shot.md` |
| Few-shot | pending run | pending | pending | `prompts/route_few_shot.md` |
| Chain-of-thought | pending run | pending | pending | `prompts/route_cot.md` |

## Deployment recommendation

No final strategy is chosen until the three strategies have been measured on
30 checked cases. The deployment we would defend:

- **Model and path:** the chosen prompt on Claude Haiku 4.5, through `src/llm.py` only.
- **A person sees:** the label `other`, confidence below 0.70, a give-up after two
  re-prompts, and any ticket that contains instructions to the system.
- **Before go-live:** 30 checked cases measured on the Claude API; the injection
  attack fails three runs out of three on the deployed model; cost per 1,000
  calls measured from `runs/`.
- **We change this if:** errors come from missing policy text (reopens retrieval),
  the deployed model fails the injection tests, or agents cannot absorb the
  number of reviews.
