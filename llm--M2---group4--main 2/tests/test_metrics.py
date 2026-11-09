"""Tests for src/metrics.py, on values we can check by hand. No model, no API.

The Pareto test uses the lecture's published figures (run on 2026-10-20). They are reference
values for the arithmetic, not this group's results.
"""
import pytest

from src.metrics import (
    Price,
    Usage,
    cache_key,
    cost,
    dominated,
    exact_match,
    normalise,
    p90,
    pareto_front,
    swap_test,
    token_f1,
)


def test_normalise_drops_euro_articles_and_punctuation():
    assert normalise("No, €4.90 per seller") == "no 4.90 per seller"
    assert normalise("The 21 days.") == "21 days"


def test_decimal_comma_equals_decimal_point():
    assert exact_match("4,90 €", "4.90 €")


def test_exact_match_misses_a_right_answer_written_another_way():
    assert not exact_match("No, €4.90 per seller", "No, it costs €4.90")


def test_token_f1_on_the_worked_example():
    # 'no 4.90 per seller' against 'no it costs 4.90': two words shared out of four each.
    assert token_f1("No, €4.90 per seller", "No, it costs €4.90") == pytest.approx(0.5)


def test_token_f1_extremes():
    assert token_f1("21 days", "21 days") == 1.0
    assert token_f1("yes", "no") == 0.0
    assert token_f1("", "") == 1.0
    assert token_f1("", "21 days") == 0.0


def test_p90_of_one_to_ten_is_nine():
    assert p90(list(range(1, 11))) == 9


def test_swap_flags_a_judge_that_always_says_a():
    pairs = [("G01", "x", "y")]
    assert swap_test(lambda item, a, b: "A", pairs) == ["G01: first both times"]


def test_swap_does_not_flag_a_judge_that_follows_the_content():
    # The judge knows which answer is right and picks it, whatever its position.
    right = "right answer"

    def judge(item, a, b):
        return "A" if a == right else "B"

    assert swap_test(judge, [("G01", right, "wrong answer")]) == []


def test_pareto_on_the_lectures_published_figures():
    # Lecture figures, run 2026-10-20: right out of 10, dollars per 1,000 questions, median seconds.
    variants = {
        "Haiku 4.5": {"right": 8, "usd": 2.39, "s": 2.9},
        "Haiku 5.5": {"right": 9, "usd": 0.37, "s": 2.5},
        "Sonnet 5.5": {"right": 9, "usd": 6.78, "s": 2.6},
    }
    assert dominated(variants["Haiku 4.5"], variants["Haiku 5.5"])
    assert pareto_front(variants) == ["Haiku 5.5"]


def test_pareto_keeps_a_variant_that_wins_on_one_axis():
    variants = {
        "cheap": {"right": 7, "usd": 0.1, "s": 1.0},
        "good": {"right": 9, "usd": 5.0, "s": 3.0},
    }
    assert set(pareto_front(variants)) == {"cheap", "good"}


def test_cache_key_depends_on_the_model():
    a = cache_key("claude-haiku-5-5", "system", "question")
    assert a == cache_key("claude-haiku-5-5", "system", "question")
    assert a != cache_key("claude-sonnet-5-5", "system", "question")
    assert len(a) == 64


def test_cost_counts_input_and_output_at_their_own_prices():
    price = Price(input=1.0, output=5.0)
    assert cost(Usage(input_tokens=1000, output_tokens=100), price) == pytest.approx(0.0015)


def test_cost_without_output_is_lower():
    price = Price(input=1.0, output=5.0)
    usage = Usage(input_tokens=1000, output_tokens=100)
    assert cost(usage, price, count_output=False) < cost(usage, price)


def test_cache_write_and_read_are_priced_as_multipliers():
    price = Price(input=2.0, output=10.0)
    usage = Usage(input_tokens=0, output_tokens=0, cache_write_tokens=1_000_000, cache_read_tokens=1_000_000)
    # write: 1.25 x input price; read: 0.10 x input price
    assert cost(usage, price) == pytest.approx(2.0 * 1.25 + 2.0 * 0.10)
