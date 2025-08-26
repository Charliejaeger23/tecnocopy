from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .config import settings
from .repo import get_conn, list_clients
from .sync import run_sync

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    return {"ok": True}


@app.get("/api/clients")
def get_clients(limit: int = 100, offset: int = 0):
    conn = get_conn(settings.db_path)
    try:
        return list_clients(conn, limit, offset)
    finally:
        conn.close()


@app.post("/api/sync")
def trigger_sync():
    return run_sync()
