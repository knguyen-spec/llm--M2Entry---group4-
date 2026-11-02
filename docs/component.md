# Our component

*Filled in from L01 and kept current: it is the page we present at the defence.*

## The task

Albert's Marketplace receives customer-support tickets about billing, delivery,
returns, accounts, sellers and product information. Customer-support agents and
marketplace operations teams need each ticket to be routed to the appropriate
team. Without a consistent classifier, routing is performed manually, which can
create delays and inconsistent categorisation. Our component classifies each
ticket into exactly one predefined support category. It supports human agents
and does not replace human review.

## Which component

We chose a prompt-driven **classifier**.

The classifier fits the task because each support ticket must receive one
predefined label. The course provides 120 labelled Albert's Marketplace support
tickets, creating a clear basis for human-checked evaluation.

The approved labels are:

- `billing`
- `delivery`
- `returns_refunds`
- `account`
- `seller`
- `product_information`
- `other`

A structured-extraction tool would be more directly transferable to
sustainability evidence workflows. A retrieval layer would be more relevant to
an enterprise sustainability assistant but would require additional document
preparation, embeddings, chunking, citation checking and prompt-injection
testing. These alternatives remain relevant to future projects but are outside
the scope of this classifier.

## Inputs and outputs

| Field | Description |
|---|---|
| Input | One Albert's Marketplace customer-support ticket in text form |
| Output | Exactly one label from the approved classification list |
| Data used | The course-approved set of 120 labelled support tickets; file name, version and checksum to be recorded after the dataset is obtained |
| Human oversight | A support agent remains responsible for reviewing and handling the ticket |
| Failure behaviour | Invalid or uncertain outputs must be flagged for validation or human review |

Example:

```text
Input:
I was charged twice for the same order.

Output:
billing
