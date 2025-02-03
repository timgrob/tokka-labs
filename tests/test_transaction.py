from models.transaction import Transaction


def test_instantiate_transaction():
    txn_info = {
        "block_number": 12345678,
        "time_stamp": 1738609294,
        "hash": "0x125e0b641d4a4b08806bf52c0c6757648c9963bcda8681e4f996f09e00d4c2cc",
        "gas_price": 1000000000,
        "gas_used": 20
    }
    txn = Transaction(**txn_info)

    assert isinstance(txn, Transaction)
    assert txn.block_number == 12345678
    assert txn.time_stamp == 1738609294
    assert txn.hash == "0x125e0b641d4a4b08806bf52c0c6757648c9963bcda8681e4f996f09e00d4c2cc"
    assert txn.gas_price == 1000000000
    assert txn.gas_used == 20
    assert txn.gas_fee == 2*1E-8


def test_instantiate_transaction_casting():
    txn_info = {
        "block_number": "12345678",
        "time_stamp": "1738609294",
        "hash": "0x125e0b641d4a4b08806bf52c0c6757648c9963bcda8681e4f996f09e00d4c2cc",
        "gas_price": "1000000000",
        "gas_used": "20"
    }
    txn = Transaction(**txn_info)

    assert isinstance(txn, Transaction)
    assert isinstance(txn.block_number, int)
    assert txn.block_number == 12345678
    assert isinstance(txn.time_stamp, int)
    assert txn.time_stamp == 1738609294
    assert txn.hash == "0x125e0b641d4a4b08806bf52c0c6757648c9963bcda8681e4f996f09e00d4c2cc"
    assert isinstance(txn.gas_price, int)
    assert txn.gas_price == 1000000000
    assert isinstance(txn.gas_used, int)
    assert txn.gas_used == 20
    assert txn.gas_fee == 2*1E-8
    