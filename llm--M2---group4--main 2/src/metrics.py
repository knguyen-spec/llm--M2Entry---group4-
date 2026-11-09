"""Scores and arithmetic that need no model and no network.

Covers: normalisation, exact match and token F1 for short answers, p90 for latency, the swap test
over any judge function, Pareto dominance, the cache key, and the cost of one call from its tokens.
Nothing here calls the API. The live figures (strategies, judge verdicts, measured cost and
latency) come from runs recorded in runs/ and stay pending until those runs exist.
"""
import hashlib
import json
import re
from dataclasses import dataclass


def normalise(s: str) -> str:
    """Lower case, no punctuation or euro signs, decimal commas as points, no articles.

    'No, €4.90 per seller' -> 'no 4.90 per seller'
    """
    s = s.lower().replace("€", " ")
    s = re.sub(r"(\d),(\d)", r"\1.\2", s)
    s = re.sub(r"(\d)\s+%", r"\1%", s)
    s = re.sub(r"(?<!\d)\.|\.(?!\d)", " ", s)
    s = re.sub(r"[^\w.% ]", " ", s)
    return " ".join(w for w in s.split() if w not in ("a", "an", "the"))


def exact_match(prediction: str, gold: str) -> bool:
    return normalise(prediction) == normalise(gold)


def token_f1(prediction: str, gold: str) -> float:
    """SQuAD-style F1 on normalised words: 0.0 for no overlap, 1.0 for the same words."""
    p, g = normalise(prediction).split(), normalise(gold).split()
    if not p or not g:
        return float(p == g)
    common = sum(min(p.count(w), g.count(w)) for w in set(p))
    if common == 0:
        return 0.0
    precision, recall = common / len(p), common / len(g)
    return 2 * precision * recall / (precision + recall)


def p90(values: list[float]) -> float:
    """The value 90% of the way up the sorted list: nine values in ten are at or below it."""
    return sorted(values)[int(0.9 * (len(values) - 1))]


def swap_test(judge_fn, pairs: list[tuple[str, str, str]]) -> list[str]:
    """Return the ids where the same POSITION won both orders: there, the order decided.

    judge_fn(item_id, a, b) -> "A" or "B". Each pair is (item_id, answer_1, answer_2), and each
    pair is judged twice: (answer_1, answer_2) and then (answer_2, answer_1).
    A judge that prefers the same answer in both orders is consistent and is not flagged.
    """
    flipped = []
    for item_id, x, y in pairs:
        first, second = judge_fn(item_id, x, y), judge_fn(item_id, y, x)
        if first == second:
            flipped.append(f"{item_id}: {'first' if first == 'A' else 'second'} both times")
    return flipped


def dominated(a: dict, b: dict) -> bool:
    """True when b is at least as good as a on every axis and better on one.

    Each variant: "right" (more is better), "usd" and "s" (less is better).
    """
    at_least = b["right"] >= a["right"] and b["usd"] <= a["usd"] and b["s"] <= a["s"]
    return at_least and (b["right"] > a["right"] or b["usd"] < a["usd"] or b["s"] < a["s"])


def pareto_front(variants: dict[str, dict]) -> list[str]:
    """The names no other variant dominates."""
    return [
        name for name, v in variants.items()
        if not any(dominated(v, w) for other, w in variants.items() if other != name)
    ]


def cache_key(model: str, system: str, question: str) -> str:
    """SHA-256 over everything that changes the answer. The model is part of the key."""
    parts = {"model": model, "system": system, "question": question}
    return hashlib.sha256(json.dumps(parts, sort_keys=True).encode()).hexdigest()


@dataclass
class Usage:
    input_tokens: int
    output_tokens: int
    cache_write_tokens: int = 0
    cache_read_tokens: int = 0


@dataclass
class Price:
    """Dollars per million tokens. Record the source and date of the prices with the run."""
    input: float
    output: float
    cache_write_multiplier: float = 1.25
    cache_read_multiplier: float = 0.10


def cost(usage: Usage, price: Price, count_output: bool = True) -> float:
    """Dollars for one call: each kind of token at its own price, divided by a million."""
    total = (
        usage.input_tokens * price.input
        + usage.cache_write_tokens * price.input * price.cache_write_multiplier
        + usage.cache_read_tokens * price.input * price.cache_read_multiplier
        + (usage.output_tokens * price.output if count_output else 0)
    )
    return total / 1e6
