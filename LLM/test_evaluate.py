"""Scorer tests on pairs whose answer we know. No model, no API."""
import pytest
from pydantic import ValidationError

from src.evaluate import (
    JudgeVerdict,
    RubricVerdict,
    exact_label_score,
    normalise_label,
    score_run,
    swap_preference,
)


def test_exact_match_is_correct():
    assert exact_label_score("billing", "billing")


def test_second_acceptable_label_is_correct():
    assert exact_label_score("billing", "returns_refunds", "returns_refunds")


def test_wrong_label_is_incorrect():
    assert not exact_label_score("billing", "delivery")


def test_invented_label_is_incorrect():
    assert not exact_label_score("billing", "refund_dispute")


def test_missing_answer_is_incorrect():
    assert not exact_label_score("billing", None)
    assert not exact_label_score("billing", "")


def test_case_spaces_and_hyphens_are_normalised():
    assert normalise_label("  Returns Refunds ") == "returns_refunds"
    assert exact_label_score("returns_refunds", "Returns-Refunds")


def test_score_run_counts_and_error_rate():
    cases = [
        {"case_id": "T1", "expected": "billing", "second_acceptable": ""},
        {"case_id": "T2", "expected": "delivery", "second_acceptable": ""},
        {"case_id": "T3", "expected": "account", "second_acceptable": "other"},
        {"case_id": "T4", "expected": "seller", "second_acceptable": ""},
    ]
    predictions = {"T1": "billing", "T2": "account", "T3": "other", "T4": None}
    correct, error_rate = score_run(cases, predictions)
    assert correct == 2
    assert error_rate == pytest.approx(0.5)


def test_judge_verdict_accepts_scores_one_to_five():
    assert JudgeVerdict(score=1, reason="wrong").score == 1
    assert JudgeVerdict(score=5, reason="right").score == 5


def test_judge_verdict_rejects_out_of_range_score():
    with pytest.raises(ValidationError):
        JudgeVerdict(score=6, reason="too high")
    with pytest.raises(ValidationError):
        JudgeVerdict(score=0, reason="too low")


def test_rubric_verdict_reads_the_judge_json_shape():
    record = RubricVerdict.model_validate({
        "correct": {"score": 5, "reason": "label matches"},
        "grounded": {"score": 4, "reason": "one claim beyond the ticket"},
        "review": {"score": 5, "reason": "flag matches confidence"},
        "format": {"score": 5, "reason": "one JSON object"},
    })
    assert record.correct.score == 5
    assert record.grounded.score == 4


def test_swap_counts_a_preference_only_when_both_orders_agree():
    assert swap_preference("A", "A") == "A"
    assert swap_preference("B", "B") == "B"
    assert swap_preference("A", "B") == "tie"
    assert swap_preference("tie", "A") == "tie"
