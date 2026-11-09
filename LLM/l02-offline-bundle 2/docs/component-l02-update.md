## L02 implementation and evidence

`src/llm.py` is the single model boundary. It validates every returned JSON
record against `TicketClassification`, checks `stop_reason` before trusting
the text, retries transient API failures through the SDK configuration, and
re-prompts on validation errors at most twice.

The current ten-case run was executed in `offline` fixture mode because no
personal API key is available. `runs/results.csv` and `runs/calls.csv` are
therefore structural test outputs, not live model evidence. Live error rate,
token usage, latency and cost are unavailable and must remain marked
**pending** in the defence documentation.
