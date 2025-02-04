import pytest
from services.etherscan import fetch_all_transactions
from models.transaction import Transaction


@pytest.mark.asyncio
async def test_fetch_all_transactions():
    response = await fetch_all_transactions()

    assert isinstance(response, list)
    assert len(response) > 0
    assert isinstance(response[0], Transaction)

    first_txn = response[0]

    assert first_txn.block_number == 12376729
    assert first_txn.time_stamp == 1620250931
    assert first_txn.hash == "0x125e0b641d4a4b08806bf52c0c6757648c9963bcda8681e4f996f09e00d4c2cc"
