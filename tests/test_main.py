from fastapi.testclient import TestClient
from main import app
import pytest


client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup():
    txn_1 = {"block_number": 1111111, "time_stamp": 1620252901, "hash": "0x00", "gas_price": 60000000000, "gas_used": 200000}
    txn_2 = {"block_number": 2222222, "time_stamp": 1620250921, "hash": "0x01", "gas_price": 61000000000, "gas_used": 210000}
    client.post("/api/v1/txn", json=txn_1)
    client.post("/api/v1/txn", json=txn_2)


def test_index():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "server is running"}


def test_create_transaction():
    txn_new = {"block_number": 3333333, "time_stamp": 1620250931, "hash": "0x02", "gas_price": 62000000000, "gas_used": 220000}
    response = client.post("/api/v1/txn", json=txn_new)
    result = response.json()["result"]

    assert response.status_code == 200
    assert isinstance(result, dict)


def test_all_transactions():
    response = client.get("/api/v1/txns")
    result = response.json()["result"]

    assert response.status_code == 200
    assert isinstance(result, list)


def test_transactions_by_hash():
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


def test_transactions_in_time_span():
    time_span_json = {"start_timestamp": 1620250931, "end_timestamp": 1620254651}
    response = client.post("/api/v1/txns", json=time_span_json)
    result = response.json()["result"]

    assert response.status_code == 200
    assert isinstance(result, list)


def test_transactions_in_time_period_faulty_time_span():
    time_span_json = {"start_timestamp": 1620252901, "end_timestamp": 1620250931}
    response = client.post("/api/v1/txns", json=time_span_json)

    assert response.status_code == 422
    assert response.json() == {"detail": [{"loc": ["body", "end_timestamp"], "msg": "end_timestamp must be after start_timestamp", "type": "value_error"}]
}

def test_transaction_fees_by_hash():
    txn_hash = "0x00"
    response = client.get(f"/api/v1/txn-fees/{txn_hash}")

    assert response.status_code == 200
    assert "gas_fee_usdt" in response.json()


def test_transaction_fees_by_hash_not_found():
    txn_hash = "0x03"
    response = client.get(f"/api/v1/txn-fees/{txn_hash}")

    assert response.status_code == 404
    assert response.json() == {"detail":"No transaction found"}


def test_transaction_fees_in_time_period():
    time_span_json = {"start_timestamp": 1620250931, "end_timestamp": 1620252901}
    response = client.post("/api/v1/txn-fees", json=time_span_json)

    assert response.status_code == 200
    assert "gas_fee_usdt" in response.json()


def test_transaction_fees_in_time_period_faulty_time_span():
    time_span_json = {"start_timestamp": 1620252901, "end_timestamp": 1620250931}
    response = client.post("/api/v1/txn-fees", json=time_span_json)

    assert response.status_code == 422
    assert response.json() == {"detail": [{"loc": ["body", "end_timestamp"], "msg": "end_timestamp must be after start_timestamp", "type": "value_error"}]
}
