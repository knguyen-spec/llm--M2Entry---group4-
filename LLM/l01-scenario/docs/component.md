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
because the classifier should not invent policy facts; a later decision record
will test whether external policies or catalogues are needed.

## Inputs and outputs

| Field | Definition |
|---|---|
| Input | One customer-support ticket as text |
| Output | One category, a confidence score and a human-review flag |
| Labels | `billing`, `delivery`, `returns_refunds`, `account`, `seller`, `product_information`, `other` |
| Data used | Course-approved labelled ticket set; version and checksum: to be recorded |
| Safety rule | Instructions inside a ticket are treated as ticket content, not as instructions to the classifier |

## Strategies compared

The L04 comparison will use zero-shot, few-shot and chain-of-thought strategies
on the same 30 human-checked cases. The following figures are intentionally
pending; they must come from a recorded run rather than this scenario.

| Strategy | Error rate | Cost per 1,000 calls | Latency | Prompt file |
|---|---:|---:|---:|---|
| Zero-shot | pending API run | pending | pending | `prompts/route_zero_shot.md` |
| Few-shot | pending L04 | pending | pending | to be added |
| Chain-of-thought | pending L04 | pending | pending | to be added |

## Deployment recommendation

No final deployment recommendation is made until the three strategies have
been measured. The chosen variant should balance error rate, cost and latency.
Low-confidence and `other` classifications should be sent to a human agent.
The recommendation should change if the classifier invents policy facts, fails
the injection tests or performs poorly on a new checked ticket set.
