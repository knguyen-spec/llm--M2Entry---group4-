# 0001: Route support tickets with a prompt-driven classifier

- **Status:** proposed
- **Date:** 2026-11-09
- **Author:** Lynn-Aurea Niat
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

We use seven labels: billing, delivery, returns_refunds, account, seller, product_information and other. They come from our own reading of the task in L01, not from the course's ticket set, which uses eight labels with product and information as two separate ones. Those two do not map onto our product_information: most of the course's information tickets ask where to find past orders, which fits our account label (the course itself gives account as their second label), and its product tickets are complaints about quality, which usually become returns_refunds because the customer wants a refund or a replacement. Our product_information is only for questions about the product itself, such as its ingredients or specifications. So when we reuse a course ticket as a test case, we never convert its label automatically: one member gives it one of our seven labels and another checks it, like every other case.

## Consequences

The group can measure routing errors directly and add structured validation in
L02. The system will not answer policy questions or resolve tickets. Ambiguous,
low-confidence and `other` cases require human review. A later decision record
must document whether retrieval is needed.
