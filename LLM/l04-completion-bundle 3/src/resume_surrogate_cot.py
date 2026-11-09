"""Resume only missing local CoT rows in the existing surrogate call log."""

from __future__ import annotations

import csv
import datetime as dt
import json
import re
import time
import urllib.request
from pathlib import Path

from src.schema import TicketClassification


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evals" / "test_cases.csv"
LOG = ROOT / "runs" / "surrogate-llama3.2-3b-calls.csv"
PROMPT = ROOT / "prompts" / "route_cot.md"
MODEL = "llama3.2:3b"
URL = "http://localhost:11434/api/chat"


def load_system_prompt() -> str:
    text = PROMPT.read_text(encoding="utf-8")
    if "## System prompt" in text:
        text = text.split("## System prompt", 1)[1]
    if "## User-message shape" in text:
        text = text.split("## User-message shape", 1)[0]
    return text.strip()


def parse_record(text: str) -> TicketClassification:
    text = text.replace("```json", "").replace("```", "").strip()
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError("no JSON object returned")
    return TicketClassification.model_validate_json(match.group(0))


def ask(system: str, ticket: str) -> tuple[dict, float]:
    payload = {
        "model": MODEL,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0, "seed": 42},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": f"Ticket:\n{ticket}"},
        ],
    }
    request = urllib.request.Request(
        URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    with urllib.request.urlopen(request, timeout=180) as response:
        body = json.loads(response.read().decode("utf-8"))
    return body, (time.perf_counter() - started) * 1000


def main() -> None:
    with CASES.open(newline="", encoding="utf-8") as handle:
        cases = list(csv.DictReader(handle))
    with LOG.open(newline="", encoding="utf-8") as handle:
        existing = list(csv.DictReader(handle))
        fieldnames = existing[0].keys() if existing else [
            "timestamp", "provider", "strategy", "model", "case_id",
            "input_tokens", "output_tokens", "latency_ms",
            "external_cost_eur", "passed_validation", "correct", "error",
        ]

    already = {(row["strategy"], row["case_id"]) for row in existing}
    missing = [
        case for case in cases
        if ("cot", case["case_id"]) not in already
    ]
    print("missing CoT cases:", ", ".join(case["case_id"] for case in missing))

    if not missing:
        print("No missing CoT rows.")
        return

    system = load_system_prompt()
    with LOG.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        for case in missing:
            error = ""
            record = None
            input_tokens = ""
            output_tokens = ""
            latency_ms = ""
            try:
                body, elapsed = ask(system, case["input"])
                latency_ms = round(elapsed, 2)
                input_tokens = body.get("prompt_eval_count", "")
                output_tokens = body.get("eval_count", "")
                record = parse_record(body["message"]["content"])
            except Exception as exc:  # record the failed call without hiding it
                error = f"{type(exc).__name__}: {exc}"

            accepted = {case["expected"], case["second_acceptable"]} - {""}
            writer.writerow({
                "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                "provider": "ollama-local",
                "strategy": "cot",
                "model": MODEL,
                "case_id": case["case_id"],
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "latency_ms": latency_ms,
                "external_cost_eur": 0,
                "passed_validation": bool(record),
                "correct": bool(record and record.label in accepted),
                "error": error,
            })
            handle.flush()
            print("appended", case["case_id"])


if __name__ == "__main__":
    main()
