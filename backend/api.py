# ... (código anterior sin tocar)

    return {
        "db": db_ok,
        "sheets": sheets_ok,
        "cursor": cursor,
        "last_sync_at": last_audit.get("ts") if last_audit else None,
    }

MAX_LIMIT = 200

@app.get("/api/clients")
def get_clients(
    limit: int = Query(100, ge=1, le=MAX_LIMIT),
    offset: int = Query(0, ge=0),
):
    conn = get_conn(settings.db_path)
    try:
        return list_clients(conn, limit, offset)
    finally:
        conn.close()

@app.get("/api/clients/search")
def search(
    q: str,
    fields: str = "name,email",
    limit: int = Query(100, ge=1, le=MAX_LIMIT),
    offset: int = Query(0, ge=0),
):
    # implementación existente; no cambies la lógica que ya tenías
    ...
