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
