from sqlmodel import SQLModel, Field
from pydantic import validator
from typing import Optional
from datetime import datetime


class TimePeriod(SQLModel):
    start_timestamp: int
    end_timestamp: Optional[int] = Field(default_factory=lambda: int(datetime.utcnow().timestamp()))


    @validator("end_timestamp")
    def validate_timestamps(cls, end_timestamp: int, values: dict):
        start_timestamp = values.get("start_timestamp")

        if start_timestamp is None:
            raise ValueError('start_timestamp must be provided before end_timestamp')
            
        if end_timestamp <= start_timestamp:
            raise ValueError("end_timestamp must be after start_timestamp")

        return end_timestamp