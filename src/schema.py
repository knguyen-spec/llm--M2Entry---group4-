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


class TicketClassification(BaseModel):
    label: Label
    confidence: float = Field(ge=0.0, le=1.0)
    needs_human_review: bool

    @model_validator(mode="after")
    def validate_review_rule(self):
        """
        A low-confidence or 'other' classification must be reviewed by a human.
        This cross-field rule cannot be expressed by the basic JSON schema alone.
        """
        if self.confidence < 0.70 and not self.needs_human_review:
            raise ValueError(
                "Set needs_human_review=true when confidence is below 0.70."
            )

        if self.label == "other" and not self.needs_human_review:
            raise ValueError(
                "Set needs_human_review=true when label is 'other'."
            )

        return self
