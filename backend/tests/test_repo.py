import sqlite3
from backend import repo


def test_upsert_and_search():
    conn = repo.get_conn(":memory:")
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
    rows = repo.search_clients(conn, "Alice", ["name"], 10, 0)
    assert len(rows) == 1
    assert rows[0]["name"] == "Alice"
