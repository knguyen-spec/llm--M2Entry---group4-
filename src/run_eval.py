"""Run the test cases through src/llm.py and summarise the results.

Usage, from the repository root:

    python -m src.run_eval

Every API call is logged by src/llm.py to runs/calls.csv. This script writes
one row per case to runs/results.csv.
"""

import csv
from pathlib import Path

from src.llm import classify

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evals" / "test_cases.csv"
RESULTS = ROOT / "runs" / "results.csv"

HEADER = ["case_id", "expected", "second_acceptable", "predicted", "confidence",
          "needs_human_review", "attempts", "reason", "correct"]


def load_cases() -> list[dict]:
    with CASES.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main() -> None:
    cases = load_cases()
    RESULTS.parent.mkdir(parents=True, exist_ok=True)

    correct = given_up = reprompted = 0
    with RESULTS.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)

        for case in cases:
            result = classify(case["input"])
            if result.attempts > 1:
                reprompted += 1

            # A label is correct if it matches expected, or the second acceptable label.
            accepted = {case["expected"]}
            if case["second_acceptable"]:
                accepted.add(case["second_acceptable"])

            if result.classification is None:
                given_up += 1
                writer.writerow([case["case_id"], case["expected"], case["second_acceptable"],
                                 "", "", "", result.attempts, result.reason, False])
                continue

            label = result.classification.label
            is_correct = label in accepted
            correct += is_correct
            writer.writerow([case["case_id"], case["expected"], case["second_acceptable"],
                             label, result.classification.confidence,
                             result.classification.needs_human_review,
                             result.attempts, result.reason, is_correct])

    total = len(cases)
    error_rate = (total - correct) / total if total else 0.0
    print(f"cases: {total}  correct: {correct}  error rate: {error_rate:.0%}")
    print(f"re-prompted: {reprompted}  given up: {given_up}")
    print(f"per-case results: {RESULTS}")


if __name__ == "__main__":
    main()
