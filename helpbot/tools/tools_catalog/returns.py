from helpbot.tools.engine.base import Tool
from helpbot.db import get_connection


class CheckReturnEligibility(Tool):
    """Check whether a customer's order is eligible for a return."""
    properties = {
        "order_id": "The order ID to check return eligibility for, e.g. PT-1001",
    }

    def run(self, order_id: str, session_email: str | None = None) -> dict:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM return_eligibility WHERE order_id = ?", (order_id.upper(),)).fetchone()
        if not row or (session_email and row["email"] != session_email):
            return {"found": False, "access_denied": True, "message": "No order found or access denied."}
        return {"found": True, **dict(row), "eligible": bool(row["eligible"])}


class GetRefundStatus(Tool):
    """Get the current processing stage of a refund for a given order."""
    properties = {
        "order_id": "The order ID to look up refund status for, e.g. PT-1001",
    }

    def run(self, order_id: str, session_email: str | None = None) -> dict:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM refunds WHERE order_id = ?", (order_id.upper(),)).fetchone()
        if not row or (session_email and row["email"] != session_email):
            return {"found": False, "access_denied": True, "message": "No order found or access denied."}
        return {"found": True, **dict(row)}
