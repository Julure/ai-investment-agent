import hashlib
import json
import sqlite3

import config

"sqlite key-value-cache to stay withing API key call limit"

def _connect() -> sqlite3.Connection:
    config.CACHE_DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(config.CACHE_DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS cache(
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            create_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    return conn

def make_key(*parts: str) -> str:
    """stabel cache key from string parts """
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode("UTF-8")).hexdigest()

def get(key: str):
    conn = _connect()
    try:
        row = conn.execute("SELECT value FROM cache WHERE key = ?", (key,)).fetchone()
        return json.loads(row[0]) if row else None
    finally:
        conn.close()


def set(key: str, value) -> None:
    conn = _connect()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO cache (key, value) VALUES (?, ?)",
            (key, json.dumps(value)),
        )
        conn.commit()
    finally:
        conn.close()


def cached(prefix: str):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            key = make_key(prefix, *map(str, args), *map(str, kwargs.values()))
            hit = get(key)
            if hit is not None:
                return hit
            result = fn(*args, **kwargs)
            set(key, result)
            return result

        return wrapper

    return decorator