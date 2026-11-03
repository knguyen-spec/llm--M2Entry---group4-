# 0003: No retrieval layer for the support-ticket classifier

*Draft. The status stays "proposed" until the evidence in this record has been produced by a real API run, and a second member has reviewed it.*

- **Status:** proposed
- **Date:** 2026-11-03
- **Author:** [name of the member who will defend this record]
- **Lesson:** L03

## Context

The classifier assigns each Albert's Marketplace support ticket to one of seven
labels (`docs/component.md`, `docs/decisions/0001-component-and-task.md`). The
classifier's input is the ticket text. Its output is one label, a confidence and
a review flag (`src/schema.py`).

Retrieval-augmented generation would add company documents to the prompt: for
example, a returns policy, a shipping table or the labelling guide. Before
choosing, we need to know whether the label depends on information that is not
in the ticket.

No figures from an API run exist yet. The evidence section below is pending.

## Options considered

| Option | For | Against |
|---|---|---|
| No retrieval: ticket text only | Simplest; no index, no citations, no added injection surface | Cannot use policy details that are not in the ticket |
| Retrieve policy documents for each ticket | Could resolve ambiguous tickets that depend on a policy | Needs parsing, chunking, embeddings and a citation check; adds untrusted text to the prompt |
| Retrieve similar labelled tickets as examples | Could improve label boundaries | Retrieved tickets are untrusted text; the evaluation set would have to exclude them to avoid inflating the score |

## Criteria

- **Need:** does the correct label depend on text outside the ticket?
- **Measured accuracy:** does the classifier fail on the test cases in a way that retrieval would fix?
- **Risk:** what new failure modes does retrieval add, including indirect prompt injection?
- **Cost and complexity:** what does retrieval add in tokens, latency and code?

## Evidence

The following must be filled in from a real API run, with the model, date,
parameters and test file recorded. Do not fill them in from expectation.

**Three ticket runs through `src/llm.py`:**

| Ticket | Expected label | Output | Confidence | Needs review | Result |
|---|---|---|---|---|---|
| [ticket id] | [label] | pending API run | pending API run | pending API run | pending API run |
| [ticket id] | [label] | pending API run | pending API run | pending API run | pending API run |
| [ticket id] | [label] | pending API run | pending API run | pending API run | pending API run |

**Injection test:** a ticket that contains an instruction to change the label or
reveal the prompt, and the classifier's output for it.

- Ticket: pending API run
- Output: pending API run
- Result: pending API run

## Decision

Do not add retrieval. The classifier routes each ticket using only the ticket
text and the label definitions in the prompt. This decision holds only if the
evidence above shows that the labels can be assigned from the ticket alone.

## Consequences

- **Easier:** no index, no embeddings, no citation check; a smaller attack
  surface; the evaluation is about the ticket text alone.
- **Harder:** tickets that depend on a policy may be sent to `other` or flagged
  for review rather than resolved.
- **Revisit if:** the failure analysis in L04 shows that a material share of
  errors come from missing policy text, or the injection test shows that the
  classifier can be steered by text in the ticket in a way that matters.
