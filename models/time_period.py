from pydantic import BaseModel
from typing import Optional


class TimePeriod(BaseModel):
    start_timestamp: int
    end_timestamp: Optional[int]