from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool
from main import app, get_session
import pytest


client = TestClient(app)

TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, echo=True, connect_args={"check_same_thread": False}, poolclass=StaticPool)


def get_test_session():
    with Session(engine) as session:
        yield session

app.dependency_overrides[get_session] = get_test_session


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def test_txns() -> list[dict]:
    txn_1 = {"block_number": 1111111, "time_stamp": 1620252901, "hash": "0x00", "gas_price": 60000000000, "gas_used": 200000}
    txn_2 = {"block_number": 2222222, "time_stamp": 1620250921, "hash": "0x01", "gas_price": 61000000000, "gas_used": 210000}
    txn_3 = {"block_number": 3333333, "time_stamp": 1620250931, "hash": "0x02", "gas_price": 62000000000, "gas_used": 220000}
    return [txn_1, txn_2, txn_3]


def test_index():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "server is running"}


def test_create_transaction(test_txns):
    txn = test_txns[0]
    response = client.post("/api/v1/txn", json=txn)
    result = response.json()["result"]

    assert response.status_code == 200
    assert isinstance(result, dict)
    assert result["hash"] == "0x00"


def test_all_transactions(test_txns):
    # Persist test transactions in database
    for txn in test_txns:
        client.post("/api/v1/txn", json=txn)

    response = client.get("/api/v1/txns")
    result = response.json()["result"]

    assert response.status_code == 200
    assert isinstance(result, list)
    assert len(result) == 3


def test_transactions_by_hash(test_txns):
    # Persist test transaction in database
    txn = test_txns[0]
    client.post("/api/v1/txn", json=txn)

    txn_hash = "0x00"
    response = client.get(f"/api/v1/txns/{txn_hash}")
    result = response.json()["result"]
    
    assert response.status_code == 200
    assert isinstance(result, list)
    assert result[0]["hash"] == "0x00"


def test_transactions_by_hash_not_found():
    txn_hash = "0x03"
    response = client.get(f"/api/v1/txns/{txn_hash}")

    assert response.status_code == 404
    assert response.json() == {"detail":"Transaction not found"}


def test_transactions_in_time_span(test_txns):
    # Persist test transactions in database
    for txn in test_txns:
        client.post("/api/v1/txn", json=txn)

    time_span_json = {"start_timestamp": 1620252900, "end_timestamp": 1620252910}
    response = client.post("/api/v1/txns", json=time_span_json)
    result = response.json()["result"]

    assert response.status_code == 200
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["hash"] == "0x00"


def test_transactions_in_time_period_faulty_time_span():
    time_span_json = {"start_timestamp": 1620250931, "end_timestamp": 1620252901}
    response = client.post("/api/v1/txns", json=time_span_json)

    assert response.status_code == 404
    assert response.json() == {'detail': 'No transactions found in time span'}


def test_transaction_fees_by_hash(test_txns):
    # Persist test transaction in database
    txn = test_txns[0]
    client.post("/api/v1/txn", json=txn)

    txn_hash = "0x00"
    response = client.get(f"/api/v1/txn-fees/{txn_hash}")

    assert response.status_code == 200
    assert response.json() == {'status': 200, 'message': 'OK', 'gas_fee_usdt': 41.320679999999996}


def test_transaction_fees_by_hash_not_found():
    txn_hash = "0x03"
    response = client.get(f"/api/v1/txn-fees/{txn_hash}")

    assert response.status_code == 404
    assert response.json() == {"detail":"No transaction found"}


def test_transaction_fees_in_time_period(test_txns):
    # Persist test transactions in database
    for txn in test_txns:
        client.post("/api/v1/txn", json=txn)

    time_span_json = {"start_timestamp": 1620250900, "end_timestamp": 1620252940}
    response = client.post("/api/v1/txn-fees", json=time_span_json)

    assert response.status_code == 200
    assert "gas_fee_usdt" in response.json()


def test_transaction_fees_in_time_period_faulty_time_span():
    time_span_json = {"start_timestamp": 1620252901, "end_timestamp": 1620250931}
    response = client.post("/api/v1/txn-fees", json=time_span_json)

    assert response.status_code == 422
    assert response.json() == {"detail": [{"loc": ["body", "end_timestamp"], "msg": "end_timestamp must be after start_timestamp", "type": "value_error"}]}
