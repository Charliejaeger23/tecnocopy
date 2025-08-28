import pytest
from fastapi.testclient import TestClient
from backend import api, repo, config


@pytest.fixture
def client(tmp_path):
    db_path = tmp_path / "test.db"
    conn = repo.get_conn(str(db_path))
    repo.upsert_client(
        conn,
        {
            "client_id": "1",
            "name": "Alice",
            "email": "a@b.com",
            "phone": "123",
            "address": "Street",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-02T00:00:00Z",
        },
    )
    conn.close()
    config.settings.db_path = str(db_path)
    return TestClient(api.app)


def test_health_returns_ok(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert "db" in body


def test_clients_search_smoke(client):
    r = client.get("/api/clients/search", params={"q": "Alice"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)
