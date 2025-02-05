from sqlmodel import SQLModel, Field
from typing import Optional

WAI = 1E-18


class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    block_number: int = Field(nullable=False)
    time_stamp: int = Field(nullable=False, index=True)
    hash: str = Field(nullable=False, index=True)
    gas_price: int = Field(nullable=False)
    gas_used: int = Field(nullable=False)

    @property
    def gas_fee(self) -> float:
        # Returns transaction gas fees in ETH
        return self.gas_used * self.gas_price * WAI
