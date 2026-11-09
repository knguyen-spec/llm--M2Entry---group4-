# Evaluation report (status)

Status: offline checks done. Live figures pending a model run. Nothing in this file is a measured result yet.

## What is checked offline (no API)

| Check | Where | Status |
|---|---|---|
| Normalisation, exact match, token F1 | `src/metrics.py`, `tests/test_metrics.py` | passing |
| p90 latency arithmetic | same | passing |
| Swap test: flags position-driven judges only | same | passing |
| Pareto front and dominance | same | passing (lecture figures as reference values) |
| Cache key includes the model | same | passing |
| Cost arithmetic, cache multipliers | same | passing |
| Label scorer and judge record | `src/evaluate.py`, `tests/test_evaluate.py` | passing (PR #11) |

Full offline suite on 2026-11-09: 57 passed, 3 skipped (the live tests, which need a key).

## Pending: needs a model run

| Item | Status |
|---|---|
| Strategy results on 30 cases (zero-shot, few-shot, chain-of-thought) | pending run |
| Right answers out of 30, by scorer | pending run |
| Cost per 1,000 calls, from `runs/` tokens | pending run |
| Median and p90 latency | pending run |
| Pareto front across strategies | pending run |
| Judge model, agreement with our own scores on 10 cases | pending run |
| Verdicts changed by the swap | pending run |
| Injection tests run several times | pending run |

Each figure, when measured, needs the model, the date, the parameters and the test file, and must be recorded in `runs/`.

## Cost formula

Cost per 1,000 calls, in US$, at Claude Haiku 4.5 list prices ($1 per million input tokens, $5 per million output tokens, checked 2026-11-09):

(average input tokens per call + 5 × average output tokens per call) ÷ 1,000

The figure itself is pending Claude token counts. Token counts from a local model are not converted: it uses a different tokenizer.

## Local surrogate evaluation

Status: pending. A local run with `llama3.2:3b` (Ollama, temperature 0, seed 42) was made on 2026-11-09 on 30 cases, but 20 of those cases had not been checked by a person, so its figures are not reported here. Results on the 10 checked cases will be added after review, labelled as a local surrogate and not as Claude API performance. Whether a local surrogate counts as evidence is pending the teacher's approval.
