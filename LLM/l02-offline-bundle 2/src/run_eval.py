"""Run the ten L01 cases through the shared classifier boundary.

Use ``LLM_MODE=offline`` when no API key is available. The resulting files
are structural/offline evidence only and must not be presented as live model
accuracy or API cost.
"""

from __future__ import annotations

import csv
import os
from pathlib import Path

from src.llm import classify


ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "evals" / "test_cases.csv"
OUTPUT_FILE = ROOT / "runs" / "results.csv"


def main() -> None:
    mode = os.getenv("LLM_MODE", "offline")
    with INPUT_FILE.open(newline="", encoding="utf-8") as source:
        cases = list(csv.DictReader(source))

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as target:
        fieldnames = [
            "case_id",
            "predicted",
            "expected",
            "second_acceptable",
            "correct_under_fixture",
            "attempts",
            "reason",
            "mode",
        ]
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()

        for case in cases:
            result = classify(case["input"], mode=mode)
            predicted = result.classification.label if result.classification else ""
            accepted = {case["expected"], case["second_acceptable"]} - {""}
            writer.writerow(
                {
                    "case_id": case["case_id"],
                    "predicted": predicted,
                    "expected": case["expected"],
                    "second_acceptable": case["second_acceptable"],
                    "correct_under_fixture": bool(predicted and predicted in accepted),
                    "attempts": result.attempts,
                    "reason": result.reason,
                    "mode": mode,
                }
            )

    print(f"Wrote {len(cases)} offline evaluation rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
