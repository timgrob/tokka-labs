from pydantic import BaseModel


class Transaction(BaseModel):
    id: int
    timestamp: int
    hash_key: str
    block_number: int
    block_hash_key: str 
    nonce: int
    gas: float
    gas_price: float
    gas_used: float

