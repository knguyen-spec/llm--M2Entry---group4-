"""The shape of the component's output, and the rules a JSON schema cannot express."""
from typing import Literal

from pydantic import BaseModel, Field, model_validator

Label = Literal[
    "billing",
    "delivery",
    "returns_refunds",
    "account",
    "seller",
    "product_information",
    "other",
]

REVIEW_THRESHOLD = 0.70


class TicketClassification(BaseModel):
    label: Label
    confidence: float = Field(ge=0.0, le=1.0)
    needs_human_review: bool

    @model_validator(mode="after")
    def check_review_rules(self):
        # These rules need two fields at once, so JSON schema cannot express them.
        if self.label == "other" and not self.needs_human_review:
            raise ValueError(
                "label is 'other', so set needs_human_review to true. "
                "Only the human reviewer can route an 'other' ticket."
            )
        if self.confidence < REVIEW_THRESHOLD and not self.needs_human_review:
            raise ValueError(
                f"confidence is {self.confidence:.2f}, below {REVIEW_THRESHOLD:.2f}, "
                "so set needs_human_review to true."
            )
        return self
