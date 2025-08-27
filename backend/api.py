from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
import json
from .config import settings
from .repo import (
    get_conn,
    get_cursor,
    list_clients,
    search_clients,
    count_clients,
    get_last_audit,
)
from .sync import run_sync
from .sheets import SheetClient

logging.basicConfig(level=logging.INFO, format="%(message)s")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


scheduler = AsyncIOScheduler()


@app.on_event("startup")
def on_startup():
    scheduler.add_job(
        run_sync,
        "interval",
        seconds=settings.sync_interval_seconds,
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()


@app.on_event("shutdown")
def on_shutdown():
    scheduler.shutdown()


@app.get("/api/health")
def health():
    conn = get_conn(settings.db_path)
    try:
        cursor = get_cursor(conn)
        db_ok = True
        last_audit = get_last_audit(conn)
    except Exception:
        db_ok = False
        cursor = None
        last_audit = None
    finally:
        conn.close()
    try:
        sheet = SheetClient(
            settings.sheets_spreadsheet_id, settings.google_application_credentials
        )
        sheets_ok = sheet.ping()
    except Exception:
        sheets_ok = False
    return {
        "db": db_ok,
        "sheets": sheets_ok,
        "cursor": cursor,
        "last_sync_at": last_audit.get("ts") if last_audit else None,
    }


@app.get("/api/clients")
def get_clients(limit: int = 100, offset: int = 0):
    conn = get_conn(settings.db_path)
    try:
        return list_clients(conn, limit, offset)
    finally:
        conn.close()


@app.get("/api/clients/search")
def search(q: str, fields: str = "name,email", limit: int = 100, offset: int = 0):
    conn = get_conn(settings.db_path)
    try:
        field_list = [f.strip() for f in fields.split(",") if f]
        return search_clients(conn, q, field_list, limit, offset)
    finally:
        conn.close()


@app.get("/api/metrics")
def metrics():
    conn = get_conn(settings.db_path)
    try:
        total = count_clients(conn)
        last = get_last_audit(conn) or {}
    finally:
        conn.close()
    return {"total_clients": total, **last}


@app.post("/api/sync")
def trigger_sync():
    return run_sync()
