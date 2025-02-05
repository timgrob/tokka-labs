from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_index():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "server is running"}


def test_all_transactions():
    response = client.get("/api/v1/txns")
    result = response.json()["result"]

    assert response.status_code == 200
    assert isinstance(result, list)


def test_transactions_by_hash():
    txn_hash = "0x125e0b641d4a4b08806bf52c0c6757648c9963bcda8681e4f996f09e00d4c2cc"
    response = client.get(f"/api/v1/txns/{txn_hash}")
    result = response.json()["result"]

    assert response.status_code == 200
    assert  isinstance(result, list)
    assert len(result) == 2


def test_transactions_by_hash_not_found():
    txn_hash = "0x01"
    response = client.get(f"/api/v1/txns/{txn_hash}")

    assert response.status_code == 404
    assert response.json() == {"detail":"Transaction not found"}


def test_transactions_in_time_span():
    time_span_json = {"start_timestamp": 1620250931, "end_timestamp": 1620254651}
    response = client.post("/api/v1/txns", json=time_span_json)
    result = response.json()["result"]

    assert response.status_code == 200
    assert isinstance(result, list)
    assert len(result) == 8


def test_transactions_in_time_period_faulty_time_span():
    time_span_json = {"start_timestamp": 1620252901, "end_timestamp": 1620250931}
    response = client.post("/api/v1/txns", json=time_span_json)

    assert response.status_code == 422
    assert response.json() == {"detail": [{"loc": ["body", "end_timestamp"], "msg": "end_timestamp must be after start_timestamp", "type": "value_error"}]
}

def test_transaction_fees_by_hash():
    txn_hash = "0x125e0b641d4a4b08806bf52c0c6757648c9963bcda8681e4f996f09e00d4c2cc"
    response = client.get(f"/api/v1/txn-fees/{txn_hash}")
    fees = response.json()["gas_fee_usdt"]

    assert response.status_code == 200
    assert fees == 1140.197909488


def test_transaction_fees_by_hash_not_found():
    txn_hash = "0x00"
    response = client.get(f"/api/v1/txn-fees/{txn_hash}")

    assert response.status_code == 404
    assert response.json() == {"detail":"No transaction found"}


def test_transaction_fees_in_time_period():
    time_span_json = {"start_timestamp": 1620250931, "end_timestamp": 1620252901}
    response = client.post("/api/v1/txn-fees", json=time_span_json)
    fees = response.json()["gas_fee_usdt"]

    assert response.status_code == 200
    assert fees == 1199.3995683250241


def test_transaction_fees_in_time_period_faulty_time_span():
    time_span_json = {"start_timestamp": 1620252901, "end_timestamp": 1620250931}
    response = client.post("/api/v1/txn-fees", json=time_span_json)

    assert response.status_code == 422
    assert response.json() == {"detail": [{"loc": ["body", "end_timestamp"], "msg": "end_timestamp must be after start_timestamp", "type": "value_error"}]
}
