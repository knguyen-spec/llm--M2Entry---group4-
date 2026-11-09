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
