import sqlite3
import hashlib


def get_conn(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT)")
    cur.execute(
        """CREATE TABLE IF NOT EXISTS clients (
        client_id TEXT PRIMARY KEY,
        name TEXT,
        email TEXT,
        phone TEXT,
        address TEXT,
        created_at TEXT,
        updated_at TEXT,
        hash TEXT
    )""",
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS sync_audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT,
        inserts INTEGER,
        updates INTEGER,
        duration REAL,
        error TEXT
    )""",
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_clients_updated_at ON clients(datetime(updated_at))"
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_clients_name ON clients(name)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_clients_email ON clients(email)")
    conn.commit()
    return conn


def get_cursor(conn: sqlite3.Connection):
    cur = conn.execute("SELECT v FROM meta WHERE k='cursor_updated_at'")
    row = cur.fetchone()
    return row["v"] if row else None


def set_cursor(conn: sqlite3.Connection, value: str):
    conn.execute(
        "INSERT OR REPLACE INTO meta(k, v) VALUES('cursor_updated_at', ?)", (value,)
    )
    conn.commit()


def compute_hash(c: dict) -> str:
    # Garantiza string en todos los campos relevantes
    fields = ("name", "email", "phone", "address", "created_at", "updated_at")
    payload = "|".join((c.get(k) or "") for k in fields)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def upsert_client(conn: sqlite3.Connection, c: dict):
    c_hash = compute_hash(c)
    cur = conn.execute("SELECT hash FROM clients WHERE client_id=?", (c["client_id"],))
    row = cur.fetchone()
    if row:
        if row["hash"] == c_hash:
            return "skip"
        conn.execute(
            """UPDATE clients SET name=?, email=?, phone=?, address=?, created_at=?, updated_at=?, hash=? WHERE client_id=?""",
            (
                c["name"],
                c["email"],
                c["phone"],
                c["address"],
                c["created_at"],
                c["updated_at"],
                c_hash,
                c["client_id"],
            ),
        )
        conn.commit()
        return "update"
    conn.execute(
        """INSERT INTO clients(client_id, name, email, phone, address, created_at, updated_at, hash)
        VALUES(?,?,?,?,?,?,?,?)""",
        (
            c["client_id"],
            c["name"],
            c["email"],
            c["phone"],
            c["address"],
            c["created_at"],
            c["updated_at"],
            c_hash,
        ),
    )
    conn.commit()
    return "insert"


def list_clients(conn: sqlite3.Connection, limit: int, offset: int):
    cur = conn.execute(
        "SELECT client_id, name, email, phone, address, created_at, updated_at FROM clients ORDER BY datetime(updated_at) DESC LIMIT ? OFFSET ?",
        (limit, offset),
    )
    return [dict(row) for row in cur.fetchall()]


def search_clients(
    conn: sqlite3.Connection, q: str, fields: list[str], limit: int, offset: int
):
    like = f"%{q.lower()}%"
    where = " OR ".join([f"lower({f}) LIKE ?" for f in fields])
    params = [like] * len(fields) + [limit, offset]
    cur = conn.execute(
        f"SELECT client_id, name, email, phone, address, created_at, updated_at FROM clients WHERE {where} ORDER BY datetime(updated_at) DESC LIMIT ? OFFSET ?",
        params,
    )
    return [dict(row) for row in cur.fetchall()]


def insert_audit(conn: sqlite3.Connection, metrics: dict):
    conn.execute(
        "INSERT INTO sync_audit(ts, inserts, updates, duration, error) VALUES(?,?,?,?,?)",
        (
            metrics.get("ts"),
            metrics.get("inserts", 0),
            metrics.get("updates", 0),
            metrics.get("duration", 0.0),
            metrics.get("error"),
        ),
    )
    conn.commit()


def count_clients(conn: sqlite3.Connection) -> int:
    cur = conn.execute("SELECT COUNT(*) FROM clients")
    return cur.fetchone()[0]


def get_last_audit(conn: sqlite3.Connection) -> dict | None:
    cur = conn.execute(
        "SELECT ts, inserts, updates, duration, error FROM sync_audit ORDER BY id DESC LIMIT 1"
    )
    row = cur.fetchone()
    return dict(row) if row else None
