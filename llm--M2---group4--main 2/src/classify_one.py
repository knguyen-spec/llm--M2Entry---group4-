"""Classify one ticket from the command line.

    python -m src.classify_one "My parcel is late and the tracking has not changed."
    python -m src.classify_one --strategy zero_shot "..."
    LLM_MODE=offline python -m src.classify_one "..."     (no API key, no cost)

Prints what the model returned (validated) and the record that would be sent.
"""

from __future__ import annotations

import argparse
import json
import os

from src.guardrails import sent_record
from src.llm import MODEL, STRATEGIES, classify


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify one support ticket.")
    parser.add_argument("ticket", help="the ticket text, in quotes")
    parser.add_argument("--strategy", choices=sorted(STRATEGIES), default="few_shot",
                        help="prompt strategy (default: few_shot, the one we recommend)")
    args = parser.parse_args()

    result = classify(args.ticket, strategy=args.strategy, case_id="cli")
    c = result.classification
    print(f"model {MODEL} | strategy {args.strategy} | mode {os.getenv('LLM_MODE', 'api')}")
    if c is None:
        print(f"no valid answer after {result.attempts} attempt(s): {result.reason}")
    else:
        print("model returned:", json.dumps(c.model_dump()))
    print("sent:          ", json.dumps(sent_record(args.ticket, c)))
    print(f"attempts {result.attempts} | cost ${result.cost_usd:.6f} | latency {result.latency_ms:.0f} ms")


if __name__ == "__main__":
    main()
