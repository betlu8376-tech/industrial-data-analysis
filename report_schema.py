from pydantic import BaseModel,Field,model_validator

from typing import Self


class FailureReport(BaseModel):
    total_count: int=Field(gt=0)
    failure_count: int=Field(ge=0)
    failure_rate_percent: float=Field(ge=0,le=100)
    conclusion: str=Field(min_length=1)

    @model_validator(mode='after')
    def check_failure_count(self) -> Self:
        if self.failure_count > self.total_count:
            raise ValueError("failure_count can not exceed total")
        expected_rate = round(self.failure_count* 100 / self.total_count, 2)
        if self.failure_rate_percent != expected_rate:
            raise ValueError("failure_rate_percent does not match counts")
        return self
