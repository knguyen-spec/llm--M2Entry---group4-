# Albert's Marketplace LLM component: group repo

This repository is our group's LLM component for **Albert's Marketplace**, the
fictional European beauty marketplace of the LLM Fundamentals, Prompting & API
Integration course (MSA-DATI07-08, Albert School).

Every lesson adds a layer to the previous one. By the end of the course, the
repository will contain the component our group defends orally: a reproducible,
evaluated and governed LLM system. xxx

Our selected component is a prompt-driven **classifier** that routes customer
support tickets.

The final project will include:

- reproducible code;
- a comparison of prompting strategies on 30 test cases;
- an evaluation report;
- prompt-injection guardrails;
- measured cost per 1,000 calls;
- a deployment recommendation.

## Team

| Name | GitHub username | Project role |
|---|---|---|
| Kelsy Nguyen | knguyen-spec | Project lead and integration owner |
| Lynn-Aurea Niat | To be confirmed | Data and evaluation lead |
| Sereine Tawamba | To be confirmed | Schema and quality lead |

GitHub usernames, repository permissions and GitHub organisational roles will
be confirmed when the team members join the repository. Project roles describe
the agreed division of work and are separate from GitHub permissions.

## L01 project decision

- **Component:** Prompt-driven classifier
- **Task:** Route Albert's Marketplace customer-support tickets to the correct category.
- **Primary users:** Customer-support agents and marketplace operations teams.
- **Data source:** The course-approved set of 120 labelled support tickets.
- **Labels:** `billing`, `delivery`, `returns_refunds`, `account`,
  `seller`, `product_information`, `other`.

We selected the classifier because the task has a clear target, an existing
labelled dataset and measurable success criteria. It allows the group to build
the complete project foundation: prompt design, API integration, structured
output, validation, evaluation, cost measurement, latency measurement and
guardrails.

A structured-extraction tool would be more directly transferable to
sustainability evidence workflows. A retrieval layer would be more relevant to
an enterprise sustainability assistant but would require additional document
preparation, embeddings, chunking, citation checking and prompt-injection
testing. Those alternatives remain relevant to future sustainability
applications but are outside the selected scope of this project.

## How this repo grows

| Lesson | What our group adds | Where |
|---|---|---|
| L01 · Tokens and prompting | The classifier task, first prompt and first 10 test cases | `docs/component.md`, `prompts/`, `evals/` |
| L02 · API and structured outputs | API calls with retries, validated output and key handling | `src/`, `requirements.txt` |
| L03 · Retrieval-augmented generation | A decision about whether retrieval is needed, with evidence | `src/`, `docs/decisions/` |
| L04 · Evaluation, cost and guardrails | Golden set, rubric, 30 cases × 3 strategies, failure analysis, cost and injection tests | `evals/`, `docs/` |
| L05 · Review | Project clinic and defence preparation | `docs/defence/` |
| L06 · Project defences | Deployment recommendation and oral defence | `docs/component.md`, `docs/defence/` |

Starter files for later lessons arrive as **pull requests** opened by the
teaching team. We review and merge them like any other change.

## How we work

- **Every change goes through a pull request**, reviewed by another member
  before it reaches `main`.
- The first team-table change is also made through a reviewed pull request.
- **One decision, one record** in `docs/decisions/`: a prompt pattern, model,
  schema, retrieval setting or evaluation choice.
- Every member writes at least one decision record.
- **The commit history is graded.** We commit in small steps with messages
  that explain why the change was made.
- **A prompt is code.** It lives in `prompts/`, under version control, and
  changes are measured on the test cases before being merged.
- Every reported figure states its model, date, parameters and test file.
- Test cases are written and checked by different human members, never by a
  model.

## Project workflow

The project changes should be committed in this order:

1. Team table.
2. Component decision.
3. First prompt.
4. Ten test cases.
5. Decision record `0001-component-and-task.md`.
6. API implementation and validated output.
7. Evaluation, cost, latency and guardrail results.

When using GitHub's web editor, create a new branch and open a pull request.
Do not commit directly to `main`.

## Your API key

**Each member uses their own key with a spending limit.**

Supported options are:

- an Anthropic key beginning with `sk-ant-`;
- an OpenRouter key beginning with `sk-or-`.

The key is personal and must never appear in:

- this repository;
- source code;
- notebooks;
- screenshots;
- chat messages;
- commit history.

Keep the key in a local `.env` file, which `.gitignore` excludes. Copy
`.env.example` to `.env` and add the appropriate key locally.

If a key reaches GitHub, even briefly, tell the teaching team immediately so it
can be revoked. Deleting the commit is not enough because the key may already
have been copied.

## Layout

```text
docs/
  component.md       the task, users, evaluation and recommendation
  decisions/         one record per project decision
prompts/             versioned prompts, beginning with L01
evals/               test cases, golden set and evaluation results
src/                 code that calls and validates the model, from L02
runs/                call logs and measured results
tests/               guardrail tests
