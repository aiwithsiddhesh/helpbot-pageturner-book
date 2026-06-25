from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import helpbot.db as db_module


def _make_test_db() -> Path:
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    db_path = Path(tmp.name)
    conn = sqlite3.connect(db_path)
    conn.executescript((Path(db_module.__file__).parent / "schema.sql").read_text())
    conn.executescript((Path(db_module.__file__).parent / "seed.sql").read_text())
    conn.close()
    return db_path


class GetConnectionTests(unittest.TestCase):
    def setUp(self):
        self.db_path = _make_test_db()

    def tearDown(self):
        self.db_path.unlink(missing_ok=True)

    def test_connection_yields_rows(self):
        with patch.object(db_module, "_DB_PATH", self.db_path):
            with db_module.get_connection() as conn:
                row = conn.execute("SELECT * FROM orders WHERE order_id = 'PT-1001'").fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["order_id"], "PT-1001")

    def test_commit_on_success(self):
        with patch.object(db_module, "_DB_PATH", self.db_path):
            with db_module.get_connection() as conn:
                conn.execute("UPDATE orders SET status = 'cancelled' WHERE order_id = 'PT-1003'")
            with db_module.get_connection() as conn:
                row = conn.execute("SELECT status FROM orders WHERE order_id = 'PT-1003'").fetchone()
        self.assertEqual(row["status"], "cancelled")

    def test_rollback_on_exception(self):
        with patch.object(db_module, "_DB_PATH", self.db_path):
            try:
                with db_module.get_connection() as conn:
                    conn.execute("UPDATE orders SET status = 'cancelled' WHERE order_id = 'PT-1001'")
                    raise RuntimeError("simulated failure")
            except RuntimeError:
                pass
            with db_module.get_connection() as conn:
                row = conn.execute("SELECT status FROM orders WHERE order_id = 'PT-1001'").fetchone()
        self.assertEqual(row["status"], "in_transit")

    def test_schema_version_triggers_reinit(self):
        with patch.object(db_module, "_DB_PATH", self.db_path):
            with patch.object(db_module, "_SCHEMA_VERSION", 999):
                self.assertTrue(db_module._schema_outdated())


class SeedDataTests(unittest.TestCase):
    def setUp(self):
        self.db_path = _make_test_db()

    def tearDown(self):
        self.db_path.unlink(missing_ok=True)

    def test_orders_seeded(self):
        with patch.object(db_module, "_DB_PATH", self.db_path):
            with db_module.get_connection() as conn:
                count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        self.assertGreater(count, 0)

    def test_books_seeded(self):
        with patch.object(db_module, "_DB_PATH", self.db_path):
            with db_module.get_connection() as conn:
                row = conn.execute("SELECT * FROM books WHERE title = 'atomic habits'").fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["status"], "in_stock")

    def test_promo_codes_seeded(self):
        with patch.object(db_module, "_DB_PATH", self.db_path):
            with db_module.get_connection() as conn:
                row = conn.execute("SELECT * FROM promo_codes WHERE code = 'SUMMER20'").fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(bool(row["valid"]), True)


if __name__ == "__main__":
    unittest.main()
