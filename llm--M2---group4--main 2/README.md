# Albert's Marketplace support-ticket router (group 4)

## What it is, and for whom

Albert's Marketplace is a European marketplace for beauty products sold by
third-party sellers. Every customer ticket lands in one support inbox, and a
person reads it just to decide which team should handle it.

This component does that first step. It reads one ticket and returns one of
seven labels: `billing`, `delivery`, `returns_refunds`, `account`, `seller`,
`product_information` or `other`. It also returns a confidence from 0 to 1 and
`needs_human_review`. A person reviews the ticket when the confidence is below
0.70, when the label is `other`, when the answer is invalid twice in a row, or
when the ticket tries to give orders to the system.

- **For whom:** the ticketing system, which puts the ticket in a team's queue,
  then the agents of that team.
- **Model:** Claude Haiku 4.5, with the few-shot prompt
  (`prompts/route_few_shot.md`). It got 27 of 30 test cases right, at $0.74
  per 1,000 calls and 1.16 s at p90 (`docs/evaluation.md`, 2026-11-09).
- **What is sent:** only `label`, `needs_human_review` and
  `injection_suspected`, built in code (`src/guardrails.py`). No text written
  by the model leaves the component.

## Install

You need Python 3.10 or later (`python3 --version`).

```bash
git clone https://github.com/lniat-coder/llm--M2---group4-.git
cd llm--M2---group4-
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Then open `.env` and fill in **your own** key. It is personal, has a spending
limit, and never goes in the repository (`.gitignore` excludes `.env`). There
are two kinds of key; uncomment the lines for yours only:

| Your key starts with | Lines to fill in `.env` |
|---|---|
| `sk-ant-` (Anthropic) | `ANTHROPIC_API_KEY=` |
| `sk-or-` (OpenRouter) | `ANTHROPIC_BASE_URL=https://openrouter.ai/api`, `ANTHROPIC_AUTH_TOKEN=`, and the two model lines `MODEL=anthropic/claude-haiku-4.5` and `JUDGE_MODEL=anthropic/claude-sonnet-4.5` |

The code is the same for both. If a key ever reaches GitHub, even for a
minute, tell the teaching team at once so it can be revoked: deleting the
commit does not help.

**Without a key**, set `LLM_MODE=offline` to run everything on a local fixture:
no network and no cost, but the answers are not the model's.

## Run it on one ticket

```bash
python -m src.classify_one "My parcel is late and the tracking has not changed."
```

It prints what the model returned (validated) and what would be sent:

```
model returned: {"label": "delivery", "confidence": 0.9, "needs_human_review": false}
sent:           {"label": "delivery", "needs_human_review": false, "injection_suspected": false}
```

Add `--strategy zero_shot` or `--strategy cot` to try the other prompts. Each
call is logged in `runs/calls.csv` (tokens, cost, latency).

## Run the evaluation

The 30 test cases are in `evals/test_cases.csv`. Each label was written by one
member and checked by the other.

```bash
python -m src.run_eval --strategy all     # 3 strategies x 30 cases: about 2 minutes, about $0.10
python -m src.summarise                   # right answers, cost per 1,000 calls, latency, Pareto front
python -m src.judge --strategy all        # the judge (Claude Sonnet 4.5) on the 4 rubric criteria
python -m src.judge --pairwise            # pairs of strategies, judged in both orders
python -m src.summarise --judge           # judge means, calibration against our hand scores, swap
python -m src.retrieval_probe             # the evidence for "no retrieval" (ADR 0003)
```

Results go to `runs/`. The report, the failure analysis and the
recommendation are in `docs/evaluation.md`. `python -m src.summarise` re-reads
`runs/` without calling the API.

## Run the tests

```bash
python -m pytest -q                                        # offline, no key needed
LIVE_TESTS=1 python -m pytest tests/test_guardrails.py -q  # injection attacks against the real model
```

Use `python -m pytest`, not `pytest` alone, so that Python finds `src`. The
live tests send 5 attacks, 3 times each, plus a normal ticket, and check that
every attack reaches a person.

## Where things are

```
docs/component.md      the task, the users, the deployment recommendation
docs/evaluation.md     strategies, judge, injection tests, failure analysis, recommendation
docs/decisions/        one record per decision (ADR 0001 to 0004)
docs/defence/          the slides of the oral defence (PDF)
prompts/               every prompt, versioned
evals/                 test cases, rubric, our hand scores
src/                   the code: llm.py is the only module that calls the API
runs/                  every recorded run (results, calls, judge)
tests/                 offline tests, and the live injection tests
```

## Team

| Name | GitHub | Role |
|---|---|---|
| Lynn-Aurea Niat | lniat-coder | task and component, test cases, judge calibration, failure analysis and recommendation (ADR 0001, ADR 0004), retrieval evidence (ADR 0003) |
| Sereine Tawamba | stawamba-commits | API module, schema and retries (ADR 0002), strategy runs, README and defence slides |
| Kelsy Nguyen | knguyen-spec | first classifier, schema and prompts, retrieval decision draft (ADR 0003) |

Every change went through a pull request reviewed by another member.

## Data

Albert's Marketplace's data and its 120 labelled support tickets are in the
company repo (link on the course site). They are synthetic or derived from
public datasets; their licence and attribution are stated there. Twenty of our
test cases come from those tickets (`source_ticket_id` in
`evals/test_cases.csv`).

## Ownership

**No licence is granted for this repository.**
- **The template:** the course's README template, the `docs/` templates and
  the folder structure remain the course author's intellectual property. Do
  not reuse them outside the course.
- **Our work:** what our group wrote here belongs to our group.
