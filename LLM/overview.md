# Albert’s Marketplace Support-Ticket Classifier

## Business problem

Albert’s Marketplace receives customer-support tickets about billing, delivery,
returns and refunds, accounts, sellers and products. Agents need a consistent
first routing decision so that tickets reach the right team quickly. The system
does not resolve the customer’s problem or make policy promises; it proposes a
category and identifies uncertain cases for human review.

## Component decision

We chose a prompt-driven classifier rather than structured extraction or
retrieval.

The classifier only needs information contained in the ticket itself. Retrieval
would become necessary if the system had to consult changing return policies,
product catalogues, seller rules or other external documents.

## Input and output

| Input | Customer-support ticket text |
|---|---|
| Output | Label, confidence score and human-review flag |
| Labels | `billing`, `delivery`, `returns_refunds`, `account`, `seller`, `product_information`, `other` |
| Validation | Pydantic schema plus cross-field rules |
| Human review | Required for low-confidence or `other` classifications |

## Technical workflow

Ticket text → versioned prompt → `src/llm.py` → structured model response →
Pydantic validation → at most two validation re-prompts → call log →
classification or clear failure.

The API is called only through `src/llm.py`. Each call records the model,
timestamp, token usage, attempt number and validation result in
`runs/calls.csv`.

## Reliability and governance

- API failures are handled through one retry layer.
- `stop_reason` is checked before trusting the response.
- Invalid records are not returned as valid classifications.
- API keys are stored locally in `.env` and never committed.
- Ticket text is treated as untrusted input.
- Prompt-injection behaviour is tested before deployment.
- Every prompt and decision is versioned through a pull request.

## Evidence

The final evaluation compares zero-shot, few-shot and chain-of-thought
strategies on the same 30 human-checked test cases.

| Strategy | Error rate | Cost/1,000 calls | Latency | Prompt |
|---|---:|---:|---:|---|
| Zero-shot | pending | pending | pending | `prompts/route_zero_shot.md` |
| Few-shot | pending | pending | pending | `prompts/route_few_shot.md` |
| Chain-of-thought | pending | pending | pending | `prompts/route_cot.md` |

Every result will state the model, date, parameters and test file. Cases used
as prompt examples remain separate from evaluation cases.

## Deployment recommendation

See `docs/component.md`. Low-confidence, `other`, give-up and instruction-bearing
tickets are routed to human agents. The recommendation must change if the model
invents policy facts, fails injection tests, becomes too expensive or performs
poorly on a new ticket set.

## Current status

Completed and tested offline (no API key): component decision, output schema,
API module with re-prompts and retries, retrieval decision (proposed), scorers,
rubric and judge record, cost and latency arithmetic, code guardrails, and the
three strategy prompts.

To complete: check 20 more cases against the company's labelled tickets to
reach 30; run the three strategies, the judge and the injection tests on the
API; compute cost per 1,000 calls from `runs/`; record decision 0004; commit
the defence slides as a PDF in `docs/defence/`.
