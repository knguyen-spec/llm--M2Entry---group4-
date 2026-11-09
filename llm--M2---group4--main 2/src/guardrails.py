"""Code defences for untrusted text, and the output check that runs before anything is sent.

No model, no API. These are the parts the component controls in code. Whether the model itself
follows an attack is measured by the live tests in tests/test_guardrails.py, which stay pending
until a model run exists.
"""
import re

# Contacts the company publishes. Fill in with the real values before the defence.
ALLOWED_CONTACTS: set[str] = set()

EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", re.IGNORECASE)
URL = re.compile(r"(?:https?://|www\.)\S+", re.IGNORECASE)
BARE_DOMAIN = re.compile(r"\b[\w-]+\.(?:example|com|net|org|io|fr|de|nl|es|it|be|ch)\b", re.IGNORECASE)
MAX_UNTRUSTED_CHARS = 500


def sanitise(untrusted: str) -> str:
    """Make untrusted text plain data before it goes into a prompt or a tool result.

    Removes links and contact details, collapses line breaks, and truncates.
    """
    text = URL.sub("[link removed]", untrusted)
    text = EMAIL.sub("[contact removed]", text)
    text = BARE_DOMAIN.sub("[domain removed]", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:MAX_UNTRUSTED_CHARS]


def output_check(text: str) -> bool:
    """True when the text contains a contact or link we do not publish. Such text must not be sent."""
    found = EMAIL.findall(text) + URL.findall(text) + BARE_DOMAIN.findall(text)
    return any(not _is_allowed(item) for item in found)


def _is_allowed(item: str) -> bool:
    return any(allowed in item.lower() for allowed in ALLOWED_CONTACTS)


REFUSAL = "I can't share that here. For any question about your order, please contact Albert's Marketplace."


def sent(text: str) -> str:
    """What really leaves the system: the model's text, or the refusal if the output check fails."""
    return REFUSAL if output_check(text) else text


# ---------------------------------------------------------------- the classifier's output check
#
# Our component never sends text written by the model: only a label from a fixed list and
# the review flag. These two functions build that record, and send a ticket to a person
# when it tries to give the model instructions. The live tests assert on this record.

INJECTION = re.compile(
    "|".join([
        r"\bignore\b.{0,40}\b(instructions?|rules?|prompt|above|previous)\b",
        r"\b(disregard|forget|override)\b.{0,40}\b(instructions?|rules?|prompt|task|previous)\b",
        r"\b(system|developer|hidden)\s*(prompt|message|instructions?)\b",
        r"\byou are now\b|\bnew (rule|instructions?)\b|\badmin mode\b|\bdeveloper mode\b",
        r"</?\s*(system|assistant|ticket|instructions?)\s*>",
        r"\b(classify|route|label|mark|set)\b.{0,30}\b(this|the)\s+(ticket|message)\b.{0,15}\bas\b",
        r"\bignore[rz]?\b.{0,30}\binstructions?\b|\boublie[rz]?\b.{0,30}\b(instructions?|consignes?)\b",
    ]),
    re.IGNORECASE | re.DOTALL,
)

SENT_KEYS = ("label", "needs_human_review", "injection_suspected")


def looks_like_injection(ticket: str) -> bool:
    """A cheap check in code. It does not need to catch everything: nothing the model
    writes is sent, and a hit only sends the ticket to a person."""
    return bool(INJECTION.search(ticket))


def sent_record(ticket: str, classification) -> dict:
    """What really leaves the component. Fails closed: no valid answer means a person reads it."""
    injection = looks_like_injection(ticket)
    if classification is None:
        return {"label": "other", "needs_human_review": True, "injection_suspected": injection}
    return {
        "label": classification.label,
        "needs_human_review": bool(classification.needs_human_review or injection),
        "injection_suspected": injection,
    }
