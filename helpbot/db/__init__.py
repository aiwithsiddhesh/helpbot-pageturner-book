import sqlite3
from pathlib import Path

_DB_PATH = Path(__file__).parent / "helpbot.db"
_SCHEMA = Path(__file__).parent / "schema.sql"
_SEED = Path(__file__).parent / "seed.sql"


def _init() -> None:
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA.read_text())
    conn.executescript(_SEED.read_text())
    conn.close()


def get_connection() -> sqlite3.Connection:
    if not _DB_PATH.exists():
        _init()
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
