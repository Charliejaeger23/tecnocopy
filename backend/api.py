from fastapi import FastAPI, Query
from .repo import get_conn, list_clients, search_clients  # ajusta a tus nombres reales
from .config import settings

app = FastAPI()

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
    conn = get_conn(settings.db_path)
    try:
        return search_clients(conn, q=q, fields=fields, limit=limit, offset=offset)
    finally:
        conn.close()
