"""Scorers that need no model, and the judge's verdict format.

The judge itself calls a model, so it goes through src/llm.py (the only module that calls the API).
Nothing here calls the API.
"""
import re
from typing import Literal, get_args

from pydantic import BaseModel, Field

from src.schema import Label

ALLOWED = set(get_args(Label))


def normalise_label(text: str) -> str:
    """Trim, lower-case, and turn spaces or hyphens into underscores: 'Returns Refunds' -> 'returns_refunds'."""
    return re.sub(r"[\s\-]+", "_", text.strip().lower())


def exact_label_score(expected: str, predicted: str | None, second_acceptable: str | None = None) -> bool:
    """True when the predicted label matches the expected one, or the second acceptable one.

    A missing answer or an invented label scores False.
    """
    if not predicted:
        return False
    p = normalise_label(predicted)
    if p not in ALLOWED:
        return False
    accepted = {normalise_label(expected)}
    if second_acceptable:
        accepted.add(normalise_label(second_acceptable))
    return p in accepted


def score_run(cases: list[dict], predictions: dict[str, str | None]) -> tuple[int, float]:
    """Count the correct cases, and the error rate. cases: rows of evals/test_cases.csv."""
    correct = sum(
        exact_label_score(c["expected"], predictions.get(c["case_id"]), c.get("second_acceptable") or None)
        for c in cases
    )
    total = len(cases)
    return correct, (1 - correct / total) if total else 0.0


class JudgeVerdict(BaseModel):
    """One criterion's verdict: a score from 1 to 5 and a one-sentence reason."""
    score: int = Field(ge=1, le=5)
    reason: str = Field(min_length=1, max_length=400)


class RubricVerdict(BaseModel):
    """The judge's full record for one answer: one verdict per rubric criterion (see evals/rubric.md)."""
    correct: JudgeVerdict
    grounded: JudgeVerdict
    review: JudgeVerdict
    format: JudgeVerdict


Side = Literal["A", "B", "tie"]


def swap_preference(first_order: Side, second_order: Side) -> Side:
    """Combine two judge runs on the same pair, with A and B swapped in the second run.

    first_order: the judge's pick when the answers were shown as (A, B).
    second_order: the judge's pick when they were shown as (B, A), mapped back to the original labels.
    A preference counts only when both orders agree; otherwise the result is 'tie'.
    """
    return first_order if first_order == second_order else "tie"
