"""The only module in the repository that calls the API. Every model call goes through classify().

Route: JSON in the prompt, validated here with Pydantic (see docs/decisions/0002).
Retry layers: the SDK retries transport errors (SDK_RETRIES). This file never retries
a transport error itself. It re-prompts only when the answer fails validation.
"""
import csv
import datetime as dt
from dataclasses import dataclass
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from pydantic import ValidationError

from src.schema import TicketClassification

load_dotenv()  # reads .env in the repository root. .env is never committed.

MODEL = "anthropic/claude-haiku-4.5"
MAX_OUTPUT_TOKENS = 300
MAX_REPROMPTS = 2  # re-prompts after the first attempt: at most 3 calls per ticket
SDK_RETRIES = 2  # the one transport retry layer
PROMPT_PATH = Path("prompts/route_zero_shot_json.md")
CALLS_LOG = Path("runs/calls.csv")
CALLS_HEADER = ["timestamp", "model", "input_tokens", "output_tokens", "attempt", "passed"]

_client = None


@dataclass
class Result:
    classification: TicketClassification | None
    attempts: int
    reason: str  # "ok", or why it failed


def _get_client():
    # Created lazily, with no key argument: the SDK reads the key from the environment (.env).
    global _client
    if _client is None:
        _client = anthropic.Anthropic(max_retries=SDK_RETRIES)
    return _client


def _send(system, messages):
    return _get_client().messages.create(
        model=MODEL,
        max_tokens=MAX_OUTPUT_TOKENS,
        system=system,
        messages=messages,
    )


def log_call(response, attempt, passed):
    """One row per API call, appended to runs/calls.csv."""
    CALLS_LOG.parent.mkdir(parents=True, exist_ok=True)
    is_new = not CALLS_LOG.exists()
    usage = getattr(response, "usage", None)
    with CALLS_LOG.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(CALLS_HEADER)
        writer.writerow([
            dt.datetime.now().isoformat(timespec="seconds"),
            MODEL,
            getattr(usage, "input_tokens", 0) or 0,
            getattr(usage, "output_tokens", 0) or 0,
            attempt,
            passed,
        ])


def _feedback(error: ValidationError) -> str:
    messages = [err["msg"].removeprefix("Value error, ") for err in error.errors()]
    return " ".join(messages)


def classify(ticket_text: str, call=None) -> Result:
    """Classify one ticket. `call` replaces the API in tests: call(system, messages) -> response."""
    system = PROMPT_PATH.read_text(encoding="utf-8")
    messages = [{"role": "user", "content": f"Ticket:\n{ticket_text}"}]
    send = call or _send
    attempt = 0

    for attempt in range(1, MAX_REPROMPTS + 2):
        try:
            response = send(system, messages)
        except anthropic.APIError as error:
            # The API failed. Return a clear failure instead of crashing.
            log_call(None, attempt, False)
            return Result(None, attempt, f"api error: {type(error).__name__}")

        # Check stop_reason before trusting the text.
        if response.stop_reason != "end_turn":
            log_call(response, attempt, False)
            return Result(None, attempt, f"stopped: {response.stop_reason}")

        text = "".join(
            block.text for block in response.content if getattr(block, "type", "") == "text"
        )
        try:
            classification = TicketClassification.model_validate_json(text)
        except ValidationError as error:
            log_call(response, attempt, False)
            messages.append({"role": "assistant", "content": text})
            messages.append({
                "role": "user",
                "content": (
                    f"That answer was rejected: {_feedback(error)} "
                    "Return the JSON again with that fixed, and nothing else."
                ),
            })
            continue

        log_call(response, attempt, True)
        return Result(classification, attempt, "ok")

    return Result(None, attempt, "gave up after re-prompts")
