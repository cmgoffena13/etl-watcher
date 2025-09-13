from pydantic import Field

from src.types import ValidatorModel


class TimelinessPostInput(ValidatorModel):
    lookback_minutes: int = Field(ge=5, default=60)


class TimelinessPostOutput(ValidatorModel):
    status: str
