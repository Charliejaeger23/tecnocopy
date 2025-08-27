import logging
import time
import json
import uuid
from datetime import datetime
from .config import settings
from .stel_client import StelClient
from .sheets import SheetClient
from .repo import (
    get_conn,
    get_cursor,
    set_cursor,
    upsert_client,
    insert_audit,
)


def normalize(raw: dict) -> dict:
    def _s(val):
        return "" if val is None else str(val).strip()

    addr = raw.get("main-address") or raw.get("address") or {}
    if isinstance(addr, dict):
        address = _s(addr.get("address") or addr.get("line") or addr.get("name"))
    else:
        address = _s(addr)

    return {
        "client_id": _s(raw.get("id") or raw.get("client-id") or raw.get("clientId")),
        "name": _s(raw.get("legal-name") or raw.get("name")),
        "email": _s(raw.get("email")),
        "phone": _s(raw.get("phone") or raw.get("phone1") or raw.get("phone2")),
        "address": address,
        # STEL suele traer estas fechas:
        "created_at": _s(
            raw.get("creation-date")
            or raw.get("created_at")
            or raw.get("utc-creation-date")
            or "1970-01-01T00:00:00Z"
        ),
        "updated_at": _s(
            raw.get("utc-last-modification-date")
            or raw.get("updated_at")
            or raw.get("modifiedAt")
            or raw.get("creation-date")
            or "1970-01-01T00:00:00Z"
        ),
    }


def run_sync():
    run_id = uuid.uuid4().hex
    start = time.time()
    metrics = {"run_id": run_id, "ts": datetime.utcnow().isoformat() + "Z"}
    conn = get_conn(settings.db_path)
    cursor = get_cursor(conn)
    stel = StelClient(
        settings.stel_base_url, settings.stel_api_key, settings.stel_page_size
    )
    sheets = SheetClient(
        settings.sheets_spreadsheet_id, settings.google_application_credentials
    )
    inserts = []
    updates = []
    max_updated = cursor
    try:
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
        metrics.update(
            {"inserts": len(inserts), "updates": len(updates), "cursor": max_updated}
        )
    except Exception as e:
        metrics["error"] = str(e)
        raise
    finally:
        metrics["duration"] = round(time.time() - start, 3)
        insert_audit(conn, metrics)
        conn.close()
        logging.info(json.dumps(metrics))
    return metrics


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_sync()
