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
    )"""
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_clients_updated_at ON clients(datetime(updated_at))")
    conn.commit()
    return conn


def get_cursor(conn: sqlite3.Connection):
    cur = conn.execute("SELECT v FROM meta WHERE k='cursor_updated_at'")
    row = cur.fetchone()
    return row["v"] if row else None


def set_cursor(conn: sqlite3.Connection, value: str):
    conn.execute("INSERT OR REPLACE INTO meta(k, v) VALUES('cursor_updated_at', ?)", (value,))
    conn.commit()


def compute_hash(data: dict) -> str:
    relevant = "|".join(
        [
            data.get("name", ""),
            data.get("email", ""),
            data.get("phone", ""),
            data.get("address", ""),
            data.get("created_at", ""),
            data.get("updated_at", ""),
        ]
    )
    return hashlib.sha256(relevant.encode("utf-8")).hexdigest()


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
