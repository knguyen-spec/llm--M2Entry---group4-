"""Summarise the strategy runs in runs/ as the tables of docs/evaluation.md. No API call.

    python -m src.summarise

Reads runs/results_<strategy>.csv (written by src/run_eval.py) and prints, in Markdown:
the table (right answers out of 30, cost per 1,000 calls, median and p90 latency),
the Pareto front, and which differences are smaller than one case.

    python -m src.summarise --judge

prints the judge's figures instead: its mean scores, its agreement with our ten hand scores
(evals/human_scores.csv), and how many pairwise verdicts the swap changed (runs/pairwise.csv).
"""

from __future__ import annotations

import csv
import statistics
from pathlib import Path

from src.metrics import p90, pareto_front


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"
NAMES = {"zero_shot": "Zero-shot", "few_shot": "Few-shot", "cot": "Chain-of-thought"}


def load(strategy: str) -> list[dict]:
    path = RUNS / f"results_{strategy}.csv"
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def metrics(rows: list[dict]) -> dict:
    n = len(rows)
    calls = sum(int(r["attempts"]) for r in rows)
    usd = sum(float(r["cost_usd"]) for r in rows)
    lat = [float(r["latency_ms"]) / 1000 for r in rows]
    return {
        "n": n,
        "right": sum(r["correct"] == "True" for r in rows),
        "strict": sum(r["predicted"] == r["expected"] for r in rows),
        "calls": calls,
        "usd_run": usd,
        "usd_1000_calls": usd / calls * 1000 if calls else 0.0,
        "median_s": statistics.median(lat),
        "p90_s": p90(lat),
        "reprompted": sum(r["reprompts"] != "0" for r in rows),
        "gave_up": sum(r["gave_up"] == "True" for r in rows),
        "model": rows[0]["model"], "date": rows[0]["date"][:10],
        "max_tokens": rows[0]["max_output_tokens"], "prompt": rows[0]["prompt_file"],
    }


CRITERIA = ("correct", "grounded", "review", "format")


def judge_report() -> None:
    def read(path):
        if not path.exists():
            return []
        with path.open(newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    print("| Strategy | correct | grounded | review | format | Judge cost |")
    print("|---|---:|---:|---:|---:|---:|")
    judged = {}
    for s, name in NAMES.items():
        rows = [r for r in read(RUNS / f"judge_{s}.csv") if r["correct"]]
        judged[s] = {r["case_id"]: r for r in rows}
        if rows:
            means = " | ".join(f"{statistics.mean(int(r[c]) for r in rows):.2f}" for c in CRITERIA)
            usd = sum(float(r["cost_usd"]) for r in read(RUNS / f"judge_{s}.csv"))
            print(f"| {name} | {means} | ${usd:.4f} |")
    model = next((r["judge_model"] for s in NAMES for r in read(RUNS / f"judge_{s}.csv")), "?")
    print(f"\nJudge model: `{model}`, scores from 1 to 5 against the expected answer (evals/rubric.md).\n")

    human = [h for h in read(ROOT / "evals" / "human_scores.csv") if h.get("correct", "").strip()]
    pairs = [(h, judged.get(h["strategy"], {}).get(h["case_id"])) for h in human]
    pairs = [(h, j) for h, j in pairs if j]
    if pairs:
        total = len(pairs) * len(CRITERIA)
        exact = sum(int(h[c]) == int(j[c]) for h, j in pairs for c in CRITERIA)
        near = sum(abs(int(h[c]) - int(j[c])) <= 1 for h, j in pairs for c in CRITERIA)
        print(f"**Calibration** on the {len(pairs)} cases we scored by hand first (evals/human_scores.csv): "
              f"same score on {exact} of {total} criterion scores ({exact * 100 / total:.0f}%), "
              f"within one point on {near} of {total} ({near * 100 / total:.0f}%).")
        for c in CRITERIA:
            same = sum(int(h[c]) == int(j[c]) for h, j in pairs)
            print(f"- {c}: same score on {same}/{len(pairs)}")
        print()
    else:
        print("**Calibration**: no hand scores yet in evals/human_scores.csv.\n")

    pw = read(RUNS / "pairwise.csv")
    if pw:
        changed = sum(r["swap_changed"] == "True" for r in pw)
        print(f"**Swap**: every pair judged in both orders. The order changed the verdict in {changed} of "
              f"{len(pw)} comparisons ({changed * 100 / len(pw):.0f}%); those count as a tie, not a preference.")
        for a, b in {(r["a"], r["b"]) for r in pw}:
            rows = [r for r in pw if r["a"] == a and r["b"] == b]
            count = lambda v: sum(r["final"] == v for r in rows)  # noqa: E731
            print(f"- {NAMES[a]} vs {NAMES[b]}: {NAMES[a]} preferred {count(a)}, {NAMES[b]} preferred {count(b)}, "
                  f"tie {count('tie')}, changed by the swap {sum(r['swap_changed'] == 'True' for r in rows)}")


def main() -> None:
    import sys

    if "--judge" in sys.argv:
        return judge_report()
    m = {s: metrics(rows) for s in NAMES if (rows := load(s))}
    if not m:
        raise SystemExit("No runs/results_<strategy>.csv yet: run python -m src.run_eval --strategy all")
    first = next(iter(m.values()))
    print("| Strategy | Right /30 (expected or second acceptable) | Right /30 (expected only) | Cost per 1,000 calls | Median latency | p90 latency | Re-prompted | Gave up | Prompt file |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|---|")
    for s, x in m.items():
        print(f"| {NAMES[s]} | {x['right']}/{x['n']} | {x['strict']}/{x['n']} | ${x['usd_1000_calls']:.2f} | "
              f"{x['median_s']:.2f} s | {x['p90_s']:.2f} s | {x['reprompted']} | {x['gave_up']} | `prompts/{x['prompt']}` |")
    print()
    print(f"Four facts: model `{first['model']}`, date {first['date']}, parameters max_output_tokens "
          f"{first['max_tokens']} and model-default sampling, test file `evals/test_cases.csv` ({first['n']} cases). "
          "Right answers by exact match on the label (no model). Cost from the measured input and output tokens "
          "of every call, each at its own price, re-prompts included. Files: `runs/results_<strategy>.csv`, `runs/calls.csv`.")
    print()
    variants = {NAMES[s]: {"right": x["right"], "usd": x["usd_1000_calls"], "s": x["p90_s"]} for s, x in m.items()}
    front = pareto_front(variants)
    print("**Pareto front** (no other strategy is at least as good on right answers, cost and p90 latency, "
          "and better on one): " + ", ".join(front) + ".")
    dominated = [v for v in variants if v not in front]
    if dominated:
        print("Dominated: " + ", ".join(dominated) + ".")
    print()
    print("**What 30 cases can tell.** One case is 3.3 points.")
    names = list(m)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            d = m[a]["right"] - m[b]["right"]
            note = ("no difference" if d == 0 else
                    "smaller than what 30 cases can resolve" if abs(d) == 1 else
                    "still weak evidence on 30 cases" if abs(d) == 2 else
                    "a difference worth reporting, on a small sample")
            print(f"- {NAMES[a]} vs {NAMES[b]}: {d:+d} case(s), {d * 100 / 30:+.1f} points: {note}.")


if __name__ == "__main__":
    main()
