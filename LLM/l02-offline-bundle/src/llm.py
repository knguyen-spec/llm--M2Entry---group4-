"""The single model boundary for the support-ticket classifier.

The production path uses the Anthropic SDK and reads credentials from the
environment. The offline path is a deterministic fixture used only to test
validation, bounded re-prompts, stop-reason handling and logging when no API
key is available. Offline output is not model-performance evidence.
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any

try:
    import anthropic
except ImportError:  # The offline tests do not require the SDK.
    anthropic = None  # type: ignore[assignment]

from dotenv import load_dotenv
from pydantic import ValidationError

from src.schema import TicketClassification


ROOT = Path(__file__).resolve().parents[1]
PROMPT_FILE = ROOT / "prompts" / "route_zero_shot.md"
CALLS_LOG = Path(os.getenv("CALLS_LOG", str(ROOT / "runs" / "calls.csv")))

MODEL = os.getenv("MODEL", "claude-haiku-4-5")
MAX_OUTPUT_TOKENS = 300
MAX_REPROMPTS = 2
SDK_RETRIES = 2

load_dotenv(ROOT / ".env")
log = logging.getLogger(__name__)

CSV_HEADER = [
    "timestamp",
    "model",
    "input_tokens",
    "output_tokens",
    "attempt",
    "passed_validation",
    "mode",
]


@dataclass(frozen=True)
class Result:
    classification: TicketClassification | None
    attempts: int
    reason: str


def _system_prompt() -> str:
    if PROMPT_FILE.exists():
        return PROMPT_FILE.read_text(encoding="utf-8")
    return (
        "Classify the ticket into the allowed labels. Return JSON only with "
        "label, confidence and needs_human_review."
    )


SYSTEM = _system_prompt()


def _usage(response: Any) -> Any:
    return getattr(response, "usage", None)


def log_call(attempt: int, usage: Any, passed: bool, mode: str) -> None:
    """Append one trace row without ever writing credentials."""

    CALLS_LOG.parent.mkdir(parents=True, exist_ok=True)
    is_new = not CALLS_LOG.exists()
    with CALLS_LOG.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        if is_new:
            writer.writerow(CSV_HEADER)
        writer.writerow(
            [
                dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                MODEL if mode == "api" else "offline-fixture-v1",
                getattr(usage, "input_tokens", "") if usage else "",
                getattr(usage, "output_tokens", "") if usage else "",
                attempt,
                passed,
                mode,
            ]
        )


def _offline_record(ticket_text: str) -> dict[str, Any]:
    """Return a deterministic fixture record for code-path testing only."""

    text = ticket_text.lower()
    if any(word in text for word in ("charged", "charge", "invoice", "vat")):
        label = "billing"
    elif any(word in text for word in ("parcel", "tracking", "delivery", "arrive")):
        label = "delivery"
    elif any(word in text for word in ("password", "login", "account")):
        label = "account"
    elif any(word in text for word in ("seller", "merchant")):
        label = "seller"
    elif any(word in text for word in ("return", "refund", "send it back")):
        label = "returns_refunds"
    elif any(word in text for word in ("vegan", "fragrance", "ingredient", "product")):
        label = "product_information"
    else:
        label = "other"

    return {
        "label": label,
        "confidence": 0.95 if label != "other" else 0.40,
        "needs_human_review": label == "other",
    }


class OfflineFixtureClient:
    """Minimal client-shaped fixture; never contacts a network."""

    def __init__(self, ticket_text: str):
        self.ticket_text = ticket_text
        self.messages = self

    def create(self, **_: Any) -> Any:
        payload = json.dumps(_offline_record(self.ticket_text))
        return SimpleNamespace(
            content=[SimpleNamespace(text=payload)],
            stop_reason="end_turn",
            usage=SimpleNamespace(input_tokens=0, output_tokens=0),
        )


def _api_client() -> Any:
    if anthropic is None:
        raise RuntimeError("Install the pinned anthropic dependency for API mode.")
    return anthropic.Anthropic(max_retries=SDK_RETRIES)


def classify(
    ticket_text: str,
    *,
    client: Any | None = None,
    mode: str | None = None,
) -> Result:
    """Classify one ticket and return only validated output or a clear failure."""

    selected_mode = mode or os.getenv("LLM_MODE", "api")
    if selected_mode not in {"api", "offline"}:
        raise ValueError("LLM_MODE must be 'api' or 'offline'.")

    active_client = client
    if active_client is None:
        active_client = (
            OfflineFixtureClient(ticket_text)
            if selected_mode == "offline"
            else _api_client()
        )

    messages: list[dict[str, str]] = [
        {"role": "user", "content": f"Ticket:\n{ticket_text}"}
    ]

    for attempt in range(1, MAX_REPROMPTS + 2):
        try:
            response = active_client.messages.create(
                model=MODEL,
                max_tokens=MAX_OUTPUT_TOKENS,
                system=SYSTEM,
                messages=messages,
            )
        except Exception as exc:
            log.exception("Model call failed on attempt %s", attempt)
            log_call(attempt, None, passed=False, mode=selected_mode)
            return Result(None, attempt, f"api error: {type(exc).__name__}")

        stop_reason = getattr(response, "stop_reason", None)
        if stop_reason != "end_turn":
            log_call(attempt, _usage(response), passed=False, mode=selected_mode)
            return Result(None, attempt, f"stopped: {stop_reason}")

        content = getattr(response, "content", [])
        text = getattr(content[0], "text", "") if content else ""
        try:
            record = TicketClassification.model_validate_json(text)
        except (ValidationError, ValueError, json.JSONDecodeError) as exc:
            log_call(attempt, _usage(response), passed=False, mode=selected_mode)
            if attempt > MAX_REPROMPTS:
                return Result(None, attempt, "validation failed after re-prompts")
            if isinstance(exc, ValidationError):
                error = "; ".join(item["msg"] for item in exc.errors())
            else:
                error = str(exc)
            messages.extend(
                [
                    {"role": "assistant", "content": text},
                    {
                        "role": "user",
                        "content": (
                            f"Your answer failed validation: {error}\n"
                            "Send corrected JSON only."
                        ),
                    },
                ]
            )
            continue

        log_call(attempt, _usage(response), passed=True, mode=selected_mode)
        return Result(record, attempt, "ok")

    return Result(None, MAX_REPROMPTS + 1, "validation failed after re-prompts")
