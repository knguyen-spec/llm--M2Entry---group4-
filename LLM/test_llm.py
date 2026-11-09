"""Offline tests: a fake client replaces the API, so no key and no paid call are needed."""
from types import SimpleNamespace

import anthropic
import httpx
import pytest
from pydantic import ValidationError

import src.llm as llm
from src.schema import TicketClassification

VALID = '{"label": "billing", "confidence": 0.92, "needs_human_review": false}'
INVALID_RULE = '{"label": "other", "confidence": 0.40, "needs_human_review": false}'
NOT_JSON = "Sure! The label is billing."


def reply(text, stop_reason="end_turn", input_tokens=100, output_tokens=20):
    return SimpleNamespace(
        stop_reason=stop_reason,
        content=[SimpleNamespace(type="text", text=text)],
        usage=SimpleNamespace(input_tokens=input_tokens, output_tokens=output_tokens),
    )


def scripted(*responses):
    """A fake call that returns the given responses in order and records the messages sent."""
    sent = []
    queue = list(responses)

    def call(system, messages):
        sent.append(list(messages))
        item = queue.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    call.sent = sent
    return call


@pytest.fixture(autouse=True)
def isolated_log(tmp_path, monkeypatch):
    monkeypatch.setattr(llm, "CALLS_LOG", tmp_path / "calls.csv")
    return tmp_path / "calls.csv"


def log_rows(path):
    return path.read_text(encoding="utf-8").splitlines()


def test_valid_answer_passes_on_first_attempt(isolated_log):
    result = llm.classify("My card was charged twice.", call=scripted(reply(VALID)))
    assert result.reason == "ok"
    assert result.attempts == 1
    assert result.classification.label == "billing"
    rows = log_rows(isolated_log)
    assert rows[0] == ",".join(llm.CALLS_HEADER)
    assert len(rows) == 2  # header plus one call
    assert rows[1].endswith(",1,True")


def test_invalid_then_valid_reprompts_with_the_error(isolated_log):
    fake = scripted(reply(INVALID_RULE), reply(VALID))
    result = llm.classify("Unclear ticket.", call=fake)
    assert result.reason == "ok"
    assert result.attempts == 2
    # The second call carries the rule message back to the model.
    feedback = fake.sent[1][-1]["content"]
    assert "needs_human_review" in feedback
    assert len(log_rows(isolated_log)) == 3  # header plus two calls


def test_gives_up_after_two_reprompts():
    fake = scripted(reply(NOT_JSON), reply(NOT_JSON), reply(NOT_JSON))
    result = llm.classify("Anything.", call=fake)
    assert result.classification is None
    assert result.reason == "gave up after re-prompts"
    assert result.attempts == 3
    assert len(fake.sent) == 3


def test_max_tokens_is_not_reprompted():
    fake = scripted(reply(VALID, stop_reason="max_tokens"))
    result = llm.classify("Anything.", call=fake)
    assert result.classification is None
    assert result.reason == "stopped: max_tokens"
    assert len(fake.sent) == 1


def test_refusal_is_not_reprompted():
    fake = scripted(reply("", stop_reason="refusal"))
    result = llm.classify("Anything.", call=fake)
    assert result.reason == "stopped: refusal"
    assert len(fake.sent) == 1


def test_api_error_returns_a_failure_instead_of_crashing():
    request = httpx.Request("POST", "https://example.invalid/v1/messages")
    error = anthropic.APIConnectionError(request=request)
    result = llm.classify("Anything.", call=scripted(error))
    assert result.classification is None
    assert result.reason == "api error: APIConnectionError"


def test_rule_other_requires_review():
    with pytest.raises(ValidationError) as info:
        TicketClassification(label="other", confidence=0.9, needs_human_review=False)
    assert "needs_human_review to true" in str(info.value)


def test_rule_low_confidence_requires_review():
    with pytest.raises(ValidationError) as info:
        TicketClassification(label="billing", confidence=0.5, needs_human_review=False)
    assert "below 0.70" in str(info.value)


def test_confidence_outside_range_is_rejected():
    with pytest.raises(ValidationError):
        TicketClassification(label="billing", confidence=1.4, needs_human_review=False)
