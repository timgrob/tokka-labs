from models.transaction import Transaction


WAI = 1E-18     # Wai unit in ETH 
GWAI = 1E-9     # Gwai unit in ETH


def calculate_total_gas_fees(txns: list[Transaction]) -> float:
    # CALCULATION FORMULA: total gas = units of gas used * (base fee + priority fee)
    # returns gas fees in ETH
    return sum([txn.gas_used * txn.gas_price * WAI for txn in txns])