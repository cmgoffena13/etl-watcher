from src.types import ValidatorModel


class TimelinessPostInput(ValidatorModel):
    lookback_minutes: int = 60


class TimelinessPostOutput(ValidatorModel):
    status: str
