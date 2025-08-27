from backend.sync import normalize


def test_normalize_basic():
    raw = {
        "id": "1",
        "legal-name": "Foo",
        "email": "a@b.com",
        "phone": "123",
        "address": {"address": "Street"},
        "creation-date": "2024-01-01T00:00:00Z",
        "utc-last-modification-date": "2024-01-02T00:00:00Z",
    }
    norm = normalize(raw)
    assert norm["client_id"] == "1"
    assert norm["name"] == "Foo"
    assert norm["email"] == "a@b.com"
    assert norm["phone"] == "123"
    assert norm["address"] == "Street"
    assert norm["created_at"] == "2024-01-01T00:00:00Z"
    assert norm["updated_at"] == "2024-01-02T00:00:00Z"
