from pydantic import BaseModel, PositiveInt


WAI = 1E-18


class Transaction(BaseModel):
    block_number: PositiveInt
    time_stamp: PositiveInt
    hash: str
    gas_price: int
    gas_used: int

    @property
    def gas_fee(self) -> float:
        # Returns transaction fees in ETH
        return self.gas_used * self.gas_price * WAI
    

