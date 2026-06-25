import sqlite3
from contextlib import contextmanager
from pathlib import Path

_DB_PATH = Path(__file__).parent / "helpbot.db"
_SCHEMA = Path(__file__).parent / "schema.sql"
_SEED = Path(__file__).parent / "seed.sql"
_SCHEMA_VERSION = 1  # bump whenever schema.sql changes


def _init() -> None:
    if _DB_PATH.exists():
        _DB_PATH.unlink()
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA.read_text())
    conn.executescript(_SEED.read_text())
    conn.close()


def _schema_outdated() -> bool:
    if not _DB_PATH.exists():
        return True
    conn = sqlite3.connect(_DB_PATH)
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    conn.close()
    return version < _SCHEMA_VERSION


@contextmanager
def get_connection():
    if _schema_outdated():
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
