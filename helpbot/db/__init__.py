import sqlite3
from contextlib import contextmanager
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


@contextmanager
def get_connection():
    if not _DB_PATH.exists():
        _init()
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
