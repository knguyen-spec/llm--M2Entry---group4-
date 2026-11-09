"""Run the three classifier prompts against a local Ollama model.

This is a local-surrogate experiment. It is not evidence for the production
provider and must not replace the pending live-provider figures.
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import os
import re
import time
import urllib.request
from pathlib import Path

from pydantic import ValidationError

from src.schema import TicketClassification


ROOT = Path(__file__).resolve().parents[1]
MODEL = os.getenv("LOCAL_MODEL", "llama3.2:3b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
CASES = ROOT / "evals" / "test_cases.csv"
RUNS = ROOT / "runs"

PROMPTS = {
    "zero_shot": ROOT / "prompts" / "route_zero_shot_json.md",
    "few_shot": ROOT / "prompts" / "route_few_shot.md",
    "cot": ROOT / "prompts" / "route_cot.md",
}

CALL_HEADER = [
    "timestamp", "provider", "strategy", "model", "case_id",
    "input_tokens", "output_tokens", "latency_ms", "external_cost_eur",
    "passed_validation", "correct", "error",
]


def system_prompt(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if "## System prompt" in text:
        text = text.split("## System prompt", 1)[1]
    if "## User-message shape" in text:
        text = text.split("## User-message shape", 1)[0]
    return text.strip()


def read_cases() -> list[dict[str, str]]:
    with CASES.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 30:
        raise SystemExit(
            f"Expected exactly 30 cases in {CASES}; found {len(rows)}. "
            "Have the additional cases reviewed and appended first."
        )
    return rows


def parse_record(text: str) -> TicketClassification:
    cleaned = text.strip().replace("```json", "").replace("```", "").strip()
    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if not match:
        raise ValueError("model did not return a JSON object")
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
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    with urllib.request.urlopen(request, timeout=180) as response:
        body = json.loads(response.read().decode("utf-8"))
    elapsed_ms = (time.perf_counter() - started) * 1000
    return body, elapsed_ms


def main() -> None:
    cases = read_cases()
    RUNS.mkdir(parents=True, exist_ok=True)
    calls_path = RUNS / "calls.csv"
    with calls_path.open("w", newline="", encoding="utf-8") as calls_file:
        calls = csv.DictWriter(calls_file, fieldnames=CALL_HEADER)
        calls.writeheader()

        for strategy, prompt_path in PROMPTS.items():
            output_path = RUNS / f"results_{strategy}.csv"
            fields = [
                "case_id", "strategy", "model", "label", "confidence",
                "needs_human_review", "expected", "second_acceptable",
                "correct", "input_tokens", "output_tokens", "latency_ms",
                "external_cost_eur", "error",
            ]
            with output_path.open("w", newline="", encoding="utf-8") as output_file:
                results = csv.DictWriter(output_file, fieldnames=fields)
                results.writeheader()
                system = system_prompt(prompt_path)

                for case in cases:
                    error = ""
                    record = None
                    input_tokens = ""
                    output_tokens = ""
                    latency_ms = ""
                    try:
                        body, elapsed = ask(system, case["input"])
                        latency_ms = round(elapsed, 2)
                        usage = body
                        input_tokens = usage.get("prompt_eval_count", "")
                        output_tokens = usage.get("eval_count", "")
                        record = parse_record(body["message"]["content"])
                    except (OSError, ValueError, KeyError, ValidationError) as exc:
                        error = f"{type(exc).__name__}: {exc}"

                    label = record.label if record else ""
                    confidence = record.confidence if record else ""
                    review = record.needs_human_review if record else ""
                    accepted = {case["expected"], case["second_acceptable"]} - {""}
                    correct = bool(record and record.label in accepted)
                    timestamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

                    calls.writerow({
                        "timestamp": timestamp,
                        "provider": "ollama-local",
                        "strategy": strategy,
                        "model": MODEL,
                        "case_id": case["case_id"],
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "latency_ms": latency_ms,
                        "external_cost_eur": 0,
                        "passed_validation": bool(record),
                        "correct": correct,
                        "error": error,
                    })
                    results.writerow({
                        "case_id": case["case_id"],
                        "strategy": strategy,
                        "model": MODEL,
                        "label": label,
                        "confidence": confidence,
                        "needs_human_review": review,
                        "expected": case["expected"],
                        "second_acceptable": case["second_acceptable"],
                        "correct": correct,
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "latency_ms": latency_ms,
                        "external_cost_eur": 0,
                        "error": error,
                    })
                    calls_file.flush()

            print(f"wrote {output_path.relative_to(ROOT)}")
    print(f"wrote {calls_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
