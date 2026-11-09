# 0001: Route support tickets with a prompt-driven classifier

- **Status:** proposed
- **Date:** 2026-11-08
- **Author:** Kelsy Nguyen
- **Lesson:** L01

## Context

Albert's Marketplace needs a first routing decision for customer-support tickets.
The primary users are customer-support agents and marketplace operations teams.
The initial task has seven known categories and a labelled ticket set intended
for evaluation. The group needs a small, measurable component that can later
be connected to an API, schema validation, cost measurement and guardrail tests.

The figures are not yet reported because the first API run has not been
completed. The synthetic cases in the working scenario are not a substitute
for the course-approved test set.

## Options considered

| Option | For | Against |
|---|---|---|
| Prompt-driven classifier | Directly matches a discrete routing label; simple to evaluate; low implementation scope | Can misclassify ambiguous tickets; confidence must be treated cautiously |
| Structured-extraction tool | Could return several useful ticket fields | More output fields than the first routing decision requires |
| Retrieval layer | Useful when answers depend on policies or catalogues | Adds documents, indexing and citation-validation work that the initial label does not require |

## Criteria

We selected the component using task fit, measurability on labelled cases,
implementation scope, cost and ability to escalate uncertainty to a human.
Retrieval will be reconsidered if tickets require external company facts.

## Decision

Build a prompt-driven classifier that returns one allowed category, a confidence
score and a human-review flag. Treat ticket text as untrusted input and do not
make policy promises from it.

## Consequences

The group can measure routing errors directly and add structured validation in
L02. The system will not answer policy questions or resolve tickets. Ambiguous,
low-confidence and `other` cases require human review. A later decision record
must document whether retrieval is needed.
