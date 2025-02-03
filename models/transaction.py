from pydantic import BaseModel


WAI = 1E-18


class Transaction(BaseModel):
    block_number: int
    time_stamp: int
    hash: str
    gas: float
    gas_price: float
    gas_used: float

    @property
    def gas_fee(self) -> float:
        # Returns transaction fees in ETH
        return self.gas_used * self.gas_price * WAI
    

