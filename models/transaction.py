from pydantic import BaseModel


class Transaction(BaseModel):
    block_number: int
    time_stamp: int
    hash: str
    gas: float
    gas_price: float
    gas_used: float

