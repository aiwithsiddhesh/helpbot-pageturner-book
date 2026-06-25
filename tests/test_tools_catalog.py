from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import helpbot.db as db_module
from helpbot.tools.tools_catalog.books import CheckBookAvailability, GetRestockDate
from helpbot.tools.tools_catalog.orders import CheckOrderStatus, CancelOrder
from helpbot.tools.tools_catalog.returns import CheckReturnEligibility
from helpbot.tools.tools_catalog.promotions import ValidatePromoCode
from helpbot.tools.tools_catalog.gifts import CheckGiftOrder


def _make_test_db() -> Path:
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    db_path = Path(tmp.name)
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.executescript((Path(db_module.__file__).parent / "schema.sql").read_text())
    conn.executescript((Path(db_module.__file__).parent / "seed.sql").read_text())
    conn.close()
    return db_path


class BookToolsTests(unittest.TestCase):
    def setUp(self):
        self.db_path = _make_test_db()
        self.patcher = patch.object(db_module, "_DB_PATH", self.db_path)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.db_path.unlink(missing_ok=True)

    def test_check_book_availability_found(self):
        result = CheckBookAvailability().run("atomic habits")
        self.assertTrue(result["found"])
        self.assertIsInstance(result["formats"], list)

    def test_check_book_availability_fuzzy(self):
        result = CheckBookAvailability().run("atomic")
        self.assertTrue(result["found"])

    def test_check_book_availability_not_found(self):
        result = CheckBookAvailability().run("nonexistent book xyz")
        self.assertFalse(result["found"])

    def test_get_restock_date_found(self):
        result = GetRestockDate().run("dune")
        self.assertTrue(result["found"])
        self.assertIsNotNone(result["restock_date"])

    def test_get_restock_date_no_restock_info(self):
        # "sapiens" has restock_confidence='unknown' and no restock_date — tool returns not found
        result = GetRestockDate().run("nonexistent book xyz")
        self.assertFalse(result["found"])


class OrderToolsTests(unittest.TestCase):
    def setUp(self):
        self.db_path = _make_test_db()
        self.patcher = patch.object(db_module, "_DB_PATH", self.db_path)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.db_path.unlink(missing_ok=True)

    def test_check_order_status_found_with_matching_session(self):
        result = CheckOrderStatus().run("PT-1001", session_email="john.doe@example.com")
        self.assertTrue(result["found"])
        self.assertEqual(result["order_id"], "PT-1001")

    def test_check_order_status_access_denied_wrong_session(self):
        result = CheckOrderStatus().run("PT-1001", session_email="wrong@example.com")
        self.assertFalse(result["found"])
        self.assertTrue(result.get("access_denied"))

    def test_cancel_order_cancellable(self):
        result = CancelOrder().run("PT-1003", session_email="john.doe@example.com")
        self.assertTrue(result["success"])

    def test_cancel_order_not_cancellable(self):
        result = CancelOrder().run("PT-1001", session_email="john.doe@example.com")
        self.assertFalse(result["success"])


class ReturnToolsTests(unittest.TestCase):
    def setUp(self):
        self.db_path = _make_test_db()
        self.patcher = patch.object(db_module, "_DB_PATH", self.db_path)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.db_path.unlink(missing_ok=True)

    def test_eligible_order_returns_bool(self):
        result = CheckReturnEligibility().run("PT-1001", session_email="john.doe@example.com")
        self.assertTrue(result["found"])
        self.assertIsInstance(result["eligible"], bool)
        self.assertTrue(result["eligible"])

    def test_ineligible_order(self):
        result = CheckReturnEligibility().run("PT-1002", session_email="jane.smith@example.com")
        self.assertTrue(result["found"])
        self.assertFalse(result["eligible"])


class PromoToolsTests(unittest.TestCase):
    def setUp(self):
        self.db_path = _make_test_db()
        self.patcher = patch.object(db_module, "_DB_PATH", self.db_path)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.db_path.unlink(missing_ok=True)

    def test_valid_promo_code(self):
        result = ValidatePromoCode().run("SUMMER20")
        self.assertTrue(result["found"])
        self.assertIsInstance(result["valid"], bool)
        self.assertTrue(result["valid"])

    def test_expired_promo_code(self):
        result = ValidatePromoCode().run("WELCOME5")
        self.assertTrue(result["found"])
        self.assertFalse(result["valid"])

    def test_nonexistent_promo_code(self):
        result = ValidatePromoCode().run("FAKE99")
        self.assertFalse(result["found"])


class GiftToolsTests(unittest.TestCase):
    def setUp(self):
        self.db_path = _make_test_db()
        self.patcher = patch.object(db_module, "_DB_PATH", self.db_path)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.db_path.unlink(missing_ok=True)

    def test_lookup_by_gift_code(self):
        result = CheckGiftOrder().run(gift_code="GFT-1001")
        self.assertTrue(result["found"])
        self.assertIsInstance(result["items"], list)

    def test_lookup_by_recipient_email(self):
        result = CheckGiftOrder().run(recipient_email="sarah.c@example.com")
        self.assertTrue(result["found"])

    def test_lookup_by_partial_recipient_name(self):
        result = CheckGiftOrder().run(recipient_name="sarah")
        self.assertTrue(result["found"])

    def test_no_identifier_provided(self):
        result = CheckGiftOrder().run()
        self.assertFalse(result["found"])

    def test_not_found(self):
        result = CheckGiftOrder().run(gift_code="GFT-9999")
        self.assertFalse(result["found"])


if __name__ == "__main__":
    unittest.main()
