# Decision 0002: structured output and bounded retries

- **Status:** proposed
- **Date:** 2026-11-09
- **Author:** Sereine Tawamba 

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

The first live run (2026-11-09, anthropic/claude-haiku-4.5 through OpenRouter, max_output_tokens 300, the first 10 cases of evals/test_cases.csv) made 11 API calls for 10 tickets. A call used 367 input tokens on average: the system prompt, which carries the JSON format instructions, plus the ticket. We did not measure the format instructions on their own, so we cannot say exactly how many tokens this route adds compared with another one.


One answer out of 10 failed validation on its first attempt and was fixed by one re-prompt; none was given up. It was case L01-07, a ticket with two problems (a double charge and a late parcel). Our log records that the first answer failed validation, but not the error message, so we cannot tell whether it was broken JSON or an answer that broke our review rule; we will log the message from now on. The re-prompt cost one extra call (about $0.0008, a full resend of the conversation) and about 1.4 s. With 1 re-prompt in 10, the route stays cheap; if re-prompts became frequent on the 30 cases, structured outputs would be worth testing.


The SDK's retry layer (max_retries=2) was not needed in this run: no transient error occurred. Run cost: $0.00648, or $0.59 per 1,000 calls.

## Consequences

The code can be reviewed and regression-tested now, without exposing another
credential or using a teammate's budget. The trade-off is that the offline
fixture cannot establish model accuracy or API economics. The later live run
must record its model, date, parameters, tokens, re-prompts, give-ups and cost.
