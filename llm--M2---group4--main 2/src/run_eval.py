"""Run the test cases through the shared classifier boundary (src/llm.py), one strategy at a time.

    python -m src.run_eval --strategy zero_shot --limit 10     # L02: the first ten cases
    python -m src.run_eval --strategy all                      # L04: the three strategies

Writes runs/results_<strategy>.csv (one row per case) and appends one row per API call to
runs/calls.csv. With LLM_MODE=offline it uses the fixture: those files are a code-path check
only, never model accuracy or cost, and are written as runs/offline_results_<strategy>.csv.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
from pathlib import Path

from src.evaluate import exact_label_score
from src.guardrails import sent_record
from src.llm import MAX_OUTPUT_TOKENS, MODEL, STRATEGIES, classify


ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "evals" / "test_cases.csv"
RUNS = ROOT / "runs"

FIELDS = [
    "date", "model", "strategy", "prompt_file", "max_output_tokens", "test_file",
    "case_id", "expected", "second_acceptable", "predicted", "correct", "confidence",
    "needs_human_review", "attempts", "reprompts", "gave_up", "reason",
    "input_tokens", "output_tokens", "cost_usd", "latency_ms", "sent", "mode",
]


def run(strategy: str, limit: int | None, mode: str) -> Path:
    with INPUT_FILE.open(newline="", encoding="utf-8") as source:
        cases = list(csv.DictReader(source))
    if limit:
        cases = cases[:limit]
    date = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    name = ("" if mode == "api" else "offline_") + f"results_{strategy}.csv"
    out = RUNS / name
    RUNS.mkdir(exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=FIELDS)
        writer.writeheader()
        for case in cases:
            result = classify(case["input"], mode=mode, strategy=strategy, case_id=case["case_id"])
            c = result.classification
            predicted = c.label if c else ""
            writer.writerow({
                "date": date, "model": MODEL if mode == "api" else "offline-fixture-v1",
                "strategy": strategy, "prompt_file": STRATEGIES[strategy].name,
                "max_output_tokens": MAX_OUTPUT_TOKENS, "test_file": "evals/test_cases.csv",
                "case_id": case["case_id"], "expected": case["expected"],
                "second_acceptable": case["second_acceptable"], "predicted": predicted,
                "correct": exact_label_score(case["expected"], predicted, case["second_acceptable"] or None),
                "confidence": c.confidence if c else "",
                "needs_human_review": c.needs_human_review if c else "",
                "attempts": result.attempts, "reprompts": max(0, result.attempts - 1),
                "gave_up": c is None, "reason": result.reason,
                "input_tokens": result.input_tokens, "output_tokens": result.output_tokens,
                "cost_usd": round(result.cost_usd, 8), "latency_ms": round(result.latency_ms, 1),
                "sent": json.dumps(sent_record(case["input"], c)), "mode": mode,
            })
            print(f"[{strategy}] {case['case_id']}: {predicted or 'FAILED'} (expected {case['expected']})")
    print(f"Wrote {len(cases)} rows to {out.relative_to(ROOT)}")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--strategy", default="zero_shot", choices=[*STRATEGIES, "all"])
    parser.add_argument("--limit", type=int, default=None, help="only the first N cases")
    args = parser.parse_args()
    mode = os.getenv("LLM_MODE", "api")
    for strategy in (list(STRATEGIES) if args.strategy == "all" else [args.strategy]):
        run(strategy, args.limit, mode)


if __name__ == "__main__":
    main()
