import logging
from .config import settings
from .stel_client import StelClient
from .sheets import SheetClient
from .repo import get_conn, get_cursor, set_cursor, upsert_client


def normalize(raw: dict) -> dict:
    created = (
        raw.get("created_at")
        or raw.get("fechaAlta")
        or "1970-01-01T00:00:00Z"
    )
    updated = (
        raw.get("updated_at")
        or raw.get("modifiedAt")
        or created
    )
    return {
        "client_id": str(raw.get("id")),
        "name": raw.get("name", ""),
        "email": raw.get("email", ""),
        "phone": raw.get("phone", ""),
        "address": raw.get("address", ""),
        "created_at": created,
        "updated_at": updated,
    }


def run_sync():
    conn = get_conn(settings.db_path)
    cursor = get_cursor(conn)
    stel = StelClient(settings.stel_base_url, settings.stel_api_key, settings.stel_page_size)
    sheets = SheetClient(settings.sheets_spreadsheet_id, settings.google_application_credentials)
    inserts = []
    updates = []
    max_updated = cursor
    for raw in stel.list_clients_incremental(cursor or "1970-01-01T00:00:00Z"):
        norm = normalize(raw)
        if cursor and norm["updated_at"] <= cursor:
            continue
        result = upsert_client(conn, norm)
        if result == "insert":
            inserts.append(norm)
        elif result == "update":
            updates.append(norm)
        if not max_updated or norm["updated_at"] > max_updated:
            max_updated = norm["updated_at"]
    sheets.upserts(inserts + updates)
    if max_updated:
        set_cursor(conn, max_updated)
    conn.close()
    metrics = {"inserts": len(inserts), "updates": len(updates), "cursor": max_updated}
    logging.info("sync metrics %s", metrics)
    return metrics


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_sync()
