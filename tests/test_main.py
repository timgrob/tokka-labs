from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_index():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "server is running"}


def test_fetch_all_transaction():
    response = client.get("/api/v1/txns")
    assert response.status_code == 200
