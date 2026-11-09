# Decision 0002: structured output and bounded retries

- **Status:** proposed
- **Date:** 2026-11-08
- **Author:** Lynn-Aurea Niat (draft assignment; confirm before merge)

## Context

The classifier must return a small record rather than free-form prose. Its
output also has a cross-field rule: low confidence or the `other` label must
request human review. A JSON schema describes the fields and ranges, but code
must enforce that cross-field rule.

## Decision

Use JSON in the version-controlled prompt, followed by Pydantic validation in
`src/llm.py`. This is the most portable route across API providers and keeps
the application-level rule under our control. `src/llm.py` is the only module
allowed to call the API.

Use the SDK's retry layer with `max_retries=2` for transient transport errors.
Validation failures are a separate application concern: the module sends the
validation error back to the model at most twice. A non-terminal
`stop_reason`, such as `max_tokens` or `refusal`, is rejected before its text
is trusted.

## Evidence and limitation

The offline test suite uses scripted responses to prove the valid-response,
re-prompt, give-up, stop-reason and logging paths without a key. The current
`runs/calls.csv` is therefore only a header, and no API token overhead, error
rate, latency or cost is claimed. Those figures remain pending until a valid
personal API key or a teacher-approved supervised run is available.

## Consequences

The code can be reviewed and regression-tested now, without exposing another
credential or using a teammate's budget. The trade-off is that the offline
fixture cannot establish model accuracy or API economics. The later live run
must record its model, date, parameters, tokens, re-prompts, give-ups and cost.
