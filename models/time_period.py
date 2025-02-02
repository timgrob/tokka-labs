from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TimePeriod(BaseModel):
    start_time: datetime
    end_time: Optional[datetime]