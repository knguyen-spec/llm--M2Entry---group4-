"""The judge, run on the results of src/run_eval.py. Every call goes through src/llm.py.

    python -m src.judge --strategy all      # one 1-5 score per rubric criterion, per case
    python -m src.judge --pairwise          # two strategies compared, in both orders (the swap)

The judge is a different model from the component's (JUDGE_MODEL vs MODEL), so it does not
favour its own answers. Score ten cases by hand in evals/human_scores.csv BEFORE reading
runs/judge_*.csv: that is the calibration.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from src.evaluate import RubricVerdict, swap_preference
from src.llm import JUDGE_MODEL, STRATEGIES, api_client, validated_call


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"
CASES = ROOT / "evals" / "test_cases.csv"
PAIRS = [("zero_shot", "few_shot"), ("zero_shot", "cot"), ("few_shot", "cot")]
SYSTEM = "You are a careful evaluator. Return one JSON object and nothing else."


class PairVerdict(BaseModel):
    reason: str = Field(min_length=1, max_length=400)
    preferred: Literal["A", "B", "tie"]


def _read(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _answer(row: dict) -> str:
    if not row["predicted"]:
        return f"NO ANSWER (the classifier gave up: {row['reason']})"
    return json.dumps({"label": row["predicted"], "confidence": float(row["confidence"]),
                       "needs_human_review": row["needs_human_review"] == "True"})


def _expected(case: dict) -> str:
    return case["expected"] + (f" (or {case['second_acceptable']})" if case["second_acceptable"] else "")


def _fill(template: str, **values: str) -> str:
    for key, value in values.items():
        template = template.replace("{" + key + "}", value)
    return template


def judge_strategy(strategy: str, client) -> Path:
    prompt = (ROOT / "prompts" / "judge.md").read_text(encoding="utf-8")
    cases = {c["case_id"]: c for c in _read(CASES)}
    out = []
    for row in _read(RUNS / f"results_{strategy}.csv"):
        case = cases[row["case_id"]]
        r = validated_call(SYSTEM, _fill(prompt, ticket=case["input"], expected=_expected(case), answer=_answer(row)),
                           RubricVerdict, client=client, mode="api", model=JUDGE_MODEL,
                           purpose="judge", strategy=strategy, case_id=row["case_id"])
        v = r.record
        out.append({"case_id": row["case_id"], "strategy": strategy, "judge_model": JUDGE_MODEL,
                    **({k: getattr(v, k).score for k in ("correct", "grounded", "review", "format")} if v
                       else {k: "" for k in ("correct", "grounded", "review", "format")}),
                    "reasons": json.dumps({k: getattr(v, k).reason for k in ("correct", "grounded", "review", "format")}) if v else r.reason,
                    "cost_usd": round(r.cost_usd, 8)})
        print(f"[judge {strategy}] {row['case_id']}: {out[-1]['correct'] or 'FAILED'}")
    path = RUNS / f"judge_{strategy}.csv"
    _write(path, out)
    return path


def judge_pairs(client) -> Path:
    prompt = (ROOT / "prompts" / "judge_pairwise.md").read_text(encoding="utf-8")
    cases = {c["case_id"]: c for c in _read(CASES)}
    results = {s: {r["case_id"]: r for r in _read(RUNS / f"results_{s}.csv")} for s in STRATEGIES}
    out = []
    for a, b in PAIRS:
        for case_id, case in cases.items():
            ra, rb = results[a].get(case_id), results[b].get(case_id)
            if not ra or not rb:
                continue
            picks = []
            for first, second in ((ra, rb), (rb, ra)):  # both orders
                r = validated_call(SYSTEM, _fill(prompt, ticket=case["input"], expected=_expected(case),
                                                 answer_a=_answer(first), answer_b=_answer(second)),
                                   PairVerdict, client=client, mode="api", model=JUDGE_MODEL,
                                   purpose="pairwise", strategy=f"{a}_vs_{b}", case_id=case_id)
                picks.append(r.record.preferred if r.record else "error")
            # Map the second order back: there, "A" was strategy b.
            second = {"A": "B", "B": "A"}.get(picks[1], picks[1])
            final = "error" if "error" in picks else swap_preference(picks[0], second)
            out.append({"case_id": case_id, "a": a, "b": b, "first_order": picks[0],
                        "second_order_mapped": second, "swap_changed": picks[0] != second,
                        "final": {"A": a, "B": b}.get(final, final)})
            print(f"[pairwise {a} vs {b}] {case_id}: {out[-1]['final']}")
    path = RUNS / "pairwise.csv"
    _write(path, out)
    changed = sum(r["swap_changed"] for r in out)
    print(f"The swap changed {changed} of {len(out)} verdicts.")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--strategy", choices=[*STRATEGIES, "all"])
    parser.add_argument("--pairwise", action="store_true")
    args = parser.parse_args()
    client = api_client()
    if args.strategy:
        for s in (list(STRATEGIES) if args.strategy == "all" else [args.strategy]):
            judge_strategy(s, client)
    if args.pairwise:
        judge_pairs(client)
    if not args.strategy and not args.pairwise:
        parser.error("give --strategy and/or --pairwise")


if __name__ == "__main__":
    main()
