# 0001: Build a prompt-driven classifier to route support tickets

*Draft prepared for the member who will defend this record. Review it, correct it and put your name in Author before merging.*

- **Status:** proposed
- **Date:** 2026-11-03
- **Author:** [name of the member who will defend this record]
- **Lesson:** L01

## Context

Albert's Marketplace receives customer-support tickets about billing, delivery,
returns, accounts, sellers and product information. Each ticket must reach the
team that can resolve it. Today this routing is manual, which causes delays and
inconsistent categories. The course provides 120 labelled support tickets.

The group must choose one component to build across the six lessons: a
classifier (one label per ticket), a structured-extraction tool (records from
tickets or reviews), or a retrieval layer (answers from company documents).

No figures yet. The first measured error rate will come from running the
zero-shot prompt on the ten test cases: model, date, parameters and test file
will be recorded in `docs/component.md`.

## Options considered

| Option | For | Against |
|---|---|---|
| Classifier | One label from a fixed list; labelled data exists; scoring is exact-match on the label | Less reusable for documents or records |
| Structured extraction | Produces records; closest to evidence-extraction work | Many fields to score; labels must be written for each field |
| Retrieval layer | Most relevant to an enterprise knowledge assistant | Needs document preparation, embeddings, chunking, citation checks and injection testing; the most risk for a first project |

## Criteria

- **Clear target and scoring:** can each output be checked against a single right answer?
- **Data available:** does a labelled set exist for the first evaluation?
- **Coverage of course lessons:** can the component use every lesson's techniques?
- **Risk to finish on time:** how much work is outside the course's core?

The classifier scores best on the first two criteria and on risk, and it
covers every lesson. Extraction and retrieval are worth revisiting later, but
each adds data preparation the first project does not need.

## Decision

Build a prompt-driven classifier that routes each Albert's Marketplace support
ticket to one of seven labels: `billing`, `delivery`, `returns_refunds`,
`account`, `seller`, `product_information`, `other`.

## Consequences

- **Easier:** exact-match scoring on labels; a clear baseline; one API call per
  ticket; a simple schema.
- **Harder:** ambiguous tickets need a second acceptable label, so label
  boundaries must be written down before the test cases are checked.
- **Watch:** label definitions in `docs/component.md` must match the course
  labelling guide. Lesson 3 must record, with evidence, why retrieval is not
  used. The classifier's error rate is measured on the 30 cases in L04, not
  only on the first ten.
