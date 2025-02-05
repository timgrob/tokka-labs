from sqlmodel import SQLModel
from pydantic import validator
from typing import Optional


class TimePeriod(SQLModel):
    start_timestamp: int
    end_timestamp: Optional[int]

    @validator("end_timestamp")
    def validate_timestamps(cls, end_timestamp: int, values: dict):
        start_timestamp = values.get("start_timestamp")

        if start_timestamp is None:
            raise ValueError('start_timestamp must be provided before end_timestamp')
            
        if end_timestamp <= start_timestamp:
            raise ValueError("end_timestamp must be after start_timestamp")

        return end_timestamp