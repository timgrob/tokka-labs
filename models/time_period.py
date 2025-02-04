from pydantic import BaseModel, PositiveInt, validator
from typing import Optional


class TimePeriod(BaseModel):
    start_timestamp: PositiveInt
    end_timestamp: Optional[PositiveInt]

    @validator("end_timestamp")
    def check_timestamp_order(cls, end_timestamp, values):
        start_timestamp = values.get("start_timestamp")
        if end_timestamp <= start_timestamp:
            raise ValueError("end_timestamp must be after start_timestamp")
        return end_timestamp