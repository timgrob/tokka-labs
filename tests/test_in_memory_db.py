import pytest
from models.transaction import Transaction
from databases.in_memory_db import InMemoryDB


@pytest.fixture
def db() -> InMemoryDB:
    return InMemoryDB()


@pytest.fixture
def txn_1() -> Transaction:
    txn = Transaction(
        block_number=1, 
        time_stamp=1738672400, 
        hash="0x00", 
        gas_price=60000000000, 
        gas_used=5000000
    )
    return txn


@pytest.fixture
def txn_2() -> Transaction:
    txn = Transaction(
        block_number=1, 
        time_stamp=1738672400, 
        hash="0x01", 
        gas_price=61000000000, 
        gas_used=5100000
    )
    return txn


@pytest.fixture
def txn_3():
    txn = Transaction(
        block_number=2, 
        time_stamp=1738672500, 
        hash="0x02", 
        gas_price=62000000000, 
        gas_used=5200000
    )
    return txn


@pytest.fixture
def txns(txn_1, txn_2, txn_3):
    return [txn_1, txn_2, txn_3]


@pytest.mark.asyncio
async def test_add_txn(db: InMemoryDB, txn_1: Transaction, txn_2: Transaction):
    await db.add_txn(txn_1)
    await db.add_txn(txn_2)

    assert len(db._hash_to_transaction) == 2

    txn1 = db._hash_to_transaction[txn_1.hash]
    assert isinstance(txn1, Transaction)
    assert txn1.block_number == 1
    assert txn1.hash == "0x00"

    txn2 = db._hash_to_transaction[txn_2.hash]
    assert isinstance(txn2, Transaction)
    assert txn2.hash == "0x01"
    assert txn2.block_number == 1


@pytest.mark.asyncio
async def test_add_txn_twice(db: InMemoryDB, txn_1: Transaction):
    await db.add_txn(txn_1)
    await db.add_txn(txn_1)

    assert len(db._hash_to_transaction) == 1


@pytest.mark.asyncio
async def test_add_txns(db: InMemoryDB, txns: list[Transaction]):
    await db.add_txns(txns)

    assert len(db._hash_to_transaction) == 3

    txn1 = db._hash_to_transaction[txns[0].hash]
    assert isinstance(txn1, Transaction)
    assert txn1.block_number == 1
    assert txn1.hash == "0x00"

    txn2 = db._hash_to_transaction[txns[1].hash]
    assert isinstance(txn2, Transaction)
    assert txn2.hash == "0x01"
    assert txn2.block_number == 1

    txn3 = db._hash_to_transaction[txns[2].hash]
    assert isinstance(txn3, Transaction)
    assert txn3.hash == "0x02"
    assert txn3.block_number == 2

    txns1 = db._timestamp_to_transaction[txns[0].time_stamp]
    assert isinstance(txns1, list)
    assert len(txns1) == 2

    txns2 = db._timestamp_to_transaction[txns[1].time_stamp]
    assert isinstance(txns2, list)
    assert len(txns2) == 2

    txns3 = db._timestamp_to_transaction[txns[2].time_stamp]
    assert isinstance(txns3, list)
    assert len(txns3) == 1
    

@pytest.mark.asyncio
async def test_clear(db: InMemoryDB, txn_1: Transaction):
    await db.add_txn(txn_1)
    assert len(db._hash_to_transaction) == 1

    await db.clear()
    assert len(db._hash_to_transaction) == 0


@pytest.mark.asyncio
async def test_has_txn_hash(db: InMemoryDB, txn_1: Transaction):
    await db.add_txn(txn_1)
    
    assert db.has_txn_hash("0x00") == True
    assert db.has_txn_hash("0x0A") == False
