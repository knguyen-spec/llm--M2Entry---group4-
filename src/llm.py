"""The only module that calls the API.

Every call the classifier makes passes through classify(). It returns a
checked TicketClassification, or a Result whose reason says why it failed.
It never returns an answer it has not checked.
"""

import csv
import datetime as dt
import logging
from dataclasses import dataclass
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from pydantic import ValidationError

from src.schema import TicketClassification

ROOT = Path(__file__).resolve().parents[1]
PROMPT_FILE = ROOT / "prompts" / "route_zero_shot_json.md"   # the JSON version matching src/schema.py
CALLS_LOG = ROOT / "runs" / "calls.csv"

MODEL = "claude-haiku-4-5"       # must match the model used for the measured prompt
MAX_OUTPUT_TOKENS = 300
MAX_REPROMPTS = 2                # validation failures only; transient errors are the SDK's job
SDK_RETRIES = 2                  # the one retry layer: the SDK retries 429, 5xx and timeouts

load_dotenv(ROOT / ".env")       # reads the key from .env; the key is never printed or passed in code
client = anthropic.Anthropic(max_retries=SDK_RETRIES)
log = logging.getLogger(__name__)

CSV_HEADER = ["timestamp", "model", "input_tokens", "output_tokens", "attempt", "passed_validation"]


def load_system_prompt() -> str:
    """The text under '## System prompt' in the prompt file, so the prompt is versioned in one place."""
    text = PROMPT_FILE.read_text(encoding="utf-8")
    start = text.index("## System prompt") + len("## System prompt")
    end = text.index("## User-message shape")
    return text[start:end].strip()


SYSTEM = load_system_prompt()
SCHEMA = anthropic.transform_schema(TicketClassification)   # verify in the pinned SDK (1.10.0)


@dataclass(frozen=True)
class Result:
    classification: TicketClassification | None
    attempts: int
    reason: str                  # "ok", or why the classification was not produced


def log_call(attempt: int, usage, passed: bool) -> None:
    """One row per API call, appended to runs/calls.csv."""
    CALLS_LOG.parent.mkdir(parents=True, exist_ok=True)
    is_new = not CALLS_LOG.exists()
    with CALLS_LOG.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(CSV_HEADER)
        writer.writerow([
            dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            MODEL,
            usage.input_tokens if usage else "",
            usage.output_tokens if usage else "",
            attempt,
            passed,
        ])


def classify(ticket_text: str) -> Result:
    messages = [{"role": "user", "content": f"Ticket:\n{ticket_text}"}]

    for attempt in range(1, MAX_REPROMPTS + 2):          # at most three attempts
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_OUTPUT_TOKENS,
                system=SYSTEM,
                messages=messages,
                output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
            )
        except anthropic.APIError as e:
            # The SDK has already retried transient errors, so this one is final.
            log.error("API error on attempt %s: %s (request %s)", attempt, type(e).__name__,
                      getattr(e, "request_id", None))
            log_call(attempt, None, passed=False)
            return Result(None, attempt, f"api error: {type(e).__name__}")

        text = response.content[0].text if response.content else ""

        # A cut-off or refused answer will not be fixed by asking again.
        if response.stop_reason != "end_turn":
            log_call(attempt, response.usage, passed=False)
            return Result(None, attempt, f"stopped: {response.stop_reason}")

        try:
            record = TicketClassification.model_validate_json(text)
        except ValidationError as e:
            log_call(attempt, response.usage, passed=False)
            if attempt > MAX_REPROMPTS:
                return Result(None, attempt, "validation failed after re-prompts")
            error = "; ".join(err["msg"] for err in e.errors())
            # Send back the model's own answer and the error, so it can correct the record.
            messages += [
                {"role": "assistant", "content": text},
                {"role": "user", "content": f"Your answer failed validation: {error}\n"
                                            "Send the corrected JSON only."},
            ]
            continue

        log_call(attempt, response.usage, passed=True)
        return Result(record, attempt, "ok")

    return Result(None, MAX_REPROMPTS + 1, "validation failed after re-prompts")   # not reached
