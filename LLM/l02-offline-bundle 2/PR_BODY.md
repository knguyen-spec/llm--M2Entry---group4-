## What

Adds the L02 classifier schema, the single model-boundary module, the ten-case
offline runner, offline control-flow tests, the key-handling note and decision
record 0002.

## Why

The code can be reviewed and tested without an API key while the live run is
pending. The offline fixture proves validation, bounded re-prompts,
stop-reason handling and logging, but it is not model-performance evidence.

## How it was checked

`tests/test_llm.py` uses scripted responses for a valid record, a validation
failure followed by a correction, three failures leading to a give-up,
`max_tokens`, and a refusal. No network call or API key is used.

`LLM_MODE=offline python3 -m src.run_eval` runs the ten cases through the same
`classify()` boundary and writes `runs/results.csv` plus offline trace rows.

## Measurement limitation

The error rate, API token usage, latency and cost remain pending a live run
with a valid personal key or a teacher-approved supervised run. No offline
number is presented as an API result.

## Checklist

- [x] No API key, `.env` file or secret
- [x] API calls are confined to `src/llm.py`
- [x] At most two validation re-prompts
- [x] Non-terminal `stop_reason` rejected before trusting text
- [x] Offline tests added
- [ ] Live API run and measurement completed
- [ ] Reviewed by another group member
